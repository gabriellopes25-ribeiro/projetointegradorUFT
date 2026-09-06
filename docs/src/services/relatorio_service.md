# RelatorioService

**Código:** [services/relatorio_service.py](../../../src/services/relatorio_service.py) · **Requisitos:** RF09

## Estado atual
Contrato abstrato.

## Responsabilidade e conteúdo
gerar_csv(simulacoes) retorna str; gerar_pdf(simulacoes) retorna bytes.

## Com quem trabalha
Recebe Simulacao; precisará também de categorias e dados para estimar arrecadação.

## Limites e cuidados
O contrato inicial ainda é insuficiente para todos os critérios de RF09. Definir quantidades, agrupamento, totais e formato antes de implementar. Não há biblioteca de PDF instalada por esta estrutura.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
