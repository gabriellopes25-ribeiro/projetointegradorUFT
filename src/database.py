"""
Módulo de Configuração e Conexão PostgreSQL - SITRIB (SEFIN Palmas / UFT)

Gerencia o pool de conexões SQLAlchemy + Psycopg2 para o PostgreSQL 16 (Docker ou Local)
e executa automaticamente a criação das tabelas e índices de alta performance (`schema.sql`).
"""

import os
from pathlib import Path
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "schema.sql"

DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://sitrib:sitrib_secret_password@localhost:5432/sitrib",
)


def obter_database_url(url_override: Optional[str] = None) -> str:
    """Normaliza a URL do PostgreSQL para o driver SQLAlchemy psycopg2."""
    url = url_override or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def criar_engine_postgres(database_url: Optional[str] = None, connect_timeout: int = 5) -> Engine:
    """Cria a Engine SQLAlchemy com Pool otimizado para cargas de 180 mil+ registros."""
    url = obter_database_url(database_url)
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args={"connect_timeout": connect_timeout},
    )


def inicializar_schema_postgres(engine: Engine) -> None:
    """Executa o schema.sql no PostgreSQL criando as 6 tabelas e todos os índices B-Tree."""
    if not SCHEMA_PATH.exists():
        return
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()

    comandos = [cmd.strip() for cmd in sql_script.split(";") if cmd.strip()]
    with engine.begin() as conn:
        for cmd in comandos:
            conn.execute(text(cmd))
