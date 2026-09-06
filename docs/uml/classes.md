# Diagrama de classes

Classes e campos abaixo existem no código. Métodos dos serviços e repositórios são abstratos. As dependências tracejadas dos serviços para repositórios representam **colaboração planejada**, ainda sem ligação executável. As relações de histórico e simulação expressam referências por id; não são chaves estrangeiras já configuradas.

```mermaid
classDiagram
    class Perfil {
        <<enumeration>>
        ADMINISTRADOR
        CONSULTA
    }
    class Usuario {
        str id
        str nome
        str email
        str senha_hash
        Perfil perfil
    }
    class Tributo {
        str id
        str nome
        str categoria
        Decimal aliquota_base
        __post_init__()
    }
    class Simulacao {
        str id
        str tributo_id
        str usuario_id
        Decimal percentual_reajuste
        Decimal valor_antes
        Decimal valor_depois
        datetime criada_em
    }
    class Historico {
        str id
        str tributo_id
        str usuario_id
        Decimal valor_anterior
        Decimal valor_atual
        datetime alterado_em
    }
    class AutenticacaoService {
        <<abstract>>
        cadastrar(nome, email, senha) Usuario
        autenticar(email, senha) Usuario
        verificar_permissao(usuario, perfil_necessario)
    }
    class TributoService {
        <<abstract>>
        cadastrar(tributo)
    }
    class CalculoService {
        <<abstract>>
        calcular(tributo, base_calculo) Decimal
    }
    class SimulacaoService {
        <<abstract>>
        simular(tributo_id, usuario_id, valor_atual, percentual) Simulacao
        comparar(cenarios) list
    }
    class RelatorioService {
        <<abstract>>
        gerar_csv(simulacoes) str
        gerar_pdf(simulacoes) bytes
    }
    class UsuarioRepository {
        <<abstract>>
        salvar(usuario)
        buscar_por_email(email) Usuario
    }
    class TributoRepository {
        <<abstract>>
        salvar(tributo)
        buscar_por_nome(nome) Tributo
    }
    Usuario --> Perfil : tem perfil
    Simulacao --> Tributo : referencia por id
    Simulacao --> Usuario : referencia por id
    Historico --> Tributo : referencia por id
    Historico --> Usuario : referencia por id
    AutenticacaoService ..> Usuario : recebe ou retorna
    AutenticacaoService ..> UsuarioRepository : uso futuro
    TributoService ..> Tributo : recebe
    TributoService ..> TributoRepository : uso futuro
    CalculoService ..> Tributo : recebe
    SimulacaoService ..> Simulacao : recebe ou retorna
    RelatorioService ..> Simulacao : recebe
```

## Como ler
Uma caixa representa uma classe; a parte interna lista dados e operações. A seta com “referencia por id” significa que um registro guarda o identificador do outro. A seta tracejada indica uso/dependência, não herança. abstract significa que falta uma classe concreta implementar os métodos.

buscar_por_email e buscar_por_nome também podem retornar None. Tipos de coleções foram abreviados para facilitar a leitura; os detalhes estão no [espelho do código](../src/README.md).

Não incluímos View, Controller ou Banco como classes existentes. Funções de validação não são classes: veja [validacoes](../src/utils/validacoes.md). Multiplicidades e integridade das relações precisarão ser definidas quando a persistência for modelada.
