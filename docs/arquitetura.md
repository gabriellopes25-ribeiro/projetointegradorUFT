# Arquitetura Inicial do Sistema

## Objetivo e escopo
Preparar o backend Python para os requisitos RF01–RF11 e RNF01–RNF05 descritos no README. Esta entrega contém entidades, contratos abstratos, validações básicas de Tributo e testes. Não entrega autenticação, banco de dados, API nem cálculo de tributos.

## Organização e decisões
- **Models:** Usuario, Tributo, Simulacao e Historico representam os dados do domínio. Dataclasses imutáveis evitam alterações acidentais.
- **Services:** contratos abstratos delimitam autenticação, cadastro, cálculo, simulação, comparação e relatórios. Não podem ser instanciados sem implementação.
- **Repositories:** contratos de acesso a usuários e tributos permitem escolher a persistência sem acoplar as regras de negócio ao banco.
- **Utils:** valida textos obrigatórios e valores Decimal finitos não negativos em Tributo; as demais políticas ainda precisam ser definidas.
- **Tests:** verificam a estrutura disponível e as validações de Tributo. Não comprovam o atendimento dos requisitos funcionais.

Valores monetários, alíquotas e percentuais usam Decimal. Alíquotas são expressas em percentual (1.25 significa 1,25%). Fórmulas por tributo, arredondamento e limites de entrada serão definidos antes da implementação de RF05.

Usuario possui senha_hash, omitido da representação textual. Isso não implementa hashing nem valida que o conteúdo seja um hash: RNF05 continua pendente. O serviço futuro deverá gerar e verificar hashes com algoritmo apropriado e nunca persistir a senha recebida. O perfil padrão é consulta; autorização e cadastro de administradores ainda serão implementados.

Simulacao representa um cenário hipotético separado do Historico de alterações reais. Datas deverão usar fuso horário explícito na implementação. Repositórios de histórico/simulações e transações serão adicionados quando a persistência for definida.

## Fluxo previsto
Usuário → Interface/API → Services → Models / Repositories → Persistência

Interface/API, injeção dos repositórios e persistência são etapas futuras. src/main.py apenas confirma que a estrutura pode ser executada.

## Relação com requisitos
| Componente | Requisitos |
|---|---|
| Usuario / AutenticacaoService | RF01, RF02, RF03 |
| Tributo / TributoService | RF04 |
| CalculoService | RF05 |
| Simulacao / SimulacaoService | RF06, RF07 |
| Historico | RF08 |
| RelatorioService | RF09 |
| Dashboard (futuro) | RF10 |
| Log (futuro) | RF11, registro de acesso negado de RF03 |

## Próximas decisões da equipe
Definir política de senha, normalização e unicidade de e-mails/tributos, banco, sessão, matriz de permissões e regras de cálculo. Detalhar o resultado da comparação (referência, diferenças e base zero) e os dados necessários à arrecadação estimada (categorias e quantidades). Os contratos iniciais podem ser refinados nessas entregas.

## Guia técnico
Consulte [desenvolvimento.md](desenvolvimento.md) para execução, regras implementadas e próximos passos. O README da aplicação fica com Rayssa e João.


## Navegação e relação com MVC
Esta organização em camadas ainda não possui View nem Controller. Consulte
[MVC e camadas](mvc-e-camadas.md) para entender a relação sem confundir os
conceitos. O [guia da equipe](README.md) reúne o espelho dos arquivos Python,
os diagramas e as decisões pendentes do Product Owner.

## Sprint 2 — Pacote de Estruturas de Dados Avançadas (src/estruturas/)

### Tabela Hash (src/estruturas/tabela_hash.py)
**Uso:** indexação e busca rápida de dados de contribuintes/dívida ativa.

**Complexidade:**
- Inserção: O(1) em média; O(n) no pior caso (colisões)
- Busca: O(1) em média; O(n) no pior caso

**Testes:** implementados e passando em `tests/test_tabela_hash.py`.

### Heap — Fila de Cobrança (src/estruturas/fila_cobranca.py)
**Uso:** priorização de contribuintes a serem cobrados, por score/prioridade,
sem precisar ordenar a lista inteira a cada consulta.

**Implementação:** heap binário via módulo `heapq`, simulando max-heap ao
armazenar `(-score, cpf)`.

**Complexidade:**
- `inserir(score, cpf)`: O(log n)
- `proximo_a_cobrar()`: O(log n)
- Espaço: O(n)

**Testes:** 3 testes em `tests/test_fila_cobranca.py`, cobrindo fila vazia,
ordem de prioridade e empate de score — todos passando.

### Grafo de Relacionamentos Fiscais (src/estruturas/grafo.py)
**Responsável:** João Pedro

**Uso:** Representação das conexões e vínculos cadastrais entre Contribuinte (CPF/CNPJ), Imóveis vinculados e Processos de Execução Fiscal. Permite identificar rapidamente a malha patrimonial e jurídica de um devedor.

**Classe:** `GrafoContribuintes`
- `adicionar_relacao(cpf_cnpj, imovel, processo)`: estabelece uma aresta direcionada entre o contribuinte e o conjunto imóvel-processo.
- `buscar_relacionados(cpf_cnpj)`: retorna a lista de todos os nós (imóveis e processos) associados ao contribuinte.

**Estrutura escolhida:** Lista de adjacência implementada com dicionário de listas (`dict[str, list[dict]]`).

**Complexidade:**
- Inserção de aresta: $O(1)$ amortizado
- Busca de adjacências diretas por nó: $O(1)$ médio
- Espaço: $O(V + E)$, onde $V$ são os contribuintes e $E$ as ligações imobiliárias/processuais.

**Testes:** Verificação de inserção e recuperação de relacionamentos via CLI em `src/grafo.py`.

---

## Sprint 2 — Seeds, Serviço de Busca e Validação Fiscal
**Responsável:** Adriel Morais

### 1. Povoamento e Mocks (`seeds/mock_data.py`)
Massa de dados realista de Palmas/TO com DTOs tipados (`ContribuinteMock`, `ImovelMock`, `DividaMock`, `ProcessoMock`) e motor plug-and-play:
- **`BancoSimuladoEmMemoria`**: emula índices de busca relacional em memória com complexidade $O(1)$ para testes unitários antes da entrega do banco real.
- **`executar_seed(model_registry, db_session)`**: aceita injeção direta das classes ORM/SQLAlchemy da Rayssa, populando o banco de forma automática no ambiente final.

### 2. Camada de Serviço de Busca (`src/services/busca_service.py`)
Implementa as regras de negócio para busca cadastral unificada e dossiê imobiliário:
- **`BuscaService`**: validação estrutural de CPF (11 dígitos) e CNPJ (14 dígitos), tratamento de erros (`DocumentoInvalidoError`, `ContribuinteNaoEncontradoError`, `ImovelNaoEncontradoError`) e consolidação de débitos e execuções fiscais por imóvel.

### 3. Integração com a Prefeitura (`docs/integracao_prefeitura.md`)
Especificação formal da comunicação assíncrona, segurança com HTTPS/TLS 1.3, autenticação JWT/API Key, rate-limiting e conformidade com a LGPD (anonimização e mascaramento de dados sensíveis).

### 4. Camada de Persistência Real (`src/repositories/sqlite_repository.py`)
**Responsável:** Gabriel (adiantado da Sprint 3)

Implementa o repositório que conecta o `BuscaService` ao banco de dados real (`sitrib.db`), substituindo o `BancoSimuladoEmMemoria` sem alterar nenhum código que já dependia dele:
- **`RepositorioSQLite`**: implementa o mesmo contrato (`buscar_contribuinte`, `buscar_imovel`, `listar_dividas_por_imovel`, `listar_processos_por_imovel`, `listar_imoveis_por_contribuinte`, além das coleções `.contribuintes` e `.imoveis`), mas lendo os dados reais via `sqlite3`.
- Testado em `tests/test_sqlite_repository.py`, incluindo testes de integração que provam que a Tabela Hash, o Heap e o Grafo funcionam sem alteração ao receber esse repositório no lugar do mock.

---

## Futuros Upgrades (Próximas Sprints / Roadmap)

1. **Controllers e Interface com Usuário (Sprint 3 — Gabriel e Equipe):**
   - Criação da camada Controller no padrão MVC para intermediar chamadas entre entrada de dados e serviços (`BuscaService`, `CalculoService`).
   - Interface interativa (CLI com menus dinâmicos ou endpoints RESTful com FastAPI).
2. **Consumo Assíncrono ao Vivo das APIs da Prefeitura:**
   - Implementação de cliente `aiohttp` com *circuit breaker* e retentativa exponencial (*exponential backoff*) seguindo as diretrizes de `docs/integracao_prefeitura.md`.
3. **Dashboard de Indicadores e Projeções (RF10):**
   - Agregação de métricas de arrecadação por zona fiscal e geração de gráficos de inadimplência.