"""
Inicializa o banco de dados PostgreSQL do SITRIB (a partir de schema.sql)
e o popula com:
  1. Massa cadastral e histórica de Dívida Ativa de Palmas (seeds/mock_data.py)
  2. Coleta ao vivo das APIs da Prefeitura de Palmas (Portal Novo NUCLEOGOV e API Antiga)
     ou carga instantânea em lote a partir dos arquivos em data/bruto/.

Uso: python -m scripts.popular_banco [--coletar-tudo]
"""

import sys
from pathlib import Path
from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from seeds.mock_data import (
    CONTRIBUINTES_SEED,
    IMOVEIS_SEED,
    DIVIDAS_SEED,
    PROCESSOS_SEED,
)
from src.database import criar_engine_postgres, inicializar_schema_postgres


def criar_banco(database_url: Optional[str] = None) -> Engine:
    """Inicializa e limpa as tabelas de Dívida Ativa no PostgreSQL."""
    engine = criar_engine_postgres(database_url)
    inicializar_schema_postgres(engine)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE processo, divida, imovel, contribuinte RESTART IDENTITY CASCADE;"))
    return engine


def popular_banco_postgres(engine: Engine) -> dict:
    """Popula as 4 tabelas de Dívida Ativa no PostgreSQL com transações em lote."""
    inicializar_schema_postgres(engine)

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE processo, divida, imovel, contribuinte RESTART IDENTITY CASCADE;"))

        id_contribuinte_por_cpf = {}
        for c in CONTRIBUINTES_SEED:
            res = conn.execute(
                text(
                    """INSERT INTO contribuinte (cpf_cnpj, nome, tipo_pessoa, email, telefone)
                       VALUES (:cpf, :nome, :tipo, :email, :tel)
                       ON CONFLICT (cpf_cnpj) DO UPDATE SET nome = EXCLUDED.nome
                       RETURNING id_contribuinte"""
                ),
                {
                    "cpf": c["cpf_cnpj"],
                    "nome": c["nome"],
                    "tipo": c.get("tipo_pessoa", "FISICA"),
                    "email": c["email"],
                    "tel": c["telefone"],
                },
            ).fetchone()
            id_contribuinte_por_cpf[c["cpf_cnpj"]] = res[0]

        id_imovel_por_cci = {}
        for i in IMOVEIS_SEED:
            id_c = id_contribuinte_por_cpf[i["cpf_cnpj_proprietario"]]
            res = conn.execute(
                text(
                    """INSERT INTO imovel (inscricao_imobiliaria, id_contribuinte, endereco, bairro, cep, tipo_imovel, valor_venal)
                       VALUES (:cci, :id_c, :end, :bairro, :cep, :tipo, :venal)
                       ON CONFLICT (inscricao_imobiliaria) DO UPDATE SET valor_venal = EXCLUDED.valor_venal
                       RETURNING id_imovel"""
                ),
                {
                    "cci": i["inscricao_cci"],
                    "id_c": id_c,
                    "end": i["endereco"],
                    "bairro": i.get("bairro", "Plano Diretor"),
                    "cep": i.get("cep", "77000-000"),
                    "tipo": i.get("tipo_imovel", "RESIDENCIAL"),
                    "venal": float(i.get("valor_venal") or 0.0),
                },
            ).fetchone()
            id_imovel_por_cci[i["inscricao_cci"]] = res[0]

        id_divida_por_codigo = {}
        for d in DIVIDAS_SEED:
            id_i = id_imovel_por_cci[d["inscricao_cci"]]
            valor_atualizado = round(float(d["valor_original"]) + float(d["juros_multa"]), 2)
            data_vencimento = f"{d['ano_exercicio']}-12-31"
            res = conn.execute(
                text(
                    """INSERT INTO divida (id_imovel, exercicio_ano, valor_original, valor_atualizado, tipo_tributo, status_divida, data_vencimento)
                       VALUES (:id_i, :ano, :orig, :atu, :trib, :status, :venc)
                       RETURNING id_divida"""
                ),
                {
                    "id_i": id_i,
                    "ano": int(d["ano_exercicio"]),
                    "orig": float(d["valor_original"]),
                    "atu": valor_atualizado,
                    "trib": d.get("tipo_tributo", "IPTU"),
                    "status": d.get("status", "ATIVO"),
                    "venc": data_vencimento,
                },
            ).fetchone()
            id_divida_por_codigo[d["codigo_debito"]] = res[0]

        for p in PROCESSOS_SEED:
            id_d = id_divida_por_codigo.get(p["codigo_debito"])
            if not id_d:
                continue
            conn.execute(
                text(
                    """INSERT INTO processo (numero_processo, id_divida, vara_judicial, status_processo, data_ajuizamento)
                       VALUES (:num, :id_d, :vara, :status, :data)
                       ON CONFLICT (numero_processo) DO NOTHING"""
                ),
                {
                    "num": p["numero_processo"],
                    "id_d": id_d,
                    "vara": p["vara"],
                    "status": p.get("status_processo", "EM_ANDAMENTO"),
                    "data": p["data_autuacao"],
                },
            )

        totais = {
            tabela: conn.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar() or 0
            for tabela in ("contribuinte", "imovel", "divida", "processo", "prefeitura_receitas", "prefeitura_historico_api_antiga")
        }
    return totais


def popular_banco(engine_ou_conn: Engine) -> dict:
    """Wrapper compatível com chamadas existentes."""
    if hasattr(engine_ou_conn, "begin"):
        return popular_banco_postgres(engine_ou_conn)
    engine = criar_engine_postgres()
    return popular_banco_postgres(engine)


def main() -> None:
    coletar_prefeitura = "--sem-api" not in sys.argv
    coletar_tudo_182k = "--coletar-tudo" in sys.argv

    engine = criar_engine_postgres()
    totais = popular_banco_postgres(engine)
    print(f"[POSTGRESQL] Seeds de Dívida Ativa carregadas: {totais}")

    if coletar_prefeitura:
        from src.coleta.coletor_prefeitura import ColetorSefinPalmasDual
        from src.repositories.postgres_repository import RepositorioPostgreSQL

        repo = RepositorioPostgreSQL()
        coletor = ColetorSefinPalmasDual()

        max_pag_novo = None if coletar_tudo_182k else 5
        print(f"\n[COLETA PREFEITURA -> POSTGRESQL] Baixando receitas reais do Portal Novo (max_paginas={max_pag_novo or 'TODAS (182k+)'})...")
        receitas = coletor.consumir_portal_novo(
            recurso="receitas",
            tamanho_pagina=1000,
            max_paginas=max_pag_novo,
        )
        qtd_rec = repo.inserir_receitas_portal_novo_em_lote(receitas, limpar_antes=True)
        print(f"[POSTGRESQL] {qtd_rec} registros reais de Receitas inseridos em `prefeitura_receitas`!")

        print("\n[COLETA PREFEITURA -> POSTGRESQL] Baixando arrecadação histórica da API Antiga...")
        historico = coletor.consumir_api_antiga(
            endpoint="arrecadacao",
            max_paginas=None if coletar_tudo_182k else 5,
        )
        qtd_ant = repo.inserir_historico_api_antiga_em_lote(historico, endpoint_origem="arrecadacao", limpar_antes=True)
        print(f"[POSTGRESQL] {qtd_ant} registros históricos inseridos em `prefeitura_historico_api_antiga`!")


if __name__ == "__main__":
    main()
