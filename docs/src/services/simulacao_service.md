# SimulacaoService

**Código:** [services/simulacao_service.py](../../../src/services/simulacao_service.py) · **Requisitos:** RF06–RF07

## Estado atual
Contrato abstrato.

## Responsabilidade e conteúdo
simular(tributo_id, usuario_id, valor_atual, percentual) retorna Simulacao; comparar(cenarios) retorna lista de dicionários de Decimal.

## Com quem trabalha
Produzirá Simulacao; poderá colaborar com dados de tributos e relatórios quando os contratos evoluírem.

## Limites e cuidados
Definir as chaves do resultado de comparação, referência, mínimo de dois cenários e base zero. Suporte a índice não está especificado no contrato. Não alterar o tributo real.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
