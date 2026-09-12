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

## Estrutura do Projeto

```text
projetointegradorUFT/
├── docs/
├── src/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Comprovação de Contribuições no Git

Cada integrante deve realizar suas alterações utilizando Git e registrar suas contribuições por meio de commits.

Fluxo básico:

```text
Branch → Commit → Push → Pull Request → Merge
```

A participação dos integrantes será comprovada por meio do **histórico de commits e painel de contribuidores do GitHub**, conforme solicitado na atividade.

---

## Status

**Sprint 1 — Em desenvolvimento**

* [x] Repositório criado
* [x] Estrutura inicial
* [x] Requisitos funcionais
* [x] Requisitos não funcionais
* [x] Priorização MoSCoW
* [ ] Implementação das funcionalidades
* [x] Documentação UML
* [x] Comprovação dos commits
