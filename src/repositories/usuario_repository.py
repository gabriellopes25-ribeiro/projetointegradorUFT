"""Contrato de persistência; implementação e unicidade ainda pendentes."""
from abc import ABC, abstractmethod
from src.models.usuario import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    def salvar(self, usuario: Usuario) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario | None:
        raise NotImplementedError
