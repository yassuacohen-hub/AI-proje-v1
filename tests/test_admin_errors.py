# -*- coding: utf-8 -*-
"""Unit tests for web_dashboard/tabs/admin_errors.py."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Modülü import et
sys.path.insert(0, str(ROOT / "web_dashboard" / "tabs"))
import admin_errors as ae


def test_error_templates_exist():
    assert "404" in ae.ERROR_TEMPLATES
    assert "500" in ae.ERROR_TEMPLATES
    assert "connection" in ae.ERROR_TEMPLATES


def test_save_error_report_creates_file(tmp_path):
    # Geçici bir data/errors dizini oluştur
    errors_dir = tmp_path / "data" / "errors"
    errors_dir.mkdir(parents=True)
    report_file = errors_dir / "error_reports.jsonl"

    # Orijinal ROOT'u geçici olarak değiştir
    original_root = ae.ROOT
    ae.ROOT = tmp_path
    try:
        report = {
            "tarih": "2026-09-18T12:00:00",
            "raporlayan": "Test",
            "email": "test@example.com",
            "hata_turu": "404",
            "aciklama": "Test hatası",
            "durum": "kayit_edildi",
        }
        ae._save_error_report(report)
        # Dosya oluşturuldu mu?
        assert report_file.exists()
        # İçerik doğru mu?
        with open(report_file, "r", encoding="utf-8") as f:
            line = f.readline()
            saved = json.loads(line)
            assert saved["raporlayan"] == "Test"
            assert saved["hata_turu"] == "404"
    finally:
        ae.ROOT = original_root


def test_error_templates_structure():
    for code, tmpl in ae.ERROR_TEMPLATES.items():
        assert "title" in tmpl
        assert "message" in tmpl
        assert "icon" in tmpl
        assert "color" in tmpl


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
