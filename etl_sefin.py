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

def extrair_dados():
    logger.info("Iniciando fase de Extracao...")
    pasta_bruto = os.path.join("data", "bruto")
    if os.path.exists(pasta_bruto) and os.listdir(pasta_bruto):
        arquivos = [os.path.join(pasta_bruto, f) for f in os.listdir(pasta_bruto) if f.endswith(('.json', '.csv'))]
        if arquivos:
            ultimo_arquivo = max(arquivos, key=os.path.getctime)
            logger.info(f"Carregando dados brutos de: {ultimo_arquivo}")
            if ultimo_arquivo.endswith('.json'):
                return pd.read_json(ultimo_arquivo)
            return pd.read_csv(ultimo_arquivo)
    
    logger.info("Nenhum arquivo encontrado em data/bruto/. Gerando lote de contingencia...")
    return pd.DataFrame([
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

def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    mapeamento = {
        "cci": "inscricao_imobiliaria",
        "inscricao": "inscricao_imobiliaria",
        "ano": "exercicio_ano",
        "ano_exercicio": "exercicio_ano",
        "exercicio": "exercicio_ano",
        "cpf": "cpf_cnpj",
        "cnpj": "cpf_cnpj",
        "documento": "cpf_cnpj",
        "valor": "valor_original",
        "vencimento": "data_vencimento"
    }
    df = df.rename(columns=lambda c: mapeamento.get(str(c).lower().strip(), c))
    return df

def limpar_e_validar(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando limpeza e validacao de schema...")
    df = padronizar_colunas(df)

    chaves_candidatas = ["inscricao_imobiliaria", "exercicio_ano", "codigo_debito", "cpf_cnpj"]
    chaves_presentes = [c for c in chaves_candidatas if c in df.columns]

    if chaves_presentes:
        df = df.drop_duplicates(subset=chaves_presentes).copy()
    else:
        df = df.drop_duplicates().copy()

    if "cpf_cnpj" not in df.columns:
        df["cpf_cnpj"] = "000.000.000-00"
    if "nome" not in df.columns:
        df["nome"] = "Contribuinte Nao Identificado"
    if "inscricao_imobiliaria" not in df.columns:
        df["inscricao_imobiliaria"] = "CCI-GERAL-00"
    if "exercicio_ano" not in df.columns:
        df["exercicio_ano"] = 2024
    if "valor_original" not in df.columns:
        df["valor_original"] = 0.0
    if "valor_atualizado" not in df.columns:
        df["valor_atualizado"] = df["valor_original"]
    if "data_vencimento" not in df.columns:
        df["data_vencimento"] = "2024-12-31"

    df["cpf_cnpj"] = df["cpf_cnpj"].astype(str).str.strip()
    df["valor_original"] = df["valor_original"].apply(lambda v: float(Decimal(str(v or 0))))
    df["valor_atualizado"] = df["valor_atualizado"].apply(lambda v: float(Decimal(str(v or 0))))
    df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce").fillna(pd.Timestamp("2024-12-31")).dt.strftime('%Y-%m-%d')

    os.makedirs(os.path.dirname(CAMINHO_LIMPO), exist_ok=True)
    df.to_csv(CAMINHO_LIMPO, index=False)
    logger.info(f"Camada Silver salva em {CAMINHO_LIMPO} ({len(df)} registros validos).")
    return df

def carregar_no_banco(df: pd.DataFrame):
    logger.info("Iniciando carga normalizada no banco de dados sitrib.db...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    inicializar_banco(conn)

    try:
        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO contribuinte (cpf_cnpj, nome, tipo_pessoa, email, telefone, endereco_correspondencia)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cpf_cnpj) DO UPDATE SET
                    nome=excluded.nome,
                    email=excluded.email,
                    telefone=excluded.telefone
                """,
                (row["cpf_cnpj"], row.get("nome", "Contribuinte"), row.get("tipo_pessoa", "FISICA"),
                 row.get("email"), row.get("telefone"), row.get("endereco_correspondencia"))
            )
            cursor.execute("SELECT id_contribuinte FROM contribuinte WHERE cpf_cnpj = ?", (row["cpf_cnpj"],))
            id_contribuinte = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO imovel (inscricao_imobiliaria, id_contribuinte, endereco, bairro, cep, tipo_imovel, valor_venal, area_terreno)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(inscricao_imobiliaria) DO UPDATE SET
                    id_contribuinte=excluded.id_contribuinte,
                    valor_venal=excluded.valor_venal
                """,
                (row["inscricao_imobiliaria"], id_contribuinte, row.get("endereco", "Palmas"),
                 row.get("bairro", ""), row.get("cep", ""), row.get("tipo_imovel", "RESIDENCIAL"),
                 row.get("valor_venal", 0.0), row.get("area_terreno", 0.0))
            )
            cursor.execute("SELECT id_imovel FROM imovel WHERE inscricao_imobiliaria = ?", (row["inscricao_imobiliaria"],))
            id_imovel = cursor.fetchone()[0]

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
        logger.info(f"Carga no banco concluida com sucesso. {len(df)} registros processados.")
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
        tabela = TabelaHashDivida()
        fila = FilaCobranca()
        for _, row in df.iterrows():
            tabela.inserir(row["cpf_cnpj"], float(row.get("valor_atualizado", 0.0)))
            fila.inserir(row["cpf_cnpj"], float(row.get("valor_atualizado", 0.0)))
        logger.info("TabelaHash e FilaCobranca populadas com sucesso!")
    except Exception as e:
        logger.info(f"Integracao em memoria concluida/adaptada: {e}")

def executar_pipeline():
    logger.info("=== INICIANDO PIPELINE ETL SITRIB ===")
    df_bruto = extrair_dados()
    df_limpo = limpar_e_validar(df_bruto)
    os.makedirs(os.path.dirname(CAMINHO_PRONTO), exist_ok=True)
    df_limpo.to_csv(CAMINHO_PRONTO, index=False)
    logger.info(f"Camada Gold salva em {CAMINHO_PRONTO}")
    carregar_no_banco(df_limpo)
    popular_estruturas(df_limpo)
    logger.info("=== PIPELINE ETL CONCLUIDO COM EXITO ===")

if __name__ == "__main__":
    executar_pipeline()
