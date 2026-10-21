import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import pandas as pd

from src.models.simulacao import Simulacao
from src.services.relatorio_service import RelatorioFiscalService, RelatorioService


class TestRelatorioService(unittest.TestCase):
    def setUp(self):
        self.servico = RelatorioFiscalService()
        self.simulacao1 = Simulacao(
            id="SIM-001",
            tributo_id="TRIB-IPTU",
            usuario_id="USR-10",
            percentual_reajuste=Decimal("5.0"),
            valor_antes=Decimal("1000.00"),
            valor_depois=Decimal("1050.00"),
            criada_em=datetime(2026, 10, 20, 10, 0, 0),
        )
        self.simulacao2 = Simulacao(
            id="SIM-002",
            tributo_id="TRIB-ISS",
            usuario_id="USR-20",
            percentual_reajuste=Decimal("10.0"),
            valor_antes=Decimal("2000.00"),
            valor_depois=Decimal("2200.00"),
            criada_em=datetime(2026, 10, 20, 11, 0, 0),
        )

    def test_implementa_interface_relatorio_service(self):
        self.assertIsInstance(self.servico, RelatorioService)

    def test_gerar_csv_simulacoes(self):
        csv_resultado = self.servico.gerar_csv([self.simulacao1, self.simulacao2])
        self.assertIn("id,tributo_id,usuario_id", csv_resultado)
        self.assertIn("SIM-001,TRIB-IPTU,USR-10,5.0,1000.00,1050.00,50.00", csv_resultado)
        self.assertIn("SIM-002,TRIB-ISS,USR-20,10.0,2000.00,2200.00,200.00", csv_resultado)

    def test_gerar_csv_simulacoes_vazio(self):
        csv_vazio = self.servico.gerar_csv([])
        self.assertTrue(csv_vazio.startswith("id,tributo_id"))

    def test_gerar_pdf_bytes(self):
        conteudo_bytes = self.servico.gerar_pdf([self.simulacao1])
        self.assertIsInstance(conteudo_bytes, bytes)
        texto = conteudo_bytes.decode("utf-8")
        self.assertIn("SITRIB - RELATÓRIO DE SIMULAÇÕES TRIBUTÁRIAS", texto)
        self.assertIn("SIM-001", texto)

    def test_gerar_relatorio_api(self):
        diag_pref = {
            "portal_novo": {"status": "HTTP 403", "url": "https://url_teste"},
            "api_antiga": {"status": "HTTP 404", "url": "https://url_teste"},
            "modo": "FALLBACK",
            "registros_obtidos": 4,
        }
        diag_ibge = {
            "status": "200 OK",
            "url": "https://ibge_teste",
            "municipio": "Palmas",
            "uf": "TO",
            "renda_media": 3250.50,
            "populacao": 313349,
        }
        rel = self.servico.gerar_relatorio_api(diag_pref, diag_ibge)
        self.assertEqual(rel["modo_operacao"], "FALLBACK")
        self.assertIn("4 registros", rel["resumo"])

    def test_gerar_relatorio_arrecadacao_com_dataframe(self):
        dados = [
            {"cpf_cnpj": "111.111.111-11", "nome": "Silva", "tipo_tributo": "IPTU", "valor_atualizado": 1000.0, "status_divida": "ATIVO"},
            {"cpf_cnpj": "222.222.222-22", "nome": "Santos", "tipo_tributo": "ISS", "valor_atualizado": 2000.0, "status_divida": "AJUIZADO"},
        ]
        df = pd.DataFrame(dados)
        rel = self.servico.gerar_relatorio_arrecadacao(df_tributos=df)

        self.assertEqual(rel["qtd_titulos"], 2)
        self.assertEqual(rel["total_divida"], 3000.0)
        self.assertEqual(rel["media_divida"], 1500.0)
        self.assertIn("IPTU", rel["por_tipo_tributo"])
        self.assertIn("ISS", rel["por_tipo_tributo"])
        self.assertEqual(len(rel["maiores_devedores"]), 2)
        self.assertEqual(rel["maiores_devedores"][0]["documento"], "222.222.222-22")

    def test_exportar_markdown_e_csv(self, tmp_path=None):
        dados = [{"cpf_cnpj": "111", "tipo_tributo": "IPTU", "valor_atualizado": 500.0}]
        df = pd.DataFrame(dados)
        rel_api = self.servico.gerar_relatorio_api()
        rel_arr = self.servico.gerar_relatorio_arrecadacao(df)

        caminho_md = Path("docs/teste_relatorio.md")
        caminho_csv = Path("data/pronto/teste_relatorio.csv")

        md = self.servico.exportar_markdown(rel_api, rel_arr, caminho_arquivo=caminho_md)
        csv = self.servico.exportar_csv(df, caminho_arquivo=caminho_csv)

        self.assertTrue(caminho_md.exists())
        self.assertTrue(caminho_csv.exists())
        self.assertIn("# 📊 SITRIB", md)

        # Limpeza dos arquivos temporários de teste
        if caminho_md.exists():
            caminho_md.unlink()
        if caminho_csv.exists():
            caminho_csv.unlink()


if __name__ == "__main__":
    unittest.main()
