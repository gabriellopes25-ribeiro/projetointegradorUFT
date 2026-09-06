# AutenticacaoService

**Código:** [services/autenticacao_service.py](../../../src/services/autenticacao_service.py) · **Requisitos:** RF01–RF03

## Estado atual
Contrato abstrato; nenhuma operação implementada.

## Responsabilidade e conteúdo
cadastrar(nome, email, senha) retorna Usuario; autenticar(email, senha) retorna Usuario; verificar_permissao(usuario, perfil_necessario) retorna None se permitido na implementação futura.

## Com quem trabalha
Deverá usar Usuario, Perfil e UsuarioRepository; sessão, hashing e logs precisam ser definidos.

## Limites e cuidados
Não pode ser instanciado diretamente. Retornar Usuario não cria uma sessão. Definir erro de acesso negado e seu registro; a matriz de permissões não se reduz necessariamente à igualdade entre perfis.

## Veja também
[Mapa de classes](../../uml/classes.md) · [Fluxos de sequência](../../uml/sequencias.md) · [Casos de uso](../../uml/casos-de-uso.md) · [Índice do código](../README.md)
