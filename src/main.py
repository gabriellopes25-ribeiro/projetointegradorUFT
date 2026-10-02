"""Ponto de entrada demonstrativo do backend do SITRIB.

Mostra, de ponta a ponta, a Tabela Hash, o Heap (fila de cobrança) e o
Grafo funcionando juntos por trás do BuscaService — agora lendo os dados
do banco SQLite real (sitrib.db), e não mais de dados fictícios em memória.
"""

from pathlib import Path

from src.services.busca_service import BuscaService
from src.repositories.sqlite_repository import RepositorioSQLite

CAMINHO_BANCO = Path(__file__).resolve().parent.parent / "sitrib.db"


def construir_servico() -> BuscaService:
    """
    Usa o banco SQLite real (sitrib.db) quando ele já foi criado e populado
    (via 'python -m scripts.popular_banco'). Caso contrário, cai de volta
    para os dados simulados em memória, para que a demonstração não quebre.
    """
    if CAMINHO_BANCO.exists():
        print(f"[Persistência] Usando banco de dados real: {CAMINHO_BANCO}")
        return BuscaService(repositorio=RepositorioSQLite(CAMINHO_BANCO))
    print("[Persistência] sitrib.db não encontrado — usando dados simulados em memória.")
    print("  (rode 'python -m scripts.popular_banco' para usar o banco real)")
    return BuscaService()


def main() -> None:
    servico = construir_servico()

    print("=" * 60)
    print("SITRIB — Demonstração da orquestração das estruturas de dados")
    print("=" * 60)

    cpf_exemplo = "123.456.789-01"
    contribuinte = servico.buscar_contribuinte(cpf_exemplo)
    print(f"\n[Hash] Contribuinte encontrado: {contribuinte['nome']}")
    servico.buscar_contribuinte(cpf_exemplo)
    print("[Hash] Segunda busca ao mesmo CPF veio da cache (O(1)).")

    servico.montar_fila_cobranca()
    proximo = servico.proximo_a_cobrar()
    print(f"\n[Heap] Próximo contribuinte a ser cobrado: {proximo}")

    relacionamentos = servico.buscar_relacionamentos(cpf_exemplo)
    print(f"\n[Grafo] Relacionamentos de {contribuinte['nome']}:")
    for rel in relacionamentos:
        print(f"  - Imóvel: {rel['imovel']} | Processo: {rel['processo']}")

    print("\nBackend orquestrado com sucesso, lendo dados persistidos de verdade.")


if __name__ == "__main__":
    main()