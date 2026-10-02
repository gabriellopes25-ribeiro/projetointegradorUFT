"""
Testes do RepositorioSQLite — prova de que a camada de persistência real
(sitrib.db) responde com os mesmos dados e no mesmo formato que o banco
simulado em memória, permitindo plugar o BuscaService nela sem alterações.
"""

import unittest
from pathlib import Path

from src.repositories.sqlite_repository import RepositorioSQLite
from src.services.busca_service import (
    BuscaService,
    ContribuinteNaoEncontradoError,
)

CAMINHO_BANCO = Path(__file__).resolve().parent.parent / "sitrib.db"


@unittest.skipUnless(CAMINHO_BANCO.exists(), "sitrib.db não encontrado — rode 'python -m scripts.popular_banco'")
class TestRepositorioSQLite(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = RepositorioSQLite(CAMINHO_BANCO)

    def test_buscar_contribuinte_por_cpf_formatado(self) -> None:
        resultado = self.repo.buscar_contribuinte("123.456.789-01")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["nome"], "Carlos Eduardo Siqueira")
        self.assertEqual(resultado["tipo_pessoa"], "FISICA")

    def test_buscar_contribuinte_por_cnpj_apenas_digitos(self) -> None:
        resultado = self.repo.buscar_contribuinte("12345678000190")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["nome"], "Tocantins Engenharia e Serviços Ltda")
        self.assertEqual(resultado["tipo_pessoa"], "JURIDICA")

    def test_buscar_contribuinte_inexistente_retorna_none(self) -> None:
        self.assertIsNone(self.repo.buscar_contribuinte("000.111.222-33"))

    def test_buscar_imovel_retorna_dados_e_proprietario(self) -> None:
        imovel = self.repo.buscar_imovel("CCI-104-NORTE-01")
        self.assertIsNotNone(imovel)
        self.assertEqual(imovel["cpf_cnpj_proprietario"], "123.456.789-01")
        self.assertEqual(imovel["tipo_imovel"], "RESIDENCIAL")

    def test_listar_dividas_por_imovel(self) -> None:
        dividas = self.repo.listar_dividas_por_imovel("CCI-104-NORTE-01")
        self.assertEqual(len(dividas), 2)
        total = round(sum(d["valor_original"] + d["juros_multa"] for d in dividas), 2)
        self.assertAlmostEqual(total, 5680.50, places=2)

    def test_listar_processos_por_imovel(self) -> None:
        processos = self.repo.listar_processos_por_imovel("CCI-104-NORTE-01")
        self.assertEqual(len(processos), 1)
        self.assertEqual(processos[0]["numero_processo"], "0012345-67.2023.8.27.2729")

    def test_imovel_sem_dividas_retorna_listas_vazias(self) -> None:
        self.assertEqual(self.repo.listar_dividas_por_imovel("CCI-GRACIOSA-LAGO-88"), [])
        self.assertEqual(self.repo.listar_processos_por_imovel("CCI-GRACIOSA-LAGO-88"), [])

    def test_listar_imoveis_por_contribuinte(self) -> None:
        imoveis = self.repo.listar_imoveis_por_contribuinte("123.456.789-01")
        self.assertEqual(len(imoveis), 2)
        inscricoes = {i["inscricao_cci"] for i in imoveis}
        self.assertEqual(inscricoes, {"CCI-104-NORTE-01", "CCI-208-SUL-42"})

    def test_colecoes_contribuintes_e_imoveis(self) -> None:
        self.assertEqual(len(self.repo.contribuintes), 5)
        self.assertEqual(len(self.repo.imoveis), 5)
        self.assertIn("123.456.789-01", self.repo.contribuintes)
        self.assertIn("CCI-104-NORTE-01", self.repo.imoveis)


@unittest.skipUnless(CAMINHO_BANCO.exists(), "sitrib.db não encontrado — rode 'python -m scripts.popular_banco'")
class TestBuscaServiceComRepositorioSQLite(unittest.TestCase):
    """
    Prova de integração: o BuscaService (hash, heap e grafo) funciona sem
    nenhuma alteração de código ao receber o RepositorioSQLite real no lugar
    do BancoSimuladoEmMemoria.
    """

    def setUp(self) -> None:
        self.servico = BuscaService(repositorio=RepositorioSQLite(CAMINHO_BANCO))

    def test_busca_contribuinte_via_banco_real(self) -> None:
        resultado = self.servico.buscar_contribuinte("123.456.789-01")
        self.assertEqual(resultado["nome"], "Carlos Eduardo Siqueira")

    def test_busca_contribuinte_inexistente_via_banco_real(self) -> None:
        with self.assertRaises(ContribuinteNaoEncontradoError):
            self.servico.buscar_contribuinte("000.111.222-33")

    def test_fila_de_cobranca_via_banco_real(self) -> None:
        fila = self.servico.montar_fila_cobranca()
        proximo = fila.proximo_a_cobrar()
        self.assertIsNotNone(proximo)

    def test_grafo_de_relacionamentos_via_banco_real(self) -> None:
        relacionados = self.servico.buscar_relacionamentos("123.456.789-01")
        self.assertEqual(len(relacionados), 2)


if __name__ == "__main__":
    unittest.main()