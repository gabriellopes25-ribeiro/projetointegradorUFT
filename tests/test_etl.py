import os
import sys
import sqlite3
import pandas as pd
import pytest

# Adiciona a raiz do projeto ao sys.path para garantir que o etl_sefin seja encontrado
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl_sefin import limpar_e_validar, carregar_no_banco, DB_PATH

def test_limpeza_remove_duplicatas():
    dados = [
        {"cpf_cnpj": "111", "inscricao_imobiliaria": "CCI-01", "exercicio_ano": 2023, "valor_original": "100.0", "valor_atualizado": "110.0", "data_vencimento": "2023-12-31"},
        {"cpf_cnpj": "111", "inscricao_imobiliaria": "CCI-01", "exercicio_ano": 2023, "valor_original": "100.0", "valor_atualizado": "110.0", "data_vencimento": "2023-12-31"},
    ]
    df = pd.DataFrame(dados)
    df_resultado = limpar_e_validar(df)
    assert len(df_resultado) == 1

def test_persistencia_sqlite():
    dados = [{
        "cpf_cnpj": "000.111.222-33", "nome": "Teste Persistencia", "tipo_pessoa": "FISICA",
        "email": "teste@uft.edu.br", "telefone": "(63) 99999-9999", "endereco_correspondencia": "Palmas",
        "inscricao_imobiliaria": "CCI-TESTE-99", "endereco": "Av JK", "bairro": "Centro",
        "cep": "77000-000", "tipo_imovel": "RESIDENCIAL", "valor_venal": 100000.0, "area_terreno": 250.0,
        "exercicio_ano": 2024, "valor_original": 500.0, "valor_atualizado": 550.0,
        "tipo_tributo": "IPTU", "status_divida": "EM_ABERTO", "data_vencimento": "2024-12-31",
        "numero_processo": "9999999-99.2024.8.27.2729", "vara_judicial": "Vara Fiscal",
        "status_processo": "EM_ANDAMENTO", "data_ajuizamento": "2024-05-10", "observacoes": ""
    }]
    df = pd.DataFrame(dados)
    carregar_no_banco(df)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT cpf_cnpj, nome FROM contribuinte WHERE cpf_cnpj = '000.111.222-33'")
    resultado = cursor.fetchone()

    # Limpeza para garantir isolamento e idempotência dos demais testes
    cursor.execute("DELETE FROM contribuinte WHERE cpf_cnpj = '000.111.222-33'")
    cursor.execute("DELETE FROM imovel WHERE inscricao_imobiliaria = 'CCI-TESTE-99'")
    conn.commit()
    conn.close()

    assert resultado is not None
    assert resultado[0] == "000.111.222-33"
