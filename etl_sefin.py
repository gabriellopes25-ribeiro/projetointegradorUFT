import os
import sys
import logging
from decimal import Decimal
import pandas as pd
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ETL_SEFIN")

SCHEMA_PATH = "schema.sql"
CAMINHO_LIMPO = os.path.join("data", "limpo", "dados_limpos.csv")
CAMINHO_PRONTO = os.path.join("data", "pronto", "dados_prontos.csv")


def extrair_dados(executar_coletor_ao_vivo: bool = True, max_paginas_portal_novo: int = 5):
    """
    Fase de Extração Integrada:
      1. Aciona o ColetorSefinPalmasDual para diagnosticar e consumir as APIs reais da Prefeitura.
      2. Persiste automaticamente os registros reais de Receitas (Portal Novo) e Arrecadação (API Antiga)
         nas tabelas dedicadas do PostgreSQL (`prefeitura_receitas` e `prefeitura_historico_api_antiga`).
      3. Retorna (DataFrame_bruto, diagnostico_coleta).
    """
    logger.info("Iniciando fase de Extração integrada (Prefeitura de Palmas -> PostgreSQL)...")
    diagnostico = {"modo": "ARQUIVO_LOCAL", "registros_obtidos": 0}

    if executar_coletor_ao_vivo:
        try:
            from src.coleta.coletor_prefeitura import ColetorSefinPalmasDual
            from src.repositories.postgres_repository import RepositorioPostgreSQL

            coletor = ColetorSefinPalmasDual()
            dados_brutos, diagnostico = coletor.coletar_com_diagnostico(
                max_paginas_portal_novo=max_paginas_portal_novo,
            )
            if dados_brutos:
                # Se forem receitas reais do Portal Novo, carrega em lote na tabela prefeitura_receitas
                if "codigo" in dados_brutos[0] and "valor_arrecado_mes" in dados_brutos[0]:
                    repo = RepositorioPostgreSQL()
                    inseridos = repo.inserir_receitas_portal_novo_em_lote(dados_brutos, limpar_antes=False)
                    logger.info(f"{inseridos} registros reais do Portal Novo persistidos no PostgreSQL (prefeitura_receitas).")

                logger.info(
                    f"Dados brutos coletados via coletor ({len(dados_brutos)} registros, modo {diagnostico.get('modo')})."
                )
                return pd.DataFrame(dados_brutos), diagnostico
        except Exception as e:
            logger.warning(f"Coletor municipal não pôde ser executado diretamente ({e}). Buscando em data/bruto/...")

    pasta_bruto = os.path.join("data", "bruto")
    if os.path.exists(pasta_bruto) and os.listdir(pasta_bruto):
        arquivos = [
            os.path.join(pasta_bruto, f)
            for f in os.listdir(pasta_bruto)
            if f.endswith((".json", ".csv"))
        ]
        if arquivos:
            ultimo_arquivo = max(arquivos, key=os.path.getctime)
            logger.info(f"Carregando dados brutos do arquivo existente: {ultimo_arquivo}")
            if ultimo_arquivo.endswith(".json"):
                df = pd.read_json(ultimo_arquivo)
            else:
                df = pd.read_csv(ultimo_arquivo, sep=";")
            diagnostico["modo"] = f"ARQUIVO ({os.path.basename(ultimo_arquivo)})"
            diagnostico["registros_obtidos"] = len(df)
            return df, diagnostico

    from seeds.mock_data import obter_dividas_mock
    dados_mock = obter_dividas_mock()
    df_fallback = pd.DataFrame(dados_mock)
    diagnostico["modo"] = "CONTINGENCIA_SEEDS"
    diagnostico["registros_obtidos"] = len(df_fallback)
    return df_fallback, diagnostico


def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    mapeamento = {
        "cci": "inscricao_imobiliaria",
        "inscricao": "inscricao_imobiliaria",
        "inscricao_cci": "inscricao_imobiliaria",
        "ano": "exercicio_ano",
        "ano_exercicio": "exercicio_ano",
        "exercicio": "exercicio_ano",
        "cpf": "cpf_cnpj",
        "cnpj": "cpf_cnpj",
        "documento": "cpf_cnpj",
        "cpf_cnpj_contribuinte": "cpf_cnpj",
        "cpf_cnpj_proprietario": "cpf_cnpj",
        "valor": "valor_original",
        "vencimento": "data_vencimento",
        "status": "status_divida",
        "tributo": "tipo_tributo",
    }
    df = df.rename(columns=lambda c: mapeamento.get(str(c).lower().strip(), c))
    return df


def limpar_e_validar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Camada Silver:
    - Se o DataFrame vier do Portal Novo (`codigo`, `valor_arrecado_mes`), calcula o `nivel_hierarquico`
      para eliminar a Armadilha 5.4 (dupla contagem contábil) e higieniza tipos monetários.
    - Se o DataFrame for de Dívida Ativa (`cpf_cnpj`, `inscricao_imobiliaria`), remove duplicatas
      e valida valores.
    """
    logger.info("Iniciando limpeza e validação de schema (Camada Silver)...")
    from src.coleta.coletor_prefeitura import nivel_hierarquico, eh_receita_raiz
    from src.repositories.postgres_repository import RepositorioPostgreSQL

    # Caso 1: DataFrame de Receitas Reais do Portal Novo (182k+ registros)
    if "codigo" in df.columns and "valor_arrecado_mes" in df.columns:
        df = df.copy()
        df["nivel_hierarquico"] = df["codigo"].map(nivel_hierarquico)
        df["eh_raiz_contabil"] = df.apply(
            lambda r: eh_receita_raiz(r.get("descricao", ""), r.get("codigo", "")),
            axis=1,
        )
        for col_val in ("valor_orcado", "valor_arrecado_mes", "valor_arrecado_periodo"):
            if col_val in df.columns:
                df[col_val] = df[col_val].map(RepositorioPostgreSQL._converter_moeda_br)
        os.makedirs(os.path.dirname(CAMINHO_LIMPO), exist_ok=True)
        df.to_csv(CAMINHO_LIMPO, index=False, sep=";")
        logger.info(f"Camada Silver (Receitas Prefeitura com Hierarquia Contábil) salva em {CAMINHO_LIMPO} ({len(df)} registros).")
        return df

    # Caso 2: DataFrame de Dívida Ativa / Contribuintes
    df = padronizar_colunas(df)

    chaves_candidatas = ["inscricao_imobiliaria", "exercicio_ano", "codigo_debito", "cpf_cnpj"]
    chaves_presentes = [c for c in chaves_candidatas if c in df.columns]

    if chaves_presentes:
        df = df.drop_duplicates(subset=chaves_presentes).copy()
    else:
        df = df.drop_duplicates().copy()

    if "cpf_cnpj" not in df.columns:
        df["cpf_cnpj"] = "000.000.000-00"

    try:
        from seeds.mock_data import CONTRIBUINTES_SEED
        mapa_nomes = {c["cpf_cnpj"]: c["nome"] for c in CONTRIBUINTES_SEED}
        df["nome"] = df.apply(
            lambda r: mapa_nomes.get(str(r.get("cpf_cnpj", "")).strip(), r.get("nome"))
            if pd.isna(r.get("nome")) or r.get("nome") in ("Contribuinte", "Contribuinte Não Identificado", None)
            else r.get("nome"),
            axis=1,
        )
    except Exception:
        pass

    if "nome" not in df.columns or df["nome"].isna().all():
        df["nome"] = "Contribuinte Não Identificado"
    if "inscricao_imobiliaria" not in df.columns:
        df["inscricao_imobiliaria"] = "CCI-GERAL-00"
    if "exercicio_ano" not in df.columns:
        df["exercicio_ano"] = 2024
    if "valor_original" not in df.columns:
        df["valor_original"] = 0.0
    if "juros_multa" not in df.columns:
        df["juros_multa"] = 0.0

    df["valor_original"] = df["valor_original"].apply(lambda v: float(Decimal(str(v or 0))))
    df["juros_multa"] = df["juros_multa"].apply(lambda v: float(Decimal(str(v or 0))))

    if "valor_atualizado" not in df.columns:
        df["valor_atualizado"] = df["valor_original"] + df["juros_multa"]
    else:
        df["valor_atualizado"] = df.apply(
            lambda r: float(r["valor_original"]) + float(r["juros_multa"])
            if (
                float(r.get("valor_atualizado", 0) or 0) == float(r.get("valor_original", 0) or 0)
                and float(r.get("juros_multa", 0) or 0) > 0
            )
            else float(Decimal(str(r.get("valor_atualizado") or r.get("valor_original") or 0))),
            axis=1,
        )
    if "data_vencimento" not in df.columns:
        df["data_vencimento"] = "2024-12-31"

    df["data_vencimento"] = (
        pd.to_datetime(df["data_vencimento"], errors="coerce")
        .fillna(pd.Timestamp("2024-12-31"))
        .dt.strftime("%Y-%m-%d")
    )

    os.makedirs(os.path.dirname(CAMINHO_LIMPO), exist_ok=True)
    df.to_csv(CAMINHO_LIMPO, index=False)
    logger.info(f"Camada Silver salva em {CAMINHO_LIMPO} ({len(df)} registros válidos).")
    return df


def enriquecer_e_transformar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Aplica enriquecimento socioeconômico via API do IBGE e engenharia de atributos."""
    logger.info("Iniciando Enriquecimento com IBGE e Engenharia de Atributos...")
    indicadores_ibge = {}
    try:
        from src.enriquecimento.integracao_ibge import enriquecer_dados, obter_indicadores_ibge
        indicadores_ibge = obter_indicadores_ibge()
        if "cpf_cnpj" in df.columns:
            df = enriquecer_dados(df)
        logger.info(
            f"Enriquecimento com IBGE concluído para {indicadores_ibge.get('municipio')}/{indicadores_ibge.get('uf')}."
        )
    except Exception as e:
        logger.warning(f"Aviso no enriquecimento IBGE: {e}")

    try:
        if "cpf_cnpj" in df.columns:
            from src.transformacao.features import gerar_atributos_inadimplencia
            df = gerar_atributos_inadimplencia(df)
            logger.info("Engenharia de atributos e score de inadimplência aplicados com sucesso.")
    except Exception as e:
        logger.warning(f"Aviso na engenharia de atributos: {e}")

    os.makedirs(os.path.dirname(CAMINHO_PRONTO), exist_ok=True)
    df.to_csv(CAMINHO_PRONTO, index=False)
    logger.info(f"Camada Gold salva em {CAMINHO_PRONTO}")
    return df, indicadores_ibge


def carregar_no_banco(df: pd.DataFrame):
    """
    Carrega o DataFrame diretamente no PostgreSQL:
      - Se for DataFrame de Receitas da Prefeitura (`codigo`, `valor_arrecado_mes`), faz Batch Insert em `prefeitura_receitas`.
      - Se for DataFrame de Dívida Ativa (`cpf_cnpj`, `inscricao_imobiliaria`), faz Upsert nas 4 tabelas fiscais.
    """
    logger.info("Iniciando carga normalizada no banco relacional PostgreSQL...")
    from src.repositories.postgres_repository import RepositorioPostgreSQL

    repo = RepositorioPostgreSQL()

    # Caso 1: Receitas do Portal Novo
    if "codigo" in df.columns and "valor_arrecado_mes" in df.columns:
        registros = df.to_dict(orient="records")
        total = repo.inserir_receitas_portal_novo_em_lote(registros, limpar_antes=False)
        logger.info(f"Carga em lote no PostgreSQL (prefeitura_receitas) concluída: {total} registros.")
        return

    # Caso 2: Dívida Ativa (contribuinte, imovel, divida, processo)
    mapa_nomes = {}
    try:
        from seeds.mock_data import CONTRIBUINTES_SEED
        mapa_nomes = {c["cpf_cnpj"]: c["nome"] for c in CONTRIBUINTES_SEED}
    except Exception:
        pass

    with repo.engine.begin() as conn_pg:
        for _, row in df.iterrows():
            cpf = str(row["cpf_cnpj"])
            nome_inf = row.get("nome")
            if not nome_inf or nome_inf in ("Contribuinte", "Contribuinte Não Identificado"):
                nome_inf = mapa_nomes.get(cpf, "Contribuinte Não Identificado")

            res_c = conn_pg.execute(
                text(
                    """
                    INSERT INTO contribuinte (cpf_cnpj, nome, tipo_pessoa, email, telefone, endereco_correspondencia)
                    VALUES (:cpf, :nome, :tipo, :email, :tel, :end)
                    ON CONFLICT (cpf_cnpj) DO UPDATE SET
                        nome = CASE
                            WHEN EXCLUDED.nome IS NOT NULL AND EXCLUDED.nome NOT IN ('Contribuinte', 'Contribuinte Não Identificado')
                            THEN EXCLUDED.nome
                            ELSE contribuinte.nome
                        END,
                        email = COALESCE(EXCLUDED.email, contribuinte.email),
                        telefone = COALESCE(EXCLUDED.telefone, contribuinte.telefone)
                    RETURNING id_contribuinte
                    """
                ),
                {
                    "cpf": cpf,
                    "nome": nome_inf,
                    "tipo": row.get("tipo_pessoa", "FISICA"),
                    "email": row.get("email"),
                    "tel": row.get("telefone"),
                    "end": row.get("endereco_correspondencia"),
                },
            ).fetchone()
            id_contribuinte = res_c[0]

            res_i = conn_pg.execute(
                text(
                    """
                    INSERT INTO imovel (inscricao_imobiliaria, id_contribuinte, endereco, bairro, cep, tipo_imovel, valor_venal, area_terreno)
                    VALUES (:cci, :id_c, :end, :bairro, :cep, :tipo, :venal, :area)
                    ON CONFLICT (inscricao_imobiliaria) DO UPDATE SET
                        id_contribuinte = EXCLUDED.id_contribuinte,
                        valor_venal = COALESCE(EXCLUDED.valor_venal, imovel.valor_venal)
                    RETURNING id_imovel
                    """
                ),
                {
                    "cci": row["inscricao_imobiliaria"],
                    "id_c": id_contribuinte,
                    "end": row.get("endereco", "Palmas"),
                    "bairro": row.get("bairro", ""),
                    "cep": row.get("cep", ""),
                    "tipo": row.get("tipo_imovel", "RESIDENCIAL"),
                    "venal": float(row.get("valor_venal", 0.0) or 0.0),
                    "area": float(row.get("area_terreno", 0.0) or 0.0),
                },
            ).fetchone()
            id_imovel = res_i[0]

            div_exist = conn_pg.execute(
                text(
                    """
                    SELECT id_divida FROM divida
                    WHERE id_imovel = :id_i AND exercicio_ano = :ano AND tipo_tributo = :trib
                    """
                ),
                {
                    "id_i": id_imovel,
                    "ano": int(row.get("exercicio_ano", 2024)),
                    "trib": row.get("tipo_tributo", "IPTU"),
                },
            ).fetchone()

            if div_exist:
                id_divida = div_exist[0]
                conn_pg.execute(
                    text(
                        """
                        UPDATE divida SET
                            valor_original = :v_orig,
                            valor_atualizado = :v_atu,
                            status_divida = :status,
                            data_vencimento = :venc
                        WHERE id_divida = :id_d
                        """
                    ),
                    {
                        "v_orig": float(row.get("valor_original", 0.0)),
                        "v_atu": float(row.get("valor_atualizado", 0.0)),
                        "status": row.get("status_divida", "EM_ABERTO"),
                        "venc": row["data_vencimento"],
                        "id_d": id_divida,
                    },
                )
            else:
                res_d = conn_pg.execute(
                    text(
                        """
                        INSERT INTO divida (id_imovel, exercicio_ano, valor_original, valor_atualizado, tipo_tributo, status_divida, data_vencimento)
                        VALUES (:id_i, :ano, :v_orig, :v_atu, :trib, :status, :venc)
                        RETURNING id_divida
                        """
                    ),
                    {
                        "id_i": id_imovel,
                        "ano": int(row.get("exercicio_ano", 2024)),
                        "v_orig": float(row.get("valor_original", 0.0)),
                        "v_atu": float(row.get("valor_atualizado", 0.0)),
                        "trib": row.get("tipo_tributo", "IPTU"),
                        "status": row.get("status_divida", "EM_ABERTO"),
                        "venc": row["data_vencimento"],
                    },
                ).fetchone()
                id_divida = res_d[0]

            num_proc = row.get("numero_processo")
            if pd.notna(num_proc) and str(num_proc).strip():
                conn_pg.execute(
                    text(
                        """
                        INSERT INTO processo (numero_processo, id_divida, vara_judicial, status_processo, data_ajuizamento, observacoes)
                        VALUES (:num, :id_d, :vara, :status, :data, :obs)
                        ON CONFLICT (numero_processo) DO NOTHING
                        """
                    ),
                    {
                        "num": str(num_proc),
                        "id_d": id_divida,
                        "vara": row.get("vara_judicial", ""),
                        "status": row.get("status_processo", "EM_ANDAMENTO"),
                        "data": row.get("data_ajuizamento", row["data_vencimento"]),
                        "obs": row.get("observacoes", ""),
                    },
                )

    logger.info(f"Carga no PostgreSQL concluída com sucesso ({len(df)} registros).")


def popular_estruturas(df: pd.DataFrame):
    if "cpf_cnpj" not in df.columns:
        return None, None, None
    try:
        from src.estruturas.tabela_hash import TabelaHashDivida
        from src.estruturas.fila_cobranca import FilaCobranca
        from src.estruturas.grafo import GrafoContribuintes

        tabela = TabelaHashDivida()
        fila = FilaCobranca()
        grafo = GrafoContribuintes()

        for _, row in df.iterrows():
            cpf = str(row["cpf_cnpj"])
            valor = float(row.get("valor_atualizado", 0.0))
            score = float(row.get("score_prioridade", valor))
            imovel = str(row.get("inscricao_imobiliaria", "CCI-00"))
            proc = str(row.get("numero_processo", "Sem Processo"))

            tabela.inserir(cpf, valor)
            fila.inserir(score, cpf)
            grafo.adicionar_relacao(cpf, imovel, proc)

        logger.info("TabelaHash, FilaCobranca (Heap) e Grafo populados com sucesso!")
        return tabela, fila, grafo
    except Exception as e:
        logger.warning(f"Aviso ao popular estruturas: {e}")
        return None, None, None


def executar_pipeline(executar_coletor: bool = True):
    logger.info("=== INICIANDO PIPELINE ETL SITRIB (POSTGRESQL) ===")
    df_bruto, diagnostico_coleta = extrair_dados(executar_coletor_ao_vivo=executar_coletor)
    df_limpo = limpar_e_validar(df_bruto)
    df_ouro, indicadores_ibge = enriquecer_e_transformar(df_limpo)
    carregar_no_banco(df_ouro)
    popular_estruturas(df_ouro)
    logger.info("=== PIPELINE ETL CONCLUÍDO COM ÊXITO ===")
    return df_ouro


if __name__ == "__main__":
    executar_pipeline()
