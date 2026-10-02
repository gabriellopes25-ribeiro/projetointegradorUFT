-- ===================================================
-- ESTRUTURA DO BANCO DE DADOS - PROJETO INTEGRADOR UFT
-- ===================================================

-- 1. TABELA CONTRIBUINTE
CREATE TABLE contribuinte (
    id_contribuinte INT AUTO_INCREMENT PRIMARY KEY,
    cpf_cnpj VARCHAR(18) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
        tipo_pessoa VARCHAR(10) DEFAULT 'FISICA',
    email VARCHAR(100),
    telefone VARCHAR(20),
    endereco_correspondencia VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELA IMÓVEL
CREATE TABLE imovel (
    id_imovel INT AUTO_INCREMENT PRIMARY KEY,
    inscricao_imobiliaria VARCHAR(50) NOT NULL UNIQUE,
    id_contribuinte INT NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    bairro VARCHAR(100),
    cep VARCHAR(10),
        tipo_imovel VARCHAR(20) DEFAULT 'RESIDENCIAL',
    valor_venal DECIMAL(12, 2),
    area_terreno DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_contribuinte) REFERENCES contribuinte(id_contribuinte) ON DELETE CASCADE
);

-- 3. TABELA DÍVIDA
CREATE TABLE divida (
    id_divida INT AUTO_INCREMENT PRIMARY KEY,
    id_imovel INT NOT NULL,
    exercicio_ano INT NOT NULL,
    valor_original DECIMAL(10, 2) NOT NULL,
    valor_atualizado DECIMAL(10, 2) NOT NULL,
    tipo_tributo VARCHAR(50) DEFAULT 'IPTU',
    status_divida VARCHAR(30) DEFAULT 'EM_ABERTO',
    data_vencimento DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_imovel) REFERENCES imovel(id_imovel) ON DELETE CASCADE
);

-- 4. TABELA PROCESSO
CREATE TABLE processo (
    id_processo INT AUTO_INCREMENT PRIMARY KEY,
    numero_processo VARCHAR(50) NOT NULL UNIQUE,
    id_divida INT NOT NULL,
    vara_judicial VARCHAR(100),
    status_processo VARCHAR(50) DEFAULT 'EM_ANDAMENTO',
    data_ajuizamento DATE NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_divida) REFERENCES divida(id_divida) ON DELETE CASCADE
);