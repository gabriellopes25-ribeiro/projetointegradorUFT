## Projeto Integrador UFT

Projeto desenvolvido para a disciplina de Projeto Integrador, aplicando conceitos de **Scrum, Engenharia de Requisitos, Git e GitHub**.

## Identificação da Equipe

| Integrante | Matrícula | GitHub | E-mail | Papel |
|------------|-----------|--------|--------|-------|
| Adriel Morais | 2026112033 | @AadrielL | adriel.morais@mail.uft.edu.br | Product Owner (PO) |
| Gabriel Lopes | 2026111910 | @gabriellopes25-ribeiro | gabriel.lopes1@mail.uft.edu.br | Scrum Master (SM) |
| João Pedro Figueredo da Cunha | 2026112216 | @406561  | cunha.joao@mail.uft.edu.br | Desenvolvedor |
| Rayssa de Oliveira Santos | 2026111525 | @rayssa-oliveira05 | rayssa.oliveira@mail.uft.edu.br | Desenvolvedora |

**Repositório:** https://github.com/gabriellopes25-ribeiro/projetointegradorUFT

---

## Objetivo

Desenvolver um sistema para **gerenciamento e análise de tributos**, permitindo realizar cálculos, simulações de reajustes, comparação de cenários e consulta de informações.

---

## Tecnologias

* **Python 3.12+**
* **Git**
* **GitHub**
* **requirements.txt**

---

## Fundamentação dos Papéis Ágeis

### Product Owner — Adriel Morais

Responsável por representar os objetivos do projeto, organizar e priorizar o Backlog, esclarecer regras de negócio e validar as funcionalidades de acordo com os critérios de aceite.

### Scrum Master — Gabriel Lopes

Responsável por auxiliar na aplicação do Scrum, organizar os alinhamentos da equipe, acompanhar a Sprint e auxiliar na resolução de impedimentos.

### Equipe de Desenvolvimento

* João Pedro Figueiredo
* Rayssa de Oliveira

Responsáveis pelo desenvolvimento, testes e manutenção do sistema.

---

## Especificação de Requisitos Funcionais (RF)

| ID | Requisito | Descrição | Critérios de Aceite (Testáveis) |
|------|-----------|-----------|--------------------------------|
| RF01 | Cadastro de Usuário | Permite o registro de servidores no sistema. | E-mail único e validado; senha com tamanho mínimo; confirmação exibida ao concluir. |
| RF02 | Autenticação | Controla o acesso de usuários registrados. | Credenciais válidas liberam a sessão; inválidas exibem alerta e bloqueiam o acesso. |
| RF03 | Perfis de Acesso | Diferencia permissões entre tipos de usuário. | Admin acessa cálculo e simulação; perfil consulta só visualiza; acesso negado é registrado. |
| RF04 | Cadastro de Tributos | Gerencia os tipos de tributo (IPTU, ISS, alvarás). | Cada tributo salvo com nome, categoria e alíquota; sistema impede tributos duplicados. |
| RF05 | Cálculo de Tributos | Calcula o valor devido de um tributo. | Cálculo retorna valor correto conforme a alíquota; entradas inválidas geram erro claro. |
| RF06 | Simulação de Reajuste | Simula reajustes sobre as tarifas atuais. | Aplica percentual informado; exibe valor antes e depois; não altera os dados reais. |
| RF07 | Comparação de Cenários | Compara diferentes simulações de reajuste. | Exibe ao menos 2 cenários lado a lado com diferença absoluta e percentual. |
| RF08 | Histórico de Tarifas | Registra alterações de valores dos tributos. | Cada alteração grava data e valor; histórico consultável por tributo. |
| RF09 | Relatório de Arrecadação | Gera relatório de arrecadação estimada. | Soma valores por categoria; relatório exportável (CSV/PDF). |
| RF10 | Painel de Indicadores | Exibe indicadores-chave dos tributos. | Painel carrega dados atualizados e exibe ao menos 3 indicadores. |
| RF11 | Log de Operações | Registra ações críticas do sistema. | Cada operação (cálculo, simulação, alteração) gera log com autor e data. |

---

## Requisitos Não Funcionais (RNF)

| ID | Categoria | Descrição da Restrição | Métrica / Forma de Teste |
|-------|-----------|------------------------|--------------------------|
| RNF01 | Tecnologia / Backend | O sistema deve ser desenvolvido em linguagem Python. | Compatível com Python 3.12 ou superior. |
| RNF02 | Portabilidade | As dependências devem estar isoladas e documentadas. | Instalação com comando padrão via requirements.txt. |
| RNF03 | Usabilidade | O sistema deve dar retorno claro a cada ação do usuário. | Feedback visual/textual de sucesso ou erro em todas as operações. |
| RNF04 | Documentação | O README deve permitir a reprodução do projeto. | Setup completo por terceiros, sem erros, seguindo o README. |
| RNF05 | Segurança | As senhas não podem ser armazenadas em texto puro. | Verificação de que a senha é gravada com hash (criptografada). |
---

## Matriz de Priorização MoSCoW

### Must Have

RF01, RF02, RF03, RF04, RF05, RF06, RNF01, RNF02, RNF05

### Should Have

RF07, RF08, RF10, RNF03, RNF04

### Could Have

RF09, melhorias visuais e funcionalidades secundárias.

### Won't Have

Funcionalidades que não fazem parte do escopo da primeira entrega.

---

## Arquitetura e Estrutura do Projeto

A arquitetura do sistema evoluiu entre as entregas, mantendo rigoroso desacoplamento e facilitando o trabalho colaborativo:

### Visão Geral da Árvore de Diretórios

```text
projetointegradorUFT/
├── docs/                        # Documentação técnica, requisitos, UML e segurança
│   ├── uml/                     # Diagramas de Casos de Uso, Classes e Sequência (Sprint 1)
│   ├── src/                     # Espelho explicativo dos arquivos de código
│   ├── integracao_prefeitura.md # [Sprint 2] Diretrizes de integração assíncrona e LGPD
│   └── arquitetura.md           # Visão arquitetural consolidada (Sprint 1 e 2)
│
├── seeds/                       # [Sprint 2] Módulo de povoamento e dados realistas
│   ├── __init__.py              # Exportações do pacote seeds
│   └── mock_data.py             # DTOs, massa de dados e motor plug-and-play
│
├── src/                         # Código-fonte principal (Padrão MVC em camadas)
│   ├── models/                  # [Sprint 1] Entidades de domínio (Usuario, Tributo, Simulacao, Historico)
│   ├── repositories/            # [Sprint 1] Contratos abstratos de acesso a dados
│   ├── services/                # Regras de negócio e serviços
│   │   ├── autenticacao_service.py # [Sprint 1] Contrato de autenticação
│   │   ├── tributo_service.py      # [Sprint 1] Contrato de tributos
│   │   ├── calculo_service.py      # [Sprint 1] Contrato de cálculo de alíquotas
│   │   ├── simulacao_service.py    # [Sprint 1] Contrato de simulação de cenários
│   │   ├── relatorio_service.py    # [Sprint 1] Contrato de arrecadação
│   │   └── busca_service.py        # [Sprint 2] Serviço de busca cadastral e dossiê fiscal
│   ├── estruturas/              # [Sprint 2] Pacote de Estruturas de Dados Avançadas
│   │   ├── __init__.py          # Exportações do pacote estruturas
│   │   ├── tabela_hash.py       # Indexação O(1) de débitos por CPF
│   │   ├── fila_cobranca.py     # Heap de priorização O(log n) de cobrança
│   │   └── grafo.py             # Mapeamento de relações Contribuinte-Imóvel-Processo
│   ├── utils/                   # [Sprint 1] Validações básicas compartilhadas
│   └── main.py                  # [Sprint 1] Ponto de entrada e diagnóstico da estrutura
│
├── tests/                       # Suíte de testes unitários e de integração
│   ├── test_tributo.py          # [Sprint 1] Testes das validações de Tributo
│   ├── test_usuario.py          # [Sprint 1] Testes de perfil padrão e segurança de Usuario
│   ├── test_calculo.py          # [Sprint 1] Testes do contrato de cálculo
│   ├── test_tabela_hash.py      # [Sprint 2] Testes da tabela hash e buscas
│   ├── test_fila_cobranca.py    # [Sprint 2] Testes do max-heap de cobrança
│   └── test_busca_validacao.py  # [Sprint 2] 13 testes de busca, dossiê e injeção de seeds
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

### O que pertencia à Sprint 1 (Base e Contratos Iniciais)
Na **Sprint 1**, o foco da equipe foi o setup do repositório, especificação de requisitos (RF01–RF11 e RNF01–RNF05), modelagem UML e os contratos fundamentais do backend:
* **`src/models/`**: Definição das dataclasses imutáveis `Usuario`, `Tributo`, `Simulacao` e `Historico`.
* **`src/repositories/`**: Interfaces abstratas de persistência (`UsuarioRepository`, `TributoRepository`).
* **`src/services/`**: Contratos abstratos para autenticação, cálculo, simulação e relatórios.
* **`src/utils/`**: Validações de textos obrigatórios e valores `Decimal` não negativos.

---

### O que foi entregue na Sprint 2 (Estruturas Avançadas, Busca e Seeds)
A **Sprint 2** agregou estruturas de dados eficientes, suíte abrangente de testes, dados fictícios/realistas e preparação para integração externa:

#### 1. Pasta `seeds/` (Povoamento e Mocks Plug-and-Play)
* **Objetivo da pasta:** Centralizar dados de teste realistas do município de Palmas/TO e permitir que o sistema rode testes completos sem depender do banco de dados físico estar finalizado.
* **Classes e Componentes:**
  * **`ContribuinteMock`**: DTO tipado para pessoa física e jurídica (Nome, CPF/CNPJ, e-mail, telefone).
  * **`ImovelMock`**: DTO com dados de Inscrição Imobiliária (CCI), endereço em quadras de Palmas, tipo de imóvel e valor venal.
  * **`DividaMock`**: DTO contendo código de débito, ano exercício, valor original, juros/multa, tributo (IPTU, ISS, Taxas) e status (`ATIVO`/`AJUIZADO`).
  * **`ProcessoMock`**: DTO de processos de execução fiscal com número no padrão CNJ, vara competente e data de autuação.
  * **`BancoSimuladoEmMemoria`**: Emulador de repositório em memória com índices rápidos para buscas por CPF/CNPJ e CCI.
  * **`executar_seed(model_registry, db_session)`**: Função inteligente que roda em modo simulado nos testes atuais e aceita injeção direta das classes ORM/SQLAlchemy da Rayssa no momento da integração final com o banco.

#### 2. Pasta `src/estruturas/` (Estruturas de Dados Avançadas)
* **`src/estruturas/tabela_hash.py` (`TabelaHashDivida`)**:
  * *O que faz:* Implementa tabela hash com tratamento de colisões para indexação e busca ultra-rápida ($O(1)$ médio) do valor de dívida ativa a partir do CPF do contribuinte.
* **`src/estruturas/fila_cobranca.py` (`FilaCobranca`)**:
  * *O que faz:* Implementa fila de prioridade baseada em max-heap binário (usando `heapq`), priorizando automaticamente contribuintes com maior score de inadimplência em tempo logarítmico ($O(\log n)$) sem necessidade de ordenação completa da lista.
* **`src/estruturas/grafo.py` (`GrafoContribuintes`)**:
  * *O que faz:* Modela um grafo por lista de adjacência (`dict[str, list[dict]]`), conectando o contribuinte aos seus respectivos imóveis e processos de execução fiscal ($O(1)$ na inserção e busca direta de adjacências).

#### 3. Pasta `src/services/` (Serviços do Domínio)
* **`src/services/busca_service.py` (`BuscaService`)**:
  * *O que faz:* Centraliza as regras de negócio para busca cadastral unificada e geração do dossiê fiscal imobiliário. Valida documentos (11 dígitos para CPF, 14 para CNPJ) e lança exceções especializadas (`DocumentoInvalidoError`, `ContribuinteNaoEncontradoError`, `ImovelNaoEncontradoError`).

#### 4. Pasta `tests/` — Testes Automatizados da Sprint 2
* **`test_tabela_hash.py`**: Validação de inserção, busca e chave não encontrada.
* **`test_fila_cobranca.py`**: Validação de ordenação por prioridade, desempate e fila vazia.
* **`test_busca_validacao.py`**: 13 testes cobrindo busca por CPF/CNPJ (com e sem máscara), tratamento de erros, dossiê do imóvel e simulação de injeção das models da Rayssa.

#### 5. Pasta `docs/` — Integração com a Prefeitura
* **`docs/integracao_prefeitura.md`**: Detalha a arquitetura assíncrona (`asyncio`/`aiohttp`), protocolo HTTPS com TLS 1.3, autenticação via JWT/API Key, limitação de taxa (*rate-limiting*) e conformidade com a LGPD (mascaramento de dados e trilhas imutáveis de auditoria).

---

### 🚀 Futuros Upgrades (Próximas Sprints / Roadmap)

1. **Camada de Persistência com Banco Relacional (Rayssa):**
   * Criação dos esquemas e tabelas em banco de dados relacional (PostgreSQL / SQLite via SQLAlchemy).
   * Integração plug-and-play imediata com `seeds.mock_data.executar_seed(model_registry, db_session)`.
2. **Camada Controller e Interface de Usuário (Gabriel, João Pedro e Equipe):**
   * Implementação dos Controllers no padrão MVC conectando as entradas do usuário aos serviços de busca e cálculo.
   * Criação de interface interativa (CLI com menus dinâmicos ou endpoints RESTful com FastAPI).
3. **Consumo Assíncrono ao Vivo das APIs Municipais:**
   * Implementação de webhooks e workers assíncronos para consumo dos dados fiscais da Prefeitura de Palmas conforme especificado em `docs/integracao_prefeitura.md`.
4. **Painel de Indicadores e Projeções Financeiras (RF10):**
   * Implementação de telas e relatórios para visualização gráfica da arrecadação e simulação de impactos orçamentários.

---

## Comprovação de Contribuições no Git

Cada integrante deve realizar suas alterações utilizando Git e registrar suas contribuições por meio de commits.

Fluxo básico:

```text
Branch → Commit → Push → Pull Request → Merge
```

A participação dos integrantes será comprovada por meio do **histórico de commits e painel de contribuidores do GitHub**, conforme solicitado na atividade.

**Painel de Contribuidores:**

<img width="900" height="906" alt="Captura de tela 2026-09-12 104343" src="https://github.com/user-attachments/assets/d4279301-6c07-4952-8a10-594a3e6bd086" />


**Histórico de Commits:**

<img width="1459" height="726" alt="Captura de tela 2026-09-12 104750" src="https://github.com/user-attachments/assets/6acca093-7577-4c1a-8fe1-b863f10e6e6c" />
<img width="1341" height="597" alt="Captura de tela 2026-09-12 104756" src="https://github.com/user-attachments/assets/24c6e3e2-217a-4f62-8f3e-09b2d5d2ae34" />


---

## Status do Projeto

* **Sprint 1 — Setup, Requisitos e Contratos Base:** ✅ **Concluída**
  * [x] Repositório estruturado com padrão Python/MVC
  * [x] Requisitos funcionais (RF01–RF11) e não funcionais (RNF01–RNF05)
  * [x] Matriz de priorização MoSCoW
  * [x] Modelagem UML (Casos de Uso, Classes, Sequência)
  * [x] Contratos e validações básicas de domínio
* **Sprint 2 — Estruturas de Dados, Busca, Seeds e Testes:** ✅ **Concluída**
  * [x] Tabela Hash para busca indexada de débitos ($O(1)$)
  * [x] Max-Heap para fila de prioridade de cobrança ($O(\log n)$)
  * [x] Grafo com lista de adjacência para relacionamento Contribuinte-Imóvel-Processo
  * [x] Povoamento com dados realistas de Palmas/TO e engine de seeds plug-and-play (`seeds/`)
  * [x] Serviço de busca unificada e dossiê fiscal imobiliário (`BuscaService`)
  * [x] Suíte de testes automatizados completa (20 testes passando)
  * [x] Documentação técnica de arquitetura assíncrona, segurança e LGPD
* **Sprint 3 — Banco Relacional, Controllers e Interface:** ⏳ **Planejada (Roadmap)**
  * [ ] Modelagem física do banco e tabelas ORM (Rayssa)
  * [ ] Controllers MVC e interface de usuário/CLI (Gabriel e João Pedro)
  * [ ] Integração ativa com endpoints externos da prefeitura
  
## Esquema do Banco de Dados

```text
[ CONTRIBUINTE ] (1 : N) ──> [ IMÓVEL ] (1 : N) ──> [ DÍVIDA ] (1 : N) ──> [ PROCESSO ]

