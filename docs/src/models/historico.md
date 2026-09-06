# Historico

**Código:** [models/historico.py](../../../src/models/historico.py) · **Requisitos:** RF08

## Estado atual
Entidade existente; gravação e consulta pendentes.

## Responsabilidade e conteúdo
Contém id, tributo_id, usuario_id, valor_anterior, valor_atual e alterado_em.

## Com quem trabalha
Um fluxo futuro de alteração real deverá gerar o registro junto com a persistência do novo valor.

## Limites e cuidados
Não é um log geral de ações e não deve registrar simulações como alterações efetivas. Ainda não há serviço ou repositório de histórico.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
