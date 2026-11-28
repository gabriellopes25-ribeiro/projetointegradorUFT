# 📘 Guia de Apresentação — Sprint 3: O Frontend, a Conexão com as APIs da Prefeitura & a Crise dos Dados

**Sistema de Inteligência Tributária (SITRIB) — Projeto Integrador UFT**  
**Período Oficial:** 18/10/2026 a 05/11/2026  
**Documento Anterior:** [`Guia_Sprint_2.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_2.md)  
**Documento Posterior:** [`Guia_Sprint_4.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_4.md)  

---

## 1. 🎯 Objetivos Centrais da Sprint 3

A Sprint 3 representou a **maior virada técnica e metodológica de todo o projeto**. A equipe enfrentou dois desafios monumentais:
1. **Desenvolvimento e Lançamento do Frontend Web:**
   * Criação de uma interface rica, reativa e profissional em **React 18 + TypeScript + Vite + Tailwind CSS** (repositório dedicado `sitrib-frontend`).
2. **A Batalha pela Realidade dos Dados:**
   * Substituir as 4 seeds mockadas do Sprint 2 pela **ingestão em larga escala de dados reais da Prefeitura de Palmas e do IBGE**.
   * Enfrentar e solucionar as instabilidades de rede, códigos HTTP de bloqueio e anomalias contábeis graves nas APIs municipais.

---

## 2. 👥 Papéis e Contribuições da Equipe na Sprint 3

| Integrante | Papel Scrum | Entregas Críticas na Sprint 3 |
| :--- | :--- | :--- |
| **Gabriel Lopes** | Scrum Master | Desenvolvimento do **`coletor_prefeitura.py`** com suporte a *rate-limiting* e exportação de dados brutos em `data/bruto/`. |
| **Rayssa de Oliveira** | Desenvolvedora | **Integração com API do IBGE** (`src/enriquecimento/integracao_ibge.py`), elaboração do **Relatório EDA** e geração do mapa geoespacial HTML (`docs/mapas/mapa_inadimplencia.html`). |
| **Adriel Morais** | Product Owner | Criação do repositório do **Frontend** (`sitrib-frontend`), pipeline de **Engenharia de Atributos** (`src/transformacao/features.py`), mascaramento de dados (LGPD) e documentação de reprodutibilidade. |
| **João Pedro Figueredo** | Desenvolvedor | Desenvolvimento do orquestrador **`etl_sefin.py`** em três camadas (Bronze/Prata/Ouro) e testes unitários do pipeline. |
| **Samuel Jacó** | Integrante Convidado | Integração do ecossistema e diagnóstico de APIs (`docs/relatorios_tecnicos/relatorio_ecossistema.md`). |

---

## 3. 📜 Relação de Commits e Autoria da Sprint 3

| Hash | Data | Autor | Mensagem do Commit | O que foi entregue |
| :---: | :---: | :--- | :--- | :--- |
| `c1b3f20` | 18/10/2026 | Gabriel Lopes | `feat(coleta): adiciona coletor da API com rate-limiting e dados brutos em data/bruto` | Módulo de conexão HTTP com backoff para os endpoints da prefeitura. |
| `16ef7d8` | 18/10/2026 | Rayssa de Oliveira | `feat(eda): adiciona integracao IBGE, relatorio EDA com frases de leitura e mapa geoespacial` | Cruzamento censitário de Palmas (313k habitantes) e mapa Folium. |
| `b023795` | 20/10/2026 | Adriel Morais | `feat(features): adiciona engenharia de atributos, mascaramento LGPD e atualiza README para reprodutibilidade` | Cálculo de features tributárias (`razao_divida_venal`, `icr_renda`) e anonimização de CPFs. |
| `1255495` | 20/10/2026 | João Pedro | `feat(etl): adiciona orquestrador etl_sefin.py, testes unitarios e requisitos atualizados` | Pipeline ETL completo com extração, limpeza e carregamento. |
| `4493710` | 20/10/2026 | Samuel Jacó | `feat: integra ecossistema, auditoria de apis e servico de relatorios` | Diagnóstico de status das APIs públicas municipais. |
| `786b8ba` | 22/10/2026 | Adriel Morais | `chore: remove dados gerados em data/ e sitrib.db do rastreamento git` | Limpeza do Git para evitar arquivos de banco de dados pesados no repositório. |
| `1000ed3` | 05/11/2026 | Adriel Morais | `feat(api): servidor REST FastAPI com 7 endpoints e suite de testes de validacao veridica` | Transição do backend para FastAPI assíncrono conectando ao Frontend. |

---

## 4. 📂 Parecer da Arquitetura de Pastas (A Chegada do Frontend e da Coleta)

A arquitetura do projeto expandiu-se com a introdução de camadas de extração em lote e da aplicação web:

```text
projetointegradorUFT/  (Evolução da Sprint 3 — Novembro/2026)
├── etl_sefin.py                      # Pipeline ETL (Extração, Limpeza, Enriquecimento e Carga)
├── data/
│   ├── bruto/                        # Arquivos brutos baixados da Prefeitura (JSON/CSV)
│   ├── limpo/                        # Dados pós-sanitização contábil
│   └── pronto/                       # Dataset final enriquecido com IBGE para ML
├── src/
│   ├── api.py                        # Primeiras rotas REST do FastAPI
│   ├── coleta/
│   │   └── coletor_prefeitura.py     # Coletor Dual: Portal Novo + API Antiga
│   ├── enriquecimento/
│   │   └── integracao_ibge.py        # Mapeamento do Censo e Renda de Palmas
│   ├── transformacao/
│   │   └── features.py               # Engenharia de atributos e mascaramento LGPD
│   └── estruturas/                   # Hash, Heap e Grafo (Sprint 2)
│
└── sitrib-frontend/                  # 📌 NOVO REPOSITÓRIO: Aplicação Web
    ├── package.json                  # Dependências React 18, Vite, Lucide Icons, Tailwind CSS
    └── src/
        ├── App.tsx                   # Roteamento de abas e contexto de sessão
        ├── components/
        │   └── Navbar.tsx            # Menu de navegação lateral por perfis (Auditor vs Cidadão)
        ├── pages/
        │   ├── Dashboard.tsx         # Visão geral de arrecadação e gráficos
        │   ├── BuscaFiscal.tsx       # Consulta unificada de CPF/CNPJ e CCI
        │   ├── FilaCobrancaView.tsx  # Fila ordenada de maiores devedores via Max-Heap
        │   └── SimuladorTributario.py# Simulação de alíquotas com cálculo dinâmico
        └── services/
            └── api.ts                # Camada de comunicação HTTP Axios com o backend
```

---

## 5. 🔍 A Grande Investigação: Os Dados Eram Reais ou Não? O que Foi Feito?

A questão dos dados foi o tópico mais crítico debatido pela equipe. Eis a verdade documental e fática:

### 5.1. A Tentativa com as APIs Oficiais da Prefeitura de Palmas
A equipe buscou integrar o SITRIB diretamente aos sistemas de transparência da Prefeitura de Palmas:
1. **API Antiga da Prefeitura (`https://integracao.palmas.to.gov.br/apirest`):**
   * *Diagnóstico:* Retornava constantemente **`HTTP 404 Not Found`** ou recusa de conexão. Tratava-se de um endpoint legado descontinuado pelo município.
2. **Portal Novo da Prefeitura (`https://acessoainformacao.palmas.to.gov.br/api` — NUCLEOGOV):**
   * *Diagnóstico:* Inicialmente retornava **`HTTP 403 Forbidden`** quando chamado via requisições GET padrão.
   * *Solução Técnica da Equipe:* Gabriel e Adriel identificaram que o portal exigia requisições `POST` com payloads JSON específicos (`{"anoExercicio": 2024, "tipoConsulta": "RECEITAS"}`) e cabeçalhos emulando requisições legítimas.
   * *Resultado:* O coletor conseguiu baixar **182.808 registros contábeis de receitas públicas** da capital.

### 5.2. O Desafio Contábil: A "Armadilha 5.4 da Prefeitura"
Ao carregar as 182.808 linhas e efetuar um `SUM(valor_arrecadado)`, os desenvolvedores depararam-se com um número absurdo: **mais de R$ 9,8 bilhões de arrecadação** para um município cujo orçamento real gira em torno de R$ 1,8 bilhão!
* **A Causa Contábil:** O Portal de Transparência de Palmas registrava a arrecadação em múltiplos níveis de detalhamento (rubricas sintéticas, analíticas, deduções do FUNDEB e transferências intraorçamentárias somadas juntas).
* **A Solução no ETL (`etl_sefin.py`):** A equipe desenvolveu uma regra de **filtro por nível hierárquico contábil e estorno**, descartando rubricas duplicadas. Com isso, os dados convergiram com precisão matemática para a receita líquida oficial do município: **R$ 1.810.016.926,07**.

### 5.3. O Paradoxo do Sigilo Fiscal (Art. 198 CTN e LGPD)
Por que a Prefeitura não fornecia dívidas individuais com CPF de pessoas físicas?
* **Razão Jurídica Insuperável:** O **Art. 198 do Código Tributário Nacional (CTN)** e o **Art. 5º da LGPD** proíbem terminantemente que qualquer prefeitura divulgue em portais abertos a lista nominal de pessoas físicas inadimplentes com CPF, endereço e patrimônio individual. Os portais públicos só publicam *Receitas Orçamentárias Agregadas*.
* **A Decisão Arquitetural Híbrida e Científica:**
  Para manter o rigor acadêmico sem violar a lei e sem operar com dados 100% fictícios, o SITRIB dividiu os dados em 3 camadas complementares:
  1. **Receitas Orçamentárias:** **100% Reais** (182.808 lançamentos do Portal Novo da Prefeitura saneados contra a Armadilha 5.4).
  2. **Indicadores Socioeconômicos:** **100% Reais** (Censo IBGE — Código 1721000 — 313.349 habitantes e rendas médias das 7 macrorregiões de Palmas).
  3. **Carteira de Dívida Ativa Individual:** Base piloto cadastral georreferenciada nos bairros oficiais de Palmas, com valores venais calibrados na Planta de Valores do Município (IPTU, ISS e Taxas), servindo de base verídica para os algoritmos de Machine Learning.

---

## 6. ⏭️ Transição e Ponte para o Sprint 4

* **Gargalo Identificado ao Final da Sprint 3:** O banco SQLite local estava sofrendo com *locks* de leitura/escrita simultânea (`database is locked`), a interface React precisava de mapas territoriais dinâmicos e faltavam os **modelos preditivos de Machine Learning** e **Agentes Inteligentes de IA Generativa** para fechar o MVP.

> 👉 **Continuação:** Veja a evolução detalhada no documento [`Guia_Sprint_4.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_4.md).
