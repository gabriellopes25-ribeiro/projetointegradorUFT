# 📘 Guia de Apresentação — Sprint 4: Machine Learning, Microsserviços com Agentes Estritos, LLM Gemini & MVP

**Sistema de Inteligência Tributária (SITRIB) — Projeto Integrador UFT**  
**Período Oficial:** 05/11/2026 a 28/11/2026  
**Documento Anterior:** [`Guia_Sprint_3.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_3.md)  
**Documento Consolidador:** [`Apresentacao_Geral_Sprints.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Apresentacao_Geral_Sprints.md)  

---

## 1. 🎯 Objetivos Centrais da Sprint 4

A Sprint 4 consolidou o produto final entregável do Projeto Integrador: o **MVP Completo do SITRIB**, unindo Ciência de Dados, Modelos Preditivos de Machine Learning, Arquitetura de Microsserviços e Inteligência Artificial Generativa real:

1. **Modelagem Preditiva & Inteligência Fiscal (Entregáveis E1 a E3):**
   * Treinamento e avaliação de modelos de classificação de inadimplência com **split temporal estrito** (sem vazamento de dados).
   * Algoritmo de **Scoring de Recuperabilidade da Dívida Ativa** (faixas Alta, Média e Baixa).
   * Métricas de **Justiça Fiscal (*Fairness*)** para mitigar viés geográfico e proteger contribuintes vulneráveis (Art. 145, §1º da CF).
2. **Migração para PostgreSQL 16 & Dockerização Total:**
   * Abandono definitivo do SQLite e transição para **PostgreSQL 16 gerenciado via Docker Compose** com healthchecks e persistência em volume.
   * Script de higienização relacional profunda (`scripts/validar_e_repopular_banco.py`), atestando **zero valores nulos, zero valores negativos e integridade cadastral total**.
3. **Arquitetura de Microsserviços com Agentes de IA Especializados:**
   * Reorganização do backend em 4 microsserviços autônomos em `src/apis/`, cada qual governado por um **Agente Estrito com Least Privilege Tool-Calling**.
4. **Inteligência Artificial Generativa Real (Google Gemini 3.5 Flash Lite):**
   * Conexão oficial à API do Gemini via variáveis de ambiente protegidas no `.env`.
   * Implementação do **Ciclo ReAct em 6 Etapas** (Validação, Pensamento, Ação, Observação do Banco, Revisão Crítica Humana e Resposta Fundamentada), eliminando fallbacks estáticos.
5. **Frontend MVP Interativo de Alto Padrão (Entregável E4):**
   * **Mapa Territorial Real (Leaflet):** Georreferenciamento das 7 Macrorregiões de Palmas com camadas temáticas de calor.
   * **Cards Analíticos & Filtros:** Visualização em grade executiva com busca instantânea.
   * **Assistente Fiscal Global (Copilot Flutuante via `Ctrl+K`):** Chatbot conectado à LLM real.
   * **Acessibilidade Universal (WCAG AAA):** Comando de voz, leitor em áudio, modos de alto contraste e botão direto de "Voltar ao Login".

---

## 2. 👥 Papéis e Contribuições da Equipe na Sprint 4

| Integrante | Papel Scrum | Entregas Oficiais da Sprint 4 |
| :--- | :--- | :--- |
| **Gabriel Lopes** | Scrum Master | **Entregável E1:** Divisão de treino com split temporal sem data leakage e treinamento dos baselines (Regressão Logística e Árvore de Decisão em `scripts/sprint4_baseline.py`). |
| **João Pedro Figueredo** | Desenvolvedor | **Entregável E2 (Parte 1):** Treinamento, tunagem de hiperparâmetros (GridSearch) do `Random Forest Classifier` e consolidação da matriz de confusão e métricas globais. |
| **Rayssa de Oliveira** | Desenvolvedora | **Entregáveis E2 (Parte 2) e E3:** Implementação do Scoring de Recuperabilidade, cálculo de métricas por subgrupo socioeconômico (Fairness) e serialização do modelo em `models/modelo_inadimplencia_v1.joblib`. |
| **Adriel Morais** | Product Owner | **Entregável E4 & Arquitetura:** Orquestração dos 4 Microsserviços, implementação dos Agentes Estritos, higienização do PostgreSQL, integração real com a LLM Google Gemini, mapa Leaflet no Frontend e acessibilidade WCAG AAA. |

---

## 3. 📜 Relação de Commits e Autoria da Sprint 4

| Hash | Data | Autor | Mensagem do Commit | O que foi entregue |
| :---: | :---: | :--- | :--- | :--- |
| `df860c3` | 05/11/2026 | Gabriel Lopes | `feat: adiciona script de baseline e split temporal da sprint 4` | Metodologia de split temporal estrito contra vazamento de dados futuros. |
| `14aef0e` | 05/11/2026 | Gabriel Lopes | `feat: finaliza execucao dos baselines e split temporal da sprint 4` | Avaliação de Regressão Logística e Árvore de Decisão. |
| `d45d2c7` | 09/11/2026 | Rayssa de Oliveira | `Foi adicionado a scoring de recuperabilidade, metricas de fairness e serializacao do modelo` | Módulo de scoring e cálculo de disparidade por faixa de renda. |
| `52508cd` | 09/11/2026 | João Pedro | `feat: adiciona modelo de machine learning e metricas de inadimplencia - Joao Pedro` | Tunagem do Random Forest com 100% de acurácia na base piloto. |
| `7ba431c` | 12/11/2026 | Adriel Morais | `feat(auth/ml): implementa autenticacao rbac e servico de predicao` | Serviço de predição integrado às regras de controle de acesso (RBAC). |
| `2aed96f` | 15/11/2026 | Adriel Morais | `feat(api-db): suporte PostgreSQL/SQLite, filtros de auditoria paginados e integracao coletor dual` | Migração do motor de persistência e suporte a PostgreSQL 16. |
| `64db375` | 15/11/2026 | Adriel Morais | `feat(auth): login oficial CPF/Senha, autenticacao Gov.br com validacao de vinculo servidor vs cidadao e remocao de bypass de homologacao` | Autenticação formal com diferenciação estrita de perfis e conformidade LGPD. |
| `a0fa213` | 25/11/2026 | Adriel Morais | `feat(backend): arquitetura de microsservicos, agentes estritos, gemini llm real e banco higienizado` | Implementação dos 4 Agentes Estritos em `src/apis/`, LLM Gemini 3.5 Flash Lite e validação do PostgreSQL. |
| `54ab677` | 25/11/2026 | Gabriel Lopes | `feat(sprint3-4): atualiza arquitetura multiagente, Docker, APIs modulares e pipeline ETL` | Adição dos 5 PDFs de guias da Sprint 4 e suíte de testes `test_api_veridica.py`. |
| `8271a7e` | 25/11/2026 | Adriel Morais | `feat(frontend): mapa territorial leaflet, cards analiticos, acessibilidade e assistente fiscal ReAct` | Frontend MVP completo com mapa Leaflet real, acessibilidade WCAG e botão de voltar ao login. |

---

## 4. 📂 Parecer da Arquitetura de Pastas: O Estado da Arte no Sprint 4

A arquitetura final do projeto reflete um ecossistema desacoplado em microsserviços conteinerizados:

```text
projetointegradorUFT/  (Sprint 4 — Versão Final de Produção)
├── docker-compose.yml                       # Orquestração dos 3 contêineres: postgres, backend, frontend
├── Dockerfile.backend                       # Imagem Python 3.12 com dependências de ML e API
├── SPRINT4.md                               # Documentação oficial das entregas E1 a E4
├── schema.sql                               # DDL PostgreSQL 16 (Tabelas Dívida Ativa + Receitas Reais)
├── models/
│   └── modelo_inadimplencia_v1.joblib       # Modelo Random Forest serializado
├── scripts/
│   ├── sprint4_baseline.py                  # Script de split temporal e baselines (E1)
│   ├── limpar_e_cruzar_dados.py             # Limpeza das 182k receitas e cálculo de indicadores
│   └── validar_e_repopular_banco.py         # Auditoria profunda de dados (zero nulos, zero negativos)
├── src/
│   ├── api.py                               # API Gateway central (FastAPI)
│   ├── database.py                          # Conexão SQLAlchemy com pool no PostgreSQL
│   ├── apis/                                # 📌 4 MICROSSERVIÇOS COM SEUS AGENTES ESTRITOS
│   │   ├── auth_api/                        # Microsserviço 1: Auth & Governança
│   │   │   └── agente_guardiao_lgpd.py      # 🛡️ Agente Guardião LGPD (Blind Inference)
│   │   ├── tributario_api/                  # Microsserviço 2: Dossiê e Fila
│   │   │   └── agente_auditor_tributario.py # 🏛️ Agente Auditor Tributário (Max-Heap)
│   │   ├── transparencia_coleta_api/        # Microsserviço 3: Orçamento Real
│   │   │   └── agente_inspetor_orcamento.py # 📊 Agente Inspetor do Orçamento (Anti-Armadilha 5.4)
│   │   └── ia_predicao_api/                 # Microsserviço 4: Modelos e Chatbot
│   │       └── agente_capacidade_fairness.py# ⚖️ Agente Capacidade & Raciocínio ReAct
│   ├── services/
│   │   ├── gemini_service.py                # Integração com API Oficial Google Gemini LLM
│   │   ├── orquestrador_agentes_service.py  # Orquestrador com Least Privilege Tool-Calling
│   │   └── predicao_service.py              # Invocação do modelo serializado .joblib
│   └── repositories/
│       └── postgres_repository.py           # Repositório PostgreSQL com consultas analíticas
└── sitrib-frontend/                         # 📌 FRONTEND MVP INTEGRADO
    ├── src/
    │   ├── components/
    │   │   ├── MapaPalmasReal.tsx           # Mapa Geoespacial Interativo com Leaflet
    │   │   ├── CardsImoveisAnalitico.tsx    # Grade de Cards com Liquidez e Filtros
    │   │   ├── AgenteFlutuanteCopilot.tsx   # Chatbot ReAct Flutuante (Ctrl+K)
    │   │   └── AcessibilidadeBar.tsx        # Acessibilidade (Voz, Áudio, Alto Contraste e Botão Login)
    │   └── pages/
    │       ├── Dashboard.tsx                # Indicadores consolidados da SEFIN Palmas
    │       ├── MacrorregioesView.tsx        # Análise territorial das 7 macrozonas
    │       └── CapacidadeFairnessView.tsx   # Painel de Quem Pode vs Quem Não Pode Pagar
```

---

## 5. 🤖 Como Opera o Agente com a LLM Real (Sem Fallback Estático)

Diferente de versões intermediárias que usavam frases fixas com `if/else`, a versão final da Sprint 4 conecta-se à **API Oficial do Google Gemini** (`gemini-3.5-flash-lite`):

1. **Injeção de Fatos Fiscais do PostgreSQL (RAG Local):**
   * Antes de enviar o prompt à LLM, o backend executa consultas em tempo real no PostgreSQL, obtendo o valor venal do imóvel, o estoque da dívida daquele bairro e a renda média do Censo IBGE.
2. **Ciclo ReAct em 6 Etapas Auditáveis:**
   * **1. Validação de Parâmetros:** Extração de intenção e conformidade estrita com o Art. 6º da LGPD (Blind Inference).
   * **2. Hipótese & Pensamento (Thought):** Raciocínio sobre capacidade contributiva e liquidez patrimonial.
   * **3. Ação & Execução de Ferramenta (Action):** Chamada das ferramentas autorizadas do respectivo microsserviço.
   * **4. Observação dos Fatos (Observation):** Análise dos números reais retornados pelo banco.
   * **5. Revisão Crítica & Salvaguardas Éticas (Review):** Verificação de não-confisco (Art. 150, IV CF) e homologação obrigatória pelo auditor humano (Art. 142 CTN / Art. 20 LGPD).
   * **6. Parecer Final Fundamentado (Final Answer):** Texto analítico gerado pela LLM real com argumentos jurídicos e econômicos direcionados à pergunta específica do auditor.

---

## 6. 📊 O Estado dos Dados no Sprint 4: 100% Higienizado e Auditável

A base de dados foi submetida a um script rigoroso de validação (`scripts/validar_e_repopular_banco.py`):
* **Zero Valores Negativos:** Nenhum lançamento com encargos ou tributos abaixo de zero.
* **Zero Imóveis com Valor Venal Zerado:** Todos os imóveis contam com avaliação imobiliária real compatível com a respectiva macrorregião (R$ 95 mil a R$ 4,5 milhões).
* **Integridade Relacional 100% Auditada:** Todos os 21 imóveis e contribuintes possuem débitos vinculados, inscrições municipais regulares e mapeamento territorial preciso.
* **Receitas do Orçamento Real da Capital:** 182.808 lançamentos contábeis reais do Portal Novo saneados contra a Armadilha 5.4, demonstrando R$ 1,81 bilhão de arrecadação municipal líquida.

---

## 7. 🏁 Conclusão da Sprint 4

O SITRIB entrega um **MVP de Inteligência Tributária completo, funcional e demonstrável ao vivo**, atendendo a 100% dos requisitos funcionais (RF01 a RF11), não-funcionais (RNF01 a RNF05) e entregáveis oficiais da disciplina (E1 a E4).

> 👉 **Visão Geral e Roteiro de Apresentação:** Consulte o documento [`Apresentacao_Geral_Sprints.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Apresentacao_Geral_Sprints.md).
