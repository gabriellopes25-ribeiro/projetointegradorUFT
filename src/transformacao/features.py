"""
Módulo de Engenharia de Atributos e Anonimização LGPD (SITRIB).

Responsável: Adriel Morais (Product Owner / Desenvolvedor)
Sprint: Sprint 3 — Pipeline ETL (Módulo 5)
Critério: E2 (parcial) + E4

Funcionalidades:
1. Engenharia de Atributos de Inadimplência:
   - tempo_inadimplencia_dias e idade_divida_anos
   - Classificação por faixa de devedor (Pequeno, Médio, Grande)
   - Extração de variáveis de sazonalidade (mês e trimestre de vencimento)
   - Cálculo de score numérico de prioridade de cobrança para alimentar a FilaCobranca (Max-Heap da Sprint 2)
2. Mascaramento e Conformidade com a LGPD (Lei nº 13.709/2018):
   - Mascaramento de CPF (***.456.789-**) e CNPJ (**.123.***/0001-**)
   - Anonimização de telefones ((63) 9****-2030) e e-mails (c***a@email.com)
   - Conforme especificado na seção 2.4 de docs/integracao_prefeitura.md
"""

from datetime import datetime, date
import re
from typing import Union
import pandas as pd
import numpy as np


# ==============================================================================
# 1. Funções Auxiliares de Mascaramento LGPD
# ==============================================================================

def mascarar_documento(doc: Union[str, int, float, None]) -> str:
    """
    Mascara CPF ou CNPJ preservando apenas fragmentos seguros conforme LGPD:
    - CPF: 123.456.789-00 -> ***.456.789-**
    - CNPJ: 12.345.678/0001-90 -> **.345.***/0001-**
    """
    if pd.isna(doc) or doc is None:
        return "NÃO INFORMADO"

    # Remove caracteres não numéricos
    apenas_digitos = re.sub(r"\D", "", str(doc))

    if len(apenas_digitos) == 11:
        # Formato CPF: ***.DDD.DDD-**
        return f"***.{apenas_digitos[3:6]}.{apenas_digitos[6:9]}-**"
    elif len(apenas_digitos) == 14:
        # Formato CNPJ: **.DDD.***/DDDD-**
        return f"**.{apenas_digitos[2:5]}.***./{apenas_digitos[8:12]}-**"
    else:
        # Documento genérico ou fora de padrão
        if len(apenas_digitos) > 4:
            return f"***{apenas_digitos[3:-2]}**"
        return "***"


def mascarar_telefone(tel: Union[str, int, float, None]) -> str:
    """
    Mascara número de telefone mantendo apenas DDD e final:
    - (63) 98765-4321 -> (63) 9****-4321
    """
    if pd.isna(tel) or tel is None:
        return "NÃO INFORMADO"

    digitos = re.sub(r"\D", "", str(tel))
    if len(digitos) >= 10:
        ddd = digitos[:2]
        final = digitos[-4:]
        return f"({ddd}) 9****-{final}"
    elif len(digitos) >= 8:
        return f"****-{digitos[-4:]}"
    return "****-****"


def mascarar_email(email: Union[str, None]) -> str:
    """
    Mascara endereço de e-mail:
    - usuario.exemplo@mail.uft.edu.br -> u***o@mail.uft.edu.br
    """
    if pd.isna(email) or not isinstance(email, str) or "@" not in email:
        return "anonimo@protegido.gov.br"

    partes = email.split("@")
    usuario = partes[0]
    dominio = partes[1]

    if len(usuario) <= 2:
        usuario_mascarado = f"{usuario[0]}***"
    else:
        usuario_mascarado = f"{usuario[0]}***{usuario[-1]}"

    return f"{usuario_mascarado}@{dominio}"


def anonimizar_lgpd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica a conformidade com a LGPD em todas as colunas que contenham
    dados pessoais identificáveis (PII) antes da gravação final.
    """
    df_anonimizado = df.copy()

    # Mascaramento de CPF / CNPJ
    for col in ["cpf_cnpj", "documento", "cpf_cnpj_proprietario"]:
        if col in df_anonimizado.columns:
            df_anonimizado[col] = df_anonimizado[col].apply(mascarar_documento)

    # Mascaramento de telefones
    for col in ["telefone", "celular", "contato"]:
        if col in df_anonimizado.columns:
            df_anonimizado[col] = df_anonimizado[col].apply(mascarar_telefone)

    # Mascaramento de e-mails
    for col in ["email", "correio_eletronico"]:
        if col in df_anonimizado.columns:
            df_anonimizado[col] = df_anonimizado[col].apply(mascarar_email)

    return df_anonimizado


# ==============================================================================
# 2. Engenharia de Atributos de Inadimplência
# ==============================================================================

def categorizar_faixa_devedor(valor_total: float) -> str:
    """
    Classifica a dívida em faixas operacionais da SEFIN:
    - Pequeno devedor: < R$ 5.000,00
    - Médio devedor: R$ 5.000,00 a R$ 50.000,00
    - Grande devedor: > R$ 50.000,00
    """
    try:
        val = float(valor_total)
    except (ValueError, TypeError):
        return "Indeterminado"

    if val < 5000.0:
        return "Pequeno devedor"
    elif val <= 50000.0:
        return "Médio devedor"
    else:
        return "Grande devedor"


def calcular_score_prioridade(df: pd.DataFrame) -> pd.Series:
    """
    Calcula um score numérico de propensão/prioridade de cobrança ($0 a 100+$).
    Combina:
      - Idade da dívida (anos): peso de relevância temporal
      - Montante devido: peso financeiro
      - Indicador socioeconômico da região (renda média): capacidade contributiva estimada

    Este score alimenta diretamente o critério de prioridade do Max-Heap
    da classe FilaCobranca (desenvolvida na Sprint 2).
    """
    valor_divida = df["valor_total"] if "valor_total" in df.columns else df.get("valor_original", 0)
    idade_anos = df.get("idade_divida_anos", 1)
    renda_regiao = df.get("renda_media_regiao", 3250.50)

    # Componentes ponderados
    peso_valor = np.log1p(valor_divida.astype(float)) * 3.5
    peso_idade = idade_anos.astype(float) * 2.0
    peso_capacidade = np.log1p(renda_regiao.astype(float)) * 1.5

    score = peso_valor + peso_idade + peso_capacidade
    return np.round(score, 2)


def gerar_atributos_inadimplencia(df: pd.DataFrame, data_referencia: Union[datetime, date, None] = None) -> pd.DataFrame:
    """
    Gera as features necessárias para análise preditiva da dívida ativa:
    - tempo_inadimplencia_dias: dias corridos desde o vencimento
    - idade_divida_anos: idade calculada em anos
    - faixa_devedor: 'Pequeno devedor', 'Médio devedor' ou 'Grande devedor'
    - mes_vencimento e trimestre_vencimento: sazonalidade temporal
    - score_prioridade: pontuação para o Max-Heap da FilaCobranca
    """
    if df.empty:
        return df

    df_transformado = df.copy()
    hoje = pd.to_datetime(data_referencia or datetime.now())

    # 1. Tratamento de valor total
    if "valor_total" not in df_transformado.columns:
        if "valor_original" in df_transformado.columns:
            juros = df_transformado.get("juros_multa", 0)
            df_transformado["valor_total"] = df_transformado["valor_original"].astype(float) + juros.astype(float)
        else:
            df_transformado["valor_total"] = 0.0

    # 2. Categorização por faixa de devedor
    df_transformado["faixa_devedor"] = df_transformado["valor_total"].apply(categorizar_faixa_devedor)

    # 3. Tratamento de datas e sazonalidade
    if "data_vencimento" in df_transformado.columns:
        datas_venc = pd.to_datetime(df_transformado["data_vencimento"], errors="coerce")
    elif "ano_exercicio" in df_transformado.columns:
        # Se só temos ano de exercício, assume vencimento padrão em 31/03 daquele ano (IPTU Palmas)
        datas_venc = pd.to_datetime(df_transformado["ano_exercicio"].astype(str) + "-03-31", errors="coerce")
    else:
        datas_venc = pd.Series([hoje] * len(df_transformado))

    # Preenche datas nulas com hoje
    datas_venc = datas_venc.fillna(hoje)

    # Cálculo dos dias e anos de inadimplência
    dias_atraso = (hoje - datas_venc).dt.days
    df_transformado["tempo_inadimplencia_dias"] = np.maximum(0, dias_atraso)
    df_transformado["idade_divida_anos"] = np.round(df_transformado["tempo_inadimplencia_dias"] / 365.25, 2)

    # Variáveis sazonais
    df_transformado["mes_vencimento"] = datas_venc.dt.month
    df_transformado["trimestre_vencimento"] = datas_venc.dt.quarter

    # 4. Cálculo do Score de Prioridade para a Fila de Cobrança
    df_transformado["score_prioridade"] = calcular_score_prioridade(df_transformado)

    return df_transformado


# ==============================================================================
# 3. Teste Rápido / Demonstração
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SITRIB - Teste do Módulo de Transformação e LGPD (Adriel Morais)")
    print("=" * 60)

    # Massa de teste simples
    dados_exemplo = pd.DataFrame([
        {
            "codigo_debito": "DEB-2023-001",
            "cpf_cnpj": "123.456.789-01",
            "email": "contribuinte.silva@mail.uft.edu.br",
            "telefone": "(63) 98401-2030",
            "ano_exercicio": 2022,
            "valor_original": 12500.0,
            "juros_multa": 1340.50,
            "renda_media_regiao": 3250.50,
        },
        {
            "codigo_debito": "DEB-2024-002",
            "cpf_cnpj": "12.345.678/0001-90",
            "email": "empresa.palmas@comercio.com",
            "telefone": "(63) 3215-1000",
            "ano_exercicio": 2024,
            "valor_original": 78900.0,
            "juros_multa": 4200.0,
            "renda_media_regiao": 4100.0,
        }
    ])

    df_feat = gerar_atributos_inadimplencia(dados_exemplo)
    df_final = anonimizar_lgpd(df_feat)

    print("\n[RESULTADO COM FEATURES E LGPD]:")
    print(df_final[[
        "codigo_debito", "cpf_cnpj", "email", "telefone",
        "valor_total", "faixa_devedor", "tempo_inadimplencia_dias", "score_prioridade"
    ]])
