"""
AGENTE 2 — Auditor Tributário Estrito (IPTU, ISSQN, Taxas & Max-Heap)
Pasta de Microsserviço: `src/apis/tributario_api/agente_auditor_tributario.py`

PRINCÍPIO DO MENOR PRIVILÉGIO (Least Privilege):
  - Este agente opera EXCLUSIVAMENTE sobre o domínio de Tributos Municipais de Palmas
    (IPTU, ISSQN, Taxa de Lixo) e a estrutura de dados Max-Heap O(log n).
  - Só aceita parâmetros validados pelo schema `ParametrosAuditoriaTributaria`.
  - Passa os dados de contribuintes pelo Guardrail de Mascaramento LGPD caso solicitado.
"""

from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field

from src.apis.deps import banco
from src.apis.auth_api.agente_guardiao_lgpd import AgenteGuardiaoLGPD
from src.estruturas.fila_cobranca import FilaCobranca


class ParametrosAuditoriaTributaria(BaseModel):
    tipo_tributo: Literal["IPTU", "ISS", "TAXA_LIXO", "TODOS"] = Field(
        "TODOS", description="Tributo municipal alvo da auditoria (IPTU patrimonial ou ISSQN serviços)"
    )
    faixa_devedor: Literal["grande", "medio", "pequeno", "todos"] = Field(
        "todos", description="Faixa de criticidade na fila Max-Heap"
    )
    limite: int = Field(5, ge=1, le=50, description="Quantidade máxima de registros do topo da Heap")
    mascarar_dados_lgpd: bool = Field(
        False, description="Se True, aplica anonimização de CPF/CNPJ na saída do agente"
    )


class AgenteAuditorTributario:
    """Agente estrito do microsserviço `tributario_api` para gestão de IPTU, ISSQN e Fila Max-Heap."""

    NOME_AGENTE = "Agente Auditor Tributário (IPTU, ISSQN & Max-Heap)"
    MICROSSERVICO = "tributario_api (src/apis/tributario_api)"
    FERRAMENTAS_PERMITIDAS: List[str] = [
        "tool_extrair_prioridades_heap",
        "tool_diagnosticar_carteira_iptu_issqn",
    ]

    def tool_extrair_prioridades_heap(self, params: ParametrosAuditoriaTributaria) -> Dict[str, Any]:
        """
        Ferramenta Estrita 1: Extrai os maiores devedores usando a árvore Max-Heap O(log n),
        separando por tributo (IPTU vs. ISSQN) e aplicando máscara LGPD quando necessário.
        """
        debitos = banco.listar_debitos_completos()
        if params.tipo_tributo != "TODOS":
            debitos = [
                d for d in debitos if (d.get("tipo_tributo") or "").upper() == params.tipo_tributo
            ]

        agrupado: Dict[str, Dict[str, Any]] = {}
        for d in debitos:
            cpf = d["cpf_cnpj_contribuinte"]
            if cpf not in agrupado:
                agrupado[cpf] = {
                    "cpf_cnpj": cpf,
                    "nome": d["nome_contribuinte"],
                    "tipo_pessoa": d["tipo_pessoa"],
                    "bairro": d["bairro"],
                    "valor_total": 0.0,
                    "qtd_debitos": 0,
                    "tributos": set(),
                    "tem_processo": False,
                }
            agrupado[cpf]["valor_total"] = round(agrupado[cpf]["valor_total"] + d["valor_atualizado"], 2)
            agrupado[cpf]["qtd_debitos"] += 1
            agrupado[cpf]["tributos"].add(d["tipo_tributo"])
            if d["tem_processo"]:
                agrupado[cpf]["tem_processo"] = True

        heap = FilaCobranca()
        itens_por_cpf: Dict[str, Dict[str, Any]] = {}

        for cpf, info in agrupado.items():
            total = info["valor_total"]
            faixa = (
                "Grande devedor"
                if total >= 50000
                else "Médio devedor"
                if total >= 10000
                else "Pequeno devedor"
            )
            if params.faixa_devedor != "todos":
                if params.faixa_devedor == "grande" and faixa != "Grande devedor":
                    continue
                if params.faixa_devedor == "medio" and faixa != "Médio devedor":
                    continue
                if params.faixa_devedor == "pequeno" and faixa != "Pequeno devedor":
                    continue

            score = min(
                100.0,
                (55.0 if total >= 50000 else 35.0 if total >= 10000 else 20.0)
                + (30.0 if info["tem_processo"] else 0.0)
                + (15.0 if info["qtd_debitos"] >= 2 else 0.0),
            )

            doc_saida = cpf
            if params.mascarar_dados_lgpd:
                doc_saida = AgenteGuardiaoLGPD.tool_mascarar_pii(
                    cpf_cnpj=cpf, exigir_mascara=True
                )["cpf_cnpj_tratado"]

            itens_por_cpf[cpf] = {
                "cpf_cnpj": doc_saida,
                "nome": info["nome"],
                "tipo_pessoa": info["tipo_pessoa"],
                "bairro": info["bairro"],
                "faixa_devedor": faixa,
                "score_max_heap": score,
                "valor_total_devido": total,
                "tributos_vinculados": sorted(list(info["tributos"])),
                "tem_execucao_fiscal": info["tem_processo"],
            }
            heap.inserir(score, cpf)

        topo: List[Dict[str, Any]] = []
        while heap.fila and len(topo) < params.limite:
            extraido = heap.proximo_a_cobrar()
            if extraido != "Fila vazia":
                cpf_k = extraido[0]
                if cpf_k in itens_por_cpf:
                    topo.append(itens_por_cpf[cpf_k])

        return {
            "agente": self.NOME_AGENTE,
            "microsservico": self.MICROSSERVICO,
            "ferramenta_executada": "tool_extrair_prioridades_heap",
            "parametros_estritos_aplicados": params.model_dump(),
            "total_contribuintes_no_filtro": len(itens_por_cpf),
            "topo_fila_max_heap": topo,
        }

    def tool_diagnosticar_carteira_iptu_issqn(self) -> Dict[str, Any]:
        """
        Ferramenta Estrita 2: Compara a composição da Dívida Ativa entre IPTU (Imobiliário),
        ISSQN (Serviços) e Taxas Municipais no PostgreSQL.
        """
        debitos = banco.listar_debitos_completos()
        resumo: Dict[str, Dict[str, Any]] = {}

        for d in debitos:
            trib = (d.get("tipo_tributo") or "IPTU").upper()
            if trib not in resumo:
                resumo[trib] = {
                    "tributo": trib,
                    "natureza_juridica": (
                        "Imposto Patrimonial Urbano (vinculado à Inscrição Imobiliária CCI)"
                        if trib == "IPTU"
                        else "Imposto Sobre Serviços de Qualquer Natureza (atividade empresarial/autônoma)"
                        if trib in ("ISS", "ISSQN")
                        else "Taxa de Poder de Polícia / Serviço Público Divisível"
                    ),
                    "quantidade_titulos": 0,
                    "valor_original_soma": 0.0,
                    "valor_atualizado_soma": 0.0,
                    "titulos_ajuizados": 0,
                }
            resumo[trib]["quantidade_titulos"] += 1
            resumo[trib]["valor_original_soma"] = round(
                resumo[trib]["valor_original_soma"] + d["valor_original"], 2
            )
            resumo[trib]["valor_atualizado_soma"] = round(
                resumo[trib]["valor_atualizado_soma"] + d["valor_atualizado"], 2
            )
            if d["tem_processo"]:
                resumo[trib]["titulos_ajuizados"] += 1

        return {
            "agente": self.NOME_AGENTE,
            "microsservico": self.MICROSSERVICO,
            "ferramenta_executada": "tool_diagnosticar_carteira_iptu_issqn",
            "analise_por_tributo": list(resumo.values()),
        }
