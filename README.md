# projetointegradorUFT
Projeto integrador - Sprint 1
## 2.3. Especificação de Requisitos Funcionais (RF)

| ID | Nome do Requisito | Descrição / História de Usuário | Critérios de Aceite (Validação) |
|------|-------------------|--------------------------------|--------------------------------|
| RF01 | Cadastro de Usuário | O sistema deve permitir o registro de servidores com e-mail, nome e senha. | 1. E-mail validado e único. 2. Senha com tamanho mínimo. 3. Mensagem clara de confirmação. |
| RF02 | Autenticação no Sistema | O sistema deve autenticar servidores registrados via credenciais válidas. | 1. Credenciais corretas liberam a sessão. 2. Credenciais inválidas alertam o usuário. |
| RF03 | Controle de Perfis de Acesso | O sistema deve diferenciar perfis (administrador e consulta), restringindo funções. | 1. Admin acessa cálculo e simulação. 2. Perfil consulta só visualiza. 3. Acesso negado é registrado. |
| RF04 | Cadastro de Tributos | O sistema deve permitir cadastrar tipos de tributo (IPTU, ISS, alvarás) com suas regras base. | 1. Cada tributo tem nome, categoria e alíquota base. 2. Não permite tributo duplicado. |
| RF05 | Cálculo de Tarifa/Tributo | O sistema deve calcular o valor de um tributo a partir dos dados informados e da alíquota vigente. | 1. Cálculo retorna valor correto conforme fórmula. 2. Entradas inválidas geram erro claro. |
| RF06 | Simulação de Reajuste | O sistema deve simular reajustes aplicando um percentual ou índice sobre as tarifas atuais. | 1. Usuário informa o percentual/índice. 2. Sistema exibe valor antes e depois. 3. Simulação não altera dados reais. |
| RF07 | Comparação de Cenários | O sistema deve permitir comparar dois ou mais cenários de reajuste lado a lado. | 1. Exibe no mínimo 2 cenários. 2. Mostra diferença absoluta e percentual. |
| RF08 | Histórico de Tarifas | O sistema deve armazenar o histórico de valores e reajustes aplicados a cada tributo. | 1. Cada alteração registra data e valor. 2. Histórico consultável por tributo. |
| RF09 | Relatório de Arrecadação Estimada | O sistema deve gerar relatório com a arrecadação estimada por tributo após um reajuste. | 1. Relatório soma valores por categoria. 2. Exportável (CSV/PDF). |
| RF10 | Painel de Indicadores | O sistema deve exibir um painel com indicadores-chave (total por tributo, variação, projeção). | 1. Painel carrega dados atualizados. 2. Exibe ao menos 3 indicadores. |
| RF11 | Registro de Log de Operações | O sistema deve registrar as ações críticas (cálculo, simulação, alteração) com autor e data. | 1. Cada operação gera log. 2. Log identifica o usuário responsável. |

## 2.4. Requisitos Não Funcionais (RNF)

| ID | Categoria | Descrição da Restrição | Métrica / Forma de Teste |
|-------|-----------|------------------------|--------------------------|
| RNF01 | Tecnologia / Backend | O sistema deve ser desenvolvido obrigatoriamente utilizando a linguagem Python. | Compatível com Python 3.12+. |
| RNF02 | Portabilidade | As dependências devem estar isoladas e descritas em arquivo de manifesto de pacotes. | Instalação com comando padrão via requirements.txt. |
| RNF03 | Usabilidade | O sistema deve fornecer mensagens claras de sucesso ou erro para todas as ações do usuário. | Feedback visual/textual imediato em todas as operações. |
| RNF04 | Documentação | O README.md deve conter instruções completas de instalação, configuração e execução. | Reprodutibilidade do setup por terceiros sem erros. |
| RNF05 | Segurança | As senhas dos usuários devem ser armazenadas de forma criptografada, nunca em texto puro. | Verificação de que a senha gravada está com hash. |
