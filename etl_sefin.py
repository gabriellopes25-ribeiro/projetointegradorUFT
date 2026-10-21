import os
import sys
import sqlite3
import logging
from decimal import Decimal
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ETL_SEFIN")

DB_PATH = "sitrib.db"
SCHEMA_PATH = "schema.sql"
CAMINHO_LIMPO = os.path.join("data", "limpo", "dados_limpos.csv")
CAMINHO_PRONTO = os.path.join("data", "pronto", "dados_prontos.csv")


def inicializar_banco(conn):
    cursor = conn.cursor()
    # Verifica se a tabela principal já existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contribuinte'")
    tabela_existe = cursor.fetchone()
    
    if not tabela_existe and os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            script_sql = f.read()
        conn.executescript(script_sql)
        logger.info("Schema do banco de dados criado com sucesso.")
    else:
        logger.info("Tabelas do banco de dados já existentes. Prosseguindo...")


def extrair_dados(executar_coletor_ao_vivo: bool = True):
    """
    Fase de Extração Integrada:
    1. Aciona o ColetorSefinPalmasDual para diagnosticar e tentar consumir as APIs municipais.
    2. Se não conseguir extrair ao vivo, utiliza dados de contingência/fallback das seeds.
    3. Retorna (DataFrame_bruto, diagnostico_coleta).
    """
    logger.info("Iniciando fase de Extração integrada...")
    diagnostico = {"modo": "ARQUIVO_LOCAL", "registros_obtidos": 0}

    if executar_coletor_ao_vivo:
        try:
            from src.coleta.coletor_prefeitura import ColetorSefinPalmasDual
            coletor = ColetorSefinPalmasDual()
            dados_brutos, diagnostico = coletor.coletar_com_diagnostico()
            if dados_brutos:
                logger.info(f"Dados brutos coletados via coletor ({len(dados_brutos)} registros, modo {diagnostico.get('modo')}).")
                return pd.DataFrame(dados_brutos), diagnostico
        except Exception as e:
            logger.warning(f"Coletor municipal não pôde ser executado diretamente ({e}). Buscando em data/bruto/...")

    # Se já houver arquivos brutos em data/bruto
    pasta_bruto = os.path.join("data", "bruto")
    if os.path.exists(pasta_bruto) and os.listdir(pasta_bruto):
        arquivos = [os.path.join(pasta_bruto, f) for f in os.listdir(pasta_bruto) if f.endswith(('.json', '.csv'))]
        if arquivos:
            ultimo_arquivo = max(arquivos, key=os.path.getctime)
            logger.info(f"Carregando dados brutos do arquivo existente: {ultimo_arquivo}")
            if ultimo_arquivo.endswith('.json'):
                df = pd.read_json(ultimo_arquivo)
            else:
                df = pd.read_csv(ultimo_arquivo)
            diagnostico["modo"] = f"ARQUIVO ({os.path.basename(ultimo_arquivo)})"
            diagnostico["registros_obtidos"] = len(df)
            return df, diagnostico

    logger.info("Nenhum arquivo encontrado em data/bruto/. Gerando lote de contingencia...")
    df_fallback = pd.DataFrame([
        {
            "cpf_cnpj": "123.456.789-01", "nome": "Carlos Eduardo Siqueira", "tipo_pessoa": "FISICA",
            "email": "carlos.siqueira@email.com", "telefone": "(63) 98111-2030", "endereco_correspondencia": "Plano Diretor Norte",
            "inscricao_imobiliaria": "CCI-104-NORTE-01", "endereco": "Quadra 104 Norte, Alameda 02, Lote 15",
            "bairro": "Plano Diretor Norte", "cep": "77006-020", "tipo_imovel": "RESIDENCIAL",
            "valor_venal": "250000.00", "area_terreno": "360.00", "exercicio_ano": 2023,
            "valor_original": "1450.50", "valor_atualizado": "1620.00", "tipo_tributo": "IPTU",
            "status_divida": "EM_ABERTO", "data_vencimento": "2023-12-31",
            "numero_processo": "0012345-67.2023.8.27.2729", "vara_judicial": "1a Vara de Execucao Fiscal de Palmas",
            "status_processo": "EM_ANDAMENTO", "data_ajuizamento": "2024-01-15", "observacoes": "Notificado via edital"
        }
    ])
    diagnostico["modo"] = "CONTINGENCIA_ESTATICA"
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
    logger.info("Iniciando limpeza e validação de schema...")
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
            axis=1
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
            if (float(r.get("valor_atualizado", 0) or 0) == float(r.get("valor_original", 0) or 0) and float(r.get("juros_multa", 0) or 0) > 0)
            else float(Decimal(str(r.get("valor_atualizado") or r.get("valor_original") or 0))),
            axis=1
        )
    if "data_vencimento" not in df.columns:
        df["data_vencimento"] = "2024-12-31"

    df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce").fillna(pd.Timestamp("2024-12-31")).dt.strftime('%Y-%m-%d')

    os.makedirs(os.path.dirname(CAMINHO_LIMPO), exist_ok=True)
    df.to_csv(CAMINHO_LIMPO, index=False)
    logger.info(f"Camada Silver salva em {CAMINHO_LIMPO} ({len(df)} registros válidos).")
    return df


def enriquecer_e_transformar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Aplica enriquecimento socioeconômico via API do IBGE
    e engenharia de atributos (score, faixas, inadimplência) + LGPD.
    """
    logger.info("Iniciando Enriquecimento com IBGE e Engenharia de Atributos...")
    indicadores_ibge = {}
    try:
        from src.enriquecimento.integracao_ibge import enriquecer_dados, obter_indicadores_ibge
        indicadores_ibge = obter_indicadores_ibge()
        df = enriquecer_dados(df)
        logger.info(f"Enriquecimento com IBGE concluído para {indicadores_ibge.get('municipio')}/{indicadores_ibge.get('uf')}.")
    except Exception as e:
        logger.warning(f"Aviso no enriquecimento IBGE: {e}")

    try:
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
    logger.info("Iniciando carga normalizada no banco de dados sitrib.db...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    inicializar_banco(conn)

    # Dicionário de apoio com nomes conhecidos das seeds
    mapa_nomes = {}
    try:
        from seeds.mock_data import CONTRIBUINTES_SEED
        mapa_nomes = {c["cpf_cnpj"]: c["nome"] for c in CONTRIBUINTES_SEED}
    except Exception:
        pass

    try:
        for _, row in df.iterrows():
            cpf = row["cpf_cnpj"]
            nome_informado = row.get("nome")
            if not nome_informado or nome_informado in ("Contribuinte", "Contribuinte Não Identificado"):
                nome_informado = mapa_nomes.get(cpf, "Contribuinte Não Identificado")

            cursor.execute(
                """
                INSERT INTO contribuinte (cpf_cnpj, nome, tipo_pessoa, email, telefone, endereco_correspondencia)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cpf_cnpj) DO UPDATE SET
                    nome = CASE 
                        WHEN excluded.nome IS NOT NULL AND excluded.nome NOT IN ('Contribuinte', 'Contribuinte Não Identificado') 
                        THEN excluded.nome 
                        ELSE contribuinte.nome 
                    END,
                    email = COALESCE(excluded.email, contribuinte.email),
                    telefone = COALESCE(excluded.telefone, contribuinte.telefone)
                """,
                (cpf, nome_informado, row.get("tipo_pessoa", "FISICA"),
                 row.get("email"), row.get("telefone"), row.get("endereco_correspondencia"))
            )
            cursor.execute("SELECT id_contribuinte FROM contribuinte WHERE cpf_cnpj = ?", (cpf,))
            id_contribuinte = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO imovel (inscricao_imobiliaria, id_contribuinte, endereco, bairro, cep, tipo_imovel, valor_venal, area_terreno)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(inscricao_imobiliaria) DO UPDATE SET
                    id_contribuinte=excluded.id_contribuinte,
                    valor_venal=COALESCE(excluded.valor_venal, imovel.valor_venal)
                """,
                (row["inscricao_imobiliaria"], id_contribuinte, row.get("endereco", "Palmas"),
                 row.get("bairro", ""), row.get("cep", ""), row.get("tipo_imovel", "RESIDENCIAL"),
                 row.get("valor_venal", 0.0), row.get("area_terreno", 0.0))
            )
            cursor.execute("SELECT id_imovel FROM imovel WHERE inscricao_imobiliaria = ?", (row["inscricao_imobiliaria"],))
            id_imovel = cursor.fetchone()[0]

            # Evita duplicatas em dívida por imóvel + exercício + tipo de tributo
            cursor.execute(
                """
                SELECT id_divida FROM divida 
                WHERE id_imovel = ? AND exercicio_ano = ? AND tipo_tributo = ?
                """,
                (id_imovel, int(row.get("exercicio_ano", 2024)), row.get("tipo_tributo", "IPTU"))
            )
            divida_existente = cursor.fetchone()
            if divida_existente:
                id_divida = divida_existente[0]
                cursor.execute(
                    """
                    UPDATE divida SET
                        valor_original = ?,
                        valor_atualizado = ?,
                        status_divida = ?,
                        data_vencimento = ?
                    WHERE id_divida = ?
                    """,
                    (float(row.get("valor_original", 0.0)), float(row.get("valor_atualizado", 0.0)),
                     row.get("status_divida", "EM_ABERTO"), row["data_vencimento"], id_divida)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO divida (id_imovel, exercicio_ano, valor_original, valor_atualizado, tipo_tributo, status_divida, data_vencimento)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (id_imovel, int(row.get("exercicio_ano", 2024)), float(row.get("valor_original", 0.0)),
                     float(row.get("valor_atualizado", 0.0)), row.get("tipo_tributo", "IPTU"),
                     row.get("status_divida", "EM_ABERTO"), row["data_vencimento"])
                )
                id_divida = cursor.lastrowid

            num_proc = row.get("numero_processo")
            if pd.notna(num_proc) and str(num_proc).strip():
                cursor.execute(
                    """
                    INSERT INTO processo (numero_processo, id_divida, vara_judicial, status_processo, data_ajuizamento, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(numero_processo) DO NOTHING
                    """,
                    (str(num_proc), id_divida, row.get("vara_judicial", ""),
                     row.get("status_processo", "EM_ANDAMENTO"), row.get("data_ajuizamento", row["data_vencimento"]),
                     row.get("observacoes", ""))
                )

        conn.commit()
        logger.info(f"Carga no banco concluída com sucesso. {len(df)} registros processados.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro na carga do banco de dados: {e}")
        raise
    finally:
        conn.close()


def popular_estruturas(df: pd.DataFrame):
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


def gerar_relatorios_finais(diagnostico_api: dict, df_ouro: pd.DataFrame, indicadores_ibge: dict):
    """Gera relatórios executivos e auditoria em Markdown e CSV."""
    logger.info("Gerando relatórios consolidados do ecossistema...")
    try:
        from src.services.relatorio_service import RelatorioFiscalService
        service = RelatorioFiscalService(caminho_banco=DB_PATH)

        relatorio_api = service.gerar_relatorio_api(
            diagnostico_prefeitura=diagnostico_api,
            diagnostico_ibge={
                "status": "200 OK" if indicadores_ibge else "LOCAL",
                "url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/1721000",
                "municipio": indicadores_ibge.get("municipio", "Palmas"),
                "uf": indicadores_ibge.get("uf", "TO"),
                "renda_media": indicadores_ibge.get("renda_media_domiciliar", 3250.50),
                "populacao": indicadores_ibge.get("populacao_estimada", 313349),
            }
        )
        relatorio_arrecadacao = service.gerar_relatorio_arrecadacao(
            df_tributos=df_ouro,
            indicadores_ibge=indicadores_ibge
        )

        caminho_md = "docs/relatorio_ecossistema.md"
        service.exportar_markdown(relatorio_api, relatorio_arrecadacao, caminho_arquivo=caminho_md)
        service.exportar_csv(df_ouro, "data/pronto/relatorio_arrecadacao.csv")
        logger.info(f"Relatório em Markdown gerado com sucesso em: {caminho_md}")
        return relatorio_api, relatorio_arrecadacao
    except Exception as e:
        logger.warning(f"Aviso na geração de relatórios: {e}")
        return None, None


def executar_pipeline(executar_coletor: bool = True):
    logger.info("=== INICIANDO PIPELINE ETL SITRIB ===")
    df_bruto, diagnostico_coleta = extrair_dados(executar_coletor_ao_vivo=executar_coletor)
    df_limpo = limpar_e_validar(df_bruto)
    df_ouro, indicadores_ibge = enriquecer_e_transformar(df_limpo)
    carregar_no_banco(df_ouro)
    popular_estruturas(df_ouro)
    gerar_relatorios_finais(diagnostico_coleta, df_ouro, indicadores_ibge)
    logger.info("=== PIPELINE ETL CONCLUÍDO COM ÊXITO ===")
    return df_ouro


if __name__ == "__main__":
    executar_pipeline()
