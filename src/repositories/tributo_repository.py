"""Contrato de persistência; implementação e unicidade ainda pendentes."""
from abc import ABC, abstractmethod
from src.models.tributo import Tributo


class TributoRepository(ABC):
    @abstractmethod
    def salvar(self, tributo: Tributo) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_nome(self, nome: str) -> Tributo | None:
        raise NotImplementedError
