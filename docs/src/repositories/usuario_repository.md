# UsuarioRepository

**Código:** [repositories/usuario_repository.py](../../../src/repositories/usuario_repository.py) · **Requisitos:** RF01–RF02

## Estado atual
Contrato abstrato; banco não escolhido.

## Responsabilidade e conteúdo
salvar(usuario) retorna None; buscar_por_email(email) retorna Usuario ou None.

## Com quem trabalha
AutenticacaoService deverá depender desse contrato; uma implementação concreta fará acesso ao armazenamento.

## Limites e cuidados
None significa não encontrado. Definir normalização e unicidade; nunca persistir senha em texto puro. O repositório não decide autorização nem exibe mensagens na tela.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
