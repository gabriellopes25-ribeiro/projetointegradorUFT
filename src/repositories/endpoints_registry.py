"""
Catálogo Central de Endpoints e Microsserviços (Service Discovery & Repository Links)
Projeto Integrador UFT - SITRIB (SEFIN Palmas)

COMO FUNCIONA:
A arquitetura do SITRIB divide as APIs em pastas independentes dentro de `src/apis/`:
  1. `src/apis/auth_api`                 -> Autenticação, Login CPF/Senha, RBAC e Gov.br
  2. `src/apis/tributario_api`           -> Contribuintes, Imóveis (CCI), Fila Max-Heap e Simulador
  3. `src/apis/transparencia_coleta_api` -> Coleta Real Prefeitura (182k+ registros), Auditoria e ETL
  4. `src/apis/ia_predicao_api`          -> Machine Learning (Random Forest), Scoring e Fairness

QUANDO COLOCAR CADA PASTA NO AR (DEPLOY SEPARADO):
Basta substituir os links abaixo (ou definir as variáveis de ambiente no seu servidor/container)
com a URL pública onde cada pasta foi hospedada (ex: Railway, Render, Fly.io, AWS).
"""

import os
from typing import Dict, Any

# URL Base do Gateway (usada quando todos os módulos rodam juntos no mesmo container/host)
GATEWAY_BASE_URL = os.getenv("SITRIB_GATEWAY_URL", "http://localhost:8000")

# ===================================================================================
# REGISTRO DE LINKS DE CADA PASTA DE API (MICROSSERVIÇOS INTERNOS)
# ===================================================================================
MICROSERVICES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "auth_api": {
        "nome": "Microsserviço de Autenticação, RBAC e Gov.br",
        "pasta": "src/apis/auth_api",
        "prefixo_rota": "/api/v1/auth",
        "url_producao": os.getenv("SITRIB_AUTH_API_URL", f"{GATEWAY_BASE_URL}/api/v1/auth"),
        "porta_container": int(os.getenv("PORT_AUTH_API", "8001")),
        "status": "ATIVO",
    },
    "tributario_api": {
        "nome": "Microsserviço Tributário, Dossiê CCI/CPF, Max-Heap e Simulador",
        "pasta": "src/apis/tributario_api",
        "prefixo_rota": "/api/v1",
        "url_producao": os.getenv("SITRIB_TRIBUTARIO_API_URL", f"{GATEWAY_BASE_URL}/api/v1"),
        "porta_container": int(os.getenv("PORT_TRIBUTARIO_API", "8002")),
        "status": "ATIVO",
    },
    "transparencia_coleta_api": {
        "nome": "Microsserviço de Coleta da Prefeitura (182k+ Registros), Auditoria e ETL",
        "pasta": "src/apis/transparencia_coleta_api",
        "prefixo_rota": "/api/v1",
        "url_producao": os.getenv("SITRIB_TRANSPARENCIA_API_URL", f"{GATEWAY_BASE_URL}/api/v1"),
        "porta_container": int(os.getenv("PORT_TRANSPARENCIA_API", "8003")),
        "status": "ATIVO",
    },
    "ia_predicao_api": {
        "nome": "Microsserviço de Inteligência Artificial e Score de Recuperabilidade",
        "pasta": "src/apis/ia_predicao_api",
        "prefixo_rota": "/api/v1",
        "url_producao": os.getenv("SITRIB_IA_PREDICAO_API_URL", f"{GATEWAY_BASE_URL}/api/v1"),
        "porta_container": int(os.getenv("PORT_IA_PREDICAO_API", "8004")),
        "status": "ATIVO",
    },
}

# ===================================================================================
# REGISTRO DAS APIS EXTERNAS OFICIAIS (PREFEITURA DE PALMAS, IBGE E GOV.BR)
# ===================================================================================
EXTERNAL_APIS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "prefeitura_portal_novo": {
        "nome": "Portal Novo da Transparência de Palmas (NUCLEOGOV)",
        "base_url": os.getenv("PALMAS_PORTAL_NOVO_BASE", "https://acessoainformacao.palmas.to.gov.br"),
        "api_url": os.getenv("PALMAS_PORTAL_NOVO_API", "https://acessoainformacao.palmas.to.gov.br/api"),
        "protocolo": "HTTPS (POST x-www-form-urlencoded com cookie de sessão)",
        "modulos": {
            "receitas": {
                "acao": "sgreceitas/listar",
                "detalhes_acao": "sgreceitas/detalhes",
                "referer_path": "/cidadao/transparencia/sgreceitas",
                "estimativa_registros": 182808,
            },
            "contratos": {
                "acao": "sgcontratos/listar",
                "referer_path": "/cidadao/transparencia/sgcontratos",
                "estimativa_registros": 8897,
            },
            "despesas": {
                "acao": "sgdespesas/listar",
                "referer_path": "/cidadao/transparencia/sgdespesas",
                "estimativa_registros": 3412,
            },
            "licitacoes": {
                "acao": "sglicitacoes/listar",
                "referer_path": "/cidadao/transparencia/sglicitacoes",
                "estimativa_registros": 2161,
            },
            "servidores": {
                "acao": "sgservidores/listar",
                "referer_path": "/cidadao/transparencia/sgservidores",
                "estimativa_registros": 16116,
            },
        },
    },
    "prefeitura_api_antiga": {
        "nome": "API Antiga de Integração da Prefeitura de Palmas (Histórico 2001-2021)",
        "base_url": os.getenv("PALMAS_API_ANTIGA_BASE", "http://integracao.palmas.to.gov.br/apirest"),
        "doc_url": "http://portaldatransparencia.palmas.to.gov.br/webservice/",
        "protocolo": "HTTP/HTTPS (Django REST Framework - GET com verify=False por cadeia SSL incompleta)",
        "endpoints": {
            "gastos-diretos": {
                "url": "http://integracao.palmas.to.gov.br/apirest/gastos-diretos/",
                "registros_congelados": 344323,
                "por_pagina": 100,
                "filtros_validos": ["inicio", "fim", "ano", "fornecedor", "cpf_cnpj", "unidade", "natureza", "empenho"],
            },
            "folha-pagamento": {
                "url": "http://integracao.palmas.to.gov.br/apirest/folha-pagamento/",
                "registros_congelados": 489378,
                "por_pagina": 400,
                "filtros_validos": ["ano", "mes"],
            },
            "arrecadacao": {
                "url": "http://integracao.palmas.to.gov.br/apirest/arrecadacao/",
                "registros_congelados": 3542,
                "por_pagina": 100,
                "filtros_validos": ["ano", "mes"],
            },
        },
    },
    "ibge_palmas": {
        "nome": "API de Serviços do IBGE - Município de Palmas/TO (1721000)",
        "url_localidades": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/1721000",
        "codigo_ibge": "1721000",
    },
}


def obter_url_microsservico(nome_servico: str) -> str:
    """Retorna a URL configurada para a pasta do microsserviço solicitado."""
    servico = MICROSERVICES_REGISTRY.get(nome_servico)
    if not servico:
        return GATEWAY_BASE_URL
    return servico["url_producao"]


def obter_catalogo_completo() -> Dict[str, Any]:
    """Retorna o mapa completo de microsserviços internos e APIs externas."""
    return {
        "gateway_url": GATEWAY_BASE_URL,
        "microsservicos": MICROSERVICES_REGISTRY,
        "apis_externas": EXTERNAL_APIS_REGISTRY,
    }
