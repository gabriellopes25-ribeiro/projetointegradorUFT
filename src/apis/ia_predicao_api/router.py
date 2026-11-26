"""
Roteador do Microsserviço de Inteligência Artificial, Capacidade Contributiva & Agentes Estritos
(`src/apis/ia_predicao_api/router.py`).

Executa:
  1. Modelo Random Forest (`models/modelo_inadimplencia_v1.joblib`) e Score de Recuperabilidade;
  2. Modelo de Capacidade Contributiva ("Quem Pode vs. Quem Não Pode Pagar" IPTU/ISSQN) com
     Blind Inference (LGPD) e Mitigação de Viés Socioeconômico/Geográfico (Fairness);
  3. Catálogo e Execução Estrita dos 4 Agentes Especializados por Microsserviço.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.apis.deps import eh_perfil_consulta, obter_usuario_logado, predicao_service
from src.apis.ia_predicao_api.agente_capacidade_fairness import (
    AgenteCapacidadeFairness,
    ParametrosCapacidadeFairness,
)
from src.models.usuario import Usuario
from src.services.orquestrador_agentes_service import OrquestradorAgentesService

router = APIRouter(tags=["4. Microsserviço de IA, Capacidade Contributiva, Fairness & Agentes"])
orquestrador_agentes = OrquestradorAgentesService()
agente_capacidade = AgenteCapacidadeFairness()


class PredicaoRequest(BaseModel):
    valor_debito: float = Field(..., example=15000.0)
    dias_atraso: int = Field(..., example=420)
    renda_media_regiao: float = Field(3200.0, example=3200.0)
    bairro: str = Field("Centro", example="Taquaralto")


class ExecucaoAgenteRequest(BaseModel):
    id_agente: str = Field(
        ...,
        example="agente_capacidade_fairness",
        description="ID do agente: agente_guardiao_lgpd, agente_auditor_tributario, agente_inspetor_orcamento, agente_capacidade_fairness",
    )
    ferramenta: str = Field(
        ...,
        example="tool_avaliar_quem_pode_pagar_com_fairness",
        description="Nome estrito da ferramenta autorizada para aquele agente",
    )
    parametros: Optional[Dict[str, Any]] = Field(default_factory=dict)


@router.post("/api/v1/predicao/inadimplencia")
@router.post("/api/v1/ia/predizer")
def executar_predicao_inadimplencia(
    dados: PredicaoRequest,
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    if eh_perfil_consulta(usuario):
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: Modelos preditivos de inadimplência são restritos a servidores da SEFIN.",
        )

    return predicao_service.predizer_contribuinte(
        valor_debito=dados.valor_debito,
        dias_atraso=dados.dias_atraso,
        renda_media_regiao=dados.renda_media_regiao,
        bairro=dados.bairro,
    )


@router.post("/api/v1/agentes/avaliar-capacidade-fairness")
def avaliar_quem_pode_pagar_fairness(
    dados: ParametrosCapacidadeFairness,
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    """
    Avalia 'Quem Pode vs. Quem Não Pode Pagar' (IPTU, ISSQN e Taxas) cruzando o
    Random Forest com o Índice de Comprometimento de Renda do IBGE, aplicando
    Blind Inference (zero CPF/Nome) e Mitigação de Viés Geográfico (Fairness).
    """
    return agente_capacidade.tool_avaliar_quem_pode_pagar_com_fairness(dados)


@router.get("/api/v1/agentes/catalogo")
def listar_agentes_microsservicos():
    """Retorna os 4 Agentes Especializados (um por pasta de microsserviço) e suas ferramentas estritas."""
    return {
        "total_agentes": 4,
        "principio_arquitetural": "Least Privilege Tool-Calling + Blind Inference LGPD + Mitigação de Viés (Fairness)",
        "agentes": orquestrador_agentes.listar_catalogo_agentes(),
    }


@router.get("/api/v1/agentes/analise-regional-palmas")
def obter_analise_regional_e_negociacao(
    tipo_tributo: str = "TODOS",
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    """
    Categoriza todos os débitos pelas 7 Macrorregiões Fiscais de Palmas, cruzando as colunas do PostgreSQL
    (`bairro`, `valor_venal`, `tipo_imovel`, `tipo_tributo`, `valor_original`, `juros_multa`, `valor_atualizado`)
    com a renda do IBGE e recomenda a melhor estratégia de negociação para cada região.
    """
    from src.apis.ia_predicao_api.agente_capacidade_fairness import ParametrosAnaliseRegional
    tributo_norm = tipo_tributo.upper() if tipo_tributo.upper() in ("IPTU", "ISS", "TAXA_LIXO", "TODOS") else "TODOS"
    return agente_capacidade.tool_mapear_estrategia_por_regiao_palmas(
        ParametrosAnaliseRegional(tipo_tributo=tributo_norm)
    )


@router.get("/api/v1/agentes/parecer-executivo-ia")
def obter_parecer_executivo_auditor(
    foco: str = "GERAL",
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    """
    Gera o Parecer Narrativo da IA ('Texto para Pensar' do Auditor) com insights estratégicos
    sobre o Dashboard, a concentração regional da dívida ativa, o peso dos juros nas negociações
    e a auditoria dos 182.808+ registros reais da Prefeitura no PostgreSQL.
    """
    return agente_capacidade.tool_gerar_parecer_executivo_auditor(foco=foco)


@router.get("/api/v1/agentes/auditoria-multas-erros-humanos")
def obter_auditoria_multas_e_perfis(
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    """
    Detecta multas tributárias desproporcionais ou com indício de erro humano de cálculo,
    sugere o valor saneado para Revisão Humana (Human-in-the-Loop / Art. 20 LGPD)
    e mapeia os 3 Perfis que mais tendem a dever em Palmas com estratégias de contorno.
    """
    return {
        "auditoria_multas": agente_capacidade.tool_auditar_anomalias_multas_erros_humanos(),
        "perfis_e_contorno": agente_capacidade.tool_mapear_perfis_inadimplencia_e_contorno(),
    }


@router.get("/api/v1/agentes/projecoes-futuras-solucao")
def obter_projecoes_futuras_e_mapa_calor(
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    """
    Retorna a progressão anual de 5 anos (Ano 1 a Ano 5) da arrecadação e recuperação fiscal,
    cruzando o valor venal dos imóveis com a macrorregião onde a pessoa reside, e o Mapa de Calor
    territorial das 7 macrozonas de Palmas com parecer explicativo dos Agentes de IA.
    """
    return agente_capacidade.tool_projetar_progressao_futura_solucoes()


class ChatAssistenteRequest(BaseModel):
    mensagem: str = Field(..., example="Quais variáveis foram usadas no modelo de IA?")
    historico: Optional[list] = Field(default_factory=list)


@router.post("/api/v1/agentes/chat-assistente-fiscal")
def conversar_com_assistente_fiscal(
    req: ChatAssistenteRequest,
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    """
    Chatbot do Agente de IA fundamentado nos dados limpos, métricas do modelo e cruzamento
    do valor venal com as 7 macrorregiões fiscais de Palmas.
    """
    return agente_capacidade.tool_responder_chat_assistente_fiscal(
        mensagem=req.mensagem,
        historico=req.historico,
    )


@router.post("/api/v1/agentes/executar")
def executar_ferramenta_agente_estrito(
    req: ExecucaoAgenteRequest,
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    """Executa uma ferramenta estrita de um dos 4 agentes respeitando o perfil RBAC e a LGPD."""
    perfil_op = str(usuario.perfil) if usuario else "administrador"
    cpf_op = usuario.cpf if usuario else None
    try:
        return orquestrador_agentes.executar_agente_estrito(
            id_agente=req.id_agente,
            ferramenta=req.ferramenta,
            parametros=req.parametros,
            perfil_operador=perfil_op,
            cpf_operador=cpf_op,
        )
    except PermissionError as err:
        raise HTTPException(status_code=403, detail=str(err))
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


app = FastAPI(title="SITRIB - Microsserviço IA, Capacidade Contributiva & Agentes API", version="2.0.0")
app.include_router(router)
