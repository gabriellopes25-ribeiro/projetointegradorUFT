"""Entidade de RF04–RF05; alíquota expressa em percentual."""
from dataclasses import dataclass
from decimal import Decimal

from src.utils.validacoes import (
    validar_decimal_nao_negativo,
    validar_texto_obrigatorio,
)


@dataclass(frozen=True, kw_only=True)
class Tributo:
    id: str
    nome: str
    categoria: str
    aliquota_base: Decimal

    def __post_init__(self) -> None:
        for campo in ("id", "nome", "categoria"):
            validar_texto_obrigatorio(getattr(self, campo), campo)
        validar_decimal_nao_negativo(self.aliquota_base, "Alíquota base")
