"""Contrato previsto; regras de negócio serão implementadas em outra entrega."""
from abc import ABC, abstractmethod
from src.models.tributo import Tributo


class TributoService(ABC):
    @abstractmethod
    def cadastrar(self, tributo: Tributo) -> None:
        raise NotImplementedError
