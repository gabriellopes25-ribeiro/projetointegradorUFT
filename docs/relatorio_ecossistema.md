# 📊 SITRIB — Relatório Integrado do Ecossistema Tributário

**Data da Geração:** 2026-10-20 21:31:40  
**Município Alvo:** Palmas/TO  
**Modo de Extração:** `AO_VIVO (Portal Novo NUCLEOGOV)`

---

## 1. 🌐 Diagnóstico de Conectividade e Auditoria das APIs

| Serviço / Endpoint | URL Base | Status / Código | Modo de Coleta |
| :--- | :--- | :---: | :---: |
| **Portal Novo (POST)** | `https://acessoainformacao.palmas.to.gov.br/api` | `HTTP 200 OK (Ao Vivo)` | `AO_VIVO (Portal Novo NUCLEOGOV)` |
| **API Antiga (GET)** | `http://integracao.palmas.to.gov.br/apirest/arrecadacao` | `HTTP 200 OK (Disponível)` | `AO_VIVO (Portal Novo NUCLEOGOV)` |
| **IBGE Localidades (REST)** | `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/1721000` | `200 OK` | `ONLINE` |

> **Nota de Auditoria:** Modo AO_VIVO (Portal Novo NUCLEOGOV): Extraídos 20 registros. IBGE Status: 200 OK.

---

## 2. 📅 Execução Orçamentária e Arrecadação Mensal (Filtro por Mês / Totais)

- **Exercício / Mês de Competência:** `10/2026`
- **Volume Total Arrecadado no Mês:** `R$ 410,975,763.48`
- **Previsão Orçamentária Vinculada:** `R$ 8,786,021,697.00`
- **Índice de Realização da Receita:** `4.68%`
- **Quantidade de Títulos/Lançamentos:** `18`
- **Valor Médio por Lançamento:** `R$ 22,831,986.86`
- **Maior Valor Registrado:** `R$ 60,495,521.31`

### Distribuição por Tipo de Tributo

| Tipo de Tributo | Quantidade | Valor Total (R$) | Participação (%) |
| :--- | :---: | :---: | :---: |
| **IMPOSTO SOBRE SERVIÇOS DE QUALQUER NATUREZA - ISSQN** | 1 | R$ 22,729,629.39 | 5.5% |
| **IMPOSTO SOBRE SERVIÇOS DE QUALQUER NATUREZA - ISSQN - PRINCIPAL** | 1 | R$ 21,952,521.07 | 5.3% |
| **IMPOSTOS** | 1 | R$ 31,833,381.96 | 7.8% |
| **IMPOSTOS SOBRE A PRODUÇÃO, CIRCULAÇÃO DE MERCADORIAS E SERVIÇOS** | 1 | R$ 22,729,629.39 | 5.5% |
| **IMPOSTOS SOBRE SERVIÇOS** | 1 | R$ 22,729,629.39 | 5.5% |
| **IMPOSTOS, TAXAS E CONTRIBUIÇÕES DE MELHORIA** | 1 | R$ 34,019,397.02 | 8.3% |
| **ISS Principal - Próprio** | 1 | R$ 13,174,408.68 | 3.2% |
| **PARTICIPAÇÃO NA RECEITA DOS ESTADOS E DISTRITO FEDERAL** | 1 | R$ 14,979,705.73 | 3.6% |
| **RECEITAS CORRENTES** | 1 | R$ 60,495,521.31 | 14.7% |
| **TRANSFERÊNCIAS CORRENTES** | 1 | R$ 26,011,344.10 | 6.3% |
| **TRANSFERÊNCIAS DA UNIÃO E DE SUAS ENTIDADES** | 1 | R$ 11,031,638.37 | 2.7% |
| **TRANSFERÊNCIAS DE OUTRAS INSTITUIÇÕES PÚBLICAS** | 1 | R$ 19,051,541.89 | 4.6% |
| **TRANSFERÊNCIAS DE RECURSOS DO FUNDO DE MANUTENÇÃO E DESENVOLVIMENTO DA EDUCAÇÃO BÁSICA E DE VALORIZAÇÃO DOS PROFISSIONAIS DA EDUCAÇÃO - FUNDEB** | 3 | R$ 57,154,625.67 | 13.9% |
| **TRANSFERÊNCIAS DE RECURSOS DO FUNDO DE MANUTENÇÃO E DESENVOLVIMENTO DA EDUCAÇÃO BÁSICA E DE VALORIZAÇÃO DOS PROFISSIONAIS DA EDUCAÇÃO - FUNDEB - PRINCIPAL** | 1 | R$ 19,051,541.89 | 4.6% |
| **TRANSFERÊNCIAS DOS ESTADOS E DO DISTRITO FEDERAL E DE SUAS ENTIDADES** | 1 | R$ 14,979,705.73 | 3.6% |
| **Transferências de Recursos do FUNDEB** | 1 | R$ 19,051,541.89 | 4.6% |

### Status dos Débitos

| Status da Dívida | Quantidade de Títulos | Total (R$) |
| :--- | :---: | :---: |

---

## 3. 🚨 Fila de Prioridade de Cobrança (Max-Heap)

Maiores devedores priorizados pelo sistema:

| Documento | Nome do Contribuinte | Tributo | Valor Devido (R$) |
| :--- | :--- | :--- | :---: |
| `000.000.000-00` | TESOURO MUNICIPAL | RECEITAS CORRENTES | **R$ 60,495,521.31** |
| `000.000.000-00` | TESOURO MUNICIPAL | IMPOSTOS, TAXAS E CONTRIBUIÇÕES DE MELHORIA | **R$ 34,019,397.02** |
| `000.000.000-00` | TESOURO MUNICIPAL | IMPOSTOS | **R$ 31,833,381.96** |
| `000.000.000-00` | TESOURO MUNICIPAL | TRANSFERÊNCIAS CORRENTES | **R$ 26,011,344.10** |
| `000.000.000-00` | TESOURO MUNICIPAL | IMPOSTOS SOBRE A PRODUÇÃO, CIRCULAÇÃO DE MERCADORIAS E SERVIÇOS | **R$ 22,729,629.39** |

---

## 4. 📈 Cruzamento Socioeconômico com o IBGE

- **Renda Média Domiciliar (Palmas/TO):** `R$ 3,250.50`
- **População Estimada:** `313,349 habitantes`
- **Razão Dívida Total / Renda Média Domiciliar:** `126434.63x` a renda mensal média
- **Impacto da Inadimplência per Capita:** `R$ 1,311.56` por habitante

---

## 5. 🔒 Conformidade LGPD

Conforme estabelecido em `docs/integracao_prefeitura.md` e `src/transformacao/features.py`, as exportações analíticas preservam o sigilo fiscal e mascaram os números de CPF/CNPJ, e-mail e telefone antes de qualquer publicação ou persistência externa.
