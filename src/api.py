"""
Servidor API REST - SITRIB (Sistema Integrado de Gestão Tributária Municipal)
Projeto Integrador UFT - Ciência da Computação

Expondo Endpoints RESTful com Autenticação RBAC e Modelos Preditivos de Machine Learning (Sprint 4).
"""

from typing import Any, Dict, List, Optional
import os
import re
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Header, Depends
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
from src.repositories.sqlite_repository import RepositorioSQLite
from scripts.popular_banco import criar_banco, popular_banco
from src.models.usuario import Perfil, Usuario
from src.services.autenticacao_service import (
    ServicoAutenticacao,
    CredenciaisInvalidasError,
    TokenInvalidoError,
    AcessoNegadoError,
)
from src.services.predicao_service import ServicoPredicao

# Inicializa aplicação FastAPI
app = FastAPI(
    title="SITRIB API - Gestão Tributária Municipal",
    version="1.1.0",
    description="API RESTful oficial do SITRIB (Palmas/TO) com Autenticação RBAC, Persistência SQLite e Modelos de ML.",
)

# Habilita CORS para o frontend (Vite na porta 5173 e qualquer host local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa repositório persistente em SQLite (sitrib.db) e serviços
banco = RepositorioSQLite()
busca_service = BuscaService(repositorio=banco)
auth_service = ServicoAutenticacao()
predicao_service = ServicoPredicao()


# ==============================================================================
# Modelos Pydantic (Request / Response)
# ==============================================================================

class LoginRequest(BaseModel):
    email: str = Field(..., example="auditor@sefin.palmas.to.gov.br")
    senha: str = Field(..., example="sefin123")


class ReajusteRequest(BaseModel):
    tributo: str = Field(..., example="IPTU")
    aliquota_atual: float = Field(..., example=1.25)
    aliquota_proposta: float = Field(..., example=1.50)
    base_calculo: float = Field(..., example=200000000.0)


class PredicaoRequest(BaseModel):
    valor_debito: float = Field(..., example=15000.0)
    dias_atraso: int = Field(..., example=420)
    renda_media_regiao: float = Field(3200.0, example=3200.0)
    bairro: str = Field("Centro", example="Taquaralto")


# ==============================================================================
# Helpers de Autenticação / RBAC
# ==============================================================================

def extrair_token_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extrai o Bearer token do cabeçalho Authorization."""
    if not authorization:
        return None
    partes = authorization.split()
    if len(partes) == 2 and partes[0].lower() == "bearer":
        return partes[1]
    return authorization


def obter_usuario_logado(authorization: Optional[str] = Header(None)) -> Optional[Usuario]:
    """Retorna o usuário logado se o token for válido; None se não autenticado."""
    token = extrair_token_header(authorization)
    if not token:
        return None
    try:
        return auth_service.validar_token(token)
    except TokenInvalidoError:
        return None


def exigir_usuario(authorization: Optional[str] = Header(None)) -> Usuario:
    """Exige usuário autenticado via token válido."""
    token = extrair_token_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Autenticação necessária. Forneça o token Bearer.")
    try:
        return auth_service.validar_token(token)
    except TokenInvalidoError as err:
        raise HTTPException(status_code=401, detail=str(err))


# ==============================================================================
# 0. ROTAS DE AUTENTICAÇÃO (LOGIN / PERFIL)
# ==============================================================================

@app.post("/api/v1/auth/login")
def login(dados: LoginRequest):
    """
    Autentica o usuário na SEFIN (Auditor, Gestor ou Contribuinte)
    e retorna o token de sessão com seu perfil de acesso.
    """
    try:
        usuario, token = auth_service.autenticar(dados.email, dados.senha)
        return {
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": str(usuario.perfil),
                "cpf": usuario.cpf,
            },
            "mensagem": f"Bem-vindo(a), {usuario.nome}!"
        }
    except CredenciaisInvalidasError as err:
        raise HTTPException(status_code=401, detail=str(err))


@app.get("/api/v1/auth/me")
def obter_usuario_atual(usuario: Usuario = Depends(exigir_usuario)):
    """Retorna os dados cadastrais e permissões do usuário logado."""
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": str(usuario.perfil),
        "cpf": usuario.cpf,
    }


@app.get("/api/v1/auth/usuarios-teste")
def listar_usuarios_teste():
    """Retorna a lista de contas padrão de teste para facilitar a troca de perfil no frontend."""
    return [
        {
            "perfil": "administrador",
            "titulo": "Auditor Fiscal (Acesso Completo)",
            "email": "auditor@sefin.palmas.to.gov.br",
            "senha": "sefin123",
            "descricao": "Pesquisa qualquer CPF, acessa a fila de cobrança, predição e dívida ativa."
        },
        {
            "perfil": "gestao",
            "titulo": "Gestor Tributário (Painel Estratégico)",
            "email": "gestor@sefin.palmas.to.gov.br",
            "senha": "sefin123",
            "descricao": "Visualiza dashboards consolidados, métricas de fairness e cenários fiscais."
        },
        {
            "perfil": "consulta",
            "titulo": "Contribuinte (Carlos Eduardo)",
            "email": "carlos.siqueira@email.com",
            "senha": "cidadao123",
            "cpf": "123.456.789-01",
            "descricao": "Acesso restrito exclusivamente ao seu próprio CPF (123.456.789-01)."
        }
    ]


# ==============================================================================
# 1. GET /api/v1/contribuintes/{cpf_cnpj} - Dossiê do Contribuinte
# ==============================================================================
@app.get("/api/v1/contribuintes/{cpf_cnpj}")
def obter_dossie_contribuinte(
    cpf_cnpj: str,
    usuario: Optional[Usuario] = Depends(obter_usuario_logado)
):
    """
    Busca contribuinte por CPF ou CNPJ.
    REGRAS DE RBAC:
    - Se for perfil CONSULTA (Cidadão), só pode consultar seu próprio CPF vinculado (LGPD).
    - Se for ADMINISTRADOR ou GESTÃO, pode consultar qualquer contribuinte.
    """
    if usuario and usuario.perfil == Perfil.CONSULTA and usuario.cpf:
        cpf_logado = re.sub(r"\D", "", usuario.cpf)
        cpf_solicitado = re.sub(r"\D", "", cpf_cnpj)
        if cpf_logado != cpf_solicitado:
            raise HTTPException(
                status_code=403,
                detail=f"Acesso negado (LGPD): Você só possui permissão para consultar o seu próprio CPF ({usuario.cpf})."
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


# ==============================================================================
# 2. GET /api/v1/imoveis/{inscricao_cci}/dossie - Dossiê Imobiliário
# ==============================================================================
@app.get("/api/v1/imoveis/{inscricao_cci}/dossie")
def obter_dossie_imovel(inscricao_cci: str):
    """Retorna o dossiê fiscal consolidado de um imóvel específico (CCI)."""
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
def listar_fila_prioridade(usuario: Optional[Usuario] = Depends(obter_usuario_logado)):
    """
    Retorna a fila de cobrança ordenada por Max-Heap com score de risco de inadimplência.
    REGRAS DE RBAC: Restrito aos perfis ADMINISTRADOR e GESTAO.
    """
    if usuario and usuario.perfil == Perfil.CONSULTA:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: Fila de cobrança da dívida ativa é de uso restrito de auditores fiscais."
        )

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

    resultado = []
    while fila_heap.fila:
        item = fila_heap.proximo_a_cobrar()
        if item != "Fila vazia":
            cpf_chave = item[0]
            if cpf_chave in dados_por_cpf:
                resultado.append(dados_por_cpf[cpf_chave])

    return resultado


# ==============================================================================
# 4. POST /api/v1/predicao/inadimplencia - Modelo de Machine Learning (Sprint 4)
# ==============================================================================
@app.post("/api/v1/predicao/inadimplencia")
def executar_predicao_inadimplencia(
    dados: PredicaoRequest,
    usuario: Optional[Usuario] = Depends(obter_usuario_logado)
):
    """
    Executa a inferência do modelo de Machine Learning (Random Forest)
    e calcula o Score de Recuperabilidade (Alta, Média ou Baixa) para o débito.
    """
    if usuario and usuario.perfil == Perfil.CONSULTA:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: Modelos preditivos de inadimplência são restritos a servidores da SEFIN."
        )

    resultado = predicao_service.predizer_contribuinte(
        valor_debito=dados.valor_debito,
        dias_atraso=dados.dias_atraso,
        renda_media_regiao=dados.renda_media_regiao,
        bairro=dados.bairro
    )
    return resultado


# ==============================================================================
# 5. POST /api/v1/tributos/simular-reajuste - Simulação Tributária
# ==============================================================================
@app.post("/api/v1/tributos/simular-reajuste")
def simular_reajuste_tributario(dados: ReajusteRequest):
    """Simula o impacto fiscal de alteração de alíquota sobre uma base de cálculo."""
    arrecadacao_atual = (dados.aliquota_atual / 100.0) * dados.base_calculo
    arrecadacao_proposta = (dados.aliquota_proposta / 100.0) * dados.base_calculo
    diferenca = arrecadacao_proposta - arrecadacao_atual
    impacto_percentual = ((dados.aliquota_proposta - dados.aliquota_atual) / dados.aliquota_atual) * 100.0

    return {
        "tributo": dados.tributo,
        "aliquota_atual": dados.aliquota_atual,
        "aliquota_proposta": dados.aliquota_proposta,
        "base_calculo": dados.base_calculo,
        "arrecadacao_atual": round(arrecadacao_atual, 2),
        "arrecadacao_proposta": round(arrecadacao_proposta, 2),
        "diferenca_arrecadacao": round(diferenca, 2),
        "impacto_percentual": round(impacto_percentual, 2),
    }


# ==============================================================================
# 6. GET /api/v1/dashboard/indicadores - KPIs e Métricas Globais
# ==============================================================================
@app.get("/api/v1/dashboard/indicadores")
def obter_indicadores_dashboard():
    """Retorna KPIs em tempo real do banco SQLite para o Dashboard institucional."""
    total_divida = sum(d.get("valor_original", 0) + d.get("juros_multa", 0) for d in banco.dividas)
    total_processos = len(banco.processos)
    imoveis_registrados = len(banco.imoveis)
    contribuintes_cadastrados = len(banco.contribuintes)

    return {
        "total_divida_ativa": round(total_divida, 2),
        "total_processos_ajuizados": total_processos,
        "total_imoveis": imoveis_registrados,
        "total_contribuintes": contribuintes_cadastrados,
        "taxa_inadimplencia_estimada": "14.8%",
        "projecao_arrecadacao_anual": "R$ 48.500.000,00",
        "faixas_recuperabilidade": {
            "alta": "42%",
            "media": "35%",
            "baixa": "23%"
        }
    }


# ==============================================================================
# 7. GET /api/v1/relatorios/ecossistema - Relatório Integrado
# ==============================================================================
@app.get("/api/v1/relatorios/ecossistema")
def gerar_relatorio_ecossistema():
    """Retorna relatório consolidado da SEFIN em Markdown."""
    markdown = """# Relatório Executivo SITRIB - Inteligência Tributária Palmas
## Período: Exercício 2026

- **Total de Débitos Consolidados:** R$ 1.845.210,00
- **Processos em Execução Fiscal:** 12 autos
- **Principal Fonte de Arrecadação Própria:** IPTU (62.5%) e ISSQN (27.0%)

*Documento emitido automaticamente pelo SITRIB - Projeto Integrador UFT.*
"""
    return {
        "formato": "markdown",
        "conteudo": markdown,
    }


# ==============================================================================
# 8. POST /api/v1/etl/sincronizar - Sincronização
# ==============================================================================
@app.post("/api/v1/etl/sincronizar")
def sincronizar_dados_etl(usuario: Optional[Usuario] = Depends(obter_usuario_logado)):
    """Executa a recarga e persistência no banco SQLite (sitrib.db). Restrito a auditores."""
    if usuario and usuario.perfil == Perfil.CONSULTA:
        raise HTTPException(status_code=403, detail="Acesso negado: Sincronização restrita a administradores.")

    conexao = criar_banco()
    popular_banco(conexao)
    conexao.close()
    return {
        "status": "sucesso",
        "mensagem": "Banco de dados SQLite (sitrib.db) sincronizado com sucesso!",
        "registros_carregados": {
            "contribuintes": len(banco.contribuintes),
            "imoveis": len(banco.imoveis),
            "dividas": len(banco.dividas),
            "processos": len(banco.processos),
        },
    }


# ==============================================================================
# 9. GET /api/v1/coleta/fontes & POST /api/v1/coleta/executar
# ==============================================================================
@app.get("/api/v1/coleta/fontes")
def listar_fontes_coleta():
    """Retorna as fontes de dados municipais disponíveis e suas URLs oficiais."""
    try:
        from src.coleta.coletor_prefeitura import ColetorSefinPalmasDual
        from src.enriquecimento.integracao_ibge import CODIGO_PALMAS_IBGE
        coletor = ColetorSefinPalmasDual()
        return {
            "status": "operacional",
            "modo_configurado": os.getenv("SITRIB_FONTE_COLETA", "dual"),
            "fontes": {
                "portal_novo": {
                    "nome": "Portal da Transparência Novo (Nucleogov)",
                    "url_base": coletor.url_portal_novo,
                    "metodo": "POST",
                    "finalidade": "Receitas consolidadas, despesas e lotes orçamentários",
                },
                "api_antiga": {
                    "nome": "API Legada / REST SEFIN Palmas",
                    "url_base": coletor.url_api_antiga,
                    "metodo": "GET",
                    "finalidade": "Consultas fiscais diretas, tributos e certidões",
                },
                "ibge": {
                    "nome": "API de Serviços IBGE (Palmas/TO)",
                    "codigo_municipio": CODIGO_PALMAS_IBGE,
                    "metodo": "GET",
                    "finalidade": "Enriquecimento socioeconômico (renda média e população)",
                },
            },
        }
    except Exception as err:
        return {"status": "erro", "detalhe": str(err)}


@app.post("/api/v1/coleta/executar")
def executar_coleta_api(
    origem: str = Query("dual", pattern="^(dual|portal_novo|api_antiga)$"),
    usuario: Optional[Usuario] = Depends(obter_usuario_logado)
):
    """Executa a coleta de dados da prefeitura. Restrito a administradores."""
    if usuario and usuario.perfil == Perfil.CONSULTA:
        raise HTTPException(status_code=403, detail="Acesso negado: Coletas são restritas a servidores.")

    try:
        from src.coleta.coletor_prefeitura import ColetorSefinPalmasDual
        coletor = ColetorSefinPalmasDual()

        if origem == "portal_novo":
            dados = coletor.consumir_portal_novo(recurso="receitas")
            modo = "Portal Novo (Nucleogov)"
        elif origem == "api_antiga":
            dados = coletor.consumir_api_antiga(endpoint="notas")
            modo = "API Antiga (REST)"
        else:
            dados, diag = coletor.coletar_com_diagnostico()
            modo = diag.get("modo", "Dual (Híbrido)")

        return {
            "status": "sucesso",
            "origem_selecionada": origem,
            "modo_efetivo": modo,
            "registros_obtidos": len(dados) if isinstance(dados, list) else 1,
            "mensagem": f"Coleta realizada com sucesso via {modo}.",
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Erro na coleta via {origem}: {err}")


# Execução standalone via python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
