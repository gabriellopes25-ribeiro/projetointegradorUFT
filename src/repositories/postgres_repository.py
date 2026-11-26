"""
Repositório Relacional Oficial PostgreSQL (SITRIB).

Conecta ao PostgreSQL via `DATABASE_URL` (SQLAlchemy + psycopg2) e gerencia:
  1. Dívida Ativa e Execução Fiscal (contribuinte, imovel, divida, processo)
  2. Base Real do Portal Novo da Prefeitura de Palmas (prefeitura_receitas - 182.808+ registros)
  3. Base Real Histórica da API Antiga (prefeitura_historico_api_antiga - 2001 a 2021)

Possui inserção em lote de alta velocidade (executemany / psycopg2 batch) capaz de
persistir 180 mil+ registros em poucos segundos, além de paginação e agregação SQL
diretas no banco (evitando a Armadilha 5.4 de dupla contagem contábil).
"""

import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.database import criar_engine_postgres, inicializar_schema_postgres
from src.coleta.coletor_prefeitura import nivel_hierarquico, eh_receita_raiz


class RepositorioPostgreSQL:
    """Camada de persistência oficial PostgreSQL para o SITRIB."""

    def __init__(self, database_url: Optional[str] = None, caminho_sqlite: Optional[Union[str, Path]] = None) -> None:
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://sitrib:sitrib_secret_password@localhost:5432/sitrib",
        )
        self.engine: Engine = criar_engine_postgres(self.database_url)
        self.modo_ativo = "PostgreSQL"
        inicializar_schema_postgres(self.engine)
        self._garantir_dados_iniciais()

    def _garantir_dados_iniciais(self) -> None:
        """Se o banco PostgreSQL estiver vazio, popula automaticamente as seeds cadastrais e os CSVs brutos da Prefeitura existentes em data/bruto."""
        with self.engine.connect() as conn:
            qtd_c = conn.execute(text("SELECT COUNT(*) FROM contribuinte")).scalar() or 0
            qtd_r = conn.execute(text("SELECT COUNT(*) FROM prefeitura_receitas")).scalar() or 0
        if qtd_c == 0:
            from scripts.popular_banco import popular_banco_postgres
            popular_banco_postgres(self.engine)
        if qtd_r == 0:
            import csv
            pasta_bruto = Path(__file__).resolve().parent.parent.parent / "data" / "bruto"
            if pasta_bruto.exists():
                for arq in sorted(pasta_bruto.glob("portal_novo_receitas*.csv"), reverse=True):
                    try:
                        with open(arq, "r", encoding="utf-8-sig") as f:
                            linhas = list(csv.DictReader(f, delimiter=";"))
                        if linhas:
                            self.inserir_receitas_portal_novo_em_lote(linhas, limpar_antes=False)
                            break
                    except Exception:
                        pass
                for arq_ant in sorted(pasta_bruto.glob("api_antiga_*.csv"), reverse=True):
                    try:
                        with open(arq_ant, "r", encoding="utf-8-sig") as f:
                            linhas_ant = list(csv.DictReader(f, delimiter=";"))
                        if linhas_ant:
                            self.inserir_historico_api_antiga_em_lote(linhas_ant, limpar_antes=False)
                            break
                    except Exception:
                        pass

    # =========================================================================
    # 1. OPERAÇÕES DE CONTRIBUINTE, IMÓVEL, DÍVIDA E PROCESSO
    # =========================================================================

    def buscar_contribuinte(self, cpf_cnpj: str) -> Optional[Dict[str, Any]]:
        if not cpf_cnpj:
            return None
        alvo_digitos = "".join(filter(str.isdigit, cpf_cnpj))
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM contribuinte")).mappings().all()
            for row in rows:
                if "".join(filter(str.isdigit, row["cpf_cnpj"])) == alvo_digitos:
                    return {
                        "id_contribuinte": row["id_contribuinte"],
                        "nome": row["nome"],
                        "cpf_cnpj": row["cpf_cnpj"],
                        "email": row["email"],
                        "telefone": row["telefone"],
                        "tipo_pessoa": row["tipo_pessoa"],
                    }
        return None

    def buscar_imovel(self, inscricao_cci: str) -> Optional[Dict[str, Any]]:
        if not inscricao_cci:
            return None
        with self.engine.connect() as conn:
            row = conn.execute(
                text(
                    """SELECT imovel.*, contribuinte.cpf_cnpj AS cpf_cnpj_proprietario
                       FROM imovel
                       JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                       WHERE imovel.inscricao_imobiliaria = :cci"""
                ),
                {"cci": inscricao_cci.strip()},
            ).mappings().first()
            if not row:
                return None
            return {
                "inscricao_cci": row["inscricao_imobiliaria"],
                "endereco": row["endereco"],
                "tipo_imovel": row["tipo_imovel"],
                "valor_venal": float(row["valor_venal"] or 0),
                "cpf_cnpj_proprietario": row["cpf_cnpj_proprietario"],
                "bairro": row["bairro"],
                "cep": row["cep"],
            }

    def listar_dividas_por_imovel(self, inscricao_cci: str) -> List[Dict[str, Any]]:
        if not inscricao_cci:
            return []
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """SELECT divida.*, imovel.inscricao_imobiliaria, contribuinte.cpf_cnpj AS cpf_cnpj_contribuinte
                       FROM divida
                       JOIN imovel ON imovel.id_imovel = divida.id_imovel
                       JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                       WHERE imovel.inscricao_imobiliaria = :cci"""
                ),
                {"cci": inscricao_cci.strip()},
            ).mappings().all()
            return [
                {
                    "codigo_debito": f"DIVIDA-{r['id_divida']}",
                    "ano_exercicio": r["exercicio_ano"],
                    "valor_original": float(r["valor_original"]),
                    "juros_multa": round(float(r["valor_atualizado"]) - float(r["valor_original"]), 2),
                    "status": r["status_divida"],
                    "inscricao_cci": r["inscricao_imobiliaria"],
                    "cpf_cnpj_contribuinte": r["cpf_cnpj_contribuinte"],
                    "tipo_tributo": r["tipo_tributo"],
                }
                for r in rows
            ]

    def listar_processos_por_imovel(self, inscricao_cci: str) -> List[Dict[str, Any]]:
        if not inscricao_cci:
            return []
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """SELECT processo.*, divida.id_divida AS id_divida_origem,
                              contribuinte.cpf_cnpj AS cpf_cnpj_contribuinte
                       FROM processo
                       JOIN divida ON divida.id_divida = processo.id_divida
                       JOIN imovel ON imovel.id_imovel = divida.id_imovel
                       JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                       WHERE imovel.inscricao_imobiliaria = :cci"""
                ),
                {"cci": inscricao_cci.strip()},
            ).mappings().all()
            return [
                {
                    "numero_processo": r["numero_processo"],
                    "vara": r["vara_judicial"],
                    "data_autuacao": str(r["data_ajuizamento"]),
                    "codigo_debito": f"DIVIDA-{r['id_divida_origem']}",
                    "cpf_cnpj_contribuinte": r["cpf_cnpj_contribuinte"],
                    "status_processo": r["status_processo"],
                }
                for r in rows
            ]

    def listar_imoveis_por_contribuinte(self, cpf_cnpj: str) -> List[Dict[str, Any]]:
        c = self.buscar_contribuinte(cpf_cnpj)
        if not c:
            return []
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """SELECT imovel.* FROM imovel
                       JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                       WHERE contribuinte.cpf_cnpj = :cpf"""
                ),
                {"cpf": c["cpf_cnpj"]},
            ).mappings().all()
            return [
                {
                    "inscricao_cci": r["inscricao_imobiliaria"],
                    "endereco": r["endereco"],
                    "tipo_imovel": r["tipo_imovel"],
                    "valor_venal": float(r["valor_venal"] or 0),
                    "cpf_cnpj_proprietario": c["cpf_cnpj"],
                    "bairro": r["bairro"],
                    "cep": r["cep"],
                }
                for r in rows
            ]

    @property
    def contribuintes(self) -> Dict[str, Dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM contribuinte")).mappings().all()
            return {
                r["cpf_cnpj"]: {
                    "nome": r["nome"],
                    "cpf_cnpj": r["cpf_cnpj"],
                    "email": r["email"],
                    "telefone": r["telefone"],
                    "tipo_pessoa": r["tipo_pessoa"],
                }
                for r in rows
            }

    @property
    def imoveis(self) -> Dict[str, Dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """SELECT imovel.*, contribuinte.cpf_cnpj AS cpf_cnpj_proprietario
                       FROM imovel
                       JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte"""
                )
            ).mappings().all()
            return {
                r["inscricao_imobiliaria"]: {
                    "inscricao_cci": r["inscricao_imobiliaria"],
                    "endereco": r["endereco"],
                    "tipo_imovel": r["tipo_imovel"],
                    "valor_venal": float(r["valor_venal"] or 0),
                    "cpf_cnpj_proprietario": r["cpf_cnpj_proprietario"],
                    "bairro": r["bairro"],
                    "cep": r["cep"],
                }
                for r in rows
            }

    @property
    def dividas(self) -> List[Dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """SELECT divida.*, imovel.inscricao_imobiliaria, contribuinte.cpf_cnpj AS cpf_cnpj_contribuinte
                       FROM divida
                       JOIN imovel ON imovel.id_imovel = divida.id_imovel
                       JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte"""
                )
            ).mappings().all()
            return [
                {
                    "codigo_debito": f"DIVIDA-{r['id_divida']}",
                    "ano_exercicio": r["exercicio_ano"],
                    "valor_original": float(r["valor_original"]),
                    "juros_multa": round(float(r["valor_atualizado"]) - float(r["valor_original"]), 2),
                    "status": r["status_divida"],
                    "inscricao_cci": r["inscricao_imobiliaria"],
                    "cpf_cnpj_contribuinte": r["cpf_cnpj_contribuinte"],
                    "tipo_tributo": r["tipo_tributo"],
                }
                for r in rows
            ]

    @property
    def processos(self) -> List[Dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """SELECT processo.*, divida.id_divida AS id_divida_origem,
                              contribuinte.cpf_cnpj AS cpf_cnpj_contribuinte
                       FROM processo
                       JOIN divida ON divida.id_divida = processo.id_divida
                       JOIN imovel ON imovel.id_imovel = divida.id_imovel
                       JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte"""
                )
            ).mappings().all()
            return [
                {
                    "numero_processo": r["numero_processo"],
                    "vara": r["vara_judicial"],
                    "data_autuacao": str(r["data_ajuizamento"]),
                    "codigo_debito": f"DIVIDA-{r['id_divida_origem']}",
                    "cpf_cnpj_contribuinte": r["cpf_cnpj_contribuinte"],
                    "status_processo": r["status_processo"],
                }
                for r in rows
            ]

    def listar_debitos_completos(self) -> List[Dict[str, Any]]:
        """Retorna visão consolidada (LEFT JOIN) de todas as dívidas com imóvel, contribuinte e processo."""
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(
                    """SELECT
                           d.id_divida,
                           d.exercicio_ano,
                           d.valor_original,
                           d.valor_atualizado,
                           d.tipo_tributo,
                           d.status_divida,
                           d.data_vencimento,
                           i.inscricao_imobiliaria,
                           i.endereco AS endereco_imovel,
                           i.bairro,
                           i.cep,
                           i.tipo_imovel,
                           i.valor_venal,
                           c.cpf_cnpj AS cpf_cnpj_contribuinte,
                           c.nome AS nome_contribuinte,
                           c.tipo_pessoa,
                           c.email AS email_contribuinte,
                           c.telefone AS telefone_contribuinte,
                           p.numero_processo,
                           p.vara_judicial,
                           p.status_processo,
                           p.data_ajuizamento
                       FROM divida d
                       JOIN imovel i ON i.id_imovel = d.id_imovel
                       JOIN contribuinte c ON c.id_contribuinte = i.id_contribuinte
                       LEFT JOIN processo p ON p.id_divida = d.id_divida"""
                )
            ).mappings().all()
            resultado: List[Dict[str, Any]] = []
            for r in rows:
                data_venc = str(r["data_vencimento"] or f"{r['exercicio_ano']}-12-31")
                partes_data = data_venc.split("-")
                mes_venc = int(partes_data[1]) if len(partes_data) >= 2 and partes_data[1].isdigit() else 12
                val_orig = float(r["valor_original"] or 0.0)
                val_atual = float(r["valor_atualizado"] or val_orig)
                tributo = (r["tipo_tributo"] or "IPTU").upper()
                origem_api = "portal_novo" if int(r["exercicio_ano"]) >= 2022 or tributo == "ISS" else "api_antiga"
                resultado.append({
                    "id_divida": r["id_divida"],
                    "codigo_debito": f"DIVIDA-{r['id_divida']}",
                    "origem_api": origem_api,
                    "exercicio_ano": int(r["exercicio_ano"]),
                    "data_vencimento": data_venc,
                    "mes_vencimento": mes_venc,
                    "valor_original": round(val_orig, 2),
                    "juros_multa": round(val_atual - val_orig, 2),
                    "valor_atualizado": round(val_atual, 2),
                    "tipo_tributo": r["tipo_tributo"],
                    "status_divida": r["status_divida"],
                    "inscricao_cci": r["inscricao_imobiliaria"],
                    "endereco_imovel": r["endereco_imovel"],
                    "bairro": r["bairro"] or "Plano Diretor",
                    "cep": r["cep"] or "77000-000",
                    "tipo_imovel": r["tipo_imovel"] or "RESIDENCIAL",
                    "valor_venal": float(r["valor_venal"] or 0.0),
                    "cpf_cnpj_contribuinte": r["cpf_cnpj_contribuinte"],
                    "nome_contribuinte": r["nome_contribuinte"],
                    "tipo_pessoa": r["tipo_pessoa"] or "FISICA",
                    "email_contribuinte": r["email_contribuinte"],
                    "telefone_contribuinte": r["telefone_contribuinte"],
                    "tem_processo": bool(r["numero_processo"]),
                    "numero_processo": r["numero_processo"],
                    "vara_judicial": r["vara_judicial"],
                    "status_processo": r["status_processo"],
                    "data_ajuizamento": str(r["data_ajuizamento"]) if r["data_ajuizamento"] else None,
                })
            return resultado

    def obter_opcoes_filtros_auditoria(self) -> Dict[str, Any]:
        """Extrai dinamicamente do PostgreSQL todas as categorias e valores únicos para filtros do Auditor."""
        debitos = self.listar_debitos_completos()
        anos = sorted({d["exercicio_ano"] for d in debitos} | {2026}, reverse=True)
        meses = sorted({d["mes_vencimento"] for d in debitos})
        tributos = sorted({d["tipo_tributo"] for d in debitos if d.get("tipo_tributo")})
        status_div = sorted({d["status_divida"] for d in debitos if d.get("status_divida")})
        bairros = sorted({d["bairro"] for d in debitos if d.get("bairro")})
        tipos_imovel = sorted({d["tipo_imovel"] for d in debitos if d.get("tipo_imovel")})
        tipos_pessoa = sorted({d["tipo_pessoa"] for d in debitos if d.get("tipo_pessoa")})
        status_proc = sorted({d["status_processo"] for d in debitos if d.get("status_processo")})
        varas = sorted({d["vara_judicial"] for d in debitos if d.get("vara_judicial")})

        with self.engine.connect() as conn:
            total_receitas_portal_novo = conn.execute(text("SELECT COUNT(*) FROM prefeitura_receitas")).scalar() or 0
            total_historico_api_antiga = conn.execute(text("SELECT COUNT(*) FROM prefeitura_historico_api_antiga")).scalar() or 0

        return {
            "banco_ativo": self.modo_ativo,
            "exercicios_ano": anos,
            "meses_vencimento_ativos": meses,
            "tipos_tributo": tributos,
            "status_divida": status_div,
            "bairros": bairros,
            "tipos_imovel": tipos_imovel,
            "tipos_pessoa": tipos_pessoa,
            "status_processo": status_proc,
            "varas_judiciais": varas,
            "fontes_coleta": ["dual", "portal_novo", "api_antiga"],
            "metricas_prefeitura_postgres": {
                "registros_portal_novo": total_receitas_portal_novo,
                "registros_api_antiga": total_historico_api_antiga,
            },
            "colunas_banco": {
                "contribuinte": ["id_contribuinte", "cpf_cnpj", "nome", "tipo_pessoa", "email", "telefone", "endereco_correspondencia"],
                "imovel": ["id_imovel", "inscricao_imobiliaria", "id_contribuinte", "endereco", "bairro", "cep", "tipo_imovel", "valor_venal", "area_terreno"],
                "divida": ["id_divida", "id_imovel", "exercicio_ano", "valor_original", "valor_atualizado", "tipo_tributo", "status_divida", "data_vencimento"],
                "processo": ["id_processo", "numero_processo", "id_divida", "vara_judicial", "status_processo", "data_ajuizamento", "observacoes"],
                "prefeitura_receitas": ["id_receita", "ano", "mes", "orgao", "orgao_nome", "unidade_nome", "codigo", "descricao", "nivel_hierarquico", "eh_raiz_contabil", "valor_orcado", "valor_arrecado_mes", "valor_arrecado_periodo", "data_coleta"],
                "prefeitura_historico_api_antiga": ["id_registro", "endpoint_origem", "ano_referencia", "mes_referencia", "codigo_conta", "descricao", "fornecedor", "cpf_cnpj_fornecedor", "valor_previsto_ou_empenhado", "valor_realizado_ou_pago", "data_coleta"],
            },
        }

    # =========================================================================
    # 2. CARGA EM LOTE (BATCH INSERT) E CONSULTA PAGINADA DOS 182 MIL+ REGISTROS
    # =========================================================================

    @staticmethod
    def _converter_moeda_br(valor: Any) -> float:
        """Converte strings numéricas ou formato brasileiro ('1.234,56' ou '1234.56') para float."""
        if valor is None or valor == "":
            return 0.0
        if isinstance(valor, (int, float)):
            return float(valor)
        texto = str(valor).strip()
        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        elif "," in texto:
            texto = texto.replace(",", ".")
        try:
            return float(texto)
        except ValueError:
            return 0.0

    def inserir_receitas_portal_novo_em_lote(
        self,
        registros: List[Dict[str, Any]],
        limpar_antes: bool = False,
        tamanho_lote: int = 5000,
    ) -> int:
        """
        Persiste milhares de registros reais do Portal Novo (`sgreceitas/listar`) no PostgreSQL
        em lotes transacionais de alta velocidade (executemany).
        """
        if not registros:
            return 0

        hoje = str(date.today())
        linhas_preparadas: List[Dict[str, Any]] = []

        for r in registros:
            # Ignora se for registro de fallback mock de dívida ativa
            if "codigo" not in r and "valor_arrecado_mes" not in r:
                continue
            cod = str(r.get("codigo") or "")
            desc = str(r.get("descricao") or "RECEITA MUNICIPAL")
            linhas_preparadas.append({
                "ano": int(r.get("ano") or 2026),
                "mes": int(r.get("mes") or 1),
                "orgao": str(r.get("orgao") or ""),
                "orgao_nome": str(r.get("orgao_nome") or ""),
                "unidade_id": str(r.get("unidade_id") or ""),
                "unidade_nome": str(r.get("unidade_nome") or ""),
                "codigo": cod,
                "codigo_original": str(r.get("codigo_original") or cod),
                "descricao": desc[:255],
                "nivel_hierarquico": int(r.get("nivel_hierarquico") or nivel_hierarquico(cod)),
                "eh_raiz_contabil": bool(str(r.get("eh_raiz_contabil", "")).lower() == "true" or eh_receita_raiz(desc, cod)),
                "valor_orcado": self._converter_moeda_br(r.get("valor_orcado")),
                "valor_arrecado_mes": self._converter_moeda_br(r.get("valor_arrecado_mes")),
                "valor_arrecado_periodo": self._converter_moeda_br(r.get("valor_arrecado_periodo")),
                "covid": str(r.get("covid") or "Não")[:10],
                "data_coleta": str(r.get("data_coleta") or hoje),
            })

        if not linhas_preparadas:
            return 0

        sql_insert = text(
            """
            INSERT INTO prefeitura_receitas (
                ano, mes, orgao, orgao_nome, unidade_id, unidade_nome,
                codigo, codigo_original, descricao, nivel_hierarquico,
                eh_raiz_contabil, valor_orcado, valor_arrecado_mes,
                valor_arrecado_periodo, covid, data_coleta
            ) VALUES (
                :ano, :mes, :orgao, :orgao_nome, :unidade_id, :unidade_nome,
                :codigo, :codigo_original, :descricao, :nivel_hierarquico,
                :eh_raiz_contabil, :valor_orcado, :valor_arrecado_mes,
                :valor_arrecado_periodo, :covid, :data_coleta
            )
            """
        )

        with self.engine.begin() as conn:
            if limpar_antes:
                conn.execute(text("TRUNCATE TABLE prefeitura_receitas RESTART IDENTITY"))
            for i in range(0, len(linhas_preparadas), tamanho_lote):
                lote = linhas_preparadas[i : i + tamanho_lote]
                conn.execute(sql_insert, lote)

        return len(linhas_preparadas)

    def inserir_historico_api_antiga_em_lote(
        self,
        registros: List[Dict[str, Any]],
        endpoint_origem: str = "arrecadacao",
        limpar_antes: bool = False,
        tamanho_lote: int = 5000,
    ) -> int:
        """
        Persiste registros reais da API Antiga (`arrecadacao/` ou `gastos-diretos/`)
        em tabela separada no PostgreSQL (respeitando o alerta da Seção 1 do Manual).
        """
        if not registros:
            return 0

        hoje = str(date.today())
        linhas_preparadas: List[Dict[str, Any]] = []

        for r in registros:
            if "receita_codigo" not in r and "empenho" not in r and "fornecedor" not in r:
                continue
            ep = str(r.get("endpoint_origem") or endpoint_origem)
            ano_ref = int(r.get("ano") or r.get("ano_referencia") or 2021)
            mes_ref = int(r.get("mes") or r.get("mes_referencia") or 1)
            cod_conta = str(r.get("receita_codigo") or r.get("cod_natureza") or r.get("empenho") or "")
            desc = str(r.get("receita_descricao") or r.get("natureza") or r.get("historico") or "")[:255]
            val_prev = self._converter_moeda_br(r.get("valor_ano") or r.get("valor_empenhado") or r.get("receita_valor"))
            val_real = self._converter_moeda_br(r.get("valor_consolidado_ano") or r.get("valor_pago") or r.get("receita_valor"))

            linhas_preparadas.append({
                "id_externo": int(r["id"]) if str(r.get("id", "")).isdigit() else None,
                "endpoint_origem": ep[:40],
                "ano_referencia": ano_ref,
                "mes_referencia": mes_ref,
                "codigo_conta": cod_conta[:60],
                "descricao": desc,
                "unidade_gestora": str(r.get("unidade") or "Prefeitura Municipal de Palmas")[:255],
                "fornecedor": str(r.get("fornecedor") or "")[:255],
                "cpf_cnpj_fornecedor": str(r.get("cpf_cnpj") or "")[:30],
                "processo_administrativo": str(r.get("processo") or "")[:60],
                "data_ocorrencia": str(r.get("receita_data_ocorrencia") or r.get("data") or "")[:30],
                "valor_previsto_ou_empenhado": val_prev,
                "valor_realizado_ou_pago": val_real,
                "data_coleta": str(r.get("data_coleta") or hoje),
            })

        if not linhas_preparadas:
            return 0

        sql_insert = text(
            """
            INSERT INTO prefeitura_historico_api_antiga (
                id_externo, endpoint_origem, ano_referencia, mes_referencia,
                codigo_conta, descricao, unidade_gestora, fornecedor,
                cpf_cnpj_fornecedor, processo_administrativo, data_ocorrencia,
                valor_previsto_ou_empenhado, valor_realizado_ou_pago, data_coleta
            ) VALUES (
                :id_externo, :endpoint_origem, :ano_referencia, :mes_referencia,
                :codigo_conta, :descricao, :unidade_gestora, :fornecedor,
                :cpf_cnpj_fornecedor, :processo_administrativo, :data_ocorrencia,
                :valor_previsto_ou_empenhado, :valor_realizado_ou_pago, :data_coleta
            )
            """
        )

        with self.engine.begin() as conn:
            if limpar_antes:
                conn.execute(text("TRUNCATE TABLE prefeitura_historico_api_antiga RESTART IDENTITY"))
            for i in range(0, len(linhas_preparadas), tamanho_lote):
                lote = linhas_preparadas[i : i + tamanho_lote]
                conn.execute(sql_insert, lote)

        return len(linhas_preparadas)

    def consultar_receitas_prefeitura_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        nivel: Optional[int] = None,
        apenas_raiz_sem_dupla_contagem: bool = False,
        orgao: Optional[str] = None,
        busca_descricao: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Consulta paginada diretamente no PostgreSQL (LIMIT / OFFSET + índices B-Tree)
        sobre os 182.808+ registros reais do Portal Novo, demonstrando a proteção
        contra a Armadilha 5.4 (soma ingênua vs. soma correta por nível hierárquico).
        """
        filtros_sql = ["1=1"]
        params: Dict[str, Any] = {}

        if ano is not None:
            filtros_sql.append("ano = :ano")
            params["ano"] = ano
        if mes is not None:
            filtros_sql.append("mes = :mes")
            params["mes"] = mes
        if nivel is not None:
            filtros_sql.append("nivel_hierarquico = :nivel")
            params["nivel"] = nivel
        if apenas_raiz_sem_dupla_contagem:
            filtros_sql.append("eh_raiz_contabil = TRUE")
        if orgao:
            filtros_sql.append("(orgao = :orgao OR LOWER(orgao_nome) LIKE :orgao_like)")
            params["orgao"] = orgao.strip()
            params["orgao_like"] = f"%{orgao.strip().lower()}%"
        if busca_descricao:
            filtros_sql.append("(LOWER(descricao) LIKE :busca OR codigo LIKE :busca)")
            params["busca"] = f"%{busca_descricao.strip().lower()}%"

        where_clause = " AND ".join(filtros_sql)
        offset = (max(1, page) - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        with self.engine.connect() as conn:
            total_registros = conn.execute(
                text(f"SELECT COUNT(*) FROM prefeitura_receitas WHERE {where_clause}"),
                params,
            ).scalar() or 0

            # Calcula a soma ingênua (todos os níveis) vs. soma real sem dupla contagem (Armadilha 5.4)
            agregados = conn.execute(
                text(
                    f"""
                    SELECT
                        COALESCE(SUM(valor_arrecado_mes), 0) AS soma_ingenua_todos_niveis,
                        COALESCE(SUM(CASE WHEN eh_raiz_contabil = TRUE THEN valor_arrecado_mes ELSE 0 END), 0) AS soma_correta_raiz_contabil,
                        COALESCE(SUM(CASE WHEN nivel_hierarquico = 3 THEN valor_arrecado_mes ELSE 0 END), 0) AS soma_nivel_3
                    FROM prefeitura_receitas
                    WHERE {where_clause}
                    """
                ),
                params,
            ).mappings().first()

            rows = conn.execute(
                text(
                    f"""
                    SELECT id_receita, ano, mes, orgao, orgao_nome, unidade_nome,
                           codigo, codigo_original, descricao, nivel_hierarquico,
                           eh_raiz_contabil, valor_orcado, valor_arrecado_mes,
                           valor_arrecado_periodo, covid, data_coleta
                    FROM prefeitura_receitas
                    WHERE {where_clause}
                    ORDER BY ano DESC, mes DESC, codigo ASC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                params,
            ).mappings().all()

        soma_ingenua = float(agregados["soma_ingenua_todos_niveis"] or 0.0)
        soma_correta = float(agregados["soma_correta_raiz_contabil"] or 0.0)
        fator_dupla_contagem = round(soma_ingenua / soma_correta, 2) if soma_correta > 0 else 1.0
        total_paginas = max(1, (total_registros + page_size - 1) // page_size)

        return {
            "banco_ativo": self.modo_ativo,
            "tabela": "prefeitura_receitas (Portal Novo NUCLEOGOV)",
            "paginacao": {
                "pagina_atual": page,
                "page_size": page_size,
                "total_registros": total_registros,
                "total_paginas": total_paginas,
                "tem_proxima": page < total_paginas,
                "tem_anterior": page > 1,
            },
            "auditoria_hierarquia_armadilha_5_4": {
                "soma_ingenua_com_dupla_contagem": round(soma_ingenua, 2),
                "soma_correta_sem_dupla_contagem_raiz": round(soma_correta, 2),
                "soma_composicao_nivel_3": round(float(agregados["soma_nivel_3"] or 0.0), 2),
                "fator_multiplicacao_detectado": f"{fator_dupla_contagem}x",
                "explicacao": "A listagem traz todos os níveis da árvore contábil. Para o total real do município, soma-se apenas a raiz (RECEITAS CORRENTES e RECEITAS DE CAPITAL) ou um único nível hierárquico.",
            },
            "itens": [
                {
                    **dict(r),
                    "valor_orcado": float(r["valor_orcado"] or 0.0),
                    "valor_arrecado_mes": float(r["valor_arrecado_mes"] or 0.0),
                    "valor_arrecado_periodo": float(r["valor_arrecado_periodo"] or 0.0),
                    "data_coleta": str(r["data_coleta"]),
                }
                for r in rows
            ],
        }


# Alias de compatibilidade para importações legadas que referenciem RepositorioSQLite
RepositorioSQLite = RepositorioPostgreSQL
