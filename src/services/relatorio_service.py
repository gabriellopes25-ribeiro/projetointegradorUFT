"""Contrato previsto; regras de negócio serão implementadas em outra entrega."""
from abc import ABC, abstractmethod
from src.models.simulacao import Simulacao


class RelatorioService(ABC):
    @abstractmethod
    def gerar_csv(self, simulacoes: list[Simulacao]) -> str:
        raise NotImplementedError

    @abstractmethod
    def gerar_pdf(self, simulacoes: list[Simulacao]) -> bytes:
        raise NotImplementedError
