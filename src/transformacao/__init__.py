"""
Pacote de Transformação e Engenharia de Atributos (SITRIB).
Responsável: Adriel Morais (Product Owner / Desenvolvedor)
Sprint 3 — Pipeline ETL (Módulo 5)
"""

from .features import (
    gerar_atributos_inadimplencia,
    calcular_score_prioridade,
    anonimizar_lgpd,
    mascarar_documento,
    mascarar_telefone,
    mascarar_email,
)

__all__ = [
    "gerar_atributos_inadimplencia",
    "calcular_score_prioridade",
    "anonimizar_lgpd",
    "mascarar_documento",
    "mascarar_telefone",
    "mascarar_email",
]
