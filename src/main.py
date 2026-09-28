"""Ponto de entrada demonstrativo do backend do SITRIB.

Mostra, de ponta a ponta, a Tabela Hash, o Heap (fila de cobrança) e o
Grafo funcionando juntos por trás do BuscaService.
"""

from src.services.busca_service import BuscaService


def main() -> None:
    servico = BuscaService()

    print("=" * 60)
    print("SITRIB — Demonstração da orquestração das estruturas de dados")
    print("=" * 60)

    # 1. Tabela Hash: primeira busca vai à base, a segunda vem da cache O(1)
    cpf_exemplo = "123.456.789-01"
    contribuinte = servico.buscar_contribuinte(cpf_exemplo)
    print(f"\n[Hash] Contribuinte encontrado: {contribuinte['nome']}")
    servico.buscar_contribuinte(cpf_exemplo)  # segunda busca, já vem da cache
    print("[Hash] Segunda busca ao mesmo CPF veio da cache (O(1)).")

    # 2. Heap: monta a fila de cobrança e mostra o próximo a ser cobrado
    servico.montar_fila_cobranca()
    proximo = servico.proximo_a_cobrar()
    print(f"\n[Heap] Próximo contribuinte a ser cobrado: {proximo}")

    # 3. Grafo: mostra imóveis e processos ligados ao mesmo contribuinte
    relacionamentos = servico.buscar_relacionamentos(cpf_exemplo)
    print(f"\n[Grafo] Relacionamentos de {contribuinte['nome']}:")
    for rel in relacionamentos:
        print(f"  - Imóvel: {rel['imovel']} | Processo: {rel['processo']}")

    print("\nBackend orquestrado com sucesso.")


if __name__ == "__main__":
    main()