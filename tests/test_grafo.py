from src.estruturas.grafo import GrafoContribuintes


def test_adicionar_e_buscar_relacao():
    grafo = GrafoContribuintes()
    grafo.adicionar_relacao(
        "123.456.789-01", "CCI-104-NORTE-01", "0012345-67.2023.8.27.2729"
    )
    relacionados = grafo.buscar_relacionados("123.456.789-01")
    assert relacionados == [
        {"imovel": "CCI-104-NORTE-01", "processo": "0012345-67.2023.8.27.2729"}
    ]


def test_buscar_cpf_sem_relacoes_retorna_lista_vazia():
    grafo = GrafoContribuintes()
    assert grafo.buscar_relacionados("999.999.999-99") == []


def test_mesmo_cpf_com_multiplas_inscricoes():
    # Caso central do requisito: mesmo CPF/CNPJ em múltiplas inscrições imobiliárias
    grafo = GrafoContribuintes()
    grafo.adicionar_relacao(
        "123.456.789-01", "CCI-104-NORTE-01", "0012345-67.2023.8.27.2729"
    )
    grafo.adicionar_relacao("123.456.789-01", "CCI-208-SUL-42", None)

    relacionados = grafo.buscar_relacionados("123.456.789-01")
    assert len(relacionados) == 2
    assert relacionados[0]["imovel"] == "CCI-104-NORTE-01"
    assert relacionados[1]["imovel"] == "CCI-208-SUL-42"


def test_amostra_simulada_de_contribuintes():
    grafo = GrafoContribuintes()
    relacoes = [
        ("111.111.111-11", "CCI-A-01", "0001-00.2024.8.27.2729"),
        ("222.222.222-22", "CCI-B-02", None),
        ("333.333.333-33", "CCI-C-03", "0003-00.2024.8.27.2729"),
    ]
    for cpf, imovel, processo in relacoes:
        grafo.adicionar_relacao(cpf, imovel, processo)

    for cpf, imovel, processo in relacoes:
        assert grafo.buscar_relacionados(cpf) == [
            {"imovel": imovel, "processo": processo}
        ]