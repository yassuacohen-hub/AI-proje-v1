# -*- coding: utf-8 -*-
"""Unit tests for web_dashboard/tabs/admin_errors.py and error_logger."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ModÃ¼lleri import et
sys.path.insert(0, str(ROOT / "web_dashboard" / "tabs"))
import admin_errors as ae
from company_master.logging.error_logger import log_error, get_recent_errors, get_error_stats, ERROR_LOG_FILE


def test_error_logger_log_and_read():
    """Hata loglama ve okuma calisir."""
    # Onceki testlerden kalan veriyi temizle
    if ERROR_LOG_FILE.exists():
        ERROR_LOG_FILE.unlink()

    try:
        raise ValueError("Test hatasi")
    except Exception as e:
        log_error(e, context={"test": True}, source="unit_test")

    errors = get_recent_errors(limit=5)
    assert len(errors) >= 1
    assert errors[0]["error_type"] == "ValueError"
    assert errors[0]["message"] == "Test hatasi"
    assert errors[0]["context"]["test"] is True
    assert errors[0]["source"] == "unit_test"


def test_error_stats():
    """Hata istatistikleri dogru hesaplanir."""
    if ERROR_LOG_FILE.exists():
        ERROR_LOG_FILE.unlink()

    # 3 hata logla
    for i in range(3):
        try:
            raise RuntimeError(f"Hata {i}")
        except Exception as e:
            log_error(e, source="test_source", level="ERROR" if i < 2 else "WARNING")

    stats = get_error_stats(days=1)
    assert stats["total"] >= 3
    assert stats["by_level"]["ERROR"] >= 2
    assert stats["by_level"]["WARNING"] >= 1
    assert stats["by_source"]["test_source"] >= 3
    assert stats["by_type"]["RuntimeError"] >= 3


def test_get_recent_errors_filters():
    """Filtreleme calisir."""
    if ERROR_LOG_FILE.exists():
        ERROR_LOG_FILE.unlink()

    # Farkli seviyelerde hata logla
    for level in ["ERROR", "WARNING", "INFO"]:
        try:
            raise Exception(f"{level} test")
        except Exception as e:
            log_error(e, source="filter_test", level=level)

    # Sadece ERROR
    errors = get_recent_errors(limit=10, level="ERROR")
    assert all(e["level"] == "ERROR" for e in errors)

    # Sadece WARNING
    errors = get_recent_errors(limit=10, level="WARNING")
    assert all(e["level"] == "WARNING" for e in errors)

    # Kaynak filtresi
    errors = get_recent_errors(limit=10, source="filter_test")
    assert all(e["source"] == "filter_test" for e in errors)


def test_admin_errors_format_error_entry():
    """_format_error_entry fonksiyonu calisir (private ama test edilebilir)."""
    entry = {
        "timestamp": "2026-09-18T12:00:00",
        "level": "ERROR",
        "source": "test",
        "error_type": "ValueError",
        "message": "Test mesaji",
        "context": {"key": "value"},
        "traceback": "Traceback...",
    }
    formatted = ae._format_error_entry(entry)
    assert "ERROR" in formatted
    assert "ValueError" in formatted
    assert "Test mesaji" in formatted
    assert "key" in formatted
    assert "Traceback" in formatted


def test_admin_errors_constants():
    """Sabitler tanimli mi?"""
    assert "ERROR" in ae.ERROR_COLORS
    assert "WARNING" in ae.ERROR_COLORS
    assert "CRITICAL" in ae.ERROR_COLORS
    assert ae.LEVEL_ORDER == ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

