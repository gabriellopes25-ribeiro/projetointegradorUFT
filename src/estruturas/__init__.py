"""
Pacote de Estruturas de Dados Avançadas (Sprint 2 - SITRIB).

Contém:
  - TabelaHashDivida: Indexação O(1) de débitos por CPF
  - FilaCobranca: Max-Heap O(log n) para ordenação de prioridade de cobrança
  - GrafoContribuintes: Mapeamento de relações Contribuinte -> Imóvel -> Processo
"""

from src.estruturas.tabela_hash import TabelaHashDivida
from src.estruturas.fila_cobranca import FilaCobranca
from src.estruturas.grafo import GrafoContribuintes

__all__ = [
    "TabelaHashDivida",
    "FilaCobranca",
    "GrafoContribuintes",
]
