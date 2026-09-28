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

