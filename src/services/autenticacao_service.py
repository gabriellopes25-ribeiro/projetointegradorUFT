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
        self._usuarios_por_id: Dict[str, Usuario] = {}
        self._inicializar_usuarios_padrao()

    def _inicializar_usuarios_padrao(self):
        """Inicializa as 3 personas oficiais do ecossistema municipal."""
        # 1. Auditor Fiscal (SEFIN) - Acesso pleno à cobrança ativa e predições
        self.cadastrar(
            id_usuario="usr_auditor_01",
            nome="Dr. Roberto Silva (Auditor Fiscal)",
            email="auditor@sefin.palmas.to.gov.br",
            senha="sefin123",
            perfil=Perfil.ADMINISTRADOR,
            cpf=None
        )

        # 2. Gestor Tributário (SEFIN) - Dashboard, métricas de fairness e cenários
        self.cadastrar(
            id_usuario="usr_gestor_01",
            nome="Dra. Mariana Costa (Diretoria de Arrecadação)",
            email="gestor@sefin.palmas.to.gov.br",
            senha="sefin123",
            perfil=Perfil.GESTAO,
            cpf=None
        )

        # 3. Contribuinte 1 (Cidadão Carlos Eduardo) - Apenas seus próprios débitos
        self.cadastrar(
            id_usuario="usr_cidadao_01",
            nome="Carlos Eduardo Siqueira",
            email="carlos.siqueira@email.com",
            senha="cidadao123",
            perfil=Perfil.CONSULTA,
            cpf="123.456.789-01"
        )

        # 4. Contribuinte 2 (Cidadã Maria Auxiliadora) - Apenas seus próprios débitos
        self.cadastrar(
            id_usuario="usr_cidadao_02",
            nome="Maria Auxiliadora Fernandes",
            email="maria.fernandes@email.com",
            senha="cidadao123",
            perfil=Perfil.CONSULTA,
            cpf="987.654.321-09"
        )

    def cadastrar(
        self,
        nome: str,
        email: str,
        senha: str,
        perfil: Perfil = Perfil.CONSULTA,
        cpf: Optional[str] = None,
        id_usuario: Optional[str] = None
    ) -> Usuario:
        email_limpo = email.strip().lower()
        if email_limpo in self._usuarios_por_email:
            return self._usuarios_por_email[email_limpo]

        uid = id_usuario or f"usr_{int(time.time() * 1000)}"
        usuario = Usuario(
            id=uid,
            nome=nome.strip(),
            email=email_limpo,
            senha_hash=gerar_hash_senha(senha),
            perfil=perfil,
            cpf=cpf
        )
        self._usuarios_por_email[email_limpo] = usuario
        self._usuarios_por_id[uid] = usuario
        return usuario

    def autenticar(self, email: str, senha: str) -> Tuple[Usuario, str]:
        email_limpo = email.strip().lower()
        usuario = self._usuarios_por_email.get(email_limpo)
        if not usuario:
            raise CredenciaisInvalidasError("E-mail não cadastrado no sistema tributário.")

        hash_teste = gerar_hash_senha(senha)
        if usuario.senha_hash != hash_teste:
            raise CredenciaisInvalidasError("Senha incorreta.")

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
