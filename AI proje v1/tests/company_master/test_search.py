import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))\

from src.company_master.search.engine import (
    _as_list,
    _row_to_dashboard,
    search_jsonl,
    _data_root,
    search_companies,
    fetch_dashboard_companies,
    count_ankara_osb_companies,
    fetch_filtered_companies,
)


def test_as_list_with_list():
    assert _as_list(["a", "b", "c"]) == ["a", "b", "c"]


def test_as_list_with_string():
    assert _as_list("a; b; c") == ["a", "b", "c"]


def test_as_list_with_none():
    assert _as_list(None) == []


def test_as_list_with_empty_string():
    assert _as_list("") == []


def test_row_to_dashboard_basic():
    row = {
        "company_id": "c1",
        "legal_name": "Firma A",
        "website_domain": "example.com",
        "web_sitesi": "www.example.com",
        "primary_phone": "0312 123 45 67",
        "primary_email": "info@example.com",
        "tax_number": "1234567890",
        "vergi_no": "1234567890",
        "osb_parsel": "123/45",
        "data_quality_score": 85.0,
        "raw_phone": "0312 123 45 67",
        "raw_email": "info@example.com",
        "raw_address": "Ankara",
        "raw_website": "example.com",
        "raw_nace": "71.12",
        "raw_payload": {"telefonler": ["0312 111 22 33"], "emailler": ["info@test.com"], "unvan": "Firma B", "sektor": "İmalat"},
        "source_name": "OSTİM OSB",
    }
    result = _row_to_dashboard(row)
    assert result["company_id"] == "c1"
    assert result["unvan"] == "Firma A"
    assert result["web_sitesi"] == "www.example.com"
    assert result["telefonler"] == ["0312 111 22 33"]
    assert result["emailler"] == ["info@test.com"]
    assert result["adres"] == "Ankara"
    assert result["vergi_no"] == "1234567890"
    assert result["osb_parsel"] == "123/45"
    assert result["sektor"] == "İmalat"
    assert result["kaynak_tipi"] == "OSTİM OSB"
    assert result["data_quality_score"] == 85.0


def test_search_jsonl_with_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data" / "ostim"
        data_dir.mkdir(parents=True)
        file_path = data_dir / "firmalar_full.jsonl"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"unvan": "ABC Makina", "sektor": "İmalat"}, ensure_ascii=False) + "\n")
            f.write(json.dumps({"unvan": "XYZ Lazer", "sektor": "İmalat"}, ensure_ascii=False) + "\n")

        with patch("src.company_master.search.engine._data_root", return_value=Path(tmpdir)):
            results = search_jsonl("ABC", limit=10)
            assert len(results) == 1
            assert results[0]["unvan"] == "ABC Makina"


def test_search_jsonl_no_match():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data" / "ostim"
        data_dir.mkdir(parents=True)
        file_path = data_dir / "firmalar_full.jsonl"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"unvan": "ABC Makina"}, ensure_ascii=False) + "\n")

        with patch("src.company_master.search.engine._data_root", return_value=Path(tmpdir)):
            results = search_jsonl("ZZZ", limit=10)
            assert len(results) == 0


def test_search_companies(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = [
        ("c1", "ABC Makina", "1234567890", "abc.com")
    ]
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.search.engine.get_engine", lambda: mock_engine)
    results = search_companies("ABC", limit=5)
    assert len(results) == 1
    assert results[0]["legal_name"] == "ABC Makina"


def test_fetch_dashboard_companies(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = [
        {
            "company_id": "c1",
            "legal_name": "Firma A",
            "website_domain": "example.com",
            "web_sitesi": None,
            "primary_phone": None,
            "primary_email": None,
            "tax_number": None,
            "vergi_no": None,
            "osb_parsel": None,
            "data_quality_score": 80.0,
            "raw_phone": None,
            "raw_email": None,
            "raw_address": None,
            "raw_website": None,
            "raw_nace": None,
            "raw_payload": {},
            "source_name": "OSTİM OSB",
        }
    ]
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.search.engine.get_engine", lambda: mock_engine)
    results = fetch_dashboard_companies(limit=10)
    assert len(results) == 1
    assert results[0]["unvan"] == "Firma A"


def test_count_ankara_osb_companies(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.scalar.return_value = 42
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.search.engine.get_engine", lambda: mock_engine)
    count = count_ankara_osb_companies()
    assert count == 42


def test_fetch_filtered_companies(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = [
        {
            "company_id": "c1",
            "legal_name": "Firma A",
            "website_domain": "example.com",
            "web_sitesi": None,
            "primary_phone": None,
            "primary_email": None,
            "tax_number": None,
            "vergi_no": None,
            "osb_parsel": None,
            "data_quality_score": 80.0,
            "raw_phone": None,
            "raw_email": None,
            "raw_address": None,
            "raw_website": None,
            "raw_nace": None,
            "raw_payload": {},
            "source_name": "OSTİM OSB",
        }
    ]
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.search.engine.get_engine", lambda: mock_engine)
    results = fetch_filtered_companies(q="Firma", limit=10)
    assert len(results) == 1
    assert results[0]["unvan"] == "Firma A"
