"""
Módulo de Seeds e Dados Históricos Oficiais (SITRIB - Projeto Integrador UFT).

Responsável: Adriel Morais (PO / Dev)
Finalidade: Fornecer massa de dados histórica completa e verossímil da dívida ativa
do município de Palmas/TO, abrangendo:
  1. Contribuintes (Pessoas Físicas e Jurídicas: Grandes, Médios e Pequenos devedores)
  2. Imóveis (Inscrições CCI nos principais setores de Palmas)
  3. Dívidas Históricas (Exercícios de 2018 a 2026: IPTU, ISS, Taxa de Lixo, etc.)
  4. Processos Judiciais (1ª e 2ª Vara de Execuções Fiscais de Palmas)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger("sitrib.seeds")


# ==============================================================================
# 1. Estruturas Tipadas de Dados (DTOs / Mocks)
# ==============================================================================

@dataclass
class ContribuinteMock:
    nome: str
    cpf_cnpj: str
    email: str
    telefone: str
    tipo_pessoa: str = "FISICA"


@dataclass
class ImovelMock:
    inscricao_cci: str
    endereco: str
    tipo_imovel: str
    valor_venal: float
    cpf_cnpj_proprietario: str
    bairro: str = "Plano Diretor"
    cep: str = "77000-000"


@dataclass
class DividaMock:
    codigo_debito: str
    ano_exercicio: int
    valor_original: float
    juros_multa: float
    status: str
    inscricao_cci: str
    cpf_cnpj_contribuinte: str
    tipo_tributo: str = "IPTU"

    @property
    def valor_total(self) -> float:
        return round(self.valor_original + self.juros_multa, 2)


@dataclass
class ProcessoMock:
    numero_processo: str
    vara: str
    data_autuacao: str
    codigo_debito: str
    cpf_cnpj_contribuinte: str
    status_processo: str = "EM_ANDAMENTO"


# ==============================================================================
# 2. Massa de Dados Histórica Completa (Palmas / TO)
# ==============================================================================

CONTRIBUINTES_SEED: List[Dict[str, Any]] = [
    # --- GRANDES DEVEDORES (PJ / ALTO IMPACTO FISCAL) ---
    {
        "nome": "Construtora Jalapão Empreendimentos S/A",
        "cpf_cnpj": "01.234.567/0001-89",
        "email": "juridico@jalapaoemp.com.br",
        "telefone": "(63) 3219-5000",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Hotel Graciosa & Convenções Ltda",
        "cpf_cnpj": "02.345.678/0001-90",
        "email": "financeiro@hotelgraciosa.com.br",
        "telefone": "(63) 3224-8800",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Tocantins Atacadista de Alimentos S/A",
        "cpf_cnpj": "03.456.789/0001-01",
        "email": "tributario@toatacadista.com.br",
        "telefone": "(63) 3216-3300",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Capim Dourado Shopping Empreendimentos Ltda",
        "cpf_cnpj": "04.567.890/0001-12",
        "email": "fiscal@capimdouradoshopping.com.br",
        "telefone": "(63) 3215-7700",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Auto Posto Serra do Carmo Ltda",
        "cpf_cnpj": "05.678.901/0001-23",
        "email": "gerencia@postoserradocarmo.com.br",
        "telefone": "(63) 3217-1122",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Hospital e Maternidade Palmas Saúde S/A",
        "cpf_cnpj": "06.789.012/0001-34",
        "email": "contabilidade@palmassaude.med.br",
        "telefone": "(63) 3232-9000",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Mineradora e Britadora Tocantins Ltda",
        "cpf_cnpj": "07.890.123/0001-45",
        "email": "financeiro@britadoratocantins.ind.br",
        "telefone": "(63) 3213-4455",
        "tipo_pessoa": "JURIDICA",
    },

    # --- MÉDIOS DEVEDORES (PJ E EMPRESAS LOCAIS) ---
    {
        "nome": "Tocantins Engenharia e Serviços Ltda",
        "cpf_cnpj": "12.345.678/0001-90",
        "email": "contato@toengenharia.com.br",
        "telefone": "(63) 3215-4000",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Araguaia Comércio de Alimentos Eireli",
        "cpf_cnpj": "98.765.432/0001-10",
        "email": "financeiro@araguaiaalimentos.com.br",
        "telefone": "(63) 3218-9900",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Colégio e Faculdade Palmas Prime",
        "cpf_cnpj": "08.901.234/0001-56",
        "email": "diretoria@palmasprime.edu.br",
        "telefone": "(63) 3225-6677",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Transportes e Logística Norte-Sul Eireli",
        "cpf_cnpj": "09.012.345/0001-67",
        "email": "operacoes@nortesullog.com.br",
        "telefone": "(63) 3214-7788",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Supermercado Serra Dourada Ltda",
        "cpf_cnpj": "11.234.567/0001-89",
        "email": "caixa@serradourada.com.br",
        "telefone": "(63) 3216-2244",
        "tipo_pessoa": "JURIDICA",
    },
    {
        "nome": "Restaurante e Churrascaria Portal do Sul",
        "cpf_cnpj": "13.456.789/0001-01",
        "email": "portaldosul@gmail.com",
        "telefone": "(63) 3218-4411",
        "tipo_pessoa": "JURIDICA",
    },

    # --- CONTRIBUINTES PESSOA FÍSICA (PEQUENOS E MÉDIOS) ---
    {
        "nome": "Carlos Eduardo Siqueira",
        "cpf_cnpj": "123.456.789-01",
        "email": "carlos.siqueira@email.com",
        "telefone": "(63) 98111-2030",
        "tipo_pessoa": "FISICA",
    },
    {
        "nome": "Roberto Albuquerque Guimarães",
        "cpf_cnpj": "234.567.890-12",
        "email": "roberto.guimaraes@email.com",
        "telefone": "(63) 99122-4455",
        "tipo_pessoa": "FISICA",
    },
    {
        "nome": "Fernanda Batista Castro",
        "cpf_cnpj": "345.678.901-23",
        "email": "fernanda.castro@email.com",
        "telefone": "(63) 98433-7788",
        "tipo_pessoa": "FISICA",
    },
    {
        "nome": "Juliana Ribeiro Prado",
        "cpf_cnpj": "456.789.012-34",
        "email": "juliana.prado@email.com",
        "telefone": "(63) 98455-1234",
        "tipo_pessoa": "FISICA",
    },
    {
        "nome": "Marcelo Henrique Viana",
        "cpf_cnpj": "567.890.123-45",
        "email": "marcelo.viana@email.com",
        "telefone": "(63) 99255-6677",
        "tipo_pessoa": "FISICA",
    },
    {
        "nome": "Camila Vasconcelos Rios",
        "cpf_cnpj": "678.901.234-56",
        "email": "camila.rios@email.com",
        "telefone": "(63) 98144-8899",
        "tipo_pessoa": "FISICA",
    },
    {
        "nome": "Renato Alencar Fontes",
        "cpf_cnpj": "789.012.345-67",
        "email": "renato.fontes@email.com",
        "telefone": "(63) 99266-1122",
        "tipo_pessoa": "FISICA",
    },
    {
        "nome": "Maria Auxiliadora Fernandes",
        "cpf_cnpj": "987.654.321-09",
        "email": "maria.fernandes@email.com",
        "telefone": "(63) 99222-3040",
        "tipo_pessoa": "FISICA",
    },
]

IMOVEIS_SEED: List[Dict[str, Any]] = [
    # Imóveis de Grandes Devedores
    {
        "inscricao_cci": "CCI-ORLA-14-SUL",
        "endereco": "Orla 14 Sul, Gleba 03, Loteamento Graciosa",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 4500000.00,
        "cpf_cnpj_proprietario": "02.345.678/0001-90",
        "bairro": "Graciosa",
        "cep": "77020-010",
    },
    {
        "inscricao_cci": "CCI-107-NORTE-SHOP",
        "endereco": "Quadra 107 Norte, Avenida NS-05, Lote 01",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 12800000.00,
        "cpf_cnpj_proprietario": "04.567.890/0001-12",
        "bairro": "107 Norte",
        "cep": "77001-080",
    },
    {
        "inscricao_cci": "CCI-IND-DISTRITO-01",
        "endereco": "Distrito Industrial de Palmas, Rodovia TO-050, Lote 45",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 3200000.00,
        "cpf_cnpj_proprietario": "03.456.789/0001-01",
        "bairro": "Distrito Industrial",
        "cep": "77050-000",
    },
    {
        "inscricao_cci": "CCI-POSTO-TEOTONIO",
        "endereco": "Avenida Teotônio Segurado, Quadra 502 Sul, Lote 10",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 2100000.00,
        "cpf_cnpj_proprietario": "05.678.901/0001-23",
        "bairro": "502 Sul",
        "cep": "77016-012",
    },
    {
        "inscricao_cci": "CCI-HOSP-501-SUL",
        "endereco": "Quadra 501 Sul, Avenida LO-11, Lote 04",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 6800000.00,
        "cpf_cnpj_proprietario": "06.789.012/0001-34",
        "bairro": "501 Sul",
        "cep": "77016-004",
    },
    {
        "inscricao_cci": "CCI-MINER-TAQUARALTO",
        "endereco": "Área Especial Taquaralto Sul, Km 12",
        "tipo_imovel": "TERRENO",
        "valor_venal": 1800000.00,
        "cpf_cnpj_proprietario": "07.890.123/0001-45",
        "bairro": "Taquaralto",
        "cep": "77064-000",
    },
    {
        "inscricao_cci": "CCI-GLEBA-JALAPAO-01",
        "endereco": "Quadra 404 Sul, Alameda 08, Lotes 10 a 20",
        "tipo_imovel": "TERRENO",
        "valor_venal": 8900000.00,
        "cpf_cnpj_proprietario": "01.234.567/0001-89",
        "bairro": "404 Sul",
        "cep": "77021-630",
    },

    # Imóveis de Médios Devedores
    {
        "inscricao_cci": "CCI-COMERCIAL-JK-10",
        "endereco": "Avenida JK, Quadra 104 Sul, Lote 22",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 950000.00,
        "cpf_cnpj_proprietario": "12.345.678/0001-90",
        "bairro": "104 Sul",
        "cep": "77020-020",
    },
    {
        "inscricao_cci": "CCI-LOTE-INDUSTRIAL-07",
        "endereco": "Setor Industrial de Taquaralto, Rua 12, Galpão B",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 680000.00,
        "cpf_cnpj_proprietario": "98.765.432/0001-10",
        "bairro": "Taquaralto",
        "cep": "77064-100",
    },
    {
        "inscricao_cci": "CCI-ESCOLA-104-SUL",
        "endereco": "Quadra 104 Sul, Rua SE-05, Lote 14",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 1400000.00,
        "cpf_cnpj_proprietario": "08.901.234/0001-56",
        "bairro": "104 Sul",
        "cep": "77020-014",
    },
    {
        "inscricao_cci": "CCI-AURENY-GALPAO",
        "endereco": "Jardim Aureny I, Rua Tocantins, Quadra 18",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 540000.00,
        "cpf_cnpj_proprietario": "09.012.345/0001-67",
        "bairro": "Jardim Aureny I",
        "cep": "77060-018",
    },
    {
        "inscricao_cci": "CCI-MERCADO-TAQUARALTO",
        "endereco": "Avenida Tocantins, Quadra 32, Taquaralto",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 780000.00,
        "cpf_cnpj_proprietario": "11.234.567/0001-89",
        "bairro": "Taquaralto",
        "cep": "77064-032",
    },
    {
        "inscricao_cci": "CCI-CHURRASCO-SUL",
        "endereco": "Rodovia BR-010, Taquaralto Sul, Lote 05",
        "tipo_imovel": "COMERCIAL",
        "valor_venal": 420000.00,
        "cpf_cnpj_proprietario": "13.456.789/0001-01",
        "bairro": "Taquaralto",
        "cep": "77064-005",
    },

    # Imóveis Pessoas Físicas
    {
        "inscricao_cci": "CCI-104-NORTE-01",
        "endereco": "Quadra 104 Norte, Alameda 02, Lote 15",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 280000.00,
        "cpf_cnpj_proprietario": "123.456.789-01",
        "bairro": "104 Norte",
        "cep": "77006-020",
    },
    {
        "inscricao_cci": "CCI-208-SUL-42",
        "endereco": "Quadra 208 Sul, Avenida LO-05, Lote 08",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 420000.00,
        "cpf_cnpj_proprietario": "234.567.890-12",
        "bairro": "208 Sul",
        "cep": "77020-550",
    },
    {
        "inscricao_cci": "CCI-303-NORTE-19",
        "endereco": "Quadra 303 Norte, Alameda 19, Casa 04",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 310000.00,
        "cpf_cnpj_proprietario": "345.678.901-23",
        "bairro": "303 Norte",
        "cep": "77001-303",
    },
    {
        "inscricao_cci": "CCI-TAQUARALTO-77",
        "endereco": "Rua 15, Quadra 44, Lote 12, Taquaralto",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 160000.00,
        "cpf_cnpj_proprietario": "456.789.012-34",
        "bairro": "Taquaralto",
        "cep": "77064-044",
    },
    {
        "inscricao_cci": "CCI-AURENY-III-10",
        "endereco": "Jardim Aureny III, Rua 32, Casa 11",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 145000.00,
        "cpf_cnpj_proprietario": "567.890.123-45",
        "bairro": "Jardim Aureny III",
        "cep": "77062-032",
    },
    {
        "inscricao_cci": "CCI-104-SUL-RESID",
        "endereco": "Quadra 104 Sul, Alameda 04, Lote 18",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 490000.00,
        "cpf_cnpj_proprietario": "678.901.234-56",
        "bairro": "104 Sul",
        "cep": "77020-004",
    },
    {
        "inscricao_cci": "CCI-BERTAVILLE-05",
        "endereco": "Setor Bertaville, Rua B-05, Lote 20",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 190000.00,
        "cpf_cnpj_proprietario": "789.012.345-67",
        "bairro": "Bertaville",
        "cep": "77070-005",
    },
    {
        "inscricao_cci": "CCI-208-SUL-APTO",
        "endereco": "Quadra 208 Sul, Alameda dos Buritis, Apto 402",
        "tipo_imovel": "RESIDENCIAL",
        "valor_venal": 350000.00,
        "cpf_cnpj_proprietario": "987.654.321-09",
        "bairro": "208 Sul",
        "cep": "77020-560",
    },
]

DIVIDAS_SEED: List[Dict[str, Any]] = [
    # --- DÍVIDAS DE GRANDES DEVEDORES (> R$ 50.000) ---
    {
        "codigo_debito": "DEB-2020-IPTU-JALAPAO",
        "ano_exercicio": 2020,
        "valor_original": 180000.00,
        "juros_multa": 65000.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-GLEBA-JALAPAO-01",
        "cpf_cnpj_contribuinte": "01.234.567/0001-89",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2021-IPTU-JALAPAO",
        "ano_exercicio": 2021,
        "valor_original": 110000.00,
        "juros_multa": 25000.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-GLEBA-JALAPAO-01",
        "cpf_cnpj_contribuinte": "01.234.567/0001-89",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2021-ISS-GRACIOSA",
        "ano_exercicio": 2021,
        "valor_original": 95000.00,
        "juros_multa": 50000.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-ORLA-14-SUL",
        "cpf_cnpj_contribuinte": "02.345.678/0001-90",
        "tipo_tributo": "ISS",
    },
    {
        "codigo_debito": "DEB-2022-IPTU-CAPIM",
        "ano_exercicio": 2022,
        "valor_original": 88000.00,
        "juros_multa": 22000.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-107-NORTE-SHOP",
        "cpf_cnpj_contribuinte": "04.567.890/0001-12",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2019-TX-MINERADORA",
        "ano_exercicio": 2019,
        "valor_original": 62000.00,
        "juros_multa": 36000.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-MINER-TAQUARALTO",
        "cpf_cnpj_contribuinte": "07.890.123/0001-45",
        "tipo_tributo": "TAXA_LIXO",
    },
    {
        "codigo_debito": "DEB-2022-ISS-POSTO",
        "ano_exercicio": 2022,
        "valor_original": 48000.00,
        "juros_multa": 17000.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-POSTO-TEOTONIO",
        "cpf_cnpj_contribuinte": "05.678.901/0001-23",
        "tipo_tributo": "ISS",
    },
    {
        "codigo_debito": "DEB-2023-ISS-HOSPITAL",
        "ano_exercicio": 2023,
        "valor_original": 55000.00,
        "juros_multa": 12000.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-HOSP-501-SUL",
        "cpf_cnpj_contribuinte": "06.789.012/0001-34",
        "tipo_tributo": "ISS",
    },
    {
        "codigo_debito": "DEB-2020-IPTU-ATACADISTA",
        "ano_exercicio": 2020,
        "valor_original": 42000.00,
        "juros_multa": 16000.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-IND-DISTRITO-01",
        "cpf_cnpj_contribuinte": "03.456.789/0001-01",
        "tipo_tributo": "IPTU",
    },

    # --- DÍVIDAS MÉDIAS (R$ 10.000 A R$ 50.000) ---
    {
        "codigo_debito": "DEB-2024-ISS-JK10",
        "ano_exercicio": 2024,
        "valor_original": 14800.00,
        "juros_multa": 1250.75,
        "status": "ATIVO",
        "inscricao_cci": "CCI-COMERCIAL-JK-10",
        "cpf_cnpj_contribuinte": "12.345.678/0001-90",
        "tipo_tributo": "ISS",
    },
    {
        "codigo_debito": "DEB-2021-TX-IND07",
        "ano_exercicio": 2021,
        "valor_original": 8300.00,
        "juros_multa": 2400.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-LOTE-INDUSTRIAL-07",
        "cpf_cnpj_contribuinte": "98.765.432/0001-10",
        "tipo_tributo": "TAXA_LIXO",
    },
    {
        "codigo_debito": "DEB-2022-ISS-PRIME",
        "ano_exercicio": 2022,
        "valor_original": 26000.00,
        "juros_multa": 8000.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-ESCOLA-104-SUL",
        "cpf_cnpj_contribuinte": "08.901.234/0001-56",
        "tipo_tributo": "ISS",
    },
    {
        "codigo_debito": "DEB-2021-IPTU-LOGISTICA",
        "ano_exercicio": 2021,
        "valor_original": 31000.00,
        "juros_multa": 11000.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-AURENY-GALPAO",
        "cpf_cnpj_contribuinte": "09.012.345/0001-67",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2023-ISS-MERCADO",
        "ano_exercicio": 2023,
        "valor_original": 19000.00,
        "juros_multa": 4500.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-MERCADO-TAQUARALTO",
        "cpf_cnpj_contribuinte": "11.234.567/0001-89",
        "tipo_tributo": "ISS",
    },
    {
        "codigo_debito": "DEB-2022-TX-CHURRASCO",
        "ano_exercicio": 2022,
        "valor_original": 11500.00,
        "juros_multa": 3200.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-CHURRASCO-SUL",
        "cpf_cnpj_contribuinte": "13.456.789/0001-01",
        "tipo_tributo": "TAXA_LIXO",
    },

    # --- DÍVIDAS PEQUENAS E MÉDIAS PESSOA FÍSICA (< R$ 10.000) ---
    {
        "codigo_debito": "DEB-2023-IPTU-104",
        "ano_exercicio": 2023,
        "valor_original": 2450.00,
        "juros_multa": 380.50,
        "status": "ATIVO",
        "inscricao_cci": "CCI-104-NORTE-01",
        "cpf_cnpj_contribuinte": "123.456.789-01",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2022-IPTU-104",
        "ano_exercicio": 2022,
        "valor_original": 2200.00,
        "juros_multa": 650.00,
        "status": "AJUIZADO",
        "inscricao_cci": "CCI-104-NORTE-01",
        "cpf_cnpj_contribuinte": "123.456.789-01",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2021-IPTU-ROBERTO",
        "ano_exercicio": 2021,
        "valor_original": 3800.00,
        "juros_multa": 1200.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-208-SUL-42",
        "cpf_cnpj_contribuinte": "234.567.890-12",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2024-TX-FERNANDA",
        "ano_exercicio": 2024,
        "valor_original": 1450.00,
        "juros_multa": 150.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-303-NORTE-19",
        "cpf_cnpj_contribuinte": "345.678.901-23",
        "tipo_tributo": "TAXA_LIXO",
    },
    {
        "codigo_debito": "DEB-2022-IPTU-MARCELO",
        "ano_exercicio": 2022,
        "valor_original": 1850.00,
        "juros_multa": 520.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-AURENY-III-10",
        "cpf_cnpj_contribuinte": "567.890.123-45",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2023-IPTU-CAMILA",
        "ano_exercicio": 2023,
        "valor_original": 4200.00,
        "juros_multa": 680.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-104-SUL-RESID",
        "cpf_cnpj_contribuinte": "678.901.234-56",
        "tipo_tributo": "IPTU",
    },
    {
        "codigo_debito": "DEB-2023-TX-RENATO",
        "ano_exercicio": 2023,
        "valor_original": 890.00,
        "juros_multa": 110.00,
        "status": "ATIVO",
        "inscricao_cci": "CCI-BERTAVILLE-05",
        "cpf_cnpj_contribuinte": "789.012.345-67",
        "tipo_tributo": "TAXA_LIXO",
    },
]

PROCESSOS_SEED: List[Dict[str, Any]] = [
    {
        "numero_processo": "0012345-67.2021.8.27.2729",
        "vara": "1ª Vara de Execução Fiscal de Palmas",
        "data_autuacao": "2021-06-15",
        "codigo_debito": "DEB-2020-IPTU-JALAPAO",
        "cpf_cnpj_contribuinte": "01.234.567/0001-89",
        "status_processo": "EM_ANDAMENTO",
    },
    {
        "numero_processo": "0023456-78.2022.8.27.2729",
        "vara": "2ª Vara de Execução Fiscal de Palmas",
        "data_autuacao": "2022-04-20",
        "codigo_debito": "DEB-2021-ISS-GRACIOSA",
        "cpf_cnpj_contribuinte": "02.345.678/0001-90",
        "status_processo": "EM_ANDAMENTO",
    },
    {
        "numero_processo": "0034567-89.2020.8.27.2729",
        "vara": "1ª Vara de Execução Fiscal de Palmas",
        "data_autuacao": "2020-09-10",
        "codigo_debito": "DEB-2019-TX-MINERADORA",
        "cpf_cnpj_contribuinte": "07.890.123/0001-45",
        "status_processo": "EM_ANDAMENTO",
    },
    {
        "numero_processo": "0045678-90.2021.8.27.2729",
        "vara": "2ª Vara de Execução Fiscal de Palmas",
        "data_autuacao": "2021-10-18",
        "codigo_debito": "DEB-2020-IPTU-ATACADISTA",
        "cpf_cnpj_contribuinte": "03.456.789/0001-01",
        "status_processo": "EM_ANDAMENTO",
    },
    {
        "numero_processo": "0056789-01.2023.8.27.2729",
        "vara": "1ª Vara de Execução Fiscal de Palmas",
        "data_autuacao": "2023-03-12",
        "codigo_debito": "DEB-2022-ISS-PRIME",
        "cpf_cnpj_contribuinte": "08.901.234/0001-56",
        "status_processo": "EM_ANDAMENTO",
    },
    {
        "numero_processo": "0012345-67.2023.8.27.2729",
        "vara": "1ª Vara de Execução Fiscal de Palmas",
        "data_autuacao": "2023-08-14",
        "codigo_debito": "DEB-2022-IPTU-104",
        "cpf_cnpj_contribuinte": "123.456.789-01",
        "status_processo": "EM_ANDAMENTO",
    },
    {
        "numero_processo": "0098765-43.2022.8.27.2729",
        "vara": "2ª Vara de Execução Fiscal de Palmas",
        "data_autuacao": "2022-11-05",
        "codigo_debito": "DEB-2021-TX-IND07",
        "cpf_cnpj_contribuinte": "98.765.432/0001-10",
        "status_processo": "EM_ANDAMENTO",
    },
]


# ==============================================================================
# 3. Funções Utilitárias para Consumo dos Mocks
# ==============================================================================

def obter_contribuintes_mock() -> List[Dict[str, Any]]:
    return [dict(item) for item in CONTRIBUINTES_SEED]


def obter_imoveis_mock() -> List[Dict[str, Any]]:
    return [dict(item) for item in IMOVEIS_SEED]


def obter_dividas_mock() -> List[Dict[str, Any]]:
    return [dict(item) for item in DIVIDAS_SEED]


def obter_processos_mock() -> List[Dict[str, Any]]:
    return [dict(item) for item in PROCESSOS_SEED]


def obter_dados_consolidados() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "contribuintes": obter_contribuintes_mock(),
        "imoveis": obter_imoveis_mock(),
        "dividas": obter_dividas_mock(),
        "processos": obter_processos_mock(),
    }


class BancoSimuladoEmMemoria:
    """Banco em memória para testes ou fallback de execução."""
    def __init__(self):
        self.contribuintes: Dict[str, Dict[str, Any]] = {}
        self.imoveis: Dict[str, Dict[str, Any]] = {}
        self.dividas: List[Dict[str, Any]] = []
        self.processos: List[Dict[str, Any]] = []

    def carregar_dados_iniciais(self):
        for c in CONTRIBUINTES_SEED:
            self.contribuintes[c["cpf_cnpj"]] = dict(c)
        for i in IMOVEIS_SEED:
            self.imoveis[i["inscricao_cci"]] = dict(i)
        self.dividas = [dict(d) for d in DIVIDAS_SEED]
        self.processos = [dict(p) for p in PROCESSOS_SEED]

    def buscar_contribuinte(self, documento: str) -> Optional[Dict[str, Any]]:
        if not documento:
            return None
        doc_limpo = "".join(filter(str.isalnum, documento))
        for k, v in self.contribuintes.items():
            if "".join(filter(str.isalnum, k)) == doc_limpo:
                return dict(v)
        return None

    def buscar_imovel(self, inscricao_cci: str) -> Optional[Dict[str, Any]]:
        if not inscricao_cci:
            return None
        return self.imoveis.get(inscricao_cci.strip())

    def listar_dividas_por_imovel(self, inscricao_cci: str) -> List[Dict[str, Any]]:
        if not inscricao_cci:
            return []
        cci = inscricao_cci.strip()
        return [dict(d) for d in self.dividas if d["inscricao_cci"] == cci]

    def listar_processos_por_imovel(self, inscricao_cci: str) -> List[Dict[str, Any]]:
        if not inscricao_cci:
            return []
        cci = inscricao_cci.strip()
        codigos_debito = {d["codigo_debito"] for d in self.dividas if d["inscricao_cci"] == cci}
        return [dict(p) for p in self.processos if p["codigo_debito"] in codigos_debito]

    def listar_imoveis_por_contribuinte(self, cpf_cnpj: str) -> List[Dict[str, Any]]:
        contribuinte = self.buscar_contribuinte(cpf_cnpj)
        if not contribuinte:
            return []
        cpf_padrao = contribuinte["cpf_cnpj"]
        return [dict(im) for im in self.imoveis.values() if im["cpf_cnpj_proprietario"] == cpf_padrao]


def executar_seed(
    model_registry: Optional[Dict[str, Any]] = None,
    db_session: Optional[Any] = None,
) -> Dict[str, Any]:
    if model_registry and db_session:
        logger.info("Executando seed integrado com models do banco de dados...")
        registros_criados: Dict[str, int] = {
            "contribuintes": 0,
            "imoveis": 0,
            "dividas": 0,
            "processos": 0,
        }
        for item in CONTRIBUINTES_SEED:
            classe = model_registry.get("Contribuinte")
            if classe:
                db_session.add(classe(**item))
                registros_criados["contribuintes"] += 1
        for item in IMOVEIS_SEED:
            classe = model_registry.get("Imovel")
            if classe:
                db_session.add(classe(**item))
                registros_criados["imoveis"] += 1
        for item in DIVIDAS_SEED:
            classe = model_registry.get("Divida")
            if classe:
                db_session.add(classe(**item))
                registros_criados["dividas"] += 1
        for item in PROCESSOS_SEED:
            classe = model_registry.get("Processo")
            if classe:
                db_session.add(classe(**item))
                registros_criados["processos"] += 1
        db_session.commit()
        return {"status": "sucesso", "modo": "integrado", "registros": registros_criados}

    banco_simulado = BancoSimuladoEmMemoria()
    banco_simulado.carregar_dados_iniciais()
    return {
        "status": "sucesso",
        "modo": "simulado",
        "banco_simulado": banco_simulado,
        "total_contribuintes": len(banco_simulado.contribuintes),
        "total_imoveis": len(banco_simulado.imoveis),
        "total_dividas": len(banco_simulado.dividas),
        "total_processos": len(banco_simulado.processos),
    }

