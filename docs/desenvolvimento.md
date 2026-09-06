# Guia de desenvolvimento

## Escopo da contribuição
Estrutura do backend, documentação técnica e validações iniciais de Tributo.
O README da aplicação fica a cargo de Rayssa e João.

## Preparação local
Requer Python 3.12+. Na raiz do repositório, usando PowerShell:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

Só a biblioteca padrão é usada nesta etapa. Não há banco, servidor ou credenciais
a configurar. O ponto de entrada apenas informa o estado do backend.

## Validações implementadas
Tributo rejeita id, nome e categoria que não sejam textos ou estejam vazios,
inclusive quando contêm apenas espaços. Os valores válidos são preservados,
sem normalização automática.

A alíquota deve ser Decimal, finita e não negativa. Zero é permitido.
Float e string não são convertidos automaticamente. O uso de Decimal("1.25")
representa uma alíquota de 1,25%. Não foi definido teto de alíquota: esse limite
depende das regras que a equipe ainda vai especificar.

Entradas inválidas geram ValueError com o campo e o motivo. Essa validação
não cadastra tributos e não verifica duplicidade; essas etapas dependem do
serviço e da persistência futuros.

## Próximos passos
1. Definir regras por categoria de tributo e política de arredondamento.
2. Implementar cadastro e unicidade usando o contrato do repositório.
3. Implementar cálculo e substituir o teste ignorado por casos de aceite.
4. Adicionar autenticação, autorização e armazenamento seguro de senhas.

## Verificação
Os testes cobrem textos inválidos, alíquotas negativas, não finitas, tipos
incorretos, zero, precisão decimal e imutabilidade. Também verificam o perfil
padrão de usuário e o contrato abstrato de cálculo. O teste funcional de RF05
continua ignorado, pois não existe implementação desse serviço.
