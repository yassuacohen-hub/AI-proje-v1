"""Veritabanı bağlantı katmanı.

SQLAlchemy veya psycopg2 kullanır. URL `.env`'deki `DATABASE_URL`'den okunur.
SQLite fallback: TEST ortamı için `sqlite:///./company_master.db`.
"""

from .connection import get_engine, get_session, init_db

__all__ = ["get_engine", "get_session", "init_db"]