# Consultas SQL de Validação — Banco SITRIB

Este documento registra as consultas SQL utilizadas para validar a estrutura e a integridade dos dados populados no banco `sitrib.db`, conforme exigido na Parte 2 (Banco de Dados) da Sprint 2.

As consultas foram executadas após a população do banco via `scripts/popular_banco.py`, com a massa de dados simulados (piloto) definida em `seeds/mock_data.py`.

---

## Consulta 1 — Total devido por contribuinte (apenas dívidas ativas)

Soma o valor atualizado das dívidas com status `ATIVO`, agrupado por contribuinte, ordenado do maior para o menor devedor.

```sql
SELECT c.nome, c.cpf_cnpj, SUM(d.valor_atualizado) AS total_devido
FROM contribuinte c
JOIN imovel i ON i.id_contribuinte = c.id_contribuinte
JOIN divida d ON d.id_imovel = i.id_imovel
WHERE d.status_divida = 'ATIVO'
GROUP BY c.id_contribuinte
ORDER BY total_devido DESC;
```

**Resultado:**

| nome | cpf_cnpj | total_devido |
|---|---|---|
| Tocantins Engenharia e Serviços Ltda | 12.345.678/0001-90 | 16050.75 |
| Carlos Eduardo Siqueira | 123.456.789-01 | 2830.50 |

---

## Consulta 2 — Contribuintes com processo judicial em andamento

Localiza os contribuintes que possuem dívidas já ajuizadas, com processo em status `EM_ANDAMENTO`.

```sql
SELECT DISTINCT c.nome, c.cpf_cnpj, p.numero_processo, p.vara_judicial
FROM contribuinte c
JOIN imovel i ON i.id_contribuinte = c.id_contribuinte
JOIN divida d ON d.id_imovel = i.id_imovel
JOIN processo p ON p.id_divida = d.id_divida
WHERE p.status_processo = 'EM_ANDAMENTO'
ORDER BY c.nome;
```

**Resultado:**

| nome | cpf_cnpj | numero_processo | vara_judicial |
|---|---|---|---|
| Araguaia Comércio de Alimentos Eireli | 98.765.432/0001-10 | 0098765-43.2022.8.27.2729 | 2ª Vara de Execução Fiscal de Palmas |
| Carlos Eduardo Siqueira | 123.456.789-01 | 0012345-67.2023.8.27.2729 | 1ª Vara de Execução Fiscal e Tributária de Palmas |

---

## Consulta 3 — Imóveis adimplentes (sem dívidas registradas)

Identifica os imóveis que não possuem nenhum registro na tabela `divida`, ou seja, estão em dia com o fisco municipal.

```sql
SELECT i.inscricao_imobiliaria, i.endereco, c.nome AS proprietario
FROM imovel i
JOIN contribuinte c ON c.id_contribuinte = i.id_contribuinte
LEFT JOIN divida d ON d.id_imovel = i.id_imovel
WHERE d.id_divida IS NULL;
```

**Resultado:**

| inscricao_imobiliaria | endereco | proprietario |
|---|---|---|
| CCI-208-SUL-42 | Quadra 208 Sul, Avenida LO-05, Lote 08 | Carlos Eduardo Siqueira |
| CCI-GRACIOSA-LAGO-88 | Orla 14, Alameda dos Ipês, Lote 22 | Maria Auxiliadora Fernandes |

---

## Observação

Os dados utilizados são simulados (piloto), já que não há, até o momento, uma base pública de dívida ativa de Palmas-TO disponível para uso em bulk. As consultas foram validadas executando `python -m scripts.popular_banco` seguido da leitura direta do arquivo `sitrib.db` gerado, e todos os valores acima foram conferidos manualmente contra a massa de dados de `seeds/mock_data.py`.