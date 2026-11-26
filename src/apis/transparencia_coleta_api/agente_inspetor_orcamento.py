"""
AGENTE 3 — Inspetor Orçamentário & Transparência (182.808+ Registros da Prefeitura)
Pasta de Microsserviço: `src/apis/transparencia_coleta_api/agente_inspetor_orcamento.py`

PRINCÍPIO DO MENOR PRIVILÉGIO (Least Privilege):
  - Este agente opera EXCLUSIVAMENTE sobre as tabelas públicas de execução orçamentária
    no PostgreSQL (`prefeitura_receitas` do Portal Novo e `prefeitura_historico_api_antiga`).
  - É terminantemente PROIBIDO a este agente acessar tabelas com CPF/CNPJ de contribuintes.
  - Aplica obrigatoriamente o tratamento da Armadilha 5.4 (dupla contagem contábil por nível
    hierárquico) e da Armadilha 5.3 (validação de filtros da API Antiga).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from sqlalchemy import text

from src.apis.deps import banco


class ParametrosInspecaoOrcamento(BaseModel):
    termo_tributo: Literal["IPTU", "ISS", "ITBI", "FPM", "TAXA", "GERAL"] = Field(
        "GERAL", description="Filtro de receita municipal nos 182.808+ registros do Portal Novo"
    )
    ano: Optional[int] = Field(None, description="Ano de exercício orçamentário")
    nivel_hierarquico: Optional[int] = Field(
        None,
        ge=1,
        le=8,
        description="Nível da árvore contábil para evitar dupla contagem (Armadilha 5.4)",
    )
    limite: int = Field(10, ge=1, le=100)


class AgenteInspetorOrcamento:
    """Agente estrito do microsserviço `transparencia_coleta_api` para auditoria das APIs da Prefeitura."""

    NOME_AGENTE = "Agente Inspetor de Transparência & Receitas (182k+ Registros)"
    MICROSSERVICO = "transparencia_coleta_api (src/apis/transparencia_coleta_api)"
    FERRAMENTAS_PERMITIDAS: List[str] = [
        "tool_auditar_arrecadacao_real_prefeitura",
        "tool_diagnosticar_armadilha_dupla_contagem",
    ]

    def tool_auditar_arrecadacao_real_prefeitura(
        self, params: ParametrosInspecaoOrcamento
    ) -> Dict[str, Any]:
        """
        Ferramenta Estrita 1: Consulta no PostgreSQL os dados reais coletados da Prefeitura
        de Palmas (Portal Novo NUCLEOGOV e API Antiga) filtrando por IPTU, ISSQN, ITBI ou FPM.
        """
        termo_busca = None if params.termo_tributo == "GERAL" else params.termo_tributo
        resultado_pg = banco.consultar_receitas_prefeitura_paginado(
            page=1,
            page_size=params.limite,
            ano=params.ano,
            nivel=params.nivel_hierarquico,
            busca_descricao=termo_busca,
        )

        # Consulta complementar na tabela histórica da API Antiga (2001-2021)
        with banco.engine.connect() as conn:
            filtro_ant = ""
            p_ant: Dict[str, Any] = {"lim": 5}
            if termo_busca:
                filtro_ant = "WHERE UPPER(descricao) LIKE :termo"
                p_ant["termo"] = f"%{termo_busca.upper()}%"
            rows_antiga = conn.execute(
                text(
                    f"""
                    SELECT ano_referencia, codigo_conta, descricao,
                           valor_previsto_ou_empenhado, valor_realizado_ou_pago
                    FROM prefeitura_historico_api_antiga
                    {filtro_ant}
                    ORDER BY ano_referencia DESC, valor_realizado_ou_pago DESC
                    LIMIT :lim
                    """
                ),
                p_ant,
            ).mappings().all()

        return {
            "agente": self.NOME_AGENTE,
            "microsservico": self.MICROSSERVICO,
            "ferramenta_executada": "tool_auditar_arrecadacao_real_prefeitura",
            "garantia_lgpd": "Zero dados pessoais (PII) acessados — leitura exclusiva de rubricas contábeis públicas.",
            "parametros_estritos_aplicados": params.model_dump(),
            "portal_novo_nucleogov": resultado_pg,
            "api_antiga_historico_separado": {
                "aviso_secao_1_manual": "Tabelas mantidas separadas para não misturar esquemas distintos entre Portal Novo e API Antiga.",
                "amostra_historica": [
                    {
                        **dict(r),
                        "valor_previsto_ou_empenhado": float(r["valor_previsto_ou_empenhado"] or 0.0),
                        "valor_realizado_ou_pago": float(r["valor_realizado_ou_pago"] or 0.0),
                    }
                    for r in rows_antiga
                ],
            },
        }

    def tool_diagnosticar_armadilha_dupla_contagem(
        self, ano: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ferramenta Estrita 2: Executa a prova matemática da Armadilha 5.4 do Manual do Professor,
        mostrando a soma por cada nível hierárquico (1 a 7) no PostgreSQL.
        """
        where_ano = "WHERE ano = :ano" if ano else ""
        params = {"ano": ano} if ano else {}

        with banco.engine.connect() as conn:
            niveis = conn.execute(
                text(
                    f"""
                    SELECT nivel_hierarquico,
                           COUNT(*) AS qtd_linhas,
                           COALESCE(SUM(valor_arrecado_mes), 0) AS soma_arrecadado_mes
                    FROM prefeitura_receitas
                    {where_ano}
                    GROUP BY nivel_hierarquico
                    ORDER BY nivel_hierarquico ASC
                    """
                ),
                params,
            ).mappings().all()

            raiz = conn.execute(
                text(
                    f"""
                    SELECT COALESCE(SUM(valor_arrecado_mes), 0)
                    FROM prefeitura_receitas
                    {where_ano + (' AND ' if where_ano else 'WHERE ')} eh_raiz_contabil = TRUE
                    """
                ),
                params,
            ).scalar() or 0.0

            total_bruto = sum(float(n["soma_arrecadado_mes"] or 0.0) for n in niveis)

        raiz_float = float(raiz)
        fator = round(total_bruto / raiz_float, 2) if raiz_float > 0 else 1.0

        return {
            "agente": self.NOME_AGENTE,
            "microsservico": self.MICROSSERVICO,
            "ferramenta_executada": "tool_diagnosticar_armadilha_dupla_contagem",
            "soma_ingenua_todos_niveis": round(total_bruto, 2),
            "soma_correta_apenas_raiz": round(raiz_float, 2),
            "fator_dupla_contagem": f"{fator}x",
            "distribuicao_por_nivel_hierarquico": [
                {
                    "nivel_hierarquico": int(n["nivel_hierarquico"]),
                    "quantidade_linhas": int(n["qtd_linhas"]),
                    "soma_arrecadado_mes": round(float(n["soma_arrecadado_mes"] or 0.0), 2),
                }
                for n in niveis
            ],
            "recomendacao_auditoria": (
                "Nunca some a tabela inteira de `sgreceitas/listar`. Utilize `eh_raiz_contabil = TRUE` "
                "para o total do município ou escolha um único `nivel_hierarquico` para análise de composição."
            ),
        }
