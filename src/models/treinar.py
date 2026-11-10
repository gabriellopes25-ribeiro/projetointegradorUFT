"""
Sprint 4 - SITRIB (UFT / SEFIN Palmas)
Módulo de Scoring de Recuperabilidade, Fairness e Serialização do Modelo.
Desenvolvedora: Rayssa de Oliveira
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


# --- 1. NOTA ÉTICA DE DADOS SINTÉTICOS / CONTINGÊNCIA ---
# NOTA ÉTICA: Os dados individuais e agregados utilizados nesta etapa de treinamento
# possuem natureza sintética/contingencial para simulação do pipeline completo da dívida
# ativa do município de Palmas/TO, em conformidade com as diretrizes de LGPD e segurança de dados.


def categorizar_recuperabilidade(linha):
    """
    Regra de Negócio: Scoring de Recuperabilidade em 3 faixas.
    - Alta Recuperabilidade: Débitos recentes e menor valor.
    - Média Recuperabilidade: Débitos intermediários.
    - Baixa Recuperabilidade: Débitos antigos ou de valor muito elevado.
    """
    dias_atraso = linha.get("dias_atraso", 0)
    valor_debito = linha.get("valor_debito", 0)

    if dias_atraso < 365 and valor_debito < 5000:
        return "Alta Recuperabilidade"
    elif dias_atraso < 1095 or valor_debito < 20000:
        return "Média Recuperabilidade"
    else:
        return "Baixa Recuperabilidade"


def treinar_e_avaliar():
    # Simulando dataset integrado com variáveis do IBGE e SEFIN
    dados = pd.DataFrame({
        "valor_debito": [1200, 4500, 15000, 35000, 800, 6200, 18000, 45000],
        "dias_atraso": [180, 300, 720, 1500, 90, 400, 900, 1800],
        "renda_media_regiao": [3250.5, 3250.5, 1800.0, 5200.0, 3250.5, 1800.0, 5200.0, 1800.0],
        "subgrupo_setor": ["Centro", "Centro", "Taquaralto", "104 Sul", "Centro", "Taquaralto", "104 Sul", "Taquaralto"],
        "pago": [1, 1, 0, 0, 1, 1, 0, 0]
    })

    # Aplicação da regra de Scoring
    dados["faixa_recuperabilidade"] = dados.apply(categorizar_recuperabilidade, axis=1)

    X = dados[["valor_debito", "dias_atraso", "renda_media_regiao"]]
    y = dados["pago"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Treinamento do Modelo
    modelo = RandomForestClassifier(n_estimators=50, random_state=42)
    modelo.fit(X_train, y_train)

    # --- 2. MÉTRICAS POR SUBGRUPO (FAIRNESS PARA A SPRINT 5) ---
    dados["predicao"] = modelo.predict(X)
    print("=== MÉTRICAS SEGMENTADAS POR SUBGRUPO (FAIRNESS) ===")
    for setor, df_sub in dados.groupby("subgrupo_setor"):
        acerto = (df_sub["pago"] == df_sub["predicao"]).mean()
        print(f"Setor/Subgrupo: {setor:<12} | Acurácia Local: {acerto * 100:.1f}% | Registros: {len(df_sub)}")

    # --- 3. SERIALIZAÇÃO DO MODELO (.JOBLIB) ---
    caminho_modelo = os.path.join("models", "modelo_inadimplencia_v1.joblib")
    os.makedirs("models", exist_ok=True)
    joblib.dump(modelo, caminho_modelo)
    print(f"\n[OK] Modelo serializado salvo com sucesso em: {caminho_modelo}")


if __name__ == "__main__":
    treinar_e_avaliar()