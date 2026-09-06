"""Resultado previsto para RF06–RF07; não modifica o tributo real."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, kw_only=True)
class Simulacao:
    id: str
    tributo_id: str
    usuario_id: str
    percentual_reajuste: Decimal
    valor_antes: Decimal
    valor_depois: Decimal
    criada_em: datetime
