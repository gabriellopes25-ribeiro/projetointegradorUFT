# 📊 SITRIB — Relatório Integrado do Ecossistema Tributário

**Data da Geração:** 2026-10-20 21:13:15  
**Município Alvo:** Palmas/TO  
**Modo de Extração:** `AO_VIVO (Portal Novo NUCLEOGOV)`

---

## 1. 🌐 Diagnóstico de Conectividade e Auditoria das APIs

| Serviço / Endpoint | URL Base | Status / Código | Modo de Coleta |
| :--- | :--- | :---: | :---: |
| **Portal Novo (POST)** | `https://acessoainformacao.palmas.to.gov.br/api` | `HTTP 200 OK (Ao Vivo)` | `AO_VIVO (Portal Novo NUCLEOGOV)` |
| **API Antiga (GET)** | `http://integracao.palmas.to.gov.br/apirest/arrecadacao` | `HTTP 200 OK (Disponível)` | `AO_VIVO (Portal Novo NUCLEOGOV)` |
| **IBGE Localidades (REST)** | `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/1721000` | `200 OK` | `ONLINE` |

> **Nota de Auditoria:** Modo AO_VIVO (Portal Novo NUCLEOGOV): Extraídos 10 registros. IBGE Status: 200 OK.

---

## 2. 💰 Indicadores Gerais da Dívida Ativa

- **Volume Total Devido:** `R$ 242,501,053.63`
- **Quantidade de Títulos/Débitos:** `8`
- **Valor Médio por Débito:** `R$ 30,312,631.70`
- **Maior Dívida Registrada:** `R$ 60,495,521.31`

### Distribuição por Tipo de Tributo

| Tipo de Tributo | Quantidade | Valor Total (R$) | Participação (%) |
| :--- | :---: | :---: | :---: |
| **IMPOSTO SOBRE SERVIÇOS DE QUALQUER NATUREZA - ISSQN** | 1 | R$ 22,729,629.39 | 9.4% |
| **IMPOSTO SOBRE SERVIÇOS DE QUALQUER NATUREZA - ISSQN - PRINCIPAL** | 1 | R$ 21,952,521.07 | 9.1% |
| **IMPOSTOS** | 1 | R$ 31,833,381.96 | 13.1% |
| **IMPOSTOS SOBRE A PRODUÇÃO, CIRCULAÇÃO DE MERCADORIAS E SERVIÇOS** | 1 | R$ 22,729,629.39 | 9.4% |
| **IMPOSTOS SOBRE SERVIÇOS** | 1 | R$ 22,729,629.39 | 9.4% |
| **IMPOSTOS, TAXAS E CONTRIBUIÇÕES DE MELHORIA** | 1 | R$ 34,019,397.02 | 14.0% |
| **RECEITAS CORRENTES** | 1 | R$ 60,495,521.31 | 24.9% |
| **TRANSFERÊNCIAS CORRENTES** | 1 | R$ 26,011,344.10 | 10.7% |

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
- **Razão Dívida Total / Renda Média Domiciliar:** `74604.23x` a renda mensal média
- **Impacto da Inadimplência per Capita:** `R$ 773.90` por habitante

---

## 5. 🔒 Conformidade LGPD

Conforme estabelecido em `docs/integracao_prefeitura.md` e `src/transformacao/features.py`, as exportações analíticas preservam o sigilo fiscal e mascaram os números de CPF/CNPJ, e-mail e telefone antes de qualquer publicação ou persistência externa.
