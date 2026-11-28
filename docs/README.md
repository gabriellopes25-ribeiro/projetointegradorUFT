# 📚 Índice Mestre da Documentação Técnica — SITRIB Palmas

Bem-vindo ao repositório de documentação técnica do **Sistema de Inteligência Tributária (SITRIB)**, desenvolvido para a Secretaria de Finanças de Palmas (SEFIN) no âmbito do Projeto Integrador da Universidade Federal do Tocantins (UFT).

Toda a documentação do projeto está categorizada em pastas temáticas para facilitar a leitura, auditoria acadêmica e apresentação para a banca avaliadora.

---

## 🧭 Mapa de Navegação da Documentação

### 1. 🚀 Guias de Apresentação das Sprints (Histórico & Metodologia)
Acesse a pasta [`docs/guias_sprints/`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints) para conferir a história completa de cada ciclo de entrega, commits, discussões e evolução dos dados:
* [📘 **Apresentação Geral e Roteiro Executivo de Apresentação**](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Apresentacao_Geral_Sprints.md) — Visão holística de todo o projeto e passo a passo para demonstração ao vivo do MVP.
* [📘 **Guia da Sprint 1: Fundação & Requisitos**](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_1.md) — Levantamento de RF/RNF, Matriz MoSCoW, papéis ágeis e esqueleto inicial.
* [📘 **Guia da Sprint 2: Estruturas de Dados & SQLite**](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_2.md) — Tabela Hash $O(1)$, Max-Heap $O(\log n)$, Grafo de Vínculos e primeira persistência relacional.
* [📘 **Guia da Sprint 3: Frontend & APIs da Prefeitura**](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_3.md) — Lançamento do React/Vite, ingestão das 182k receitas do Portal Novo e a Armadilha 5.4.
* [📘 **Guia da Sprint 4: IA, Microsserviços & MVP**](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_4.md) — Modelos Random Forest, 4 Agentes Estritos, LLM Google Gemini com ReAct e Mapa Leaflet.
* [📁 **PDFs Individuais de Orientações da Sprint 4**](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprint4) — Guias em PDF para cada membro da equipe.

---

### 2. 🏛️ Arquitetura de Software e Microsserviços
Acesse a pasta [`docs/arquitetura/`](file:///C:/Users/morai/projetointegradorUFT/docs/arquitetura) para detalhes dos diagramas e da topologia de serviços:
* [🏗️ **Arquitetura Antes vs. Depois**](file:///C:/Users/morai/projetointegradorUFT/docs/arquitetura/arquitetura_antes_depois.md) — Comparativo completo das árvores de pastas do projeto (do monólito ao multi-container).
* [📐 **Arquitetura Inicial do Sistema**](file:///C:/Users/morai/projetointegradorUFT/docs/arquitetura/arquitetura_inicial.md) — Modelo conceitual fundacional em camadas.
* [🧩 **Conceitos de MVC e Camadas**](file:///C:/Users/morai/projetointegradorUFT/docs/arquitetura/mvc_e_camadas.md) — Desacoplamento entre Models, Services, Repositories e Controllers.
* [📊 **Fluxograma Orquestrado do SITRIB (SVG)**](file:///C:/Users/morai/projetointegradorUFT/docs/fluxo_orquestrado_sitrib.svg) — Diagrama visual de comunicação entre o usuário, frontend, microsserviços e banco.

---

### 3. 📋 Engenharia de Requisitos & Gestão de Produto
Acesse a pasta [`docs/requisitos_produto/`](file:///C:/Users/morai/projetointegradorUFT/docs/requisitos_produto) para a fundamentação ágil:
* [📝 **Rastreabilidade de Requisitos (RF e RNF)**](file:///C:/Users/morai/projetointegradorUFT/docs/requisitos_produto/requisitos.md) — Matriz completa de atendimento dos 11 RFs e 5 RNFs.
* [🎯 **Acompanhamento do Product Owner**](file:///C:/Users/morai/projetointegradorUFT/docs/requisitos_produto/produto.md) — Perguntas de negócio validadas e critérios de aceite.
* [⏱️ **Planejamento Ágil Scrum & Matriz MoSCoW**](file:///C:/Users/morai/projetointegradorUFT/docs/requisitos_produto/planejamento_scrum.md) — Cerimônias, papéis e priorização de escopo.

---

### 4. 🔬 Relatórios Técnicos, Ciência de Dados & Coleta
Acesse a pasta [`docs/relatorios_tecnicos/`](file:///C:/Users/morai/projetointegradorUFT/docs/relatorios_tecnicos) para os laudos de auditoria de dados:
* [📈 **Relatório de Análise Exploratória de Dados (EDA)**](file:///C:/Users/morai/projetointegradorUFT/docs/relatorios_tecnicos/relatorio_eda.md) — Estatísticas descritivas e cruzamento com o IBGE.
* [🌐 **Relatório Integrado do Ecossistema Tributário**](file:///C:/Users/morai/projetointegradorUFT/docs/relatorios_tecnicos/relatorio_ecossistema.md) — Diagnóstico de conectividade e taxas das APIs de Palmas.
* [🔐 **Integração Segura com a Prefeitura (LGPD & Segurança)**](file:///C:/Users/morai/projetointegradorUFT/docs/relatorios_tecnicos/integracao_prefeitura.md) — Criptografia TLS 1.3, anonimização e RBAC.
* [🔍 **Consultas SQL de Validação do Banco**](file:///C:/Users/morai/projetointegradorUFT/docs/relatorios_tecnicos/consultas_validacao.md) — Consultas executadas para validar integridade referencial.
* [💻 **Guia de Desenvolvimento Local**](file:///C:/Users/morai/projetointegradorUFT/docs/relatorios_tecnicos/desenvolvimento.md) — Instruções para execução de rotinas e testes unitários.

---

### 5. 🗺️ Mapas e Diagramas UML
* [🗺️ **Mapa Interativo Geoespacial de Palmas (HTML)**](file:///C:/Users/morai/projetointegradorUFT/docs/mapas/mapa_inadimplencia.html) — Mapa territorial Folium exportado.
* [📐 **Pasta de Diagramas UML**](file:///C:/Users/morai/projetointegradorUFT/docs/uml) — Diagramas de Casos de Uso, Diagrama de Classes e Sequência.
* [🔎 **Espelho do Código Fonte Python**](file:///C:/Users/morai/projetointegradorUFT/docs/src) — Documentação espelhada dos módulos do backend.
