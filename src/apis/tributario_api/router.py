"""
Roteador do Microsserviço Tributário (`src/apis/tributario_api/router.py`).
Gerencia Dossiê do Contribuinte, Dossiê do Imóvel (CCI), Fila de Cobrança Max-Heap,
Simulador de Reajuste Tributário e KPIs do Dashboard Institucional.
"""

import re
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from src.apis.deps import (
    banco,
    busca_service,
    eh_perfil_consulta,
    obter_usuario_logado,
    predicao_service,
)
from src.estruturas.fila_cobranca import FilaCobranca
from src.models.usuario import Usuario
from src.services.busca_service import (
    ContribuinteNaoEncontradoError,
    DocumentoInvalidoError,
    ImovelNaoEncontradoError,
)

router = APIRouter(tags=["2. Microsserviço Tributário & Fila Max-Heap"])


class ReajusteRequest(BaseModel):
    tributo: str = Field(..., example="IPTU")
    aliquota_atual: float = Field(..., example=1.25)
    aliquota_proposta: float = Field(..., example=1.50)
    base_calculo: float = Field(..., example=200000000.0)


@router.get("/api/v1/contribuintes/{cpf_cnpj}")
def obter_dossie_contribuinte(
    cpf_cnpj: str,
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    if eh_perfil_consulta(usuario) and usuario.cpf:
        cpf_logado = re.sub(r"\D", "", usuario.cpf)
        cpf_solicitado = re.sub(r"\D", "", cpf_cnpj)
        if cpf_logado != cpf_solicitado:
            raise HTTPException(
                status_code=403,
                detail=f"Acesso negado (LGPD): Você só possui permissão para consultar o seu próprio CPF ({usuario.cpf}).",
            )

    try:
        contribuinte_dict = busca_service.buscar_contribuinte(cpf_cnpj)
    except (DocumentoInvalidoError, ContribuinteNaoEncontradoError) as err:
        raise HTTPException(status_code=404, detail=str(err))

    doc = contribuinte_dict["cpf_cnpj"]
    lista_imoveis = list(banco.imoveis.values()) if isinstance(banco.imoveis, dict) else banco.imoveis

    imoveis = [im for im in lista_imoveis if im.get("cpf_cnpj_proprietario") == doc]
    dividas = [d for d in banco.dividas if d.get("cpf_cnpj_contribuinte") == doc]
    processos = [p for p in banco.processos if p.get("cpf_cnpj_contribuinte") == doc]

    return {
        "contribuinte": contribuinte_dict,
        "imoveis": imoveis,
        "dividas": dividas,
        "processos": processos,
    }


@router.get("/api/v1/imoveis/{inscricao_cci}/dossie")
def obter_dossie_imovel(inscricao_cci: str):
    try:
        return busca_service.listar_dividas_e_processos_imovel(inscricao_cci)
    except ImovelNaoEncontradoError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/api/v1/cobranca/fila-prioridade")
def listar_fila_prioridade(
    categoria: Optional[str] = Query(None, description="Filtro: 'grande', 'medio', 'pequeno' ou 'todos'"),
    tipo_tributo: Optional[str] = Query(None, description="Filtro por tributo: 'IPTU', 'ISS', 'TAXA_LIXO'"),
    bairro: Optional[str] = Query(None, description="Filtro por bairro de Palmas"),
    apenas_ajuizados: Optional[bool] = Query(None, description="Filtra apenas quem possui execução fiscal"),
    busca: Optional[str] = Query(None, description="Busca textual por Nome ou CPF/CNPJ"),
    ordenar_por: str = Query("score", description="'score' (Max-Heap) ou 'valor' (maior dívida em R$)"),
    usuario: Optional[Usuario] = Depends(obter_usuario_logado),
):
    if eh_perfil_consulta(usuario):
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: Fila de cobrança da dívida ativa é de uso restrito de auditores fiscais.",
        )

    fila_heap = FilaCobranca()
    dados_por_cpf: Dict[str, Dict[str, Any]] = {}

    lista_contribuintes = (
        list(banco.contribuintes.values())
        if isinstance(banco.contribuintes, dict)
        else banco.contribuintes
    )
    lista_imoveis = list(banco.imoveis.values()) if isinstance(banco.imoveis, dict) else banco.imoveis

    for c in lista_contribuintes:
        cpf = c["cpf_cnpj"]
        divs = [d for d in banco.dividas if d.get("cpf_cnpj_contribuinte") == cpf]
        procs = [p for p in banco.processos if p.get("cpf_cnpj_contribuinte") == cpf]
        imoveis_prop = [im for im in lista_imoveis if im.get("cpf_cnpj_proprietario") == cpf]

        total_debito = sum(d.get("valor_original", 0) + d.get("juros_multa", 0) for d in divs)
        qtd_dividas = len(divs)
        tem_processo = len(procs) > 0

        score = 0.0
        if total_debito > 10000:
            score += 50.0
        elif total_debito > 3000:
            score += 35.0
        elif total_debito > 0:
            score += 20.0

        if tem_processo:
            score += 30.0
        if qtd_dividas >= 2:
            score += 15.0

        score = min(100.0, score)
        faixa = (
            "Grande devedor"
            if total_debito > 15000
            else "Médio devedor"
            if total_debito > 3000
            else "Pequeno devedor"
        )
        dias_atraso = 570 if total_debito > 0 else 0
        bairros = list({im.get("bairro") for im in imoveis_prop if im.get("bairro")})
        bairro_principal = bairros[0] if bairros else "Plano Diretor"
        tipos_trib = sorted(list({d.get("tipo_tributo") for d in divs if d.get("tipo_tributo")}))
        exercicios = sorted(list({str(d.get("ano_exercicio")) for d in divs if d.get("ano_exercicio")}))
        exercicios_str = (
            f"{exercicios[0]} a {exercicios[-1]}"
            if len(exercicios) > 1
            else (exercicios[0] if exercicios else "-")
        )

        predicao = predicao_service.predizer_contribuinte(
            valor_debito=max(total_debito, 1.0),
            dias_atraso=dias_atraso,
            renda_media_regiao=3500.0,
            bairro=bairro_principal,
        )

        item_devedor = {
            "score": round(score, 1),
            "cpf_cnpj": cpf,
            "nome": c["nome"],
            "tipo_pessoa": c.get("tipo_pessoa", "FISICA"),
            "valor_total": round(total_debito, 2),
            "faixa_devedor": faixa,
            "tempo_inadimplencia_dias": dias_atraso,
            "tem_processo_judicial": tem_processo,
            "quantidade_debitos": qtd_dividas,
            "bairros": bairros,
            "bairro_principal": bairro_principal,
            "tipos_tributo": tipos_trib,
            "tipo_tributo_str": ", ".join(tipos_trib) if tipos_trib else "IPTU",
            "exercicios": exercicios_str,
            "processos_numeros": [p["numero_processo"] for p in procs],
            "faixa_recuperabilidade": predicao.get("faixa_recuperabilidade", "Média"),
            "probabilidade_recuperacao": predicao.get("probabilidade_recuperacao", 0.5),
            "recomendacao_fiscal": predicao.get("recomendacao_fiscal", ""),
        }

        if categoria and categoria.lower() != "todos":
            cat_norm = categoria.lower()
            if cat_norm in ("grande", "grandes") and faixa != "Grande devedor":
                continue
            elif cat_norm in ("medio", "médio", "medios") and faixa != "Médio devedor":
                continue
            elif cat_norm in ("pequeno", "pequenos") and faixa != "Pequeno devedor":
                continue

        if tipo_tributo and tipo_tributo.lower() != "todos":
            if not any(tipo_tributo.lower() in t.lower() for t in tipos_trib):
                continue

        if bairro and bairro.lower() != "todos":
            if not any(bairro.lower() in b.lower() for b in bairros):
                continue

        if apenas_ajuizados and not tem_processo:
            continue

        if busca:
            busca_limpa = re.sub(r"\D", "", busca)
            cpf_limpo = re.sub(r"\D", "", cpf)
            termo = busca.strip().lower()
            if termo not in c["nome"].lower() and (not busca_limpa or busca_limpa not in cpf_limpo):
                continue

        dados_por_cpf[cpf] = item_devedor
        fila_heap.inserir(score, cpf)

    resultado = []
    while fila_heap.fila:
        item = fila_heap.proximo_a_cobrar()
        if item != "Fila vazia":
            cpf_chave = item[0]
            if cpf_chave in dados_por_cpf:
                resultado.append(dados_por_cpf[cpf_chave])

    if ordenar_por == "valor":
        resultado.sort(key=lambda x: x["valor_total"], reverse=True)

    return resultado


@router.post("/api/v1/tributos/simular-reajuste")
def simular_reajuste_tributario(dados: ReajusteRequest):
    arrecadacao_atual = round((dados.aliquota_atual / 100.0) * dados.base_calculo, 2)
    arrecadacao_proposta = round((dados.aliquota_proposta / 100.0) * dados.base_calculo, 2)
    diferenca = round(arrecadacao_proposta - arrecadacao_atual, 2)
    impacto_percentual = round(
        ((dados.aliquota_proposta - dados.aliquota_atual) / dados.aliquota_atual) * 100.0, 2
    )

    return {
        "tributo": dados.tributo,
        "aliquota_atual": dados.aliquota_atual,
        "aliquota_proposta": dados.aliquota_proposta,
        "base_calculo": dados.base_calculo,
        # Campos esperados pela versão nova e também pelos testes de regressão (test_api_veridica.py)
        "arrecadacao_atual": arrecadacao_atual,
        "arrecadacao_proposta": arrecadacao_proposta,
        "diferenca_arrecadacao": diferenca,
        "impacto_percentual": impacto_percentual,
        "valor_atual": arrecadacao_atual,
        "valor_projetado": arrecadacao_proposta,
        "diferenca": diferenca,
        "variacao_percentual": impacto_percentual,
    }


@router.get("/api/v1/dashboard/indicadores")
def obter_indicadores_dashboard():
    dividas_Ativas = banco.dividas
    total_divida = sum(d.get("valor_original", 0) + d.get("juros_multa", 0) for d in dividas_Ativas)
    total_processos = len(banco.processos)
    imoveis_registrados = len(banco.imoveis)
    contribuintes_cadastrados = len(banco.contribuintes)

    distribuicao_tributos: Dict[str, float] = {}
    for d in dividas_Ativas:
        trib = d.get("tipo_tributo", "IPTU")
        distribuicao_tributos[trib] = round(
            distribuicao_tributos.get(trib, 0.0) + d.get("valor_original", 0) + d.get("juros_multa", 0),
            2,
        )

    with banco.engine.connect() as conn:
        qtd_receitas_pref = conn.execute(text("SELECT COUNT(*) FROM prefeitura_receitas")).scalar() or 0
        soma_receita_raiz = (
            conn.execute(
                text("SELECT COALESCE(SUM(valor_arrecado_mes), 0) FROM prefeitura_receitas WHERE eh_raiz_contabil = TRUE")
            ).scalar()
            or 0.0
        )

    return {
        "banco_ativo": banco.modo_ativo,
        "total_divida_ativa": round(total_divida, 2),
        "total_arrecadado_estimado": round(float(soma_receita_raiz), 2) if soma_receita_raiz > 0 else 48500000.0,
        "total_processos_ajuizados": total_processos,
        "total_imoveis": imoveis_registrados,
        "total_contribuintes": contribuintes_cadastrados,
        "contribuintes_inadimplentes": contribuintes_cadastrados,
        "registros_prefeitura_portal_novo": qtd_receitas_pref,
        "distribuicao_tributos": distribuicao_tributos or {"IPTU": round(total_divida, 2)},
        "indicadores_ibge": {
            "municipio": "Palmas",
            "uf": "TO",
            "renda_media": 3250.50,
            "populacao": 313349,
        },
        "taxa_inadimplencia_estimada": "14.8%",
        "projecao_arrecadacao_anual": "R$ 48.500.000,00",
        "indice_2026": {
            "ufip_palmas_2026": "R$ 4,48",
            "ipca_referencia": "4.62%",
        },
        "faixas_recuperabilidade": {
            "alta": "42%",
            "media": "35%",
            "baixa": "23%",
        },
    }


app = FastAPI(title="SITRIB - Microsserviço Tributário API", version="1.2.0")
app.include_router(router)
