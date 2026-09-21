from src.fila_cobranca import FilaCobranca


def test_fila_vazia_retorna_mensagem():
    fila = FilaCobranca()
    assert fila.proximo_a_cobrar() == "Fila vazia"


def test_ordem_por_prioridade():
    fila = FilaCobranca()
    fila.inserir(30, "111.111.111-11")
    fila.inserir(90, "222.222.222-22")
    fila.inserir(60, "333.333.333-33")

    assert fila.proximo_a_cobrar() == ("222.222.222-22", 90)
    assert fila.proximo_a_cobrar() == ("333.333.333-33", 60)
    assert fila.proximo_a_cobrar() == ("111.111.111-11", 30)


def test_empate_de_score_nao_quebra():
    fila = FilaCobranca()
    fila.inserir(80, "222.222.222-22")
    fila.inserir(80, "111.111.111-11")

    primeiro = fila.proximo_a_cobrar()
    segundo = fila.proximo_a_cobrar()
    assert primeiro[1] == 80 and segundo[1] == 80


def test_amostra_simulada_de_contribuintes():
    fila = FilaCobranca()
    contribuintes = [
        (95, "111.111.111-11"),
        (60, "222.222.222-22"),
        (78, "333.333.333-33"),
        (40, "444.444.444-44"),
        (88, "555.555.555-55"),
    ]
    for score, cpf in contribuintes:
        fila.inserir(score, cpf)

    ordem_esperada = sorted(contribuintes, key=lambda x: -x[0])
    for score_esperado, cpf_esperado in ordem_esperada:
        resultado = fila.proximo_a_cobrar()
        assert resultado == (cpf_esperado, score_esperado)