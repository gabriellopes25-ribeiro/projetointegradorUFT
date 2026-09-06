# Usuario e Perfil

**Código:** [models/usuario.py](../../../src/models/usuario.py) · **Requisitos:** RF01–RF03

## Estado atual
Entidades existentes; autenticação e validação de cadastro pendentes.

## Responsabilidade e conteúdo
Usuario contém id, nome, email, senha_hash e perfil. Perfil define administrador e consulta; consulta é o padrão.

## Com quem trabalha
AutenticacaoService deverá criar e autenticar usuários usando UsuarioRepository.

## Limites e cuidados
O campo senha_hash é omitido da representação textual, mas isso não gera nem verifica hashes. Nunca enviar esse campo à View. Não há autorização pronta.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
