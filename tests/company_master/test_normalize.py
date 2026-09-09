import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))\

from src.company_master.etl.normalize import _map_row, run_normalize, NormalizeResult, main


def test_map_row_basic():
    row = {
        "source_record_id": "sr_001",
        "raw_name": "  Test Firma A.Ş.  ",
        "raw_phone": "0312 123 45 67",
        "raw_email": "info@testfirma.com",
        "raw_website": "https://testfirma.com",
        "raw_tax_number": "1234567890",
        "raw_payload": {"nace_confidence": "high"},
    }
    result = _map_row(row, "osb_001")
    assert result["legal_name"] == "TEST FIRMA A.Ş."
    assert result["tax_number"] == "1234567890"
    assert result["website_domain"] == "https://testfirma.com"
    assert result["primary_phone"] == "0312 123 45 67"
    assert result["primary_email"] == "info@testfirma.com"
    assert result["osb_id"] == "osb_001"
    assert result["is_osb_member"] is True
    assert result["is_ankara"] is True
    assert result["status"] == "active"
    assert result["nace_validity"] == "high"
    assert result["data_quality_score"] == 40.0  # yeni formul: telefon 10 + email 5 + web 15 + vergi 20 - adres cezasi 10 = 40
    assert result["entity_confidence"] == 0.9


def test_map_row_no_phone():
    row = {
        "source_record_id": "sr_002",
        "raw_name": "Test Firma",
        "raw_phone": "",
        "raw_email": "",
        "raw_website": None,
        "raw_tax_number": None,
        "raw_payload": {"nace_confidence": "low"},
    }
    result = _map_row(row, None)
    assert result["legal_name"] == "TEST FIRMA"
    assert result["primary_phone"] is None
    assert result["primary_email"] is None
    assert result["data_quality_score"] == 0.0
    assert result["nace_validity"] == "unknown"


def test_map_row_medium_confidence():
    row = {
        "source_record_id": "sr_003",
        "raw_name": "Firma",
        "raw_phone": "",
        "raw_email": "",
        "raw_website": None,
        "raw_tax_number": None,
        "raw_payload": {"nace_confidence": "medium"},
    }
    result = _map_row(row, "osb_001")
    assert result["nace_validity"] == "medium"


def test_run_normalize_empty(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = []
    mock_engine = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.etl.normalize.get_engine", lambda: mock_engine)
    res = run_normalize()
    assert res.total == 0
    assert res.written == 0


def test_run_normalize_writes_records(monkeypatch):
    mock_rows = [
        {
            "source_record_id": "sr_001",
            "raw_name": "Firma A",
            "raw_phone": "0312 123 45 67",
            "raw_email": "info@a.com",
            "raw_website": "https://a.com",
            "raw_tax_number": "111",
            "raw_payload": {"nace_confidence": "high"},
        }
    ]
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = mock_rows
    mock_conn.execute.return_value.first.return_value = ("osb_001",)
    mock_engine = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.etl.normalize.get_engine", lambda: mock_engine)
    res = run_normalize()
    assert res.total == 1
    assert res.written == 1


def test_run_normalize_idempotent(monkeypatch):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = []
    mock_engine = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.etl.normalize.get_engine", lambda: mock_engine)
    res1 = run_normalize()
    assert res1.written == 0
    res2 = run_normalize()
    assert res2.total == 0


def test_run_normalize_with_limit(monkeypatch):
    mock_rows = [
        {
            "source_record_id": f"sr_{i:03d}",
            "raw_name": f"Firma {i}",
            "raw_phone": "",
            "raw_email": "",
            "raw_website": None,
            "raw_tax_number": None,
            "raw_payload": {"nace_confidence": "low"},
        }
        for i in range(10)
    ]
    mock_conn = MagicMock()
    mock_conn.execute.return_value.mappings.return_value.all.return_value = mock_rows
    mock_conn.execute.return_value.first.return_value = ("osb_001",)
    mock_engine = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_conn
    monkeypatch.setattr("src.company_master.etl.normalize.get_engine", lambda: mock_engine)
    res = run_normalize(limit=3)
    assert res.total == 3
    assert res.written == 3


def test_main_returns_zero_on_success(monkeypatch, capsys):
    monkeypatch.setattr("src.company_master.etl.normalize.run_normalize", lambda limit=None: NormalizeResult(total=0, written=0))
    with patch("sys.argv", ["normalize"]):
        rc = main()
    assert rc == 0


def test_main_returns_one_on_error(monkeypatch):
    monkeypatch.setattr("src.company_master.etl.normalize.run_normalize", lambda limit=None: NormalizeResult(total=1, written=1, errors=["hata"]))
    with patch("sys.argv", ["normalize"]):
        rc = main()
    assert rc == 1
