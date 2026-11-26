"""
Dependências e Instâncias Compartilhadas pelos Microsserviços (src/apis/*).
Conecta todos os roteadores ao Repositório Oficial PostgreSQL.
"""

from typing import Any, Optional
from fastapi import Header, HTTPException

from src.repositories.postgres_repository import RepositorioPostgreSQL
from src.services.busca_service import BuscaService
from src.services.autenticacao_service import (
    ServicoAutenticacao,
    TokenInvalidoError,
)
from src.services.predicao_service import ServicoPredicao
from src.services.govbr_service import GovBrOAuthService
from src.models.usuario import Perfil, Usuario

banco = RepositorioPostgreSQL()
busca_service = BuscaService(repositorio=banco)
auth_service = ServicoAutenticacao()
predicao_service = ServicoPredicao()
govbr_service = GovBrOAuthService()


def extrair_token_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization:
        return None
    partes = authorization.split()
    if len(partes) == 2 and partes[0].lower() == "bearer":
        return partes[1]
    return authorization


def obter_usuario_logado(authorization: Optional[str] = Header(None)) -> Optional[Usuario]:
    token = extrair_token_header(authorization)
    if not token:
        return None
    try:
        return auth_service.validar_token(token)
    except TokenInvalidoError:
        return None


def exigir_usuario(authorization: Optional[str] = Header(None)) -> Usuario:
    token = extrair_token_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Autenticação necessária. Forneça o token Bearer.")
    try:
        return auth_service.validar_token(token)
    except TokenInvalidoError as err:
        raise HTTPException(status_code=401, detail=str(err))


def eh_perfil_consulta(usuario: Any) -> bool:
    return isinstance(usuario, Usuario) and usuario.perfil == Perfil.CONSULTA
