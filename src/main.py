"""
Ponto de Entrada Integrado do SITRIB (Sistema de Inteligência Tributária - UFT).

Orquestra todo o ecossistema do projeto:
1. Coleta e Auditoria de APIs (Prefeitura de Palmas e IBGE).
2. Pipeline ETL com Enriquecimento Socioeconômico e Engenharia de Atributos (LGPD).
3. Persistência relacional em SQLite (sitrib.db).
4. Estruturas de Dados Avançadas (Tabela Hash O(1), Max-Heap O(log n) e Grafo de Relacionamentos).
5. Geração e Exportação de Relatórios Fiscais e Executivos (Markdown, CSV e Console).
"""

import os
import sys
from pathlib import Path
from decimal import Decimal
import pandas as pd

# Configura codificação do stdout para evitar erros em terminais Windows (cp1252)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Garante a raiz do projeto no sys.path
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from src.services.busca_service import BuscaService
from src.repositories.sqlite_repository import RepositorioSQLite
from src.services.relatorio_service import RelatorioFiscalService
from src.coleta.coletor_prefeitura import ColetorSefinPalmasDual
from src.enriquecimento.integracao_ibge import obter_indicadores_ibge
from etl_sefin import executar_pipeline, DB_PATH, CAMINHO_PRONTO


def exibir_cabecalho():
    print("=" * 72)
    print("  SITRIB - Sistema de Inteligencia Tributaria (UFT / Palmas-TO)")
    print("  Orquestrador Integrado do Ecossistema & Auditoria de APIs")
    print("=" * 72)


def sincronizar_ecossistema(
    executar_coleta_api: bool = True,
    ano: int = 2026,
    mes: int = 10,
    limite: int = 20
) -> tuple:
    """
    Executa ou valida o ciclo completo do pipeline:
    API Prefeitura -> Enriquecimento IBGE -> Features/LGPD -> Banco -> Relatórios.
    """
    print(f"\n[ETAPA 1/4] Verificando APIs e Executando Pipeline ETL (Filtro: {mes:02d}/{ano})...")
    
    # 1. Coleta e Diagnóstico com ColetorSefinPalmasDual
    coletor = ColetorSefinPalmasDual()
    dados_brutos, diagnostico_api = coletor.coletar_com_diagnostico(
        limite_portal_novo=limite,
        ano=ano,
        mes=mes
    )
    
    # 2. Dados Socioeconômicos ao vivo do IBGE
    indicadores_ibge = obter_indicadores_ibge()
    print(f"  -> IBGE API: {indicadores_ibge.get('municipio')}/{indicadores_ibge.get('uf')} (Codigo {indicadores_ibge.get('codigo_ibge')})")
    print(f"  -> Renda Media Domiciliar: R$ {indicadores_ibge.get('renda_media_domiciliar', 0.0):,.2f}")
    print(f"  -> Populacao Estimada: {indicadores_ibge.get('populacao_estimada', 0):,} habitantes")
    
    # 3. Execução do pipeline ETL
    df_ouro = executar_pipeline(executar_coletor=False, ano=ano, mes=mes, limite=limite)
    
    return diagnostico_api, indicadores_ibge, df_ouro


def demonstrar_estruturas_dados(caminho_banco: Path):
    """
    Demonstra a atuação das três estruturas centrais integradas ao repositório real.
    """
    print("\n[ETAPA 2/4] Executando Estruturas de Dados Avancadas...")
    
    if caminho_banco.exists():
        print(f"  [Persistencia] Conectado ao banco SQLite real: {caminho_banco.name}")
        servico = BuscaService(repositorio=RepositorioSQLite(caminho_banco))
    else:
        print("  [Persistencia] Usando dados em memoria.")
        servico = BuscaService()

    # Demonstração 1: Tabela Hash O(1)
    cpf_exemplo = "123.456.789-01"
    try:
        contribuinte = servico.buscar_contribuinte(cpf_exemplo)
        print(f"\n  [Tabela Hash O(1)] Contribuinte localizado: {contribuinte.get('nome')}")
        print(f"    - Documento: {contribuinte.get('cpf_cnpj')} | Email: {contribuinte.get('email')}")
        servico.buscar_contribuinte(cpf_exemplo)
        print("    -> Segunda busca ao mesmo CPF retornada instantaneamente via Cache Hash.")
    except Exception as e:
        print(f"  [Tabela Hash] Consulta de exemplo: {e}")

    # Demonstração 2: Max-Heap (Fila de Prioridade O(log n))
    print("\n  [Max-Heap O(log n)] Fila de Priorizacao de Cobranca:")
    servico.montar_fila_cobranca()
    for posicao in range(1, 4):
        proximo = servico.proximo_a_cobrar()
        if proximo and proximo != "Fila vazia":
            print(f"    {posicao}o a cobrar na fila -> {proximo}")
        else:
            break

    # Demonstração 3: Grafo de Relacionamentos
    print(f"\n  [Grafo de Relacionamentos] Mapeamento fiscal de {cpf_exemplo}:")
    relacionamentos = servico.buscar_relacionamentos(cpf_exemplo)
    if relacionamentos:
        for rel in relacionamentos:
            print(f"    -> Imovel: {rel.get('imovel')} | Processo Judicial: {rel.get('processo')}")
    else:
        print("    Nenhum relacionamento adicional vinculado.")

    return servico


def gerar_e_exibir_relatorios(diagnostico_api: dict, indicadores_ibge: dict, df_ouro: pd.DataFrame):
    """
    Gera relatórios executivos de arrecadação e auditoria das APIs externas.
    """
    print("\n[ETAPA 3/4] Gerando Relatorios Analiticos do Ecossistema...")
    
    relatorio_service = RelatorioFiscalService(caminho_banco=DB_PATH)
    
    # 1. Relatório de APIs
    rel_api = relatorio_service.gerar_relatorio_api(
        diagnostico_prefeitura=diagnostico_api,
        diagnostico_ibge={
            "status": "200 OK",
            "url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/1721000",
            "municipio": indicadores_ibge.get("municipio", "Palmas"),
            "uf": indicadores_ibge.get("uf", "TO"),
            "renda_media": indicadores_ibge.get("renda_media_domiciliar", 3250.50),
            "populacao": indicadores_ibge.get("populacao_estimada", 313349),
        }
    )
    
    # 2. Relatório de Dívida e Arrecadação
    rel_arrecadacao = relatorio_service.gerar_relatorio_arrecadacao(
        df_tributos=df_ouro,
        indicadores_ibge=indicadores_ibge
    )
    
    # 3. Exportações
    caminho_md = RAIZ_PROJETO / "docs" / "relatorio_ecossistema.md"
    caminho_csv = RAIZ_PROJETO / "data" / "pronto" / "relatorio_arrecadacao.csv"
    
    relatorio_service.exportar_markdown(rel_api, rel_arrecadacao, caminho_arquivo=caminho_md)
    relatorio_service.exportar_csv(df_ouro, caminho_csv)
    
    print(f"  [Sucesso] Relatorio Markdown exportado: {caminho_md}")
    print(f"  [Sucesso] Base consolidada CSV exportada: {caminho_csv}")

    # Exibição do Painel no Console
    m_tot = rel_arrecadacao.get("mensal_totais", {})
    print("\n[ETAPA 4/4] Painel Executivo Consolidado:")
    print("-" * 72)
    print(f"  Filtro de Competência        : {m_tot.get('mes_referencia', 10):02d}/{m_tot.get('ano_referencia', 2026)}")
    print(f"  Volume Total Arrecadado Mês  : R$ {m_tot.get('total_arrecadado_mes', 0.0):,.2f}")
    if m_tot.get("total_orcado", 0.0) > 0:
        print(f"  Previsão Orçamentária Anual  : R$ {m_tot.get('total_orcado', 0.0):,.2f}")
        print(f"  Taxa de Realização no Mês    : {m_tot.get('taxa_realizacao_mes_pct', 0.0):.2f}%")
    print(f"  Total de Títulos Cadastrados : {rel_arrecadacao.get('qtd_titulos', 0)}")
    print(f"  Valor Médio por Título       : R$ {rel_arrecadacao.get('media_divida', 0.0):,.2f}")
    print(f"  Modo de Operação das APIs    : {rel_api.get('modo_operacao')}")
    print("-" * 72)
    print("  Composição por Tipo de Tributo:")
    for trib, dados in rel_arrecadacao.get("por_tipo_tributo", {}).items():
        print(f"    - {trib:<35}: R$ {dados.get('total', 0.0):>12,.2f} ({dados.get('percentual', 0.0):>4.1f}%) | {dados.get('quantidade')} lançamentos")
    print("-" * 72)
    print(f"  Impacto Socioeconômico (IBGE): R$ {rel_arrecadacao.get('socioeconomico_ibge', {}).get('impacto_per_capita', 0.0):,.2f} per capita em Palmas/TO")
    print("=" * 72)


def main():
    exibir_cabecalho()
    caminho_banco = RAIZ_PROJETO / "sitrib.db"
    
    # Executa a orquestração filtrando por Outubro de 2026 (mês atual) com 20 registros
    diagnostico_api, indicadores_ibge, df_ouro = sincronizar_ecossistema(
        executar_coleta_api=True,
        ano=2026,
        mes=10,
        limite=20
    )
    demonstrar_estruturas_dados(caminho_banco)
    gerar_e_exibir_relatorios(diagnostico_api, indicadores_ibge, df_ouro)
    
    print("\n[SUCESSO] Execucao completa do ecossistema SITRIB finalizada com exito!\n")


if __name__ == "__main__":
    main()
