"""
Gateway Principal API REST - SITRIB (Sistema Integrado de Gestão Tributária Municipal)
Projeto Integrador UFT - Ciência da Computação

Agrega os 4 Microsserviços independentes localizados em `src/apis/`:
  1. `src/apis/auth_api`                 -> Autenticação, Login CPF/Senha, RBAC e Gov.br
  2. `src/apis/tributario_api`           -> Contribuintes, Imóveis (CCI), Fila Max-Heap e Simulador
  3. `src/apis/transparencia_coleta_api` -> Coleta Real Prefeitura (182k+ registros), Auditoria e ETL
  4. `src/apis/ia_predicao_api`          -> Machine Learning (Random Forest) e Score de Recuperabilidade

Os links de deploy de cada pasta ficam centralizados em `src/repositories/endpoints_registry.py`.
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.apis.deps import (
    auth_service,
    banco,
    busca_service,
    eh_perfil_consulta,
    exigir_usuario,
    extrair_token_header,
    govbr_service,
    obter_usuario_logado,
    predicao_service,
)
from src.apis.auth_api.router import router as auth_router
from src.apis.tributario_api.router import router as tributario_router
from src.apis.transparencia_coleta_api.router import router as transparencia_router
from src.apis.ia_predicao_api.router import router as ia_router

app = FastAPI(
    title="SITRIB API Gateway - Gestão Tributária Municipal (PostgreSQL)",
    version="2.0.0",
    description=(
        "Gateway Oficial do SITRIB (Palmas/TO) orquestrando os microsserviços de Autenticação/Gov.br, "
        "Gestão Tributária/Max-Heap, Coleta Real da Prefeitura (182.808+ registros no PostgreSQL) e IA."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os roteadores de cada pasta de microsserviço
app.include_router(auth_router)
app.include_router(tributario_router)
app.include_router(transparencia_router)
app.include_router(ia_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
