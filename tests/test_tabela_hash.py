from src.tabela_hash import TabelaHashDivida


def test_inserir_e_buscar_divida():
    divida_ativa = TabelaHashDivida()
    divida_ativa.inserir("111.111.111-11", 1500.00)
    assert divida_ativa.buscar("111.111.111-11") == 1500.00


def test_buscar_cpf_nao_encontrado():
    divida_ativa = TabelaHashDivida()
    divida_ativa.inserir("111.111.111-11", 1500.00)
    assert divida_ativa.buscar("999.999.999-99") == "CPF não encontrado"


def test_amostra_simulada_de_contribuintes():
    divida_ativa = TabelaHashDivida()
    contribuintes = [
        ("111.111.111-11", 1500.00),
        ("222.222.222-22", 3200.50),
        ("333.333.333-33", 890.75),
        ("444.444.444-44", 12000.00),
        ("555.555.555-55", 430.20),
    ]
    for cpf, valor in contribuintes:
        divida_ativa.inserir(cpf, valor)

    for cpf, valor_esperado in contribuintes:
        assert divida_ativa.buscar(cpf) == valor_esperado