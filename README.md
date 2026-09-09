# Projeto Integrador UFT

Projeto desenvolvido para a disciplina de Projeto Integrador, aplicando conceitos de **Scrum, Engenharia de Requisitos, Git e GitHub**.

## 👥 Equipe

| Integrante                | Papel              |
| ------------------------- | ------------------ |
| **Adriel Morais**         | Product Owner (PO) |
| **Gabriel Lopes**         | Scrum Master (SM)  |
| **João Pedro Figueiredo** | Desenvolvedor      |
| **Rayssa de Oliveira**    | Desenvolvedora     |
| **[5º Integrante]**       | Desenvolvedor      |

**Repositório:**
https://github.com/gabriellopes25-ribeiro/projetointegradorUFT

---

## 🎯 Objetivo

Desenvolver um sistema para **gerenciamento e análise de tributos**, permitindo realizar cálculos, simulações de reajustes, comparação de cenários e consulta de informações.

---

## 🛠️ Tecnologias

* **Python 3.12+**
* **Git**
* **GitHub**
* **requirements.txt**

---

## 🔄 Papéis Ágeis

### Product Owner — Adriel Morais

Responsável por representar os objetivos do projeto, organizar e priorizar o Backlog, esclarecer regras de negócio e validar as funcionalidades de acordo com os critérios de aceite.

### Scrum Master — Gabriel Lopes

Responsável por auxiliar na aplicação do Scrum, organizar os alinhamentos da equipe, acompanhar a Sprint e auxiliar na resolução de impedimentos.

### Equipe de Desenvolvimento

* João Pedro Figueiredo
* Rayssa de Oliveira
* [5º Integrante]

Responsáveis pelo desenvolvimento, testes e manutenção do sistema.

---

# 📋 Requisitos Funcionais

| ID       | Requisito                | Critério de Aceite                                         |
| -------- | ------------------------ | ---------------------------------------------------------- |
| **RF01** | Cadastro de Usuário      | Permitir cadastro com e-mail, nome e senha.                |
| **RF02** | Autenticação             | Permitir acesso somente com credenciais válidas.           |
| **RF03** | Perfis de Acesso         | Diferenciar permissões de administrador e consulta.        |
| **RF04** | Cadastro de Tributos     | Permitir cadastrar tipos de tributos e suas regras.        |
| **RF05** | Cálculo de Tributos      | Calcular o valor conforme os dados e alíquotas informados. |
| **RF06** | Simulação de Reajuste    | Permitir simular reajustes sem alterar os dados reais.     |
| **RF07** | Comparação de Cenários   | Permitir comparar diferentes cenários de reajuste.         |
| **RF08** | Histórico de Tarifas     | Registrar e permitir consultar alterações de valores.      |
| **RF09** | Relatório de Arrecadação | Gerar relatório com a arrecadação estimada.                |
| **RF10** | Painel de Indicadores    | Exibir indicadores relacionados aos tributos.              |
| **RF11** | Log de Operações         | Registrar operações importantes realizadas no sistema.     |

A atividade exige no mínimo **10 requisitos funcionais com critérios de aceite testáveis**.

---

# ⚙️ Requisitos Não Funcionais

| ID        | Categoria     | Requisito                                                       |
| --------- | ------------- | --------------------------------------------------------------- |
| **RNF01** | Tecnologia    | O sistema deve utilizar Python 3.12+.                           |
| **RNF02** | Portabilidade | As dependências devem estar descritas no `requirements.txt`.    |
| **RNF03** | Usabilidade   | O sistema deve apresentar mensagens claras de sucesso e erro.   |
| **RNF04** | Documentação  | O projeto deve possuir documentação para instalação e execução. |
| **RNF05** | Segurança     | As senhas devem ser armazenadas de forma segura.                |

---

# 📊 Priorização MoSCoW

### Must Have

RF01, RF02, RF03, RF04, RF05, RF06, RNF01, RNF02, RNF05

### Should Have

RF07, RF08, RF10, RNF03, RNF04

### Could Have

RF09, melhorias visuais e funcionalidades secundárias.

### Won't Have

Funcionalidades que não fazem parte do escopo da primeira entrega.

---

# 📁 Estrutura

```text
projetointegradorUFT/
├── docs/
├── src/
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🌿 Git e Colaboração

Cada integrante deve realizar suas alterações utilizando Git e registrar suas contribuições por meio de commits.

Fluxo básico:

```text
Branch → Commit → Push → Pull Request → Merge
```

A participação dos integrantes será comprovada por meio do **histórico de commits e painel de contribuidores do GitHub**, conforme solicitado na atividade.

---

## 📌 Status

**Sprint 1 — Em desenvolvimento**

* [x] Repositório criado
* [x] Estrutura inicial
* [x] Requisitos funcionais
* [x] Requisitos não funcionais
* [x] Priorização MoSCoW
* [ ] Implementação das funcionalidades
* [x] Documentação UML
* [x] Comprovação dos commits
