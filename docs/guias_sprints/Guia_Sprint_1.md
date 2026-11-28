# 📘 Guia de Apresentação — Sprint 1: Fundação do Sistema & Engenharia de Requisitos

**Sistema de Inteligência Tributária (SITRIB) — Projeto Integrador UFT**  
**Período Oficial:** 05/09/2026 a 12/09/2026  
**Público-Alvo:** Coordenação do Curso, Professores Avaliadores e Equipe de Engenharia  
**Repositório Base:** `https://github.com/gabriellopes25-ribeiro/projetointegradorUFT`  

---

## 1. 🎯 Objetivos Centrais da Sprint 1

A Sprint 1 teve como meta primordial a **concepção metodológica, levantamento de requisitos de software e estabelecimento da fundação arquitetural** do SITRIB para a Secretaria de Finanças de Palmas (SEFIN):

1. **Definição de Escopo e Engenharia de Requisitos:**
   * Levantamento de 11 Requisitos Funcionais (RF01 a RF11) e 5 Requisitos Não-Funcionais (RNF01 a RNF05).
   * Priorização do backlog de produto utilizando a matriz ágil **MoSCoW** (*Must Have, Should Have, Could Have, Won't Have*).
2. **Definição dos Papéis Ágeis (Scrum Framework):**
   * Alocação oficial de responsabilidades para assegurar autonomia, auditoria de commits e rastreabilidade:
     * **Product Owner (PO):** Adriel Morais
     * **Scrum Master (SM):** Gabriel Lopes
     * **Desenvolvedores:** João Pedro Figueredo e Rayssa de Oliveira
3. **Esqueleto Inicial do Backend Python (3.12+):**
   * Estruturação inicial em camadas conceituais (`src/models`, `src/services`, `src/repositories`, `src/utils`).
   * Implementação de contratos abstratos e validações matemáticas rígidas de alíquotas tributárias utilizando `decimal.Decimal` (evitando perdas de precisão de ponto flutuante IEEE 754).

---

## 2. 👥 Papéis Ágeis e Divisão de Responsabilidades

| Integrante | Papel Scrum | Responsabilidades na Sprint 1 |
| :--- | :--- | :--- |
| **Adriel Morais** | Product Owner (PO) | Elaboração da arquitetura inicial modular, redação dos requisitos técnicos, contratos de serviços e modelagem da entidade `Tributo`. |
| **Gabriel Lopes** | Scrum Master (SM) | Inicialização do repositório Git/GitHub, configuração de dependências (`requirements.txt`), documentação dos requisitos RF/RNF e controle de branches. |
| **João Pedro Figueredo** | Desenvolvedor | Implementação da documentação de planejamento ágil (`docs/planejamento_scrum.md`) e preparação dos modelos conceituais. |
| **Rayssa de Oliveira** | Desenvolvedora | Estruturação e padronização do `README.md` principal, documentação dos fluxos de execução e validações iniciais. |

---

## 3. 📜 Relação de Commits e Autoria da Sprint 1

Abaixo estão os commits fundacionais registrados no histórico oficial do Git:

| Hash | Data | Autor | Mensagem do Commit | Impacto Arquitetural |
| :---: | :---: | :--- | :--- | :--- |
| `d7a97e3` | 05/09/2026 | Gabriel Lopes | `Initial commit` | Inicialização do repositório Git. |
| `627c950` | 05/09/2026 | Gabriel Lopes | `Create .gitkeep` | Estruturação de diretórios vazios iniciais. |
| `34bf5c9` | 05/09/2026 | Gabriel Lopes | `Create requirements.txt` | Isolamento das dependências fundamentais. |
| `1f4a657` | 06/09/2026 | Gabriel Lopes | `Add functional and non-functional requirements` | Especificação formal dos 11 RFs e 5 RNFs. |
| `e4d91b5` | 06/09/2026 | Adriel Morais | `Adiciona novas alterações do projeto integrador, instruções e melhoria de escopo da arquitetura e esqueleto do projeto` | Criação do esqueleto Python, contratos abstratos e validação de `Decimal`. |
| `7f5905a` | 06/09/2026 | Adriel Morais | `Merge pull request #1 from AadrielL/Adriel-develop` | Integração da arquitetura desacoplada na branch `main`. |
| `b4ca63b` | 07/09/2026 | João Pedro | `documentacao agil` | Criação do documento de governança ágil e MoSCoW. |
| `898c413` | 07/09/2026 | João Pedro | `Merge pull request #2 from gabriellopes25-ribeiro/docs/planejamento-agil` | Incorporação das diretrizes do Scrum na `main`. |
| `4575009` | 09/09/2026 | Rayssa de Oliveira | `Estrutuanção do README.` | Formatação da documentação oficial do repositório. |
| `6a658ee` | 12/09/2026 | Gabriel Lopes | `Merge pull request #3 from rayssa-oliveira05/Rayssa_Dev` | Unificação final dos entregáveis da Sprint 1. |
| `20f4d1f` | 12/09/2026 | Gabriel Lopes | `Update README.md` | Ajuste nos critérios de aceite testáveis. |

---

## 4. 📂 Parecer da Arquitetura de Pastas (O que existia no Sprint 1)

Nesta primeira etapa, o projeto não possuía banco de dados nem interface web. A estrutura refletia um **esqueleto de domínio em camadas preliminar**:

```text
projetointegradorUFT/  (Sprint 1 — Setembro/2026)
├── README.md                 # Documento principal com identificação, RFs e RNFs
├── requirements.txt          # Apenas biblioteca padrão Python nesta fase
├── docs/                     # Documentação conceitual e teórica
│   ├── arquitetura.md        # Visão de camadas conceituais
│   ├── desenvolvimento.md    # Guia para testes locais via unittest
│   ├── mvc-e-camadas.md      # Esclarecimento conceitual: por que ainda não era MVC
│   ├── planejamento_scrum.md # Papéis, cerimônias ágeis e matriz MoSCoW
│   ├── produto.md            # Acompanhamento do PO com perguntas em aberto
│   └── requisitos.md         # Rastreabilidade entre código e RF/RNF
├── src/                      # Código-fonte Python
│   ├── main.py               # Ponto de entrada demonstrativo (sem servidor/API)
│   ├── models/               # Entidades de domínio em Dataclasses
│   │   ├── historico.py
│   │   ├── simulacao.py
│   │   ├── tributo.py        # Validação estrita de alíquota com Decimal
│   │   └── usuario.py        # Entidade com hash de senha simulado
│   ├── repositories/         # Apenas contratos abstratos (interfaces puras)
│   │   ├── tributo_repository.py
│   │   └── usuario_repository.py
│   ├── services/             # Interfaces de serviços não implementadas
│   │   ├── autenticacao_service.py
│   │   ├── calculo_service.py
│   │   ├── relatorio_service.py
│   │   ├── simulacao_service.py
│   │   └── tributo_service.py
│   └── utils/
│       └── validacoes.py     # Funções puras de checagem de tipos e valores
└── tests/                    # Testes estruturais unitários
    ├── test_calculo.py       # Teste abstrato (marcado como ignorado para aceite futuro)
    ├── test_tributo.py       # Cobertura das validações de alíquota e texto
    └── test_usuario.py       # Checagem da omissão da senha no __repr__
```

---

## 5. 💡 Discussões Levantadas e Decisões de Design

Durante as reuniões de alinhamento da Sprint 1, quatro discussões críticas foram registradas:

1. **Decisão sobre Ponto Flutuante vs. `Decimal`:**
   * *Discussão:* Usar tipos `float` convencionais causaria dízimas e imprecisões de centavos ao somar IPTU e ISS de milhares de lançamentos.
   * *Decisão:* Adotou-se obrigatoriamente a biblioteca `decimal.Decimal` em todas as grandezas monetárias e alíquotas tributárias.
2. **Separação Rígida entre Entidade e Persistência:**
   * *Discussão:* Se deveríamos colocar queries SQL diretamente dentro dos métodos de modelo (estilo Active Record).
   * *Decisão:* Vetado categoricamente. Adotou-se o padrão **Repository Pattern** para que a lógica tributária não ficasse acoplada a nenhum mecanismo de banco específico.
3. **Escopo da Entrega Inicial (A Filosofia "Sem Falsa Implementação"):**
   * *Discussão:* Se deveríamos implementar telas ou APIs simuladas rapidamente.
   * *Decisão do PO:* Entregar apenas o que estava testado e validado. Métodos futuros foram mantidos como contratos abstratos (`raise NotImplementedError`), impedindo débitos técnicos disfarçados.

---

## 6. 📊 A Realidade dos Dados no Sprint 1: Havia dados reais?

* **Situação Factual:** **Zero dados reais e zero banco de dados.**
* **Diagnóstico:** Nesta fase inicial, não havia conexão com banco de dados (nem SQLite, nem PostgreSQL) e nenhuma consulta às APIs da Prefeitura de Palmas havia sido realizada.
* **Massa de Teste:** Restrita a dados sintéticos instanciados diretamente em memória dentro dos testes unitários (`test_tributo.py`), testando apenas se alíquotas negativas geravam exceções ou se strings vazias eram rejeitadas.

---

## 7. ⏭️ Transição e Ponte para o Sprint 2

* **Gargalo Identificado:** Como processar com alta performance consultas fiscais de centenas de milhares de contribuintes quando a persistência for introduzida?
* **Ponte para o Sprint 2:** A equipe definiu que o próximo passo exigiria **estruturas de dados em memória de alta performance** (Tabelas Hash para busca $O(1)$, Max-Heaps para filas de cobrança $O(\log n)$ e Grafos de relacionamento), além da primeira camada de **persistência relacional com SQLite**.

> 👉 **Continuação:** Veja a evolução detalhada no documento [`Guia_Sprint_2.md`](file:///C:/Users/morai/projetointegradorUFT/docs/guias_sprints/Guia_Sprint_2.md).
