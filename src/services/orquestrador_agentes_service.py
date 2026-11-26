"""
Orquestrador Central dos 4 Agentes Estritos por Microsserviço (`src/services/orquestrador_agentes_service.py`).

Garante:
  1. Isolamento estrito de ferramentas (Least Privilege): cada agente só pode executar
     as ferramentas registradas na sua própria pasta de microsserviço (`src/apis/*`).
  2. Validação rigorosa de parâmetros via Pydantic antes de invocar qualquer ferramenta.
  3. Passagem obrigatória pelo Guardrail de LGPD e de Mitigação de Viés (Fairness).
"""

from typing import Any, Dict, List, Optional
from src.apis.auth_api.agente_guardiao_lgpd import AgenteGuardiaoLGPD, ParametrosValidacaoLGPD
from src.apis.tributario_api.agente_auditor_tributario import (
    AgenteAuditorTributario,
    ParametrosAuditoriaTributaria,
)
from src.apis.transparencia_coleta_api.agente_inspetor_orcamento import (
    AgenteInspetorOrcamento,
    ParametrosInspecaoOrcamento,
)
from src.apis.ia_predicao_api.agente_capacidade_fairness import (
    AgenteCapacidadeFairness,
    ParametrosCapacidadeFairness,
)
from src.repositories.endpoints_registry import MICROSERVICES_REGISTRY


class OrquestradorAgentesService:
    """Coordena os 4 Agentes Especializados do SITRIB respeitando limites de escopo e LGPD."""

    def __init__(self) -> None:
        self.agente_lgpd = AgenteGuardiaoLGPD()
        self.agente_tributario = AgenteAuditorTributario()
        self.agente_orcamento = AgenteInspetorOrcamento()
        self.agente_fairness = AgenteCapacidadeFairness()

    def listar_catalogo_agentes(self) -> List[Dict[str, Any]]:
        """Retorna a lista completa dos 4 agentes, seus microsserviços, ferramentas estritas e guardrails."""
        return [
            {
                "id_agente": "agente_guardiao_lgpd",
                "nome": self.agente_lgpd.NOME_AGENTE,
                "microsservico_pasta": "src/apis/auth_api",
                "url_servico": MICROSERVICES_REGISTRY["auth_api"]["url_producao"],
                "escopo_estrito": "Autenticação, controle RBAC e anonimização de dados pessoais (LGPD Art. 46 e CTN Art. 198).",
                "ferramentas_permitidas": self.agente_lgpd.FERRAMENTAS_PERMITIDAS,
                "proibicoes": ["Não acessa tabelas de receitas", "Não executa modelos preditivos"],
            },
            {
                "id_agente": "agente_auditor_tributario",
                "nome": self.agente_tributario.NOME_AGENTE,
                "microsservico_pasta": "src/apis/tributario_api",
                "url_servico": MICROSERVICES_REGISTRY["tributario_api"]["url_producao"],
                "escopo_estrito": "Auditoria de IPTU, ISSQN e Taxas Municipais com priorização via árvore Max-Heap O(log n).",
                "ferramentas_permitidas": self.agente_tributario.FERRAMENTAS_PERMITIDAS,
                "proibicoes": ["Não altera lançamentos brutos", "Aplica máscara LGPD quando solicitado"],
            },
            {
                "id_agente": "agente_inspetor_orcamento",
                "nome": self.agente_orcamento.NOME_AGENTE,
                "microsservico_pasta": "src/apis/transparencia_coleta_api",
                "url_servico": MICROSERVICES_REGISTRY["transparencia_coleta_api"]["url_producao"],
                "escopo_estrito": "Inspeção dos 182.808+ registros reais do Portal Novo e API Antiga com proteção contra a Armadilha 5.4 (dupla contagem contábil).",
                "ferramentas_permitidas": self.agente_orcamento.FERRAMENTAS_PERMITIDAS,
                "proibicoes": ["Proibido acessar qualquer tabela com CPF/CNPJ de contribuintes (Zero PII)"],
            },
            {
                "id_agente": "agente_capacidade_fairness",
                "nome": self.agente_fairness.NOME_AGENTE,
                "microsservico_pasta": "src/apis/ia_predicao_api",
                "url_servico": MICROSERVICES_REGISTRY["ia_predicao_api"]["url_producao"],
                "escopo_estrito": "Avaliação de Quem Pode vs. Quem Não Pode Pagar (IPTU/ISSQN) com Blind Inference (sem CPF/Nome) e mitigação de viés socioeconômico/IBGE (Fairness).",
                "ferramentas_permitidas": self.agente_fairness.FERRAMENTAS_PERMITIDAS,
                "proibicoes": ["Proibido receber Nome, CPF, E-mail ou Telefone na inferência da IA"],
            },
        ]

    def executar_agente_estrito(
        self,
        id_agente: str,
        ferramenta: str,
        parametros: Optional[Dict[str, Any]] = None,
        perfil_operador: str = "administrador",
        cpf_operador: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executa uma ferramenta de um agente específico validando se a ferramenta pertence
        estritamente àquele microsserviço.
        """
        parametros = parametros or {}

        if id_agente == "agente_guardiao_lgpd":
            if ferramenta not in self.agente_lgpd.FERRAMENTAS_PERMITIDAS:
                raise PermissionError(f"Ferramenta '{ferramenta}' não autorizada para {self.agente_lgpd.NOME_AGENTE}.")
            if ferramenta == "tool_verificar_permissao_consulta":
                p = ParametrosValidacaoLGPD(
                    perfil_operador=perfil_operador if perfil_operador in ("administrador", "gestao", "consulta") else "consulta",
                    cpf_operador=cpf_operador,
                    cpf_alvo=parametros.get("cpf_alvo"),
                    finalidade_consulta=parametros.get("finalidade_consulta", "AUDITORIA_FISCAL_SEFIN"),
                )
                return self.agente_lgpd.tool_verificar_permissao_consulta(p)
            return self.agente_lgpd.tool_auditar_conformidade_lgpd(perfil_operador=perfil_operador)

        if id_agente == "agente_auditor_tributario":
            if ferramenta not in self.agente_tributario.FERRAMENTAS_PERMITIDAS:
                raise PermissionError(f"Ferramenta '{ferramenta}' não autorizada para {self.agente_tributario.NOME_AGENTE}.")
            if ferramenta == "tool_diagnosticar_carteira_iptu_issqn":
                return self.agente_tributario.tool_diagnosticar_carteira_iptu_issqn()
            p_trib = ParametrosAuditoriaTributaria(
                tipo_tributo=parametros.get("tipo_tributo", "TODOS"),
                faixa_devedor=parametros.get("faixa_devedor", "todos"),
                limite=int(parametros.get("limite", 5)),
                mascarar_dados_lgpd=bool(parametros.get("mascarar_dados_lgpd", perfil_operador == "consulta")),
            )
            return self.agente_tributario.tool_extrair_prioridades_heap(p_trib)

        if id_agente == "agente_inspetor_orcamento":
            if ferramenta not in self.agente_orcamento.FERRAMENTAS_PERMITIDAS:
                raise PermissionError(f"Ferramenta '{ferramenta}' não autorizada para {self.agente_orcamento.NOME_AGENTE}.")
            if ferramenta == "tool_diagnosticar_armadilha_dupla_contagem":
                return self.agente_orcamento.tool_diagnosticar_armadilha_dupla_contagem(
                    ano=parametros.get("ano")
                )
            p_orc = ParametrosInspecaoOrcamento(
                termo_tributo=parametros.get("termo_tributo", "GERAL"),
                ano=parametros.get("ano"),
                nivel_hierarquico=parametros.get("nivel_hierarquico"),
                limite=int(parametros.get("limite", 10)),
            )
            return self.agente_orcamento.tool_auditar_arrecadacao_real_prefeitura(p_orc)

        if id_agente == "agente_capacidade_fairness":
            if ferramenta not in self.agente_fairness.FERRAMENTAS_PERMITIDAS:
                raise PermissionError(f"Ferramenta '{ferramenta}' não autorizada para {self.agente_fairness.NOME_AGENTE}.")
            if ferramenta == "tool_auditar_vies_geografico_carteira":
                return self.agente_fairness.tool_auditar_vies_geografico_carteira()
            if ferramenta == "tool_mapear_estrategia_por_regiao_palmas":
                from src.apis.ia_predicao_api.agente_capacidade_fairness import ParametrosAnaliseRegional
                p_reg = ParametrosAnaliseRegional(
                    regiao_filtro=parametros.get("regiao_filtro"),
                    tipo_tributo=parametros.get("tipo_tributo", "TODOS"),
                )
                return self.agente_fairness.tool_mapear_estrategia_por_regiao_palmas(p_reg)
            if ferramenta == "tool_gerar_parecer_executivo_auditor":
                return self.agente_fairness.tool_gerar_parecer_executivo_auditor(
                    foco=parametros.get("foco", "GERAL")
                )
            if ferramenta == "tool_auditar_anomalias_multas_erros_humanos":
                return self.agente_fairness.tool_auditar_anomalias_multas_erros_humanos()
            if ferramenta == "tool_mapear_perfis_inadimplencia_e_contorno":
                return self.agente_fairness.tool_mapear_perfis_inadimplencia_e_contorno()
            if ferramenta == "tool_projetar_progressao_futura_solucoes":
                return self.agente_fairness.tool_projetar_progressao_futura_solucoes()
            if ferramenta == "tool_responder_chat_assistente_fiscal":
                return self.agente_fairness.tool_responder_chat_assistente_fiscal(
                    mensagem=parametros.get("mensagem", ""),
                    historico=parametros.get("historico", []),
                )
            p_cap = ParametrosCapacidadeFairness(
                valor_debito=float(parametros.get("valor_debito", 12000.0)),
                dias_atraso=int(parametros.get("dias_atraso", 360)),
                tipo_tributo=parametros.get("tipo_tributo", "IPTU"),
                tipo_pessoa=parametros.get("tipo_pessoa", "FISICA"),
                bairro=parametros.get("bairro", "Plano Diretor"),
                quantidade_imoveis=int(parametros.get("quantidade_imoveis", 1)),
            )
            return self.agente_fairness.tool_avaliar_quem_pode_pagar_com_fairness(p_cap)

        raise ValueError(f"Agente '{id_agente}' não existe no catálogo de microsserviços.")
