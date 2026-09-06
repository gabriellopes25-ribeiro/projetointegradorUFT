"""Contrato previsto; regras de negócio serão implementadas em outra entrega."""
from abc import ABC, abstractmethod
from decimal import Decimal
from src.models.simulacao import Simulacao


class SimulacaoService(ABC):
    @abstractmethod
    def simular(self, tributo_id: str, usuario_id: str, valor_atual: Decimal, percentual: Decimal) -> Simulacao:
        raise NotImplementedError

    @abstractmethod
    def comparar(self, cenarios: list[Simulacao]) -> list[dict[str, Decimal]]:
        raise NotImplementedError
