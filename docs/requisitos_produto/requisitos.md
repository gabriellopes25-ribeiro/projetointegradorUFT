# Rastreabilidade dos Requisitos

A fonte dos critérios de aceite é o README.md. "Estrutura preparada" significa entidade ou contrato criado; nenhum RF está concluído nesta entrega.

| Requisito | Módulo previsto | Status e pendências |
|---|---|---|
| RF01 | usuario / autenticacao / usuario_repository | Estrutura preparada; cadastro, validações, unicidade e confirmação pendentes |
| RF02 | autenticacao | Contrato preparado; credenciais e sessão pendentes |
| RF03 | usuario / autenticacao | Perfis definidos; autorização e log de negação pendentes |
| RF04 | tributo / tributo_service / tributo_repository | Validação básica da entidade implementada; cadastro e duplicidade pendentes |
| RF05 | calculo | Contrato preparado; fórmula e validações pendentes |
| RF06 | simulacao | Estrutura preparada; aplicação de reajuste pendente |
| RF07 | simulacao | Contrato preparado; comparação e diferenças pendentes |
| RF08 | historico | Entidade preparada; persistência e consulta pendentes |
| RF09 | relatorio | Contratos CSV/PDF preparados; agregação e exportação pendentes |
| RF10 | dashboard | Planejado |
| RF11 | log | Planejado |

| Requisito não funcional | Evidência atual | Pendência |
|---|---|---|
| RNF01 | Código Python com alvo 3.12+ | Verificar também no Python 3.12 |
| RNF02 | requirements.txt; apenas biblioteca padrão nesta etapa | Atualizar manifesto ao adicionar dependências |
| RNF03 | Mensagem demonstrativa e erros claros na validação de Tributo | Feedback de cada operação |
| RNF04 | Guia técnico em docs/desenvolvimento.md | README da aplicação a cargo de Rayssa e João |
| RNF05 | Campo senha_hash sem exposição em repr | Implementar e testar hashing e persistência segura |

## Testes iniciais
- test_usuario.py: perfil padrão consulta e hash omitido na representação.
- test_tributo.py: preservação de Decimal, imutabilidade e validação de campos e alíquotas, incluindo zero e valores não finitos.
- test_calculo.py: contrato abstrato não pode ser usado como cálculo pronto; teste funcional explicitamente ignorado até RF05 ser implementado.

Os testes estruturais não substituem os critérios de aceite. Cada integrante deve implementar e testar sua contribuição e realizar commits com a própria conta.


## Documentação por componente e fluxo
Consulte o [espelho do código](src/README.md), o [diagrama de classes](uml/classes.md),
os [casos de uso](uml/casos-de-uso.md) e as [sequências planejadas](uml/sequencias.md).
Os identificadores UC01–UC11 são auxiliares e correspondem a RF01–RF11; os
critérios oficiais continuam no README da aplicação.
