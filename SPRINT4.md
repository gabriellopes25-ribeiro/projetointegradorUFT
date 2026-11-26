# Sprint 4 — Sistema de Inteligência Tributária (SITRIB)
## Predição de Inadimplência, Scoring de Recuperabilidade e MVP

**Universidade Federal do Tocantins (UFT) — BIINAR**  
**Eixo II — Projeto Integrador: Inteligência Tributária (Sefin Palmas)**  
**Período:** 29/10 a 11/11/2026 | **Entrega:** 11/11/2026, às 23h59  
**Coordenação:** Prof. Dr. David Nadler Prata  
**Equipe:** Adriel Morais, Gabriel Lopes, João Pedro Figueredo, Rayssa de Oliveira (+ 5º integrante)

---

## 1. Objetivo da Sprint 4

Transformar dados preparados em inteligência acionável:
1. Treinar e avaliar o **modelo de predição de inadimplência**.
2. Construir o **scoring de recuperabilidade da dívida ativa** municipal (alta, média e baixa recuperabilidade).
3. Expor os resultados num **MVP interativo** para os analistas da Secretaria de Finanças de Palmas (SEFIN).

---

## 2. Entregáveis Oficiais (E1 a E4)

* **E1 — Metodologia de treino (Peso 25%):**
  - Divisão treino/validação/teste com **split temporal estrito** (sem *data leakage* de exercícios futuros).
  - Modelos baseline de referência implementados e registrados: **Regressão Logística** e **Árvore de Decisão**.
* **E2 — Modelos finais avaliados (Peso 30%):**
  - Modelo de classificação de inadimplência (Random Forest / XGBoost) com tunagem de hiperparâmetros.
  - Métricas completas: acurácia, precisão, recall, F1-Score e matriz de confusão.
  - Modelo complementar de **scoring de recuperabilidade** (faixas alta, média e baixa probabilidade).
  - **Métricas registradas por subgrupo** (faixa de renda e setor censitário) para subsidiar a análise de *fairness* da Sprint 5.
* **E3 — Notebook documentado + modelo serializado (Peso 15%):**
  - Trilha metodológica reprodutível: EDA $\rightarrow$ pré-processamento $\rightarrow$ treinamento $\rightarrow$ avaliação.
  - Modelo final serializado (`.joblib` ou `.pkl`) versionado no diretório `/models`.
* **E4 — MVP com interface (Peso 30%):**
  - Painel interativo demonstrável ao vivo: ranking de devedores por score de recuperabilidade, mapa de calor de inadimplência por setor e projeção de arrecadação potencial.

---

## 3. Arquitetura de Coleta: Suporte a Duas APIs Municipais

O servidor do SITRIB está preparado para consumir dados tributários de **duas APIs da Prefeitura de Palmas**:

1. **API Antiga da Prefeitura (REST - GET):**  
   - Endpoint base: `https://integracao.palmas.to.gov.br/apirest`  
   - Finalidade: dados pontuais cadastrais, certidões e débitos individuais.
2. **Portal Novo da Prefeitura (Nucleogov - POST):**  
   - Endpoint base: `https://acessoainformacao.palmas.to.gov.br/api`  
   - Finalidade: extração agregada de receitas, despesas e lotes orçamentários.
3. **Modo Híbrido / Fallback:**  
   - O servidor FastAPI possui controle de rota e contingência local para garantir operabilidade caso os serviços da prefeitura sofram bloqueios de taxa (*rate-limiting*).

---

## 4. Divisão de Trabalho da Equipe

| Integrante | Papel Principal | Entregáveis sob Responsabilidade |
| :--- | :--- | :--- |
| **Adriel Morais** | Backend, APIs Duais & Persistência | Orquestração do servidor FastAPI com seleção de fontes duais (Portal Novo e API Antiga), persistência do banco e endpoints de inferência do modelo para o MVP. |
| **Gabriel Lopes** | Engenharia de Features & Baselines | **E1:** Definição do split temporal sem vazamento de dados, engenharia de features tributárias e treinamento dos modelos baseline (Regressão Logística e Árvore de Decisão). |
| **João Pedro Figueredo** | Modelagem Avançada & Tunagem | **E2 (Parte 1):** Treinamento de Random Forest e XGBoost, tunagem de hiperparâmetros (GridSearch) e consolidação da matriz de confusão e métricas globais. |
| **Rayssa de Oliveira** | Scoring, Fairness & Serialização | **E2 (Parte 2) e E3:** Criação do score de recuperabilidade (alta/média/baixa), cálculo de métricas por subgrupo (renda/setor para a Sprint 5) e serialização do modelo em `/models/*.joblib`. |
| **5º Integrante / Front** | MVP e Painel Interativo | **E4:** Implementação do painel com ranking por recuperabilidade predita, mapa de calor por setor e simulador de arrecadação potencial conectado à API. |

---

## 5. Cronograma e Marcos Semanais

* **Semana 1 (02/11 a 06/11):** Split temporal documentado no notebook + baselines treinados + suporte a duas APIs ativo no backend.
* **Semana 2 (07/11 a 11/11):** Modelo final tunado + scoring de recuperabilidade com métricas por subgrupo + modelo salvo em `/models` + MVP funcional demonstrável.
* **Quarta-feira, 11/11/2026 até as 23h59:** Merge da branch da Sprint 4 e envio do link do repositório à coordenação.
