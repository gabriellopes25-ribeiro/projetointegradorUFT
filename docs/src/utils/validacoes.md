# Funções de validação

**Código:** [utils/validacoes.py](../../../src/utils/validacoes.py) · **Requisitos:** RF04; apoio a RNF03

## Estado atual
Implementadas e chamadas por Tributo.

## Responsabilidade e conteúdo
validar_texto_obrigatorio rejeita valores que não sejam texto ou estejam vazios após strip. validar_decimal_nao_negativo exige Decimal finito e não negativo. Ambas retornam None ou lançam ValueError.

## Com quem trabalha
Tributo chama as funções em __post_init__. São funções, não classes de serviço.

## Limites e cuidados
Não normalizam os campos nem convertem float. Não validam e-mail, senha, duplicidade ou regras legais. A interface futura deverá apresentar os erros de forma clara.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
