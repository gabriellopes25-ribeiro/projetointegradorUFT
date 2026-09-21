import heapq


class FilaCobranca:
    def __init__(self):
        self.fila = []

    def inserir(self, score, cpf):
        heapq.heappush(self.fila, (-score, cpf))

    def proximo_a_cobrar(self):
        if self.fila:
            score, cpf = heapq.heappop(self.fila)
            return cpf, -score
        return "Fila vazia"


# --- Teste da Fila de Cobranca ---
fila = FilaCobranca()

fila.inserir(30, "111.111.111-11")
fila.inserir(90, "222.222.222-22")
fila.inserir(60, "333.333.333-33")

print("Ordem de cobranca (maior score primeiro):")
print(fila.proximo_a_cobrar())
print(fila.proximo_a_cobrar())
print(fila.proximo_a_cobrar())
print(fila.proximo_a_cobrar())  # fila vazia — deve imprimir "Fila vazia"