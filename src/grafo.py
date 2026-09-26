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


Organização e Pesquisa de Contribuintes (Grafos)
A funcionalidade de organização e pesquisa de dados dos contribuintes foi desenvolvida utilizando a estrutura de dados de um Grafo, implementada através de uma lista de adjacências (dicionário em Python). O código foi construído para associar um nó principal (o CPF ou CNPJ do contribuinte) a múltiplos nós secundários, que representam os seus respetivos imóveis e processos.
Esta estrutura foi a forma escolhida para organizar as informações porque espelha perfeitamente as relações do mundo real (um contribuinte para vários bens/processos). Além disso, ao utilizar um dicionário como base para o grafo, a pesquisa por um CPF ou CNPJ torna-se extremamente rápida e direta, localizando o histórico completo do utilizador instantaneamente, sem a necessidade de percorrer uma base de dados inteira linha a linha.
