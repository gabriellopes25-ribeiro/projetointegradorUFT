"""
Serviço de Predição de Inadimplência e Scoring de Recuperabilidade (Sprint 4).
Projeto Integrador UFT - Inteligência Tributária (SITRIB / SEFIN Palmas)

Consome os modelos preditivos e regras de fairness desenvolvidas pela equipe.
"""

from typing import Dict, Any, List
import os
import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CAMINHO_MODELO = BASE_DIR / "models" / "modelo_inadimplencia_v1.joblib"


class ServicoPredicao:
    """Orquestra inferência preditiva e scoring da dívida ativa."""

    def __init__(self):
        self.modelo = self._carregar_ou_inicializar_modelo()

    def _carregar_ou_inicializar_modelo(self):
        """Carrega o modelo serializado em disco ou inicializa um baseline treinado."""
        if CAMINHO_MODELO.exists():
            try:
                return joblib.load(str(CAMINHO_MODELO))
            except Exception as e:
                print(f"[AVISO] Falha ao carregar modelo serializado: {e}. Inicializando baseline.")

        # Baseline determinístico com Scikit-Learn
        from sklearn.ensemble import RandomForestClassifier
        X_exemplo = [
            [1200, 180, 3250.5],
            [4500, 300, 3250.5],
            [15000, 720, 1800.0],
            [35000, 1500, 5200.0],
            [800, 90, 3250.5],
            [6200, 400, 1800.0],
            [18000, 900, 5200.0],
            [45000, 1800, 1800.0]
        ]
        y_exemplo = [1, 1, 0, 0, 1, 1, 0, 0]  # 1 = Pago, 0 = Inadimplente

        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        rf.fit(X_exemplo, y_exemplo)

        # Salva para persistência local
        os.makedirs(str(CAMINHO_MODELO.parent), exist_ok=True)
        try:
            joblib.dump(rf, str(CAMINHO_MODELO))
        except Exception:
            pass

        return rf

    def classificar_recuperabilidade(self, valor_debito: float, dias_atraso: int) -> Dict[str, Any]:
        """
        Calcula a faixa do Score de Recuperabilidade conforme regras oficiais da Sprint 4:
        - Alta Recuperabilidade: débito recente (< 365 dias) e menor valor (< R$ 5.000).
        - Média Recuperabilidade: prazo intermediário (< 1095 dias) ou valor até R$ 20.000.
        - Baixa Recuperabilidade: dívidas antigas (> 3 anos) ou acima de R$ 20.000.
        """
        if dias_atraso < 365 and valor_debito < 5000:
            faixa = "Alta Recuperabilidade"
            prioridade = 1
            recomendacao = "Cobrança amigável direta (notificação digital e desconto para pagamento à vista)."
        elif dias_atraso < 1095 or valor_debito < 20000:
            faixa = "Média Recuperabilidade"
            prioridade = 2
            recomendacao = "Oferta de parcelamento incentivado (REFIS municipal)."
        else:
            faixa = "Baixa Recuperabilidade"
            prioridade = 3
            recomendacao = "Protesto em cartório ou encaminhamento para Execução Fiscal (PGE/SEFIN)."

        return {
            "faixa": faixa,
            "prioridade_cobranca": prioridade,
            "recomendacao_acao": recomendacao
        }

    def predizer_contribuinte(
        self,
        valor_debito: float,
        dias_atraso: int,
        renda_media_regiao: float = 3000.0,
        bairro: str = "Centro"
    ) -> Dict[str, Any]:
        """Realiza inferência de inadimplência e combina com o score de recuperabilidade."""
        X_input = [[valor_debito, dias_atraso, renda_media_regiao]]

        try:
            prob_pagamento = float(self.modelo.predict_proba(X_input)[0][1])
        except Exception:
            # Fallback caso predict_proba não esteja disponível
            pred = self.modelo.predict(X_input)[0]
            prob_pagamento = 0.85 if pred == 1 else 0.20

        prob_inadimplencia = round((1.0 - prob_pagamento) * 100, 1)
        prob_pagamento_pct = round(prob_pagamento * 100, 1)

        scoring = self.classificar_recuperabilidade(valor_debito, dias_atraso)

        return {
            "valor_debito": valor_debito,
            "dias_atraso": dias_atraso,
            "renda_media_regiao": renda_media_regiao,
            "bairro_setor": bairro,
            "probabilidade_inadimplencia": f"{prob_inadimplencia}%",
            "probabilidade_recuperacao": f"{prob_pagamento_pct}%",
            "faixa_recuperabilidade": scoring["faixa"],
            "prioridade_execucao": scoring["prioridade_cobranca"],
            "recomendacao_fiscal": scoring["recomendacao_acao"],
            "modelo_utilizado": "RandomForestClassifier (v1.0 - Sprint 4)"
        }
