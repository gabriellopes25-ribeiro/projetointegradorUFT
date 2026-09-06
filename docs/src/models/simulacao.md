# Simulacao

**Código:** [models/simulacao.py](../../../src/models/simulacao.py) · **Requisitos:** RF06–RF07

## Estado atual
Entidade existente; regras e persistência pendentes.

## Responsabilidade e conteúdo
Contém id, tributo_id, usuario_id, percentual_reajuste, valor_antes, valor_depois e criada_em.

## Com quem trabalha
SimulacaoService deverá produzir cenários; RelatorioService poderá consumir resultados.

## Limites e cuidados
Os campos *_id são referências por identificador, não objetos associados automaticamente. Criar uma simulação não deve aplicar reajuste real. A entidade ainda não valida coerência dos valores.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
