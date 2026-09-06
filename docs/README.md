# Guia da equipe — documentação do backend

Este é o índice técnico em docs. O README da aplicação continua reservado à Rayssa e ao João.

## Por onde começar
1. Leia [MVC e camadas](mvc-e-camadas.md).
2. Veja [casos de uso](uml/casos-de-uso.md): o que a pessoa quer fazer.
3. Consulte [classes](uml/classes.md): quem representa os dados e quem executa cada tarefa.
4. Acompanhe [sequências](uml/sequencias.md): em que ordem os participantes conversam.
5. Use o [espelho do código](src/README.md) para localizar cada arquivo.
6. Consulte [rastreabilidade](requisitos.md) e [decisões do Product Owner](produto.md).

**Estado atual:** entidades e validação básica de Tributo existem. Services e Repositories são contratos abstratos, sem implementação. Telas, controllers, banco, dashboard e logs ainda não existem.

Diagramas Mermaid são renderizados pelo GitHub. Nas sequências, todos os fluxos de negócio são propostas futuras; não significam que o sistema já funciona. Para editar, altere o bloco de texto entre as marcas mermaid e revise a visualização no GitHub.

## Como manter
Ao mudar um arquivo Python, revise o Markdown correspondente, os diagramas relacionados e a rastreabilidade. Documente o comportamento observado; marque propostas como planejadas. Não registre requisitos como concluídos apenas porque existe uma classe.
