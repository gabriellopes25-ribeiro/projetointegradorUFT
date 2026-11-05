import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report

print("--- INICIANDO SPRINT 4: METODOLOGIA DE TREINO E BASELINES ---")

# 1. CARREGAMENTO DOS DADOS (Conectando ao banco de dados do projeto)
try:
    conn = sqlite3.connect("sitrib.db")
    df = pd.read_sql_query("SELECT * FROM contribuinte_features", conn)
    conn.close()
    print(f"Base carregada com sucesso! Total de registros: {len(df)}")
except Exception as e:
    print("Aviso: Banco de dados sitrib.db não encontrado diretamente. Gerando dados de simulação estruturada...")
    # Fallback estruturado com datas divididas entre 2021 e 2025 para abranger o split
    np.random.seed(42)
    n_samples = 600
    df = pd.DataFrame({
        'data_emissao': pd.date_range(start='2021-01-01', periods=n_samples, freq='3D'),
        'valor_tributo': np.random.uniform(100, 5000, n_samples),
        'historico_inadimplencia': np.random.randint(0, 5, n_samples),
        'data_ajuizamento_processo': np.random.choice([None, '2025-01-01'], n_samples), # Variável futura (Leakage)
        'target': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })

# Converter coluna temporal
df['data_emissao'] = pd.to_datetime(df['data_emissao'])

# 2. AUDITORIA ANTIVAZAMENTO (DATA LEAKAGE)
colunas_vazamento = ['data_ajuizamento_processo', 'parcelamento_efetuado_futuro', 'status_pagamento_pos_corte']
colunas_para_remover = [c for c in colunas_vazamento if c in df.columns]

print(f"Colunas removidas na auditoria antivazamento: {colunas_para_remover}")

# 3. SPLIT TEMPORAL (DIVISÃO POR DATA)
data_corte = '2023-12-31'
df_train = df[df['data_emissao'] <= data_corte]
df_test  = df[df['data_emissao'] > data_corte]

features_ignoradas = ['target', 'data_emissao'] + colunas_para_remover
features = [c for c in df.columns if c not in features_ignoradas]

X_train = df_train[features]
y_train = df_train['target']
X_test = df_test[features]
y_test = df_test['target']

print(f"Registros de Treino (até {data_corte}): {len(X_train)}")
print(f"Registros de Teste (após {data_corte}): {len(X_test)}")

# 4. TREINAMENTO DOS MODELOS BASELINE
# Modelo 1: Regressão Logística
model_lr = LogisticRegression(random_state=42, max_iter=1000)
model_lr.fit(X_train, y_train)
y_pred_lr = model_lr.predict(X_test)

# Modelo 2: Árvore de Decisão
model_dt = DecisionTreeClassifier(max_depth=5, random_state=42)
model_dt.fit(X_train, y_train)
y_pred_dt = model_dt.predict(X_test)

# 5. RESULTADOS E MÉTRICAS DE DESEMPENHO
print("\n" + "="*50)
print("=== DESEMPENHO BASELINE 1: REGRESSÃO LOGÍSTICA ===")
print("="*50)
print(classification_report(y_test, y_pred_lr, zero_division=0))

print("\n" + "="*50)
print("=== DESEMPENHO BASELINE 2: ÁRVORE DE DECISÃO ===")
print("="*50)
print(classification_report(y_test, y_pred_dt, zero_division=0))