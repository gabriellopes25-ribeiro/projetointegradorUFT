# CalculoService

**Código:** [services/calculo_service.py](../../../src/services/calculo_service.py) · **Requisitos:** RF05

## Estado atual
Contrato abstrato; teste funcional ignorado.

## Responsabilidade e conteúdo
calcular(tributo, base_calculo) declara retorno Decimal.

## Com quem trabalha
Recebe Tributo. Autorização de administrador e log da operação deverão integrar o fluxo futuro.

## Limites e cuidados
Não há fórmula implementada. Não assumir que toda categoria usa a mesma fórmula. Definir precisão, arredondamento e validação da base antes de concluir RF05.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
