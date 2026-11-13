"""Entidade de Usuário e Perfis de Acesso (RBAC) para o SITRIB / SEFIN Palmas."""
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional


class Perfil(StrEnum):
    ADMINISTRADOR = "administrador"  # Auditor Fiscal (acesso irrestrito e cobrança ativa)
    GESTAO = "gestao"                # Gestor/Secretário (dashboards, mapas e fairness)
    CONSULTA = "consulta"            # Contribuinte/Cidadão (apenas sua própria inscrição)


@dataclass(frozen=True, kw_only=True)
class Usuario:
    id: str
    nome: str
    email: str
    senha_hash: str = field(repr=False)
    perfil: Perfil = Perfil.CONSULTA
    cpf: Optional[str] = None        # Vinculado para perfil CONSULTA (LGPD)
