# Tributo

**Código:** [models/tributo.py](../../../src/models/tributo.py) · **Requisitos:** RF04–RF05

## Estado atual
Entidade e validações básicas implementadas.

## Responsabilidade e conteúdo
Contém id, nome, categoria e aliquota_base (Decimal em percentual). __post_init__ valida campos obrigatórios e alíquota finita não negativa.

## Com quem trabalha
TributoService deverá cadastrar; TributoRepository persistir; CalculoService calcular a partir da entidade.

## Limites e cuidados
Não consulta duplicidade, não salva e não calcula imposto. Zero é aceito; float e string são rejeitados na alíquota. Fórmulas e limites específicos seguem pendentes.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
