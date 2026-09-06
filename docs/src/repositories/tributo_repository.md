# TributoRepository

**Código:** [repositories/tributo_repository.py](../../../src/repositories/tributo_repository.py) · **Requisitos:** RF04

## Estado atual
Contrato abstrato; banco não escolhido.

## Responsabilidade e conteúdo
salvar(tributo) retorna None; buscar_por_nome(nome) retorna Tributo ou None.

## Com quem trabalha
TributoService deverá depender desse contrato.

## Limites e cuidados
Definir duplicidade e persistência. Ainda não há busca por id nem listagem; fluxos futuros que precisarem delas exigem ampliar o contrato.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
