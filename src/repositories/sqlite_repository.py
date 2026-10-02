"""
Repositório SQLite (SITRIB) — camada de persistência real.

Camada: Repository (MVC)

Implementa o mesmo contrato de `seeds.mock_data.BancoSimuladoEmMemoria`
(buscar_contribuinte, buscar_imovel, listar_dividas_por_imovel,
listar_processos_por_imovel, listar_imoveis_por_contribuinte, além das
coleções `.contribuintes` e `.imoveis`), mas lendo os dados reais do banco
SQLite (`sitrib.db`), criado a partir de `schema.sql` e populado por
`scripts/popular_banco.py`.

Como a interface pública é idêntica à do banco simulado em memória, qualquer
código que já dependia dele (BuscaService, main.py) passa a funcionar sem
nenhuma alteração ao receber uma instância deste repositório no lugar.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class RepositorioSQLite:
    """Camada de acesso a dados que consulta o banco SQLite real (sitrib.db)."""

    def __init__(self, caminho_banco: Optional[Union[str, Path]] = None) -> None:
        self.caminho_banco = Path(
            caminho_banco or Path(__file__).resolve().parent.parent.parent / "sitrib.db"
        )
        if not self.caminho_banco.exists():
            raise FileNotFoundError(
                f"Banco de dados não encontrado em '{self.caminho_banco}'. "
                "Rode 'python -m scripts.popular_banco' antes de usar o RepositorioSQLite."
            )

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho_banco)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON;")
        return conexao

    # --- Conversores: linha do SQLite -> dict no formato usado pelo resto do sistema ---

    @staticmethod
    def _contribuinte_para_dict(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "nome": row["nome"],
            "cpf_cnpj": row["cpf_cnpj"],
            "email": row["email"],
            "telefone": row["telefone"],
            "tipo_pessoa": row["tipo_pessoa"],
        }

    @staticmethod
    def _imovel_para_dict(row: sqlite3.Row, cpf_cnpj_proprietario: str) -> Dict[str, Any]:
        return {
            "inscricao_cci": row["inscricao_imobiliaria"],
            "endereco": row["endereco"],
            "tipo_imovel": row["tipo_imovel"],
            "valor_venal": row["valor_venal"],
            "cpf_cnpj_proprietario": cpf_cnpj_proprietario,
            "bairro": row["bairro"],
            "cep": row["cep"],
        }

    @staticmethod
    def _divida_para_dict(row: sqlite3.Row, inscricao_cci: str, cpf_cnpj_contribuinte: str) -> Dict[str, Any]:
        juros_multa = round(row["valor_atualizado"] - row["valor_original"], 2)
        return {
            "codigo_debito": f"DIVIDA-{row['id_divida']}",
            "ano_exercicio": row["exercicio_ano"],
            "valor_original": row["valor_original"],
            "juros_multa": juros_multa,
            "status": row["status_divida"],
            "inscricao_cci": inscricao_cci,
            "cpf_cnpj_contribuinte": cpf_cnpj_contribuinte,
            "tipo_tributo": row["tipo_tributo"],
        }

    @staticmethod
    def _processo_para_dict(row: sqlite3.Row, codigo_debito: str, cpf_cnpj_contribuinte: str) -> Dict[str, Any]:
        return {
            "numero_processo": row["numero_processo"],
            "vara": row["vara_judicial"],
            "data_autuacao": row["data_ajuizamento"],
            "codigo_debito": codigo_debito,
            "cpf_cnpj_contribuinte": cpf_cnpj_contribuinte,
            "status_processo": row["status_processo"],
        }

    # --- Operações usadas pelo BuscaService ---

    def buscar_contribuinte(self, cpf_cnpj: str) -> Optional[Dict[str, Any]]:
        """Busca contribuinte por CPF/CNPJ, formatado ou apenas dígitos."""
        if not cpf_cnpj:
            return None
        alvo_digitos = "".join(filter(str.isdigit, cpf_cnpj))
        with self._conectar() as conexao:
            for row in conexao.execute("SELECT * FROM contribuinte"):
                if "".join(filter(str.isdigit, row["cpf_cnpj"])) == alvo_digitos:
                    return self._contribuinte_para_dict(row)
        return None

    def buscar_imovel(self, inscricao_cci: str) -> Optional[Dict[str, Any]]:
        """Busca imóvel por inscrição imobiliária (CCI)."""
        if not inscricao_cci:
            return None
        with self._conectar() as conexao:
            row = conexao.execute(
                """SELECT imovel.*, contribuinte.cpf_cnpj AS cpf_cnpj_proprietario
                   FROM imovel
                   JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                   WHERE imovel.inscricao_imobiliaria = ?""",
                (inscricao_cci.strip(),),
            ).fetchone()
            if not row:
                return None
            return self._imovel_para_dict(row, row["cpf_cnpj_proprietario"])

    def listar_dividas_por_imovel(self, inscricao_cci: str) -> List[Dict[str, Any]]:
        """Retorna as dívidas (ativas ou ajuizadas) associadas ao imóvel informado."""
        if not inscricao_cci:
            return []
        with self._conectar() as conexao:
            linhas = conexao.execute(
                """SELECT divida.*, imovel.inscricao_imobiliaria, contribuinte.cpf_cnpj AS cpf_cnpj_contribuinte
                   FROM divida
                   JOIN imovel ON imovel.id_imovel = divida.id_imovel
                   JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                   WHERE imovel.inscricao_imobiliaria = ?""",
                (inscricao_cci.strip(),),
            ).fetchall()
            return [
                self._divida_para_dict(row, row["inscricao_imobiliaria"], row["cpf_cnpj_contribuinte"])
                for row in linhas
            ]

    def listar_processos_por_imovel(self, inscricao_cci: str) -> List[Dict[str, Any]]:
        """Retorna os processos de execução fiscal ligados às dívidas do imóvel."""
        if not inscricao_cci:
            return []
        with self._conectar() as conexao:
            linhas = conexao.execute(
                """SELECT processo.*, divida.id_divida AS id_divida_origem,
                          contribuinte.cpf_cnpj AS cpf_cnpj_contribuinte
                   FROM processo
                   JOIN divida ON divida.id_divida = processo.id_divida
                   JOIN imovel ON imovel.id_imovel = divida.id_imovel
                   JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                   WHERE imovel.inscricao_imobiliaria = ?""",
                (inscricao_cci.strip(),),
            ).fetchall()
            return [
                self._processo_para_dict(
                    row, f"DIVIDA-{row['id_divida_origem']}", row["cpf_cnpj_contribuinte"]
                )
                for row in linhas
            ]

    def listar_imoveis_por_contribuinte(self, cpf_cnpj: str) -> List[Dict[str, Any]]:
        """Retorna os imóveis vinculados a um contribuinte."""
        contribuinte = self.buscar_contribuinte(cpf_cnpj)
        if not contribuinte:
            return []
        with self._conectar() as conexao:
            linhas = conexao.execute(
                """SELECT imovel.* FROM imovel
                   JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte
                   WHERE contribuinte.cpf_cnpj = ?""",
                (contribuinte["cpf_cnpj"],),
            ).fetchall()
            return [self._imovel_para_dict(row, contribuinte["cpf_cnpj"]) for row in linhas]

    # --- Coleções usadas diretamente pela fila de cobrança e pelo grafo ---

    @property
    def contribuintes(self) -> Dict[str, Dict[str, Any]]:
        with self._conectar() as conexao:
            return {
                row["cpf_cnpj"]: self._contribuinte_para_dict(row)
                for row in conexao.execute("SELECT * FROM contribuinte")
            }

    @property
    def imoveis(self) -> Dict[str, Dict[str, Any]]:
        with self._conectar() as conexao:
            linhas = conexao.execute(
                """SELECT imovel.*, contribuinte.cpf_cnpj AS cpf_cnpj_proprietario
                   FROM imovel
                   JOIN contribuinte ON contribuinte.id_contribuinte = imovel.id_contribuinte"""
            ).fetchall()
            return {
                row["inscricao_imobiliaria"]: self._imovel_para_dict(row, row["cpf_cnpj_proprietario"])
                for row in linhas
            }