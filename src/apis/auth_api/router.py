"""
Roteador do Microsserviço de Autenticação (`src/apis/auth_api/router.py`).
Pode rodar acoplado ao Gateway (`src/api.py`) ou como container isolado na porta 8001.
"""

import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, FastAPI
from pydantic import BaseModel, Field

from src.apis.deps import auth_service, banco, exigir_usuario, govbr_service
from src.models.usuario import Perfil, Usuario
from src.services.autenticacao_service import CredenciaisInvalidasError

router = APIRouter(tags=["1. Microsserviço de Autenticação & Gov.br"])


class LoginRequest(BaseModel):
    identificador: Optional[str] = Field(None, example="0865743101", description="CPF ou E-mail cadastrado")
    email: Optional[str] = Field(None, example="auditor@sefin.palmas.to.gov.br")
    senha: str = Field(..., example="109924303")


class CadastroRequest(BaseModel):
    nome: str = Field(..., example="Adriel Morais da Silva")
    email: str = Field(..., example="adrie3lmorais@gmail.com")
    senha: str = Field(..., example="109924303")
    cpf: str = Field(..., example="0865743101")
    telefone: Optional[str] = Field(None, example="(63) 98111-2030")


class GovBrLoginRequest(BaseModel):
    cpf: str = Field(..., example="0865743101", description="CPF do Cidadão ou Servidor Gov.br")
    nome: Optional[str] = Field(None, example="Adriel Morais da Silva")
    nivel_govbr: str = Field("OURO", example="OURO", description="Nível de confiabilidade: BRONZE, PRATA ou OURO")


class CpfIdentificacaoRequest(BaseModel):
    cpf: str = Field(..., example="123.456.789-01")


class GovBrCallbackRequest(BaseModel):
    code: str = Field(..., example="govbr_auth_code_123")
    state: Optional[str] = Field(None)


@router.post("/api/v1/auth/cadastrar")
def cadastrar_usuario(dados: CadastroRequest):
    try:
        usuario = auth_service.cadastrar(
            nome=dados.nome,
            email=dados.email,
            senha=dados.senha,
            cpf=dados.cpf,
        )
        _, token = auth_service.autenticar(dados.cpf or dados.email, dados.senha)
        return {
            "status": "sucesso",
            "mensagem": "Usuário cadastrado com sucesso no SITRIB!",
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": str(usuario.perfil),
                "cpf": usuario.cpf,
                "matricula_servidor": usuario.matricula_servidor,
            },
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.post("/api/v1/auth/govbr/autenticar")
def autenticar_govbr(dados: GovBrLoginRequest):
    try:
        usuario, token = auth_service.autenticar_com_govbr(
            cpf=dados.cpf,
            nome=dados.nome,
            nivel_govbr=dados.nivel_govbr,
        )
        tipo_vinculo = (
            "Servidor Público / Auditor Fiscal"
            if usuario.perfil == Perfil.ADMINISTRADOR
            else "Cidadão Contribuinte"
        )
        return {
            "status": "sucesso",
            "metodo": "Gov.br (Login Único)",
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": str(usuario.perfil),
                "cpf": usuario.cpf,
                "nivel_govbr": usuario.nivel_govbr,
                "vinculo_govbr": usuario.vinculo_govbr,
                "tipo_vinculo": tipo_vinculo,
                "matricula_servidor": usuario.matricula_servidor,
            },
            "mensagem": f"Autenticação Gov.br confirmada com sucesso! Vínculo: {tipo_vinculo}.",
        }
    except CredenciaisInvalidasError as err:
        raise HTTPException(status_code=401, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/api/v1/auth/govbr/url")
def obter_url_govbr():
    return {"url": govbr_service.gerar_url_autorizacao()}


@router.post("/api/v1/auth/govbr/callback")
def processar_callback_govbr(dados: GovBrCallbackRequest):
    token_resp = govbr_service.trocar_codigo_por_token(dados.code)
    access_token = token_resp.get("access_token", "")
    info_cidadao = govbr_service.obter_dados_cidadao(access_token)
    cpf_govbr = info_cidadao.get("cpf", "0865743101")
    usuario, token = auth_service.autenticar_com_govbr(
        cpf=cpf_govbr,
        nome=info_cidadao.get("name"),
        nivel_govbr=info_cidadao.get("nivel_confiabilidade", "OURO"),
    )
    return {
        "token": token,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": str(usuario.perfil),
            "cpf": usuario.cpf,
        },
        "mensagem": f"Autenticado com sucesso via Gov.br ({usuario.nome})!",
    }


@router.post("/api/v1/auth/identificar-cpf")
def identificar_cpf_dinamico(dados: CpfIdentificacaoRequest):
    doc_limpo = re.sub(r"\D", "", dados.cpf)
    if not doc_limpo:
        raise HTTPException(status_code=400, detail="CPF/CNPJ inválido ou vazio.")

    if doc_limpo in auth_service._servidores_autorizados:
        srv = auth_service._servidores_autorizados[doc_limpo]
        return {
            "tipo": "auditor",
            "nome": srv["nome"],
            "email": "auditor@sefin.palmas.to.gov.br",
            "perfil": str(srv["perfil"]),
            "precisa_senha": True,
            "mensagem": "Servidor público municipal identificado. Digite sua senha institucional.",
        }

    contribuinte = banco.buscar_contribuinte(dados.cpf)
    if contribuinte:
        usuario, token = auth_service.autenticar_com_govbr(
            cpf=contribuinte["cpf_cnpj"],
            nome=contribuinte["nome"],
        )
        return {
            "tipo": "contribuinte",
            "nome": contribuinte["nome"],
            "email": contribuinte.get("email"),
            "cpf": contribuinte["cpf_cnpj"],
            "perfil": "consulta",
            "precisa_senha": False,
            "token": token,
            "mensagem": f"Contribuinte localizado no Cadastro Imobiliário de Palmas: {contribuinte['nome']}",
        }

    return {
        "tipo": "nao_encontrado",
        "cpf": dados.cpf,
        "mensagem": "CPF/CNPJ não localizado na base ativa de Palmas.",
    }


@router.post("/api/v1/auth/login")
def login(dados: LoginRequest):
    identificador = dados.identificador or dados.email
    if not identificador:
        raise HTTPException(status_code=422, detail="Forneça o CPF ou E-mail para login.")

    try:
        usuario, token = auth_service.autenticar(identificador, dados.senha)
        return {
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": str(usuario.perfil),
                "cpf": usuario.cpf,
                "matricula_servidor": usuario.matricula_servidor,
                "nivel_govbr": usuario.nivel_govbr,
            },
            "mensagem": f"Bem-vindo(a), {usuario.nome}!",
        }
    except CredenciaisInvalidasError as err:
        raise HTTPException(status_code=401, detail=str(err))


@router.get("/api/v1/auth/me")
def obter_usuario_atual(usuario: Usuario = Depends(exigir_usuario)):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": str(usuario.perfil),
        "cpf": usuario.cpf,
        "matricula_servidor": usuario.matricula_servidor,
        "nivel_govbr": usuario.nivel_govbr,
    }


@router.get("/api/v1/auth/usuarios-teste")
def listar_usuarios_teste():
    raise HTTPException(
        status_code=403,
        detail="Acesso de homologação rápida desativado. Utilize o login oficial com CPF/Senha ou a autenticação Gov.br.",
    )


# App standalone caso esta pasta seja publicada separadamente
app = FastAPI(title="SITRIB - Microsserviço Auth API", version="1.2.0")
app.include_router(router)
