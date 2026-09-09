import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))\

from src.company_master.db.connection import (
    get_database_url,
    get_engine,
    _engine_for,
    init_db,
    _find_root,
    _load_env,
    get_session,
)


@pytest.fixture(autouse=True)
def _temiz_get_engine_cache():
    """get_engine @lru_cache'ini her testten once/sonra temizler.

    get_engine() maxsize=1 lru_cache oldugu icin test_get_engine_sqlite
    DATABASE_URL'i geri almadan sqlite:// engine uretiyor; sonraki testler
    cache'ten eski engine'i alip fail oluyordu (test pollution).
    """
    _engine_for.cache_clear()
    yield
    _engine_for.cache_clear()


def test_get_database_url_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
    assert get_database_url() == "postgresql://test:test@localhost/testdb"


def test_get_database_url_fallback(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url() == "sqlite:///./company_master.db"


def test_get_engine_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    engine = get_engine()
    assert engine is not None


def test_get_engine_postgresql_converts_psycopg(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    with patch("src.company_master.db.connection.HAS_SQLALCHEMY", True):
        with patch("src.company_master.db.connection.create_engine") as mock_create:
            get_engine()
            args = mock_create.call_args[0]
            assert args[0].startswith("postgresql+psycopg://")


def test_get_engine_fallback_without_sqlalchemy(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    with patch("src.company_master.db.connection.HAS_SQLALCHEMY", False):
        conn = get_engine()
        import sqlite3
        assert isinstance(conn, sqlite3.Connection)


def test_get_engine_fallback_non_sqlite_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    with patch("src.company_master.db.connection.HAS_SQLALCHEMY", False):
        conn = get_engine()
        import sqlite3
        assert isinstance(conn, sqlite3.Connection)


def test_get_session_with_sqlalchemy(monkeypatch):
    monkeypatch.setattr("src.company_master.db.connection.HAS_SQLALCHEMY", True)
    with patch("src.company_master.db.connection.get_engine") as mock_engine:
        mock_session = MagicMock()
        with patch("src.company_master.db.connection.sessionmaker", return_value=lambda: mock_session):
            session = get_session()
            assert session is not None


def test_get_session_returns_none_without_sqlalchemy(monkeypatch):
    monkeypatch.setattr("src.company_master.db.connection.HAS_SQLALCHEMY", False)
    assert get_session() is None


def test_init_db_creates_tables(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
        init_db()
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        conn.close()
        assert "companies" in tables
        assert "osbs" in tables
        assert "quarantine_firms" in tables


def test_init_db_handles_sql_error(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    with tempfile.TemporaryDirectory() as tmpdir:
        sql_path = Path(tmpdir) / "test.sql"
        sql_path.write_text("CREATE TABLE test (id INT);", encoding="utf-8")
        with patch("src.company_master.db.connection.HAS_SQLALCHEMY", True):
            with patch("src.company_master.db.connection.create_engine") as mock_engine:
                mock_conn = MagicMock()
                mock_conn.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
                mock_conn.begin.return_value.__exit__ = MagicMock(return_value=False)
                mock_conn.execute.side_effect = Exception("SQL error")
                mock_engine.return_value = mock_conn
                init_db(sql_path=str(sql_path))


def test_init_db_with_custom_sql_path(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
        sql_path = Path(tmpdir) / "test.sql"
        sql_path.write_text("CREATE TABLE IF NOT EXISTS test (id INT);", encoding="utf-8")
        with patch("src.company_master.db.connection.create_engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.begin.return_value.__exit__ = MagicMock(return_value=False)
            mock_engine.return_value = mock_conn
            init_db(sql_path=str(sql_path))


def test_find_root_finds_env():
    root = _find_root()
    assert (root / ".env").exists()


def test_load_env_no_env_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.company_master.db.connection._find_root", return_value=Path(tmpdir)):
            _load_env()


def test_load_env_sets_variables():
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"
        env_path.write_text("TEST_VAR_12345=hello\n", encoding="utf-8")
        with patch("src.company_master.db.connection._find_root", return_value=Path(tmpdir)):
            _load_env()
            assert os.getenv("TEST_VAR_12345") == "hello"
            os.environ.pop("TEST_VAR_12345", None)


def test_load_env_skips_comments_and_blank():
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"
        env_path.write_text("# comment\n\nKEY1=val1\n", encoding="utf-8")
        with patch("src.company_master.db.connection._find_root", return_value=Path(tmpdir)):
            _load_env()
            assert os.getenv("KEY1") == "val1"
            os.environ.pop("KEY1", None)


def test_load_env_skips_existing_keys(monkeypatch):
    monkeypatch.setenv("SKIP_KEY", "existing")
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"
        env_path.write_text("SKIP_KEY=new_value\n", encoding="utf-8")
        with patch("src.company_master.db.connection._find_root", return_value=Path(tmpdir)):
            _load_env()
            assert os.getenv("SKIP_KEY") == "existing"
