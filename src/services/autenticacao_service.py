"""Contrato previsto; regras de negócio serão implementadas em outra entrega."""
from abc import ABC, abstractmethod
from src.models.usuario import Usuario, Perfil


class AutenticacaoService(ABC):
    @abstractmethod
    def cadastrar(self, nome: str, email: str, senha: str) -> Usuario:
        raise NotImplementedError

    @abstractmethod
    def autenticar(self, email: str, senha: str) -> Usuario:
        raise NotImplementedError

    @abstractmethod
    def verificar_permissao(self, usuario: Usuario, perfil_necessario: Perfil) -> None:
        raise NotImplementedError
