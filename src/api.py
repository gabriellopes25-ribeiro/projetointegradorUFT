"""
Servidor API REST - SITRIB (Sistema Integrado de Gestão Tributária Municipal)
Projeto Integrador UFT - Ciência da Computação

Expondo os 7 Endpoints RESTful para integração com o Frontend React/Vite.
"""

from typing import Any, Dict, List, Optional
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Adiciona o diretório raiz do backend ao sys.path para importações locais
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.services.busca_service import (
    BuscaService,
    ContribuinteNaoEncontradoError,
    DocumentoInvalidoError,
    ImovelNaoEncontradoError,
)
from src.estruturas.fila_cobranca import FilaCobranca
from seeds.mock_data import (
    BancoSimuladoEmMemoria,
    CONTRIBUINTES_SEED,
    IMOVEIS_SEED,
    DIVIDAS_SEED,
    PROCESSOS_SEED,
)

# Inicializa aplicação FastAPI
app = FastAPI(
    title="SITRIB API - Gestão Tributária Municipal",
    version="1.0.0",
    description="API RESTful oficial do SITRIB (Palmas/TO) para integração com o frontend desacoplado.",
)

# Habilita CORS para o frontend (Vite na porta 5173 e qualquer host local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa serviços e repositório
banco = BancoSimuladoEmMemoria()
banco.carregar_dados_iniciais()
busca_service = BuscaService(repositorio=banco)


# ==============================================================================
# Modelos Pydantic (Request / Response)
# ==============================================================================

class ReajusteRequest(BaseModel):
    tributo: str = Field(..., example="IPTU")
    aliquota_atual: float = Field(..., example=1.25)
    aliquota_proposta: float = Field(..., example=1.50)
    base_calculo: float = Field(..., example=200000000.0)


# ==============================================================================
# 1. GET /api/v1/contribuintes/{cpf_cnpj} - Dossiê do Contribuinte
# ==============================================================================
@app.get("/api/v1/contribuintes/{cpf_cnpj}")
def obter_dossie_contribuinte(cpf_cnpj: str):
    """
    Busca contribuinte por CPF ou CNPJ (com ou sem máscara) e retorna:
    - Dados cadastrais do contribuinte (com mascaramento LGPD)
    - Lista de imóveis vinculados
    - Lista de dívidas e pendências tributárias
    - Processos de execução fiscal
    """
    try:
        contribuinte_dict = busca_service.buscar_contribuinte(cpf_cnpj)
    except (DocumentoInvalidoError, ContribuinteNaoEncontradoError) as err:
        raise HTTPException(status_code=404, detail=str(err))

    doc = contribuinte_dict["cpf_cnpj"]

    lista_imoveis = list(banco.imoveis.values()) if isinstance(banco.imoveis, dict) else banco.imoveis

    # Busca imóveis do proprietário
    imoveis = [im for im in lista_imoveis if im.get("cpf_cnpj_proprietario") == doc]

    # Busca dívidas do contribuinte
    dividas = [d for d in banco.dividas if d.get("cpf_cnpj_contribuinte") == doc]

    # Busca processos judiciais do contribuinte
    processos = [p for p in banco.processos if p.get("cpf_cnpj_contribuinte") == doc]

    return {
        "contribuinte": contribuinte_dict,
        "imoveis": imoveis,
        "dividas": dividas,
        "processos": processos,
    }


# ==============================================================================
# 2. GET /api/v1/imoveis/{inscricao_cci}/dossie - Dossiê Imobiliário
# ==============================================================================
@app.get("/api/v1/imoveis/{inscricao_cci}/dossie")
def obter_dossie_imovel(inscricao_cci: str):
    """
    Retorna o dossiê fiscal consolidado de um imóvel específico (CCI).
    """
    try:
        return busca_service.listar_dividas_e_processos_imovel(inscricao_cci)
    except ImovelNaoEncontradoError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


# ==============================================================================
# 3. GET /api/v1/cobranca/fila-prioridade - Fila de Cobrança (Max-Heap)
# ==============================================================================
@app.get("/api/v1/cobranca/fila-prioridade")
def listar_fila_prioridade():
    """
    Retorna a fila de cobrança ordenada por Max-Heap O(log n)
    com score de risco de inadimplência e classificação de devedores.
    """
    # Mapeia contribuintes e calcula débitos consolidados
    fila_heap = FilaCobranca()
    dados_por_cpf: Dict[str, Dict[str, Any]] = {}

    lista_contribuintes = list(banco.contribuintes.values()) if isinstance(banco.contribuintes, dict) else banco.contribuintes

    for c in lista_contribuintes:
        cpf = c["cpf_cnpj"]
        divs = [d for d in banco.dividas if d.get("cpf_cnpj_contribuinte") == cpf]
        procs = [p for p in banco.processos if p.get("cpf_cnpj_contribuinte") == cpf]

        total_debito = sum(d.get("valor_original", 0) + d.get("juros_multa", 0) for d in divs)
        qtd_dividas = len(divs)
        tem_processo = len(procs) > 0

        # Algoritmo de Score de Risco (0 a 100)
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

        faixa = "Grande devedor" if total_debito > 15000 else "Médio devedor" if total_debito > 3000 else "Pequeno devedor"

        dados_por_cpf[cpf] = {
            "score": round(score, 1),
            "cpf_cnpj": cpf,
            "nome": c["nome"],
            "valor_total": round(total_debito, 2),
            "faixa_devedor": faixa,
            "tempo_inadimplencia_dias": 570 if total_debito > 0 else 0,
            "tem_processo_judicial": tem_processo,
            "quantidade_debitos": qtd_dividas,
        }
        fila_heap.inserir(score, cpf)

    # Extrai ordenado do heap
    resultado = []
    while fila_heap.fila:
        item = fila_heap.proximo_a_cobrar()
        if item != "Fila vazia":
            cpf, score = item
            if cpf in dados_por_cpf:
                resultado.append(dados_por_cpf[cpf])

    return resultado


# ==============================================================================
# 4. POST /api/v1/tributos/simular-reajuste - Simulação de Reajuste (RF06 / RF07)
# ==============================================================================
@app.post("/api/v1/tributos/simular-reajuste")
def simular_reajuste_tributario(dados: ReajusteRequest):
    """
    Simula o impacto financeiro de alteração de alíquota sem alterar dados reais.
    Retorna comparativo lado a lado e variação percentual.
    """
    if dados.aliquota_atual <= 0 or dados.aliquota_proposta <= 0:
        raise HTTPException(status_code=400, detail="Alíquotas devem ser maiores que zero.")

    valor_atual = round(dados.base_calculo * (dados.aliquota_atual / 100), 2)
    valor_projetado = round(dados.base_calculo * (dados.aliquota_proposta / 100), 2)
    diferenca = round(valor_projetado - valor_atual, 2)
    variacao_percentual = round(((dados.aliquota_proposta - dados.aliquota_atual) / dados.aliquota_atual) * 100, 2)

    return {
        "id": f"SIM-{os.urandom(4).hex().upper()}",
        "nome": f"Simulação de {dados.tributo} ({dados.aliquota_atual}% → {dados.aliquota_proposta}%)",
        "tributo": dados.tributo,
        "aliquota_atual": dados.aliquota_atual,
        "aliquota_proposta": dados.aliquota_proposta,
        "base_calculo": dados.base_calculo,
        "valor_atual": valor_atual,
        "valor_projetado": valor_projetado,
        "diferenca": diferenca,
        "variacao_percentual": variacao_percentual,
    }


# ==============================================================================
# 5. GET /api/v1/dashboard/indicadores - KPIs e Resumo da Arrecadação
# ==============================================================================
@app.get("/api/v1/dashboard/indicadores")
def obter_indicadores_dashboard():
    """
    Retorna indicadores consolidados de arrecadação, dívida ativa e cruzamento com dados do IBGE.
    """
    total_divida_ativa = sum(
        d.get("valor_original", 0) + d.get("juros_multa", 0)
        for d in banco.dividas
        if d.get("status") in ("ATIVO", "AJUIZADO")
    )

    lista_contribuintes = list(banco.contribuintes.values()) if isinstance(banco.contribuintes, dict) else banco.contribuintes

    return {
        "total_arrecadado_estimado": 45890000.0,
        "total_divida_ativa": round(total_divida_ativa, 2),
        "contribuintes_inadimplentes": len([c for c in lista_contribuintes if any(d.get("cpf_cnpj_contribuinte") == c["cpf_cnpj"] for d in banco.dividas)]),
        "distribuicao_tributos": {
            "IPTU": 62.5,
            "ISS": 27.0,
            "Taxas": 10.5,
        },
        "indicadores_ibge": {
            "municipio": "Palmas",
            "uf": "TO",
            "renda_media": 3250.50,
            "populacao": 313349,
        },
    }


# ==============================================================================
# 6. GET /api/v1/relatorios/ecossistema - Relatório Geral em Markdown / Texto
# ==============================================================================
@app.get("/api/v1/relatorios/ecossistema")
def gerar_relatorio_ecossistema():
    """
    Gera o relatório do ecossistema municipal, auditabilidade e integração de dados fiscais.
    """
    total_contribuintes = len(banco.contribuintes)
    total_imoveis = len(banco.imoveis)
    total_dividas = len(banco.dividas)
    total_processos = len(banco.processos)

    markdown = f"""# Relatório Geral do Ecossistema Tributário — SITRIB
**Município:** Palmas / TO  
**Status do Sistema:** Operacional e Integrado (FastAPI + React SPA)

## 1. Estatísticas de Cadastro
- **Total de Contribuintes Ativos:** {total_contribuintes}
- **Imóveis Mapeados no Cadastro Técnico Municipal:** {total_imoveis}
- **Débitos Tributários em Cobrança:** {total_dividas}
- **Processos Judiciais de Execução Fiscal:** {total_processos}

## 2. Indicadores Socioeconômicos (Fonte: IBGE / SEFIN Palmas)
- **População:** 313.349 habitantes
- **Renda Média:** R$ 3.250,50
- **Principal Fonte de Arrecadação Própria:** IPTU (62.5%) e ISSQN (27.0%)

*Documento emitido automaticamente pelo SITRIB - Projeto Integrador UFT.*
"""
    return {
        "formato": "markdown",
        "conteudo": markdown,
    }


# ==============================================================================
# 7. POST /api/v1/etl/sincronizar - Pipeline de Sincronização / Atualização
# ==============================================================================
@app.post("/api/v1/etl/sincronizar")
def sincronizar_dados_etl():
    """
    Executa a recarga da base de dados e recalculação das filas e índices de dívida ativa.
    """
    banco.carregar_dados_iniciais()
    return {
        "status": "sucesso",
        "mensagem": "Pipeline de ETL executado com sucesso. Índices de busca e Max-Heap sincronizados.",
        "registros_carregados": {
            "contribuintes": len(banco.contribuintes),
            "imoveis": len(banco.imoveis),
            "dividas": len(banco.dividas),
            "processos": len(banco.processos),
        },
    }


# Execução standalone via python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
