import os
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any

# Tenta importar o fallback das seeds
try:
    from seeds.mock_data import obter_dividas_mock
except ImportError:
    # Caso seja executado de subpastas
    from seeds.mock_data import obter_dividas_mock


class ColetorSefinPalmas:
    """
    Coletor para consumo da API da Prefeitura de Palmas (SEFIN).
    Implementa rate-limiting, retentativas com exponential backoff
    e fallback automático para dados simulados em memória.
    """

    def __init__(self, url_base: str = "https://api.sefin.palmas.to.gov.br/v1/notas"):
        self.url_base = url_base
        self.headers = {
            "User-Agent": "SITRIB-UFT/1.0",
            "Accept": "application/json"
        }
        self.diretorio_destino = os.path.join("data", "bruto")
        os.makedirs(self.diretorio_destino, exist_ok=True)

    def consumir_api(self) -> List[Dict[str, Any]]:
        """
        Consome os registros da API da prefeitura tratando rate-limit e retentativas.
        Se o endpoint estiver inacessível, ativa o fallback automático.
        """
        dados_coletados = []
        pagina = 1
        max_retentativas = 3

        print(f"[COLETA] Iniciando requisições em {self.url_base}...")

        while True:
            url_com_paginacao = f"{self.url_base}?page={pagina}"
            sucesso = False

            for tentativa in range(1, max_retentativas + 1):
                try:
                    # Rate-limiting ético: máximo de 60 req/min (delay de 1s)
                    time.sleep(1.0)

                    response = requests.get(url_com_paginacao, headers=self.headers, timeout=10)

                    # Trata status de sucesso
                    if response.status_code == 200:
                        novos_dados = response.json()
                        if not novos_dados:
                            # Fim da paginação
                            sucesso = True
                            break

                        dados_coletados.extend(novos_dados)
                        print(f"  -> Página {pagina} coletada ({len(novos_dados)} registros).")
                        sucesso = True
                        break

                    # Trata códigos de erro com Exponential Backoff
                    elif response.status_code in [429, 500, 502, 503]:
                        tempo_espera = 2 ** tentativa
                        print(f"  [AVISO] Status {response.status_code} na página {pagina}. "
                              f"Retentativa {tentativa}/{max_retentativas} em {tempo_espera}s...")
                        time.sleep(tempo_espera)
                    else:
                        print(f"  [ERRO] Erro não tratável HTTP {response.status_code} na página {pagina}.")
                        break

                except (requests.exceptions.RequestException, Exception) as e:
                    tempo_espera = 2 ** tentativa
                    print(f"  [AVISO] Erro de conexão ({e.__class__.__name__}). "
                          f"Retentativa {tentativa}/{max_retentativas} em {tempo_espera}s...")
                    time.sleep(tempo_espera)

            # Se falhou após todas as retentativas na primeira página, ativa o fallback
            if not sucesso:
                if pagina == 1:
                    print("\n[FALLBACK] Endpoint externo inacessível. Usando seeds/mock_data.py...")
                    return self._executar_fallback()
                else:
                    # Se falhar em páginas posteriores, encerra a coleta mantendo o que já coletou
                    print("  [ERRO] Encerrando paginação por falha de conexão.")
                    break

            pagina += 1

        return dados_coletados

    def _executar_fallback(self) -> List[Dict[str, Any]]:
        """Consome a fonte alternativa local de dados em seeds/mock_data.py"""
        try:
            return obter_dividas_mock()
        except Exception as e:
            print(f"[ERRO FALLBACK] Não foi possível carregar mock_data: {e}")
            return []

    def salvar_dados_brutos(self, dados: List[Dict[str, Any]]) -> str:
        """Salva a massa de dados bruta em JSON com timestamp YYYYMMDD_HHMM."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_arquivo = f"dados_sefin_{timestamp}.json"
        caminho_completo = os.path.join(self.diretorio_destino, nome_arquivo)

        with open(caminho_completo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        print(f"\n[SUCESSO] Dados brutos salvos em: {caminho_completo}")
        return caminho_completo


if __name__ == "__main__":
    coletor = ColetorSefinPalmas()
    print("=" * 60)
    print("SITRIB - Execução do Coletor de Dados Brutos da Prefeitura")
    print("=" * 60)
    
    dados = coletor.consumir_api()
    if dados:
        caminho_salvo = coletor.salvar_dados_brutos(dados)
        print(f"Resumo: {len(dados)} registros brutos processados com sucesso.")
    else:
        print("Nenhum dado pôde ser coletado ou gerado.")