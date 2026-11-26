"""
Serviço de Inteligência Artificial Generativa - Gemini (SITRIB Palmas).
Orquestra chamadas à API oficial do Google Gemini com Thinking e Self-Reflection.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

logger = logging.getLogger("sitrib.gemini")


def _obter_api_key_padrao() -> str:
    chave = os.getenv("GEMINI_API_KEY")
    if chave:
        return chave
    caminhos = [".env", "/app/.env", os.path.join(os.path.dirname(__file__), "../../.env")]
    for p in caminhos:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for linha in f:
                        linha = linha.strip()
                        if linha.startswith("GEMINI_API_KEY=") and not linha.startswith("#"):
                            return linha.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return ""


GEMINI_API_KEY = _obter_api_key_padrao()
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
]


class ServicoGemini:
    """Gerencia a comunicação com a API do Google Gemini com prompt auditável para o SITRIB."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY

    def gerar_resposta_assistente_fiscal(
        self,
        mensagem_usuario: str,
        contexto_tributario: Optional[Dict[str, Any]] = None,
        historico: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Executa a geração com Gemini, aplicando pensamento prévio e auto-revisão
        para garantir que a resposta seja sob medida para a pergunta do usuário.
        """
        contexto = contexto_tributario or {}
        obs = contexto.get("observacao_fatos", "")
        rev = contexto.get("revisao_critica", "")
        detalhes_contexto = ""
        if obs:
            detalhes_contexto += f"\nOBSERVAÇÕES REAIS DO BANCO DE DADOS (PostgreSQL):\n{obs}\n"
        if rev:
            detalhes_contexto += f"\nSALVAGUARDAS ÉTICAS E JURÍDICAS APLICÁVEIS:\n{rev}\n"
        
        prompt_sistema = f"""Você é o Assistente Fiscal Oficial de Inteligência Artificial do SITRIB (Sistema Fazendário da Prefeitura de Palmas/TO).
Você está prestando consultoria em tempo real para os Auditores Fiscais e Gestores da Secretaria de Finanças (SEFIN).

DADOS REAIS E VERIFICADOS DO MUNICÍPIO DE PALMAS:
- Base Contábil: 182.808 lançamentos auditados do IPTU, ISSQN e taxas municipais.
- Dívida Ativa Atual no PostgreSQL: R$ 1.084.481,25 (21 contribuintes cadastrados no piloto, 7 execuções fiscais ajuizadas).
- Arrecadação Oficial Auditada: R$ 1.810.016.926,07.
- População e Renda IBGE Palmas: 313.349 habitantes, com Renda Média Domiciliar de R$ 3.250,50/mês.
- Índices Fiscais 2026: UFIP de R$ 4,48 e IPCA referencial de 4.62% ao ano.
- Jardins Aureny (I a IV), Taquari e Região Sul: Imóveis populares (R$ 95.000 a R$ 210.000), renda familiar entre R$ 1.980 e R$ 2.350/mês. Dificuldade máxima de pagamento (vulnerabilidade crônica / risco de subsistência). Uma execução judicial custa R$ 4.500 ao erário, superando o próprio débito de IPTU. Diretriz recomendada: REFIS Social com até 95% de anistia de juros/multas e parcelas de até 10% da renda (R$ 198/mês).
- Plano Diretor (Sul e Norte) e Orla 14 Graciosa: Imóveis de alto padrão e corporativos (R$ 2.500.000 a R$ 4.500.000+), concentrando mais de 75% do montante da dívida ativa municipal. Renda média acima de R$ 4.850 a R$ 7.200+/mês. A dívida representa menos de 2% a 3% do valor venal. Inadimplência estratégica de caixa. Diretriz recomendada: Notificação firme para conciliação (entrada de 20% + até 12x), com protesto imediato de CDA em caso de recusa.
- Taquaralto e Expansão Sul: Imóveis mistos/comércio local (R$ 180.000 a R$ 450.000), renda de R$ 2.450 a R$ 2.900/mês. Dificuldade transitória. Diretriz: Acordo Digital em até 36x com 75% de desconto de encargos sem judicialização.

INSTRUÇÕES RIGOROSAS DE RESPOSTA:
1. Responda DIRETAMENTE e COM PRECISÃO ao que o auditor acabou de perguntar. Nunca use textos pré-fabricados ou respostas evasivas.
2. Seja fluente, analítico, persuasivo e empático com o cenário fiscal e social de Palmas.
3. NÃO gere tabelas cruas com barras de markdown ('| :--- |') na resposta principal; use parágrafos executivos bem estruturados, tópicos claros com marcadores e destaques em negrito.
4. Auto-revisão: Pense criticamente antes de emitir a resposta, verificando se ela reflete o princípio da capacidade contributiva (Art. 145 §1º CF) e o não-confisco (Art. 150 IV CF).
"""

        prompt_completo = f"""{prompt_sistema}
{detalhes_contexto}
PERGUNTA FEITA PELO AUDITOR FISCAL / GESTOR:
"{mensagem_usuario}"

PENSE E ELABORE O PARECER FISCAL GERATIVO DIRECIONADO PARA ESTA PERGUNTA:"""

        # Tenta os modelos compatíveis
        for modelo in GEMINI_MODELS:
            try:
                resposta_texto = self._chamar_api_gemini(modelo, prompt_completo)
                if resposta_texto:
                    return {
                        "sucesso": True,
                        "modelo_usado": modelo,
                        "resposta": resposta_texto,
                    }
            except Exception as e:
                logger.warning(f"Tentativa com {modelo} falhou: {e}")
                continue

        return {
            "sucesso": False,
            "modelo_usado": "fallback_local",
            "resposta": None,
        }

    def _chamar_api_gemini(self, modelo: str, prompt: str) -> str:
        """Executa a requisição HTTP POST para a API do Gemini."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.9,
                "maxOutputTokens": 2048,
            },
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=18) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()

        raise RuntimeError(f"Resposta vazia da API do Gemini ({modelo})")
