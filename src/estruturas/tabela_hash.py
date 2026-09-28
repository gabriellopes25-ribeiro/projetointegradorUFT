class TabelaHashDivida:
    def __init__(self):
        self.tabela = {}

    def inserir(self, cpf, valor_divida):
        self.tabela[cpf] = valor_divida

    def buscar(self, cpf):
        return self.tabela.get(cpf, "CPF não encontrado")    

