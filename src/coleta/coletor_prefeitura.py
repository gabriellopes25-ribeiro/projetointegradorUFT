import os
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Tenta importar o fallback das seeds
try:
    from seeds.mock_data import obter_dividas_mock
except ImportError:
    from seeds.mock_data import obter_dividas_mock


class ColetorSefinPalmasDual:
    """
    Coletor unificado para a Prefeitura de Palmas (SITRIB-UFT).
    Alterna dinamicamente entre o Portal Novo (Nucleogov - POST) 
    e a API Antiga (REST - GET) dependendo da fonte/tipo de dado.
    """

    def __init__(self):
        # Endereços mapeados dos dois sistemas da prefeitura
        self.url_portal_novo = "https://acessoainformacao.palmas.to.gov.br/api"
        self.url_api_antiga = "https://integracao.palmas.to.gov.br/apirest"
        
        self.headers_comum = {
            "User-Agent": "SITRIB-UFT/1.0",
            "Accept": "application/json"
        }
        self.diretorio_destino = os.path.join("data", "bruto")
        os.makedirs(self.diretorio_destino, exist_ok=True)

    def consumir_portal_novo(self, recurso: str = "receitas", payload: dict = None) -> List[Dict[str, Any]]:
        """
        Consome dados do Portal Novo (Nucleogov) via POST com formulário/payload.
        Ideal para: Receitas, despesas, servidores, contratos e licitações atualizadas.
        """
        url_endpoint = f"{self.url_portal_novo}/{recurso}"
        payload = payload or {}
        max_retentativas = 3

        print(f"[COLETA - PORTAL NOVO] Requisitando POST em {url_endpoint}...")

        for tentativa in range(1, max_retentativas + 1):
            try:
                time.sleep(1.0)
                # O Portal Novo geralmente exige POST com dados enviados no corpo (data ou json)
                response = requests.post(url_endpoint, headers=self.headers_comum, data=payload, timeout=15)

                if response.status_code == 200:
                    dados = response.json()
                    print(f"  [SUCESSO] Dados do Portal Novo obtidos com sucesso ({len(dados) if isinstance(dados, list) else 1} registros).")
                    return dados if isinstance(dados, list) else [dados]
                
                elif response.status_code in [429, 500, 502, 503]:
                    tempo_espera = 2 ** tentativa
                    print(f"  [AVISO] Status {response.status_code}. Tentativa {tentativa}/{max_retentativas} em {tempo_espera}s...")
                    time.sleep(tempo_espera)
                else:
                    print(f"  [ERRO] HTTP {response.status_code} no Portal Novo.")
                    break

            except (requests.exceptions.RequestException, Exception) as e:
                tempo_espera = 2 ** tentativa
                print(f"  [AVISO] Erro de conexão ({e.__class__.__name__}). Tentativa {tentativa} em {tempo_espera}s...")
                time.sleep(tempo_espera)

        print("\n[FALLBACK] Falha no Portal Novo. Acionando dados locais...")
        return self._executar_fallback()

    def consumir_api_antiga(self, endpoint: str = "notas") -> List[Dict[str, Any]]:
        """
        Consome dados da API Antiga via GET com paginação.
        Ideal para: Gastos diretos, arrecadação histórica e folha até junho/2021.
        Nota: Lida com certificados/HTTP se necessário.
        """
        url_base = f"{self.url_api_antiga}/{endpoint}"
        dados_coletados = []
        pagina = 1
        max_retentativas = 3

        print(f"[COLETA - API ANTIGA] Iniciando paginação em {url_base}...")

        while True:
            url_com_paginacao = f"{url_base}?page={pagina}"
            sucesso = False

            for tentativa in range(1, max_retentativas + 1):
                try:
                    time.sleep(1.0)
                    # verify=False pode ser necessário caso o certificado SSL da API antiga falhe
                    response = requests.get(url_com_paginacao, headers=self.headers_comum, timeout=10, verify=False)

                    if response.status_code == 200:
                        novos_dados = response.json()
                        if not novos_dados:
                            sucesso = True
                            break

                        dados_coletados.extend(novos_dados)
                        print(f"  -> Página {pagina} coletada ({len(novos_dados)} registros).")
                        sucesso = True
                        break

                    elif response.status_code in [429, 500, 502, 503]:
                        tempo_espera = 2 ** tentativa
                        print(f"  [AVISO] Status {response.status_code} na página {pagina}. Tentando em {tempo_espera}s...")
                        time.sleep(tempo_espera)
                    else:
                        print(f"  [ERRO] HTTP {response.status_code} na página {pagina}.")
                        break

                except (requests.exceptions.RequestException, Exception) as e:
                    tempo_espera = 2 ** tentativa
                    print(f"  [AVISO] Erro de conexão ({e.__class__.__name__}). Tentando em {tempo_espera}s...")
                    time.sleep(tempo_espera)

            if not sucesso:
                if pagina == 1:
                    print("\n[FALLBACK] API Antiga inacessível. Usando seeds/mock_data.py...")
                    return self._executar_fallback()
                else:
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

    def salvar_dados_brutos(self, dados: List[Dict[str, Any]], prefixo: str = "sefin") -> str:
        """Salva a massa de dados bruta em JSON com timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_arquivo = f"dados_{prefixo}_{timestamp}.json"
        caminho_completo = os.path.join(self.diretorio_destino, nome_arquivo)

        with open(caminho_completo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        print(f"\n[SUCESSO] Dados brutos salvos em: {caminho_completo}")
        return caminho_completo

    def coletar_com_diagnostico(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executa a coleta avaliando a saúde de ambos os sistemas (Portal Novo e API Antiga).
        Retorna (dados_coletados, diagnostico_execucao).
        """
        diagnostico = {
            "portal_novo": {"url": f"{self.url_portal_novo}/receitas", "status": "INICIANDO"},
            "api_antiga": {"url": f"{self.url_api_antiga}/notas", "status": "INICIANDO"},
            "modo": "FALLBACK",
            "registros_obtidos": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # 1. Tenta API Antiga
        inicio = time.time()
        try:
            r = requests.get(f"{self.url_api_antiga}/notas?page=1", headers=self.headers_comum, timeout=5, verify=False)
            diagnostico["api_antiga"]["status"] = f"HTTP {r.status_code}"
            diagnostico["api_antiga"]["tempo_ms"] = int((time.time() - inicio) * 1000)
            if r.status_code == 200:
                dados = r.json()
                if dados:
                    diagnostico["modo"] = "AO_VIVO (API Antiga)"
                    diagnostico["registros_obtidos"] = len(dados)
                    self.salvar_dados_brutos(dados, prefixo="api_antiga")
                    return dados, diagnostico
        except Exception as e:
            diagnostico["api_antiga"]["status"] = f"ERRO ({e.__class__.__name__})"
            diagnostico["api_antiga"]["tempo_ms"] = int((time.time() - inicio) * 1000)

        # 2. Tenta Portal Novo
        inicio = time.time()
        try:
            r = requests.post(f"{self.url_portal_novo}/receitas", headers=self.headers_comum, data={"ano": 2026}, timeout=5)
            diagnostico["portal_novo"]["status"] = f"HTTP {r.status_code}"
            diagnostico["portal_novo"]["tempo_ms"] = int((time.time() - inicio) * 1000)
            if r.status_code == 200:
                dados = r.json()
                dados_lista = dados if isinstance(dados, list) else [dados]
                diagnostico["modo"] = "AO_VIVO (Portal Novo)"
                diagnostico["registros_obtidos"] = len(dados_lista)
                self.salvar_dados_brutos(dados_lista, prefixo="portal_novo")
                return dados_lista, diagnostico
        except Exception as e:
            diagnostico["portal_novo"]["status"] = f"ERRO ({e.__class__.__name__})"
            diagnostico["portal_novo"]["tempo_ms"] = int((time.time() - inicio) * 1000)

        # 3. Fallback controlado
        dados_fallback = self._executar_fallback()
        diagnostico["modo"] = "FALLBACK (Seeds / Dívidas Simuladas)"
        diagnostico["registros_obtidos"] = len(dados_fallback)
        self.salvar_dados_brutos(dados_fallback, prefixo="fallback_sefin")
        return dados_fallback, diagnostico


# Alias para retrocompatibilidade
ColetorSefinPalmas = ColetorSefinPalmasDual


if __name__ == "__main__":
    coletor = ColetorSefinPalmasDual()
    print("=" * 60)
    print("SITRIB - Coletor Multi-Sistema (Prefeitura de Palmas)")
    print("=" * 60)

    # Exemplo 1: Tentando buscar dados tributários/arrecadação na API Antiga
    print("\n--- Executando Coleta na API Antiga ---")
    dados_antigos = coletor.consumir_api_antiga(endpoint="notas")
    if dados_antigos:
        coletor.salvar_dados_brutos(dados_antigos, prefixo="api_antiga")

    # Exemplo 2: Tentando buscar dados atualizados no Portal Novo (Nucleogov)
    print("\n--- Executando Coleta no Portal Novo ---")
    dados_novos = coletor.consumir_portal_novo(recurso="receitas", payload={"ano": 2026})
    if dados_novos:
        coletor.salvar_dados_brutos(dados_novos, prefixo="portal_novo")
