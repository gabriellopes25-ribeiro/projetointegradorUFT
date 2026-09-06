# TributoService

**Código:** [services/tributo_service.py](../../../src/services/tributo_service.py) · **Requisitos:** RF04

## Estado atual
Contrato abstrato.

## Responsabilidade e conteúdo
cadastrar(tributo) recebe Tributo e declara retorno None.

## Com quem trabalha
Deverá usar TributoRepository para pesquisar duplicidade e salvar; a entidade já valida campos básicos.

## Limites e cuidados
Busca seguida de salvamento não garante unicidade em concorrência: a persistência futura também deverá assegurá-la. Quem pode cadastrar ainda deve ser definido.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
