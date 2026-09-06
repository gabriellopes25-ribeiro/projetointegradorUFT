# Arquitetura Inicial do Sistema

## Objetivo e escopo
Preparar o backend Python para os requisitos RF01–RF11 e RNF01–RNF05 descritos no README. Esta entrega contém entidades, contratos abstratos, validações básicas de Tributo e testes. Não entrega autenticação, banco de dados, API nem cálculo de tributos.

## Organização e decisões
- **Models:** Usuario, Tributo, Simulacao e Historico representam os dados do domínio. Dataclasses imutáveis evitam alterações acidentais.
- **Services:** contratos abstratos delimitam autenticação, cadastro, cálculo, simulação, comparação e relatórios. Não podem ser instanciados sem implementação.
- **Repositories:** contratos de acesso a usuários e tributos permitem escolher a persistência sem acoplar as regras de negócio ao banco.
- **Utils:** valida textos obrigatórios e valores Decimal finitos não negativos em Tributo; as demais políticas ainda precisam ser definidas.
- **Tests:** verificam a estrutura disponível e as validações de Tributo. Não comprovam o atendimento dos requisitos funcionais.

Valores monetários, alíquotas e percentuais usam Decimal. Alíquotas são expressas em percentual (1.25 significa 1,25%). Fórmulas por tributo, arredondamento e limites de entrada serão definidos antes da implementação de RF05.

Usuario possui senha_hash, omitido da representação textual. Isso não implementa hashing nem valida que o conteúdo seja um hash: RNF05 continua pendente. O serviço futuro deverá gerar e verificar hashes com algoritmo apropriado e nunca persistir a senha recebida. O perfil padrão é consulta; autorização e cadastro de administradores ainda serão implementados.

Simulacao representa um cenário hipotético separado do Historico de alterações reais. Datas deverão usar fuso horário explícito na implementação. Repositórios de histórico/simulações e transações serão adicionados quando a persistência for definida.

## Fluxo previsto
Usuário → Interface/API → Services → Models / Repositories → Persistência

Interface/API, injeção dos repositórios e persistência são etapas futuras. src/main.py apenas confirma que a estrutura pode ser executada.

## Relação com requisitos
| Componente | Requisitos |
|---|---|
| Usuario / AutenticacaoService | RF01, RF02, RF03 |
| Tributo / TributoService | RF04 |
| CalculoService | RF05 |
| Simulacao / SimulacaoService | RF06, RF07 |
| Historico | RF08 |
| RelatorioService | RF09 |
| Dashboard (futuro) | RF10 |
| Log (futuro) | RF11, registro de acesso negado de RF03 |

## Próximas decisões da equipe
Definir política de senha, normalização e unicidade de e-mails/tributos, banco, sessão, matriz de permissões e regras de cálculo. Detalhar o resultado da comparação (referência, diferenças e base zero) e os dados necessários à arrecadação estimada (categorias e quantidades). Os contratos iniciais podem ser refinados nessas entregas.

## Guia técnico
Consulte [desenvolvimento.md](desenvolvimento.md) para execução, regras implementadas e próximos passos. O README da aplicação fica com Rayssa e João.


## Navegação e relação com MVC
Esta organização em camadas ainda não possui View nem Controller. Consulte
[MVC e camadas](mvc-e-camadas.md) para entender a relação sem confundir os
conceitos. O [guia da equipe](README.md) reúne o espelho dos arquivos Python,
os diagramas e as decisões pendentes do Product Owner.
