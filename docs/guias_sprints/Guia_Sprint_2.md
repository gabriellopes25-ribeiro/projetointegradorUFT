# 📘 Guia de Apresentação — Sprint 2: Estruturas de Dados Avançadas & Persistência Relacional (SQLite)

**Sistema de Inteligência Tributária (SITRIB) — Projeto Integrador UFT**  
**Período Oficial:** 20/09/2026 a 02/10/2026  
**Documento Anterior:** [`Guia_Sprint_1.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_1.md)  
**Documento Posterior:** [`Guia_Sprint_3.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_3.md)  

---

## 1. 🎯 Objetivos Centrais da Sprint 2

A Sprint 2 marcou a transição de um esqueleto puramente teórico para um **motor de processamento tributário em memória com persistência em banco de dados relacional**:

1. **Implementação de Estruturas de Dados Fundamentais:**
   * **Tabela Hash ($O(1)$):** Indexação direta de contribuintes e débitos por CPF/CNPJ ou inscrição imobiliária (CCI).
   * **Fila de Prioridade / Max-Heap ($O(\log n)$):** Ordenação dinâmica automática dos maiores devedores para direcionar cobrança administrativa da SEFIN Palmas.
   * **Grafo de Relacionamentos:** Modelagem em rede de contribuintes, sócios, múltiplos imóveis e execuções fiscais ajuizadas.
2. **Primeira Camada de Persistência Relacional:**
   * Modelagem do esquema relacional DDL em `schema.sql` (tabelas `contribuinte`, `imovel`, `divida`, `processo`).
   * Implementação do `RepositorioSQLite` (`src/repositories/sqlite_repository.py`) gerando o banco local `sitrib.db`.
3. **Criação de Massa de Dados Simulada (Seeds Realistas):**
   * Criação do módulo `seeds/mock_data.py` e script de população automatizada `scripts/popular_banco.py`.

---

## 2. 👥 Papéis e Contribuições da Equipe na Sprint 2

| Integrante | Papel Scrum | Principais Entregas na Sprint 2 |
| :--- | :--- | :--- |
| **Gabriel Lopes** | Scrum Master | Implementação da **Tabela Hash**, do **Max-Heap (Fila de Cobrança)**, do `RepositorioSQLite` e integração no `main.py`. |
| **João Pedro Figueredo** | Desenvolvedor | Concepção e implementação da classe **`GrafoContribuintes`** e algoritmos de busca de relacionamentos societários/patrimoniais. |
| **Adriel Morais** | Product Owner | Elaboração das **seeds simuladas realistas** (`seeds/mock_data.py`), arquitetura de serviços de busca, documentação de integração com prefeitura e refatoração para o pacote `src/estruturas/`. |
| **Rayssa de Oliveira** | Desenvolvedora | Criação da DDL relacional oficial (`schema.sql`), script de população do banco (`scripts/popular_banco.py`) e consultas SQL de validação. |

---

## 3. 📜 Relação de Commits e Autoria da Sprint 2

Abaixo estão os commits fundamentais registrados na Sprint 2:

| Hash | Data | Autor | Mensagem do Commit | O que foi entregue |
| :---: | :---: | :--- | :--- | :--- |
| `0b988cb` | 20/09/2026 | Gabriel Lopes | `add estrutura tabela hash para indexacao da divida ativa` | Classe `TabelaHashDivida` com resolução de colisões por encadeamento. |
| `01d76c5` | 20/09/2026 | Gabriel Lopes | `feat: implementa e testa heap FilaCobranca (Sprint 2)` | Implementação do Max-Heap com complexidade de extração $O(\log n)$. |
| `fae3a25` | 22/09/2026 | João Pedro | `Cria classe GrafoContribuintes e métodos de busca` | Estrutura de Grafo para mapeamento de conexões entre devedores e imóveis. |
| `ea85994` | 27/09/2026 | Adriel Morais | `feat(adriel): adiciona seeds realistas, servico de busca, testes e documentacao de integracao` | Seeds tributárias piloto, serviço de busca desacoplado e documentação de integração. |
| `9be7407` | 27/09/2026 | Adriel Morais | `refactor: organiza estruturas de dados em src/estruturas, atualiza testes e documentacao com diagrama` | Centralização modular de Tabela Hash, Heap e Grafo em `src/estruturas/`. |
| `b92a91d` | 27/09/2026 | Gabriel Lopes | `feat: conecta heap (fila de cobranca) para priorizar contribuintes` | Integração do Max-Heap na orquestração de cobrança fiscal. |
| `4c3edcc` | 29/09/2026 | Rayssa de Oliveira | `Adicionado schema.sql e atualiza readme` | Criação do esquema relacional de 4 tabelas fundamentais. |
| `c57dd77` | 01/10/2026 | Rayssa de Oliveira | `Criado pasta scripts onde contem o banco popular e codigo em pyton.` | Script `scripts/popular_banco.py` para carregamento de dados no SQLite. |
| `8edfffd` | 02/10/2026 | Gabriel Lopes | `Corrige caminho do schema, popula banco SQLite e adiciona relatorio da Sprint 2` | Ajustes de caminhos e documentação da Sprint 2 (`SPRINT2.md`). |
| `e583b30` | 02/10/2026 | Gabriel Lopes | `Adiciona testes do grafo de relacionamentos e diagrama ER do banco` | Testes automatizados do Grafo e diagrama relacional ER. |
| `3017756` | 02/10/2026 | Gabriel Lopes | `Adiciona camada de persistencia real com SQLite (RepositorioSQLite)` | Repositório concreto para persistência em disco com `sqlite3`. |

---

## 4. 📂 Parecer da Arquitetura de Pastas (Antes vs. Depois da Sprint 2)

```text
projetointegradorUFT/  (Evolução da Sprint 2 — Outubro/2026)
├── SPRINT2.md                        # Relatório descritivo da Sprint 2
├── schema.sql                        # DDL Relacional (contribuinte, imovel, divida, processo)
├── sitrib.db                         # Banco de dados SQLite persistente em disco
├── scripts/
│   └── popular_banco.py              # Script executor da população do SQLite via seeds
├── seeds/
│   └── mock_data.py                  # Dicionários de seeds simuladas piloto
├── src/
│   ├── main.py                       # Orquestrador executivo demonstrando Hash, Heap e Grafo
│   ├── estruturas/                   # 📌 NOVO PACOTE: Estruturas de Dados em Memória
│   │   ├── fila_cobranca.py          # Max-Heap O(log n) para ordenação de débitos
│   │   ├── grafo.py                  # Grafo de relacionamentos Contribuinte-Imóvel-Processo
│   │   └── tabela_hash.py            # Tabela Hash O(1) com encadeamento
│   ├── repositories/
│   │   └── sqlite_repository.py      # Repositório concreto com queries SQL de consulta
│   └── services/
│       └── busca_service.py          # Serviço de busca rápida utilizando Tabela Hash
└── tests/
    ├── test_fila_cobranca.py
    ├── test_grafo.py
    ├── test_tabela_hash.py
    └── test_busca_validacao.py
```

---

## 5. 💡 Discussões Levantadas na Equipe

1. **Por que implementar Tabela Hash e Heap do zero se o Python já tem `dict` e `heapq`?**
   * *Discussão:* A disciplina exigia a demonstração formal das estruturas de dados e sua aplicação prática a problemas reais da gestão pública.
   * *Resolução:* Implementou-se classes didáticas e robustas encapsulando os conceitos computacionais (tratamento de colisão por lista encadeada e algoritmo de subida/descida do heap).
2. **Decisão pelo SQLite na Sprint 2:**
   * *Discussão:* Usar PostgreSQL ou SQLite?
   * *Resolução:* Optou-se pelo SQLite temporariamente pela ausência de dependências de infraestrutura externa (Docker/servidor de banco) nos notebooks dos desenvolvedores, permitindo validar rapidamente as constraints de integridade referencial (`FOREIGN KEY`, `ON DELETE CASCADE`).
3. **Modelagem de Relacionamento Contribuinte $\leftrightarrow$ Imóvel:**
   * *Discussão:* Um contribuinte pode ter vários imóveis, e um imóvel pode acumular IPTU de diferentes exercícios fiscais.
   * *Resolução:* O `schema.sql` garantiu a cardinalidade $1:N$ entre `contribuinte` e `imovel`, e $1:N$ entre `imovel` e `divida`, com `processo` judicial atrelado à dívida individualizada.

---

## 6. 📊 A Realidade dos Dados no Sprint 2: Os Dados Eram Reais?

* **Situação Factual:** **Os dados eram 100% MOCK (Simulados).**
* **Composição das Seeds (`seeds/mock_data.py`):**
  * 4 Contribuintes (ex: "Tocantins Engenharia", "Araguaia Alimentos", "Carlos Eduardo Siqueira").
  * 4 Imóveis fictícios em quadras de Palmas.
  * 4 Débitos tributários (somando exatamente **R$ 32.431,25**).
  * 2 Execuções fiscais simuladas em varas judiciais fictícias.
* **Por que foram usados dados mockados?**
  * Permitiram validar a Tabela Hash, os testes unitários e as consultas SQL sem depender da disponibilidade de servidores externos ou credenciais da Prefeitura de Palmas.
  * **Problema Identificado ao Final da Sprint:** Uma massa de apenas 4 débitos não permitia treinar modelos de Machine Learning, não cobria a diversidade socioeconômica de Palmas e gerava um sistema puramente ilustrativo. A equipe precisava conectar-se urgentemente às fontes de dados reais da SEFIN Palmas.

---

## 7. ⏭️ Transição e Ponte para o Sprint 3

* **O Desafio do Próximo Ciclo:** Desenvolver uma interface web completa (Frontend) para visualização e partir para a **extração ao vivo das APIs da Prefeitura de Palmas e Censo do IBGE**, iniciando o saneamento real dos dados orçamentários.

> 👉 **Continuação:** Veja a evolução detalhada no documento [`Guia_Sprint_3.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_3.md).
