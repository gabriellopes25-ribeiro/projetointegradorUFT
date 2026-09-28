class GrafoContribuintes:
    def __init__(self):
        # Lista de adjacência (dicionário de listas)
        self.grafo = {}

    def adicionar_relacao(self, cpf_cnpj, imovel, processo):
        # Insere a ligação
        if cpf_cnpj not in self.grafo:
            self.grafo[cpf_cnpj] = []
        self.grafo[cpf_cnpj].append({"imovel": imovel, "processo": processo})

    def buscar_relacionados(self, cpf_cnpj):
        # Retorna todos os imóveis/processos ligados àquele CPF/CNPJ
        return self.grafo.get(cpf_cnpj, [])

# Teste local simulado rodando o arquivo direto com um print simples
if __name__ == "__main__":
    grafo = GrafoContribuintes()
    grafo.adicionar_relacao("123.456.789-00", "Lote 12 - Quadra 5", "Processo 2026/001")
    print("Testando busca:", grafo.buscar_relacionados("123.456.789-00"))
