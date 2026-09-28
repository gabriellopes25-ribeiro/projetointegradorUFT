"""
Serviço de Busca e Validação Cadastral e Fiscal (SITRIB).

Responsável: Adriel Morais (PO / Dev)
Camada: Service (MVC)

Fornece operações de busca unificada e validação para:
  - Contribuinte (por CPF ou CNPJ)
  - Imóveis, Dívidas e Processos de Execução Fiscal associados

Projetado para operar em modo simulado (com massa de seeds) ou integrado ao
repositório/banco de dados real quando implementado pela equipe.
"""

from typing import Any, Dict, List, Optional
import re
from seeds.mock_data import BancoSimuladoEmMemoria
from src.estruturas.tabela_hash import TabelaHashDivida
from src.estruturas.fila_cobranca import FilaCobranca
from src.estruturas.grafo import GrafoContribuintes


class DocumentoInvalidoError(ValueError):
    """Lançada quando um CPF ou CNPJ possui formato ou dígitos inválidos."""
    pass


class ContribuinteNaoEncontradoError(LookupError):
    """Lançada quando um contribuinte não é localizado na base cadastral."""
    pass


class ImovelNaoEncontradoError(LookupError):
    """Lançada quando uma inscrição imobiliária (CCI) não é encontrada."""
    pass


def normalizar_documento(doc: str) -> str:
    """Remove caracteres não numéricos de CPF ou CNPJ."""
    if not isinstance(doc, str):
        raise DocumentoInvalidoError("Documento deve ser informado como texto.")
    apenas_digitos = re.sub(r"\D", "", doc.strip())
    if len(apenas_digitos) not in (11, 14):
        raise DocumentoInvalidoError(
            f"Documento inválido. Esperado CPF (11 dígitos) ou CNPJ (14 dígitos), recebido: {doc}"
        )
    return apenas_digitos


class BuscaService:
    """
    Camada de serviço responsável pelas consultas fiscais e cruzamento de informações.
    Recebe um repositório ou banco de dados (por padrão, o BancoSimuladoEmMemoria).
    """

    def __init__(self, repositorio: Optional[Any] = None) -> None:
        if repositorio is None:
            self.repo = BancoSimuladoEmMemoria()
            self.repo.carregar_dados_iniciais()
        else:
            self.repo = repositorio
        self.cache_contribuintes = TabelaHashDivida()

    def buscar_contribuinte(self, cpf_cnpj: str) -> Dict[str, Any]:
        """
        Busca contribuinte por CPF ou CNPJ.
        Valida a formatação e lança ContribuinteNaoEncontradoError se não existir.
        """
        if not cpf_cnpj or not str(cpf_cnpj).strip():
            raise DocumentoInvalidoError("CPF/CNPJ não pode ser vazio.")

        # Valida se é CPF ou CNPJ válido em quantidade de dígitos
        cpf_normalizado = normalizar_documento(cpf_cnpj)

        # Primeiro consulta a cache (tabela hash) — é instantâneo
        em_cache = self.cache_contribuintes.buscar(cpf_normalizado)
        if em_cache != "CPF não encontrado":
            return em_cache

        # Não estava na cache: busca na base e guarda na cache pra próxima vez
        resultado = self.repo.buscar_contribuinte(cpf_cnpj)
        if not resultado:
            raise ContribuinteNaoEncontradoError(
                f"Contribuinte com documento '{cpf_cnpj}' não foi encontrado."
            )
        self.cache_contribuintes.inserir(cpf_normalizado, resultado)
        return resultado

    def buscar_imovel(self, inscricao_cci: str) -> Dict[str, Any]:
        """Busca imóvel por inscrição imobiliária."""
        if not inscricao_cci or not str(inscricao_cci).strip():
            raise ValueError("Inscrição do imóvel (CCI) não pode ser vazia.")

        imovel = self.repo.buscar_imovel(inscricao_cci.strip())
        if not imovel:
            raise ImovelNaoEncontradoError(
                f"Imóvel com inscrição '{inscricao_cci}' não foi encontrado."
            )
        return imovel

    def listar_dividas_e_processos_imovel(self, inscricao_cci: str) -> Dict[str, Any]:
        """
        Retorna o dossiê fiscal completo de um imóvel:
        - Dados cadastrais do imóvel
        - Lista de dívidas em aberto / ajuizadas
        - Lista de processos de execução fiscal vinculados
        """
        imovel = self.buscar_imovel(inscricao_cci)
        dividas = self.repo.listar_dividas_por_imovel(imovel["inscricao_cci"])
        processos = self.repo.listar_processos_por_imovel(imovel["inscricao_cci"])

        total_debito = round(sum(d.get("valor_original", 0) + d.get("juros_multa", 0) for d in dividas), 2)

        return {
            "imovel": imovel,
            "total_dividas": len(dividas),
            "valor_total_devido": total_debito,
            "dividas": dividas,
            "total_processos": len(processos),
            "processos": processos,
        }

    def montar_fila_cobranca(self) -> FilaCobranca:
        """
        Monta a fila de cobrança priorizando contribuintes com maior valor
        devido e com processos judiciais em andamento (que pesam mais).
        """
        fila = FilaCobranca()
        for cpf, _contribuinte in self.repo.contribuintes.items():
            imoveis = self.repo.listar_imoveis_por_contribuinte(cpf)
            valor_total = 0.0
            tem_processo = False
            for imovel in imoveis:
                dividas = self.repo.listar_dividas_por_imovel(imovel["inscricao_cci"])
                valor_total += sum(d["valor_original"] + d["juros_multa"] for d in dividas)
                if self.repo.listar_processos_por_imovel(imovel["inscricao_cci"]):
                    tem_processo = True
            if valor_total <= 0:
                continue
            score = valor_total + (5000 if tem_processo else 0)
            fila.inserir(round(score, 2), cpf)
        self.fila_cobranca = fila
        return fila

    def proximo_a_cobrar(self) -> Any:
        """Retorna o próximo contribuinte a ser cobrado, por ordem de prioridade."""
        if not hasattr(self, "fila_cobranca"):
            self.montar_fila_cobranca()
        return self.fila_cobranca.proximo_a_cobrar()

    def _construir_grafo(self) -> GrafoContribuintes:
        """
        Popula o grafo com as relações contribuinte -> imóvel -> processo,
        permitindo identificar quando o mesmo CPF/CNPJ aparece em
        múltiplas inscrições e processos de execução fiscal.
        """
        grafo = GrafoContribuintes()
        for imovel in self.repo.imoveis.values():
            cpf_cnpj = imovel["cpf_cnpj_proprietario"]
            processos = self.repo.listar_processos_por_imovel(imovel["inscricao_cci"])
            if processos:
                for processo in processos:
                    grafo.adicionar_relacao(cpf_cnpj, imovel["inscricao_cci"], processo["numero_processo"])
            else:
                grafo.adicionar_relacao(cpf_cnpj, imovel["inscricao_cci"], None)
        self.grafo = grafo
        return grafo

    def buscar_relacionamentos(self, cpf_cnpj: str) -> List[Dict[str, Any]]:
        """
        Retorna todos os imóveis e processos ligados a um contribuinte —
        útil para detectar o mesmo CPF/CNPJ em várias inscrições.
        """
        contribuinte = self.buscar_contribuinte(cpf_cnpj)
        if not hasattr(self, "grafo"):
            self._construir_grafo()
        return self.grafo.buscar_relacionados(contribuinte["cpf_cnpj"])