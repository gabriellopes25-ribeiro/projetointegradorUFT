# Sprint 2 — Sistema de Inteligência Tributária (SITRIB)

**Equipe:** Adriel Morais, Gabriel Lopes, João Pedro Figueredo, Rayssa de Oliveira
**Entrega:** 02/10/2026

## O que foi feito

Nesta sprint, implementamos as três estruturas de dados centrais do sistema — tabela hash, heap (fila de prioridade) e grafo — e as integramos ao backend da aplicação. Também construímos o banco de dados relacional completo: modelagem normalizada (3FN), criação do schema, população com uma massa de dados simulados (piloto) e consultas SQL de validação sobre esses dados. Por fim, documentamos a arquitetura do sistema e o plano de integração e segurança com os sistemas da Prefeitura de Palmas.

- **Tabela Hash:** indexação da dívida ativa por CPF/CNPJ, permitindo buscas O(1) em média.
- **Heap (fila de cobrança):** fila de prioridade ordenada por score de recuperabilidade, usada para decidir a ordem de cobrança dos contribuintes.
- **Grafo:** mapeamento das relações entre contribuinte, imóvel e processo judicial, permitindo identificar o mesmo CPF/CNPJ associado a múltiplas inscrições imobiliárias.
- **Orquestração no backend:** as três estruturas foram conectadas em `busca_service.py`, que serve como camada única de acesso a elas, e demonstradas em conjunto em `main.py`.
- **Banco de dados:** schema relacional normalizado (`schema.sql`) com as tabelas `contribuinte`, `imovel`, `divida` e `processo`; script de população (`scripts/popular_banco.py`) que gera o banco SQLite (`sitrib.db`) a partir de dados simulados; consultas de validação documentadas em `docs/consultas_validacao.md`.
- **Integração e segurança (E3):** documento `docs/integracao_prefeitura.md` especificando comunicação assíncrona, HTTPS/TLS 1.3, autenticação via JWT/API Key, rate-limiting e conformidade com a LGPD.

## Decisões de modelagem

Optamos por um modelo relacional normalizado em 3FN, separando contribuinte, imóvel, dívida e processo em tabelas distintas conectadas por chaves estrangeiras, o que evita redundância e permite que um mesmo contribuinte tenha múltiplos imóveis e um mesmo imóvel tenha múltiplas dívidas ao longo dos anos. Como ainda não há acesso a uma base pública de dívida ativa de Palmas-TO em formato de dados em lote, utilizamos dados fictícios (piloto) para popular e validar o banco, mantendo a estrutura compatível com uma futura carga de dados reais.

## Divisão de trabalho

- **Gabriel:** implementação da tabela hash e do heap (fila de cobrança), orquestração das três estruturas no backend, e redação deste relatório.
- **João Pedro:** implementação do grafo de relacionamentos contribuinte-imóvel-processo.
- **Adriel:** criação da massa de dados simulados (seeds), camada de serviço de busca e documento de integração com a Prefeitura.
- **Rayssa:** modelagem do diagrama ER, criação do schema do banco de dados e implementação do script de população do banco SQLite.

## Impedimentos para a Sprint 3

Ainda não temos acesso a uma base pública de dívida ativa de Palmas-TO em formato de dados em lote (apenas um portal de consulta individual está disponível), o que nos levou a usar dados simulados nesta sprint. Para a próxima sprint, pretendemos buscar uma fonte de dados real junto à Prefeitura ou ao professor da disciplina, além de evoluir o schema do banco com campos complementares (tipo de pessoa, tipo de imóvel, valor venal) identificados durante a modelagem.