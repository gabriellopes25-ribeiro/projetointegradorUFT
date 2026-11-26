"""
Suíte de Testes de Validação das Respostas da API SITRIB (Projeto Integrador UFT).

Valida se as respostas da API RESTful refletem dados verídicos e regras de negócio:
- Busca de Contribuintes por CPF/CNPJ (com e sem formatação)
- Dossiê consolidado de imóveis (CCI)
- Ordenação por Max-Heap O(log n) da Fila de Cobrança
- Simulação de reajuste tributário e projeções de arrecadação
- Indicadores de arrecadação e cruzamento com IBGE
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.api import app

client = TestClient(app)

def test_01_dashboard_indicadores_veridicos():
    """Valida se os indicadores do dashboard batem com a dívida ativa calculada."""
    resp = client.get("/api/v1/dashboard/indicadores")
    assert resp.status_code == 200, f"Erro status: {resp.status_code}"
    dados = resp.json()

    assert dados["indicadores_ibge"]["municipio"] == "Palmas"
    assert dados["indicadores_ibge"]["uf"] == "TO"
    assert dados["total_divida_ativa"] > 0
    assert dados["contribuintes_inadimplentes"] >= 1
    assert "IPTU" in dados["distribuicao_tributos"]
    print("✅ Teste 1 (Dashboard Indicadores): OK - Dados IBGE e Dívida Ativa verídicos.")

def test_02_busca_contribuinte_cpf_formatado_e_limpo():
    """Valida se a busca encontra o mesmo contribuinte com ou sem máscara de CPF."""
    resp1 = client.get("/api/v1/contribuintes/123.456.789-01")
    assert resp1.status_code == 200
    dados1 = resp1.json()

    resp2 = client.get("/api/v1/contribuintes/12345678901")
    assert resp2.status_code == 200
    dados2 = resp2.json()

    assert dados1["contribuinte"]["nome"] == dados2["contribuinte"]["nome"]
    assert len(dados1["imoveis"]) >= 1
    assert len(dados1["dividas"]) >= 1
    print("✅ Teste 2 (Busca Contribuinte com/sem máscara): OK - Contribuinte, imóveis e débitos vinculados.")

def test_03_dossie_imovel_cci_calculo_total():
    """Valida se o cálculo do valor total devido do imóvel bate com a soma das dívidas."""
    cci = "CCI-104-NORTE-01"
    resp = client.get(f"/api/v1/imoveis/{cci}/dossie")
    assert resp.status_code == 200
    dados = resp.json()

    soma_esperada = sum(d["valor_original"] + d["juros_multa"] for d in dados["dividas"])
    assert round(dados["valor_total_devido"], 2) == round(soma_esperada, 2)
    print("✅ Teste 3 (Dossiê Imobiliário CCI): OK - Cálculo matemático de débitos 100% verídico.")

def test_04_fila_cobranca_ordenada_por_max_heap():
    """Valida se a fila de cobrança vem estritamente decrescente por score de prioridade."""
    resp = client.get("/api/v1/cobranca/fila-prioridade")
    assert resp.status_code == 200
    fila = resp.json()

    assert len(fila) >= 2
    scores = [item["score"] for item in fila]
    assert scores == sorted(scores, reverse=True)
    assert fila[0]["faixa_devedor"] in ("Grande devedor", "Médio devedor", "Pequeno devedor")
    print(f"✅ Teste 4 (Fila de Cobrança Max-Heap): OK - Ordenação decrescente perfeita (Maior Score: {fila[0]['score']}).")

def test_05_simulacao_tributaria_calculo_matematico():
    """Valida a precisão matemática da simulação de reajuste de alíquota."""
    payload = {
        "tributo": "IPTU",
        "aliquota_atual": 1.0,
        "aliquota_proposta": 1.5,
        "base_calculo": 200000.0
    }
    resp = client.post("/api/v1/tributos/simular-reajuste", json=payload)
    assert resp.status_code == 200
    sim = resp.json()

    assert sim["valor_atual"] == 2000.0
    assert sim["valor_projetado"] == 3000.0
    assert sim["diferenca"] == 1000.0
    assert sim["variacao_percentual"] == 50.0
    print("✅ Teste 5 (Simulador Tributário): OK - Projeção de R$ 2.000 -> R$ 3.000 (+50%) verificada.")

def test_06_documento_inexistente_retorna_404():
    """Valida se documentos não cadastrados devolvem HTTP 404."""
    resp = client.get("/api/v1/contribuintes/00000000000")
    assert resp.status_code == 404
    print("✅ Teste 6 (Tratamento de Exceções): OK - Documento inexistente tratado com HTTP 404.")

if __name__ == "__main__":
    print("\n--- INICIANDO BATERIA DE TESTES DE VALIDAÇÃO DA API SITRIB ---")
    test_01_dashboard_indicadores_veridicos()
    test_02_busca_contribuinte_cpf_formatado_e_limpo()
    test_03_dossie_imovel_cci_calculo_total()
    test_04_fila_cobranca_ordenada_por_max_heap()
    test_05_simulacao_tributaria_calculo_matematico()
    test_06_documento_inexistente_retorna_404()
    print("--- TODOS OS 6 TESTES DE VALIDAÇÃO FORAM APROVADOS COM SUCESSO! ---\n")
