# -*- coding: utf-8 -*-
"""db/connection.py, etl/normalize.py, search/engine.py, etl/pipeline.py
icin ek edge-case testleri. Var olan testlere ek katki saglar."""

import os
import sys
import tempfile
import json
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.company_master.db.connection import (
    get_database_url, get_engine,
    _engine_for, init_db, _load_env,
)
from src.company_master.etl.normalize import (
    _data_quality_score, _map_row, run_normalize,
)
from src.company_master.search.engine import (
    _as_list, _row_to_dashboard, _data_root,
    search_jsonl, fetch_filtered_companies,
)

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _temiz_get_engine_cache():
    """test_connection.py ile ayni onlem: lru_cache engine sizintisini engelle."""
    _engine_for.cache_clear()
    yield
    _engine_for.cache_clear()

@contextmanager
def _tmpdir():
    with tempfile.TemporaryDirectory() as p:
        yield Path(p)

def test_get_database_url_returns_string(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/d")
    assert get_database_url() == "postgresql://u:p@h/d"

def test_get_engine_postgresql_no_double_replace(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h/d")
    with patch("src.company_master.db.connection.HAS_SQLALCHEMY", True):
        with patch("src.company_master.db.connection.create_engine") as mock_create:
            get_engine()
            args = mock_create.call_args[0]
            assert args[0] == "postgresql+psycopg://u:p@h/d"

def test_get_engine_postgresql_with_kwargs(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/d")
    with patch("src.company_master.db.connection.HAS_SQLALCHEMY", True):
        with patch("src.company_master.db.connection.create_engine") as mock_create:
            get_engine()
            kwargs = mock_create.call_args[1]
            assert kwargs["echo"] is False
            assert kwargs["future"] is True

def test_load_env_quoted_value():
    with _tmpdir() as tmp:
        env_path = tmp / ".env"
        env_path.write_text("QKEY=\"quoted value\"" + chr(10), encoding="utf-8")
        with patch("src.company_master.db.connection._find_root", return_value=tmp):
            _load_env()
            assert os.getenv("QKEY") == "quoted value"
            os.environ.pop("QKEY", None)

def test_load_env_single_quoted_value():
    with _tmpdir() as tmp:
        env_path = tmp / ".env"
        env_path.write_text("SKEY='single quote'" + chr(10), encoding="utf-8")
        with patch("src.company_master.db.connection._find_root", return_value=tmp):
            _load_env()
            assert os.getenv("SKEY") == "single quote"
            os.environ.pop("SKEY", None)

def test_init_db_creates_quarantine(monkeypatch):
    with _tmpdir() as tmp:
        db_path = tmp / "q.db"
        monkeypatch.setenv("DATABASE_URL", "sqlite:///" + str(db_path))
        init_db()
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quarantine_firms'")
        assert cur.fetchone() is not None
        conn.close()

def test_data_quality_score_empty_row():
    assert _data_quality_score({}) == 0.0

def test_data_quality_score_website_domain_only():
    row = {
        "raw_website": None,
        "website_domain": "firma.com",
        "raw_tax_number": "1234567890",
        "raw_payload": {"adres": "Ankara"},
    }
    skor = _data_quality_score(row)
    assert skor == 55.0

def test_data_quality_score_all_critical_filled():
    row = {
        "raw_phone": "0312 111 22 33",
        "raw_email": "info@firma.com",
        "raw_website": "firma.com",
        "raw_tax_number": "1234567890",
        "raw_payload": {
            "adres": "Ankara",
            "sektor": "Imalat",
            "osb_parsel": "123/45",
            "nace_code": "71.12",
        },
    }
    skor = _data_quality_score(row)
    assert skor == 100.0

def test_data_quality_score_clamped_at_zero():
    row = {"raw_payload": {}}
    skor = _data_quality_score(row)
    assert 0.0 <= skor <= 100.0

def test_map_row_multi_phone():
    row = {
        "source_record_id": "sr_x",
        "raw_name": "X",
        "raw_phone": "0312 1; 0312 2",
        "raw_email": "",
        "raw_website": None,
        "raw_tax_number": None,
        "raw_payload": {},
    }
    out = _map_row(row, None)
    assert out["primary_phone"] == "0312 1"

def test_run_normalize_no_osb(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.first.return_value = None
    mock_conn.execute.return_value.mappings.return_value.all.return_value = []
    mock_engine = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.etl.normalize.get_engine", lambda: mock_engine)
    res = run_normalize()
    assert res.total == 0

def test_search_as_list_keeps_nonempty():
    assert _as_list(["a", None, "", "b"]) == ["a", "b"]

def test_search_as_list_str_split_semicolon():
    assert _as_list("a; ; b") == ["a", "b"]

def test_search_row_to_dashboard_no_payload():
    row = {
        "company_id": "c2",
        "legal_name": "Firma B",
        "data_quality_score": None,
        "raw_payload": None,
    }
    out = _row_to_dashboard(row)
    assert out["unvan"] == "Firma B"
    assert out["data_quality_score"] is None

def test_search_row_to_dashboard_payload_not_dict():
    row = {
        "company_id": "c3",
        "legal_name": "Firma C",
        "raw_payload": "string payload",
    }
    out = _row_to_dashboard(row)
    assert out["unvan"] == "Firma C"

def test_data_root_finds_ostim_dir():
    root = _data_root()
    assert isinstance(root, Path)

def test_search_jsonl_filters_nace():
    with _tmpdir() as tmp:
        data_dir = tmp / "data" / "ostim"
        data_dir.mkdir(parents=True)
        fp = data_dir / "firmalar_full.jsonl"
        with open(fp, "w", encoding="utf-8") as f:
            f.write(json.dumps({"unvan": "ABC", "nace_code": "71.12"}, ensure_ascii=False) + chr(10))
            f.write(json.dumps({"unvan": "ABC2", "nace_code": "25.62"}, ensure_ascii=False) + chr(10))
        with patch("src.company_master.search.engine._data_root", return_value=tmp):
            res = search_jsonl("ABC", nace_code="71.12", limit=10)
            assert len(res) == 1
            assert res[0]["nace_code"] == "71.12"

def test_fetch_filtered_companies_with_sectors(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = []
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.search.engine.get_engine", lambda: mock_engine)
    out = fetch_filtered_companies(q="x", sectors=["Imalat"], has_phone=True, has_email=True, has_web=True, limit=5, offset=0)
    assert out == []
    assert mock_conn.execute.called

def test_fetch_filtered_companies_with_extra(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = []
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.search.engine.get_engine", lambda: mock_engine)
    out = fetch_filtered_companies(q="x", kalite_min=10.0, kalite_max=90.0, limit=2, offset=5)
    assert out == []

def test_search_jsonl_skips_missing_files(monkeypatch):
    with _tmpdir() as tmp:
        with patch("src.company_master.search.engine._data_root", return_value=tmp):
            res = search_jsonl("anything", limit=5)
            assert res == []
