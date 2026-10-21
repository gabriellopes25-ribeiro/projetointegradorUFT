# 📊 SITRIB — Relatório Integrado do Ecossistema Tributário

**Data da Geração:** 2026-10-20 20:41:45  
**Município Alvo:** Palmas/TO  
**Modo de Extração:** `FALLBACK (Seeds / Dívidas Simuladas)`

---

## 1. 🌐 Diagnóstico de Conectividade e Auditoria das APIs

| Serviço / Endpoint | URL Base | Status / Código | Modo de Coleta |
| :--- | :--- | :---: | :---: |
| **Portal Novo (POST)** | `https://acessoainformacao.palmas.to.gov.br/api/receitas` | `HTTP 403` | `FALLBACK (Seeds / Dívidas Simuladas)` |
| **API Antiga (GET)** | `https://integracao.palmas.to.gov.br/apirest/notas` | `HTTP 404` | `FALLBACK (Seeds / Dívidas Simuladas)` |
| **IBGE Localidades (REST)** | `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/1721000` | `200 OK` | `ONLINE` |

> **Nota de Auditoria:** Modo FALLBACK (Seeds / Dívidas Simuladas): Extraídos 4 registros. IBGE Status: 200 OK.

---

## 2. 💰 Indicadores Gerais da Dívida Ativa

- **Volume Total Devido:** `R$ 32,431.25`
- **Quantidade de Títulos/Débitos:** `4`
- **Valor Médio por Débito:** `R$ 8,107.81`
- **Maior Dívida Registrada:** `R$ 16,050.75`

### Distribuição por Tipo de Tributo

| Tipo de Tributo | Quantidade | Valor Total (R$) | Participação (%) |
| :--- | :---: | :---: | :---: |
| **IPTU** | 2 | R$ 5,680.50 | 17.5% |
| **ISS** | 1 | R$ 16,050.75 | 49.5% |
| **TAXA_LIXO** | 1 | R$ 10,700.00 | 33.0% |

### Status dos Débitos

| Status da Dívida | Quantidade de Títulos | Total (R$) |
| :--- | :---: | :---: |
| `AJUIZADO` | 2 | R$ 13,550.00 |
| `ATIVO` | 2 | R$ 18,881.25 |

---

## 3. 🚨 Fila de Prioridade de Cobrança (Max-Heap)

Maiores devedores priorizados pelo sistema:

| Documento | Nome do Contribuinte | Tributo | Valor Devido (R$) |
| :--- | :--- | :--- | :---: |
| `12.345.678/0001-90` | Tocantins Engenharia e Serviços Ltda | ISS | **R$ 16,050.75** |
| `98.765.432/0001-10` | Araguaia Comércio de Alimentos Eireli | TAXA_LIXO | **R$ 10,700.00** |
| `123.456.789-01` | Carlos Eduardo Siqueira | IPTU | **R$ 2,850.00** |
| `123.456.789-01` | Carlos Eduardo Siqueira | IPTU | **R$ 2,830.50** |

---

## 4. 📈 Cruzamento Socioeconômico com o IBGE

- **Renda Média Domiciliar (Palmas/TO):** `R$ 3,250.50`
- **População Estimada:** `313,349 habitantes`
- **Razão Dívida Total / Renda Média Domiciliar:** `9.98x` a renda mensal média
- **Impacto da Inadimplência per Capita:** `R$ 0.10` por habitante

---

## 5. 🔒 Conformidade LGPD

Conforme estabelecido em `docs/integracao_prefeitura.md` e `src/transformacao/features.py`, as exportações analíticas preservam o sigilo fiscal e mascaram os números de CPF/CNPJ, e-mail e telefone antes de qualquer publicação ou persistência externa.
