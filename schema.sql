-- ===================================================================================
-- ESTRUTURA DO BANCO DE DADOS OFICIAL POSTGRESQL 16 - PROJETO INTEGRADOR UFT (SITRIB)
-- ===================================================================================
-- Compatível com: PostgreSQL 16+ (Docker / Produção)
-- Inclui:
--   1. Gestão da Dívida Ativa e Execução Fiscal (contribuinte, imovel, divida, processo)
--   2. Base Real do Portal Novo da Prefeitura de Palmas (prefeitura_receitas - 182.800+ registros)
--   3. Base Real Histórica da API Antiga (prefeitura_historico_api_antiga - 2001 a 2021)
-- ===================================================================================

-- 1. TABELA CONTRIBUINTE
CREATE TABLE IF NOT EXISTS contribuinte (
    id_contribuinte SERIAL PRIMARY KEY,
    cpf_cnpj VARCHAR(18) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    tipo_pessoa VARCHAR(10) DEFAULT 'FISICA',
    email VARCHAR(100),
    telefone VARCHAR(20),
    endereco_correspondencia VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELA IMÓVEL (CCI PALMAS)
CREATE TABLE IF NOT EXISTS imovel (
    id_imovel SERIAL PRIMARY KEY,
    inscricao_imobiliaria VARCHAR(50) NOT NULL UNIQUE,
    id_contribuinte INT NOT NULL REFERENCES contribuinte(id_contribuinte) ON DELETE CASCADE,
    endereco VARCHAR(255) NOT NULL,
    bairro VARCHAR(100),
    cep VARCHAR(10),
    tipo_imovel VARCHAR(20) DEFAULT 'RESIDENCIAL',
    valor_venal NUMERIC(14, 2),
    area_terreno NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABELA DÍVIDA ATIVA
CREATE TABLE IF NOT EXISTS divida (
    id_divida SERIAL PRIMARY KEY,
    id_imovel INT NOT NULL REFERENCES imovel(id_imovel) ON DELETE CASCADE,
    exercicio_ano INT NOT NULL,
    valor_original NUMERIC(14, 2) NOT NULL,
    valor_atualizado NUMERIC(14, 2) NOT NULL,
    tipo_tributo VARCHAR(50) DEFAULT 'IPTU',
    status_divida VARCHAR(30) DEFAULT 'EM_ABERTO',
    data_vencimento DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABELA PROCESSO DE EXECUÇÃO FISCAL
CREATE TABLE IF NOT EXISTS processo (
    id_processo SERIAL PRIMARY KEY,
    numero_processo VARCHAR(50) NOT NULL UNIQUE,
    id_divida INT NOT NULL REFERENCES divida(id_divida) ON DELETE CASCADE,
    vara_judicial VARCHAR(100),
    status_processo VARCHAR(50) DEFAULT 'EM_ANDAMENTO',
    data_ajuizamento DATE NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABELA REAL DO PORTAL NOVO (NUCLEOGOV - sgreceitas/listar - 182.808+ REGISTROS)
-- Nota: Separada da tabela da API Antiga conforme Seção 1 do Manual de Coleta
-- e equipada com nivel_hierarquico para evitar a Armadilha 5.4 (dupla contagem 6,6x).
CREATE TABLE IF NOT EXISTS prefeitura_receitas (
    id_receita SERIAL PRIMARY KEY,
    ano INT NOT NULL,
    mes INT NOT NULL,
    orgao VARCHAR(30),
    orgao_nome VARCHAR(255),
    unidade_id VARCHAR(30),
    unidade_nome VARCHAR(255),
    codigo VARCHAR(60) NOT NULL,
    codigo_original VARCHAR(60),
    descricao VARCHAR(255) NOT NULL,
    nivel_hierarquico INT NOT NULL DEFAULT 1,
    eh_raiz_contabil BOOLEAN NOT NULL DEFAULT FALSE,
    valor_orcado NUMERIC(16, 2) DEFAULT 0.00,
    valor_arrecado_mes NUMERIC(16, 2) DEFAULT 0.00,
    valor_arrecado_periodo NUMERIC(16, 2) DEFAULT 0.00,
    covid VARCHAR(10),
    data_coleta DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. TABELA REAL DA API ANTIGA (integracao.palmas.to.gov.br/apirest/ - 2001 a 2021)
-- Armazena registros históricos de arrecadacao/ e gastos-diretos/
CREATE TABLE IF NOT EXISTS prefeitura_historico_api_antiga (
    id_registro SERIAL PRIMARY KEY,
    id_externo BIGINT,
    endpoint_origem VARCHAR(40) NOT NULL DEFAULT 'arrecadacao',
    ano_referencia INT NOT NULL,
    mes_referencia INT NOT NULL DEFAULT 1,
    codigo_conta VARCHAR(60),
    descricao VARCHAR(255),
    unidade_gestora VARCHAR(255),
    fornecedor VARCHAR(255),
    cpf_cnpj_fornecedor VARCHAR(30),
    processo_administrativo VARCHAR(60),
    data_ocorrencia VARCHAR(30),
    valor_previsto_ou_empenhado NUMERIC(16, 2) DEFAULT 0.00,
    valor_realizado_ou_pago NUMERIC(16, 2) DEFAULT 0.00,
    data_coleta DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================================
-- ÍNDICES B-TREE DE ALTA PERFORMANCE PARA CONSULTAS EM 182 MIL+ REGISTROS
-- ===================================================================================
CREATE INDEX IF NOT EXISTS idx_contribuinte_cpf ON contribuinte(cpf_cnpj);
CREATE INDEX IF NOT EXISTS idx_imovel_cci ON imovel(inscricao_imobiliaria);
CREATE INDEX IF NOT EXISTS idx_imovel_contribuinte ON imovel(id_contribuinte);
CREATE INDEX IF NOT EXISTS idx_imovel_bairro ON imovel(bairro);
CREATE INDEX IF NOT EXISTS idx_divida_imovel ON divida(id_imovel);
CREATE INDEX IF NOT EXISTS idx_divida_exercicio ON divida(exercicio_ano);
CREATE INDEX IF NOT EXISTS idx_divida_status ON divida(status_divida);
CREATE INDEX IF NOT EXISTS idx_divida_tipo ON divida(tipo_tributo);
CREATE INDEX IF NOT EXISTS idx_processo_divida ON processo(id_divida);

CREATE INDEX IF NOT EXISTS idx_pref_rec_ano_mes ON prefeitura_receitas(ano, mes);
CREATE INDEX IF NOT EXISTS idx_pref_rec_nivel ON prefeitura_receitas(nivel_hierarquico);
CREATE INDEX IF NOT EXISTS idx_pref_rec_codigo ON prefeitura_receitas(codigo);
CREATE INDEX IF NOT EXISTS idx_pref_rec_orgao ON prefeitura_receitas(orgao);
CREATE INDEX IF NOT EXISTS idx_pref_rec_raiz ON prefeitura_receitas(eh_raiz_contabil);

CREATE INDEX IF NOT EXISTS idx_pref_ant_endpoint_ano ON prefeitura_historico_api_antiga(endpoint_origem, ano_referencia);
CREATE INDEX IF NOT EXISTS idx_pref_ant_codigo ON prefeitura_historico_api_antiga(codigo_conta);
