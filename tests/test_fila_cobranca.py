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