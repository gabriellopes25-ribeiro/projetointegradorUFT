"""
Redirecionador de Compatibilidade para o Repositório Oficial PostgreSQL.

O banco SQLite foi descartado em favor do PostgreSQL (`sitrib-postgres` na porta 5432).
Qualquer código ou teste que importe `RepositorioSQLite` utiliza automaticamente
o `RepositorioPostgreSQL`.
"""

from src.repositories.postgres_repository import RepositorioPostgreSQL

RepositorioSQLite = RepositorioPostgreSQL
