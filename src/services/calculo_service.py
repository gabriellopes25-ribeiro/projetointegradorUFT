"""Contrato previsto; regras de negócio serão implementadas em outra entrega."""
from abc import ABC, abstractmethod
from decimal import Decimal
from src.models.tributo import Tributo


class CalculoService(ABC):
    @abstractmethod
    def calcular(self, tributo: Tributo, base_calculo: Decimal) -> Decimal:
        raise NotImplementedError
