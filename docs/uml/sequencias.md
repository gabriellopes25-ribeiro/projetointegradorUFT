# Diagramas de sequência

Leia de cima para baixo: cada coluna é um participante e cada seta é uma
mensagem. Setas de volta mostram respostas. alt separa caminhos alternativos.

**Todos os fluxos abaixo são planejados.** Hoje só a criação e a validação
básica de Tributo têm execução concreta. View, Controller, banco, sessão,
hashing e Log são participantes futuros. As chamadas descritivas, sem nome
de método Python, ainda não são contratos implementados.

## 1. Cadastro de usuário — RF01
```mermaid
sequenceDiagram
    actor P as Pessoa
    participant V as View futura
    participant C as Controller futuro
    participant S as AutenticacaoService futuro
    participant R as UsuarioRepository futuro
    P->>V: Informar nome, email e senha
    V->>C: Enviar cadastro
    C->>S: cadastrar(nome, email, senha)
    S->>S: Validar email e política de senha
    alt Dados inválidos
        S-->>C: Erro de validação
        C-->>V: Mensagem clara
    else Dados válidos
        S->>R: buscar_por_email(email)
        R-->>S: Usuario ou None
        alt Email já cadastrado
            S-->>C: Cadastro recusado
            C-->>V: Mensagem de duplicidade
        else Email disponível
            S->>S: Gerar hash e criar Usuario com perfil consulta
            S->>R: salvar(usuario)
            Note over S,R: Persistência deve garantir unicidade também em concorrência
            R-->>S: Confirmação
            S-->>C: Usuario
            C-->>V: Confirmação sem senha_hash
        end
    end
```

Nunca devolver a entidade completa com hash à tela. Definir posteriormente
o formato da resposta e o tratamento de falhas de gravação.

## 2. Autenticação e autorização — RF02–RF03
```mermaid
sequenceDiagram
    actor P as Servidor
    participant C as Controller futuro
    participant S as AutenticacaoService futuro
    participant R as UsuarioRepository futuro
    participant L as Log futuro
    P->>C: Informar credenciais
    C->>S: autenticar(email, senha)
    S->>R: buscar_por_email(email)
    R-->>S: Usuario ou None
    S->>S: Verificar hash quando houver usuário
    alt Credenciais inválidas
        S-->>C: Falha de autenticação
        C-->>P: Credenciais inválidas
    else Credenciais válidas
        S-->>C: Usuario
        C->>C: Criar sessão por mecanismo ainda a definir
        C-->>P: Sessão liberada
        P->>C: Solicitar cálculo ou simulação
        C->>S: verificar_permissao(usuario, ADMINISTRADOR)
        alt Acesso negado
            S->>L: Registrar negação com autor e data
            S-->>C: Erro de permissão
            C-->>P: Acesso negado
        else Acesso permitido
            S-->>C: Permissão confirmada
            C->>C: Encaminhar ao serviço da operação
        end
    end
```

Login identifica a pessoa; autorização decide o que ela pode fazer. São
verificações diferentes, mesmo que o contrato inicial as reúna no mesmo serviço.

## 3. Cadastro de tributo — RF04
```mermaid
sequenceDiagram
    actor P as Pessoa autorizada
    participant C as Controller futuro
    participant T as Tributo existente
    participant S as TributoService futuro
    participant R as TributoRepository futuro
    P->>C: Enviar dados de tributo
    Note over P,C: Autorização de cadastro ainda deve ser definida e verificada
    C->>T: Criar com id, nome, categoria e Decimal
    T->>T: Validar campos em __post_init__
    alt Campo inválido
        T-->>C: ValueError com motivo
        C-->>P: Corrigir dados
    else Dados básicos válidos
        T-->>C: Entidade válida
        C->>S: cadastrar(tributo)
        S->>R: buscar_por_nome(tributo.nome)
        R-->>S: Tributo ou None
        alt Duplicado
            S-->>C: Erro de duplicidade
            C-->>P: Cadastro recusado
        else Disponível
            S->>R: salvar(tributo)
            Note over S,R: Armazenamento também deverá impor unicidade
            R-->>S: Confirmação
            S-->>C: Concluído
            C-->>P: Cadastro confirmado
        end
    end
```

A entidade não salva a si mesma. O serviço coordena e o repositório salva.
A conversão dos dados da interface para Decimal também precisa tratar entrada inválida.

## 4. Simulação e comparação — RF06–RF07 e RF11
```mermaid
sequenceDiagram
    actor A as Administrador
    participant C as Controller futuro
    participant S as SimulacaoService futuro
    participant M as Simulacao
    participant L as Log futuro
    Note over A,C: Sessão e permissão verificadas antes deste fluxo
    A->>C: Informar tributo, valor e reajuste
    C->>S: simular(tributo_id, usuario_id, valor_atual, percentual)
    S->>S: Validar entradas e calcular conforme regra aprovada
    S->>M: Criar cenário com antes, depois e data
    M-->>S: Simulacao
    S->>L: Registrar simulação com autor e data
    S-->>C: Simulacao
    C-->>A: Exibir antes e depois
    Note over S,M: Não salvar alterações reais no tributo ou em Historico
    A->>C: Selecionar cenários
    C->>S: comparar(cenarios)
    alt Menos de dois ou incompatíveis
        S-->>C: Erro de comparação
        C-->>A: Mensagem clara
    else Cenários válidos
        S->>S: Calcular diferenças absoluta e percentual
        Note over S: Regra para referência zero ainda pendente
        S-->>C: Resultados de comparação
        C-->>A: Exibir lado a lado
    end
```

## Fluxos que ainda precisam ser detalhados
- RF05: após autorização, chamar calcular(tributo, base_calculo), tratar entradas inválidas, registrar autor/data e apresentar valor. A fórmula ainda precisa de aprovação.
- RF08: alteração real e gravação do histórico devem ser coordenadas; a persistência e sua transação ainda não estão desenhadas.
- RF09: reunir categorias e quantidades antes de chamar geração CSV/PDF. O contrato atual precisa evoluir para atender essa necessidade.
- RF10: definir as fontes e os três indicadores antes de desenhar a sequência.
- RF11: definir armazenamento do log e comportamento em caso de falha.

Não transformar estes diagramas em código sem resolver as pendências listadas em
[produto.md](../produto.md). Eles orientam a conversa e não comprovam aceitação.
