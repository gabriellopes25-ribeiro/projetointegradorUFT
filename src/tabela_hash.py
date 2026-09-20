class TabelaHashDivida:
    def __init__(self):
        self.tabela = {}

    def inserir(self, cpf, valor_divida):
        self.tabela[cpf] = valor_divida

    def buscar(self, cpf):
        return self.tabela.get(cpf, "CPF não encontrado")    

    
# --- Teste da Tabela Hash ---
divida_ativa = TabelaHashDivida()

divida_ativa.inserir("111.111.111-11", 1500.00)
divida_ativa.inserir("222.222.222-22", 3200.50)
divida_ativa.inserir("333.333.333-33", 890.75)

print("Dívida do CPF 222:", divida_ativa.buscar("222.222.222-22"))
print("Dívida do CPF 999:", divida_ativa.buscar("999.999.999-99"))