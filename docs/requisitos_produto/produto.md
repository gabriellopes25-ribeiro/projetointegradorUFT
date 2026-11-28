# Acompanhamento do Product Owner

O Product Owner ajuda a esclarecer necessidades, ordenar o trabalho e verificar o resultado com os critérios de aceite. Este documento registra pontos para discussão; não inventa decisões já aprovadas pela equipe.

## Funcionalidades e colaboração
| Funcionalidade | Classes que colaboram | O que falta esclarecer |
|---|---|---|
| Cadastro e acesso — RF01–03 | Usuario, Perfil, AutenticacaoService, UsuarioRepository | Política de senha, sessão, criação de administrador e matriz de permissões |
| Cadastro de tributo — RF04 | Tributo, TributoService, TributoRepository | Critério de duplicidade e normalização de nome |
| Cálculo — RF05 | Tributo, CalculoService | Fórmulas por categoria, entradas e arredondamento |
| Simulação e comparação — RF06–07 | Simulacao, SimulacaoService | Índices, cenário de referência e comparação com base zero |
| Histórico — RF08 | Historico, Tributo | Consulta, persistência e aplicação de reajuste real |
| Relatório — RF09 | RelatorioService, Simulacao e dados futuros de tributos | Quantidades, categorias e regra de arrecadação |
| Indicadores e logs — RF10–11 | Componentes ainda não criados | Indicadores, eventos e forma de armazenamento |

## Perguntas para validar em equipe
- Quem pode cadastrar tributos, consultar histórico e exportar relatórios? RF03 só explicita cálculo e simulação para administrador e consulta somente para visualização.
- Como identificar tributo duplicado? Nome sozinho ou combinação de campos?
- Quem aplica um reajuste real? Simular não aplica alterações.
- Quais dados tornam uma simulação uma estimativa de arrecadação? Somar tarifas isoladas não basta.
- Como calcular diferença percentual quando o valor de referência é zero?

## Como aceitar uma entrega
Use os critérios do README e registre evidência: cenário, entrada, resultado esperado, resultado obtido e teste. Uma assinatura de método é estrutura preparada, não requisito entregue. A aceitação final depende do comportamento completo e da revisão da equipe.

A documentação descreve as validações básicas de Tributo já implementadas. Os demais fluxos dos diagramas são planejados. A priorização definitiva deve ser acordada com a equipe; nenhuma prioridade foi inventada aqui.
