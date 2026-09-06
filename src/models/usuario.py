"""Entidade prevista para RF01–RF03. Não recebe senha em texto puro."""
from dataclasses import dataclass, field
from enum import StrEnum


class Perfil(StrEnum):
    ADMINISTRADOR = "administrador"
    CONSULTA = "consulta"


@dataclass(frozen=True, kw_only=True)
class Usuario:
    id: str
    nome: str
    email: str
    senha_hash: str = field(repr=False)
    perfil: Perfil = Perfil.CONSULTA
