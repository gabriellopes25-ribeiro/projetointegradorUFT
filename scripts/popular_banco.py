"""
Cria o banco de dados SQLite do SITRIB (a partir de seeds/schema.sql) e o popula
com a massa de dados simulados de seeds/mock_data.py.

Uso: python -m scripts.popular_banco
"""

import sqlite3
from pathlib import Path

from seeds.mock_data import (
    CONTRIBUINTES_SEED,
    IMOVEIS_SEED,
    DIVIDAS_SEED,
    PROCESSOS_SEED,
)

# Aponta corretamente para seeds/schema.sql e para a raiz do projeto para o sitrib.db
CAMINHO_SCHEMA = Path(__file__).resolve().parent.parent / "schema.sql"
CAMINHO_BANCO = Path(__file__).resolve().parent.parent / "sitrib.db"


def criar_banco() -> sqlite3.Connection:
    if CAMINHO_BANCO.exists():
        CAMINHO_BANCO.unlink()
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON;")
    with open(CAMINHO_SCHEMA, encoding="utf-8") as f:
        schema = f.read()
    schema_sqlite = schema.replace(
        "INT AUTO_INCREMENT PRIMARY KEY",
        "INTEGER PRIMARY KEY AUTOINCREMENT",
    )
    conexao.executescript(schema_sqlite)
    return conexao


def popular_banco(conexao: sqlite3.Connection) -> None:
    cursor = conexao.cursor()

    id_contribuinte_por_cpf = {}
    for c in CONTRIBUINTES_SEED:
        cursor.execute(
            "INSERT INTO contribuinte (cpf_cnpj, nome, email, telefone) VALUES (?, ?, ?, ?)",
            (c["cpf_cnpj"], c["nome"], c["email"], c["telefone"]),
        )
        id_contribuinte_por_cpf[c["cpf_cnpj"]] = cursor.lastrowid

    id_imovel_por_cci = {}
    for i in IMOVEIS_SEED:
        id_contribuinte = id_contribuinte_por_cpf[i["cpf_cnpj_proprietario"]]
        cursor.execute(
            "INSERT INTO imovel (inscricao_imobiliaria, id_contribuinte, endereco, bairro, cep) VALUES (?, ?, ?, ?, ?)",
            (i["inscricao_cci"], id_contribuinte, i["endereco"], i["bairro"], i["cep"]),
        )
        id_imovel_por_cci[i["inscricao_cci"]] = cursor.lastrowid

    id_divida_por_codigo = {}
    for d in DIVIDAS_SEED:
        id_imovel = id_imovel_por_cci[d["inscricao_cci"]]
        valor_atualizado = round(d["valor_original"] + d["juros_multa"], 2)
        data_vencimento = f"{d['ano_exercicio']}-12-31"
        cursor.execute(
            """INSERT INTO divida (id_imovel, exercicio_ano, valor_original, valor_atualizado,
               tipo_tributo, status_divida, data_vencimento) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (id_imovel, d["ano_exercicio"], d["valor_original"], valor_atualizado,
             d["tipo_tributo"], d["status"], data_vencimento),
        )
        id_divida_por_codigo[d["codigo_debito"]] = cursor.lastrowid

    for p in PROCESSOS_SEED:
        id_divida = id_divida_por_codigo[p["codigo_debito"]]
        cursor.execute(
            "INSERT INTO processo (numero_processo, id_divida, vara_judicial, status_processo, data_ajuizamento) VALUES (?, ?, ?, ?, ?)",
            (p["numero_processo"], id_divida, p["vara"], p["status_processo"], p["data_autuacao"]),
        )

    conexao.commit()


def main() -> None:
    conexao = criar_banco()
    popular_banco(conexao)
    totais = {
        tabela: conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        for tabela in ("contribuinte", "imovel", "divida", "processo")
    }
    print(f"Banco criado em: {CAMINHO_BANCO}")
    print(f"Registros inseridos: {totais}")
    conexao.close()


if __name__ == "__main__":
    main()