"""Validações básicas compartilhadas pelas entidades do domínio."""
from decimal import Decimal


def validar_texto_obrigatorio(valor: str, campo: str) -> None:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} deve ser um texto não vazio.")


def validar_decimal_nao_negativo(valor: Decimal, campo: str) -> None:
    # Não converte float silenciosamente, para preservar precisão decimal.
    if not isinstance(valor, Decimal):
        raise ValueError(f"{campo} deve ser informado como Decimal.")
    if not valor.is_finite() or valor < 0:
        raise ValueError(f"{campo} deve ser finito e maior ou igual a zero.")
