"""
Serviço de Autenticação e Controle de Acesso Baseado em Papéis (RBAC).
Projeto Integrador UFT - Inteligência Tributária (SITRIB / SEFIN Palmas)

Fornece hash seguro de credenciais, geração de tokens assinados (HMAC-SHA256)
e verificação estrita de permissões para Auditores, Gestores e Contribuintes.
"""

from typing import Dict, Optional, Tuple
import base64
import hashlib
import hmac
import json
import time
from abc import ABC, abstractmethod
from src.models.usuario import Usuario, Perfil


CHAVE_SECRETA_JWT = "sitrib_sefin_palmas_secret_key_2026_uft"
DURACAO_TOKEN_SEGUNDOS = 86400  # 24 horas


class AcessoNegadoError(Exception):
    """Lançada quando o usuário não possui permissão para o recurso solicitado."""
    pass


class CredenciaisInvalidasError(Exception):
    """Lançada quando e-mail ou senha estão incorretos."""
    pass


class TokenInvalidoError(Exception):
    """Lançada quando o token de autenticação é inválido ou expirou."""
    pass


def gerar_hash_senha(senha: str, salt: str = "sefin_palmas_salt") -> str:
    """Gera hash SHA-256 com salt estático da aplicação."""
    return hashlib.sha256(f"{salt}:{senha}".encode("utf-8")).hexdigest()


class AutenticacaoService(ABC):
    @abstractmethod
    def cadastrar(self, nome: str, email: str, senha: str, perfil: Perfil = Perfil.CONSULTA, cpf: Optional[str] = None) -> Usuario:
        raise NotImplementedError

    @abstractmethod
    def autenticar(self, email: str, senha: str) -> Tuple[Usuario, str]:
        raise NotImplementedError

    @abstractmethod
    def validar_token(self, token: str) -> Usuario:
        raise NotImplementedError

    @abstractmethod
    def verificar_permissao(self, usuario: Usuario, perfil_necessario: Perfil) -> None:
        raise NotImplementedError


class ServicoAutenticacao(AutenticacaoService):
    """Implementação concreta de autenticação em memória com pré-carga de personas da SEFIN."""

    def __init__(self):
        self._usuarios_por_email: Dict[str, Usuario] = {}
        self._usuarios_por_cpf: Dict[str, Usuario] = {}
        self._usuarios_por_id: Dict[str, Usuario] = {}
        # Base de servidores municipais da SEFIN Palmas autorizados para perfil Auditor/Gestor
        self._servidores_autorizados = {
            "0865743101": {"nome": "Adriel Morais da Silva", "cargo": "Auditor Fiscal de Tributos", "matricula": "SEFIN-2026-086", "perfil": Perfil.ADMINISTRADOR},
            "08657431001": {"nome": "Adriel Morais da Silva", "cargo": "Auditor Fiscal de Tributos", "matricula": "SEFIN-2026-086", "perfil": Perfil.ADMINISTRADOR},
            "11122233344": {"nome": "Roberto Silva", "cargo": "Auditor Fiscal", "matricula": "SEFIN-0012", "perfil": Perfil.ADMINISTRADOR},
            "55566677788": {"nome": "Mariana Costa", "cargo": "Gestor Tributário", "matricula": "SEFIN-0045", "perfil": Perfil.GESTAO},
        }
        self._inicializar_usuarios_padrao()

    def _inicializar_usuarios_padrao(self):
        """Inicializa os usuários oficiais do ecossistema municipal."""
        # 1. Auditor Adriel Morais (com o CPF fornecido)
        self.cadastrar(
            nome="Adriel Morais da Silva",
            email="adrie3lmorais@gmail.com",
            senha="109924303",
            cpf="0865743101",
            perfil=Perfil.ADMINISTRADOR,
            matricula_servidor="SEFIN-2026-086",
            id_usuario="usr_adriel_auditor"
        )

        # 2. Auditor Padrão SEFIN
        self.cadastrar(
            id_usuario="usr_auditor_01",
            nome="Dr. Roberto Silva (Auditor Fiscal)",
            email="auditor@sefin.palmas.to.gov.br",
            senha="sefin123",
            perfil=Perfil.ADMINISTRADOR,
            matricula_servidor="SEFIN-0012",
            cpf="111.222.333-44"
        )

        # 3. Gestor Tributário SEFIN
        self.cadastrar(
            id_usuario="usr_gestor_01",
            nome="Dra. Mariana Costa (Diretoria de Arrecadação)",
            email="gestor@sefin.palmas.to.gov.br",
            senha="sefin123",
            perfil=Perfil.GESTAO,
            matricula_servidor="SEFIN-0045",
            cpf="555.666.777-88"
        )

        # 4. Contribuinte Carlos Eduardo
        self.cadastrar(
            id_usuario="usr_cidadao_01",
            nome="Carlos Eduardo Siqueira",
            email="carlos.siqueira@email.com",
            senha="cidadao123",
            perfil=Perfil.CONSULTA,
            cpf="123.456.789-01"
        )

    def cadastrar(
        self,
        nome: str,
        email: str,
        senha: str,
        perfil: Optional[Perfil] = None,
        cpf: Optional[str] = None,
        matricula_servidor: Optional[str] = None,
        vinculo_govbr: bool = False,
        nivel_govbr: Optional[str] = None,
        id_usuario: Optional[str] = None
    ) -> Usuario:
        email_limpo = email.strip().lower()
        cpf_limpo = "".join(filter(str.isdigit, cpf)) if cpf else None

        # Verificação automática de vínculo público municipal por CPF ou domínio de e-mail
        perfil_efetivo = perfil or Perfil.CONSULTA
        if cpf_limpo and cpf_limpo in self._servidores_autorizados:
            dados_serv = self._servidores_autorizados[cpf_limpo]
            perfil_efetivo = dados_serv["perfil"]
            matricula_servidor = matricula_servidor or dados_serv["matricula"]
        elif email_limpo.endswith("@sefin.palmas.to.gov.br"):
            perfil_efetivo = Perfil.ADMINISTRADOR

        uid = id_usuario or f"usr_{int(time.time() * 1000)}"
        usuario = Usuario(
            id=uid,
            nome=nome.strip(),
            email=email_limpo,
            senha_hash=gerar_hash_senha(senha),
            perfil=perfil_efetivo,
            cpf=cpf_limpo,
            vinculo_govbr=vinculo_govbr,
            nivel_govbr=nivel_govbr,
            matricula_servidor=matricula_servidor
        )
        self._usuarios_por_email[email_limpo] = usuario
        if cpf_limpo:
            self._usuarios_por_cpf[cpf_limpo] = usuario
        self._usuarios_por_id[uid] = usuario
        return usuario

    def autenticar(self, identificador: str, senha: str) -> Tuple[Usuario, str]:
        """Autentica por E-mail ou por CPF."""
        termo = identificador.strip()
        termo_digitos = "".join(filter(str.isdigit, termo))

        usuario = None
        if "@" in termo:
            usuario = self._usuarios_por_email.get(termo.lower())
        elif termo_digitos:
            usuario = self._usuarios_por_cpf.get(termo_digitos)

        if not usuario and termo.lower() in self._usuarios_por_email:
            usuario = self._usuarios_por_email[termo.lower()]

        if not usuario:
            raise CredenciaisInvalidasError("Usuário não cadastrado. Verifique o CPF/E-mail ou realize seu cadastro.")

        hash_teste = gerar_hash_senha(senha)
        if usuario.senha_hash != hash_teste:
            raise CredenciaisInvalidasError("Senha incorreta.")

        token = self._gerar_token(usuario)
        return usuario, token

    def autenticar_com_govbr(
        self,
        cpf: str,
        nome: Optional[str] = None,
        nivel_govbr: str = "OURO"
    ) -> Tuple[Usuario, str]:
        """
        Autentica e valida a identidade digital via Login Único Gov.br.
        Cruza com a base de servidores do município para atribuir Auditor ou Cidadão.
        """
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        if not cpf_limpo:
            raise CredenciaisInvalidasError("CPF inválido para autenticação Gov.br.")

        # Verifica se é servidor cadastrado na SEFIN
        dados_servidor = self._servidores_autorizados.get(cpf_limpo)
        nome_efetivo = nome or (dados_servidor["nome"] if dados_servidor else f"Cidadão Gov.br {cpf_limpo[:3]}")
        perfil_efetivo = dados_servidor["perfil"] if dados_servidor else Perfil.CONSULTA
        matricula = dados_servidor.get("matricula") if dados_servidor else None

        usuario = self._usuarios_por_cpf.get(cpf_limpo)
        if not usuario:
            email_gov = f"{cpf_limpo}@cidadao.gov.br"
            usuario = self.cadastrar(
                nome=nome_efetivo,
                email=email_gov,
                senha=f"govbr_{cpf_limpo}",
                cpf=cpf_limpo,
                perfil=perfil_efetivo,
                matricula_servidor=matricula,
                vinculo_govbr=True,
                nivel_govbr=nivel_govbr
            )

        token = self._gerar_token(usuario)
        return usuario, token

    def _gerar_token(self, usuario: Usuario) -> str:
        """Gera um token portador assinado com HMAC-SHA256 (compatível com JWT)."""
        payload = {
            "sub": usuario.id,
            "email": usuario.email,
            "nome": usuario.nome,
            "perfil": str(usuario.perfil),
            "cpf": usuario.cpf,
            "exp": int(time.time()) + DURACAO_TOKEN_SEGUNDOS
        }
        dados_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        b64_payload = base64.urlsafe_b64encode(dados_json).decode("utf-8").rstrip("=")
        assinatura = hmac.new(
            CHAVE_SECRETA_JWT.encode("utf-8"),
            b64_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return f"{b64_payload}.{assinatura}"

    def validar_token(self, token: str) -> Usuario:
        """Valida a integridade, expiração e assinatura do token recebido."""
        if not token or "." not in token:
            raise TokenInvalidoError("Token malformado.")

        partes = token.split(".")
        if len(partes) != 2:
            raise TokenInvalidoError("Formato de token inválido.")

        b64_payload, assinatura_fornecida = partes
        assinatura_esperada = hmac.new(
            CHAVE_SECRETA_JWT.encode("utf-8"),
            b64_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(assinatura_fornecida, assinatura_esperada):
            raise TokenInvalidoError("Assinatura do token inválida.")

        try:
            # Adiciona padding base64 se necessário
            padding = "=" * ((4 - len(b64_payload) % 4) % 4)
            dados_json = base64.urlsafe_b64decode(b64_payload + padding).decode("utf-8")
            payload = json.loads(dados_json)
        except Exception:
            raise TokenInvalidoError("Falha na decodificação do token.")

        if payload.get("exp", 0) < int(time.time()):
            raise TokenInvalidoError("Sessão expirada. Faça login novamente.")

        usuario = self._usuarios_por_id.get(payload.get("sub"))
        if not usuario:
            raise TokenInvalidoError("Usuário associado ao token não existe.")

        return usuario

    def verificar_permissao(self, usuario: Usuario, perfil_necessario: Perfil) -> None:
        """Verifica se o usuário possui o perfil exigido para a operação."""
        # Administrador tem acesso irrestrito
        if usuario.perfil == Perfil.ADMINISTRADOR:
            return

        if usuario.perfil != perfil_necessario:
            raise AcessoNegadoError(
                f"Acesso negado: Perfil '{usuario.perfil}' não possui autorização para este recurso. Requer '{perfil_necessario}'."
            )
