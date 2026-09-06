"""Registro previsto para RF08; separado de simulações hipotéticas."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, kw_only=True)
class Historico:
    id: str
    tributo_id: str
    usuario_id: str
    valor_anterior: Decimal
    valor_atual: Decimal
    alterado_em: datetime
