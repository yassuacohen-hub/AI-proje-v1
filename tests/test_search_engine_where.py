# -*- coding: utf-8 -*-
"""V10-HIJYEN-01: fetch_filtered_companies WHERE bloğu regresyon testi.

Bug (B-14): engine.py:182-187'de mükerrer + bozuk bir where bloğu vardı.
Python implicit string concatenation nedeniyle `<> ""` ifadesi SQL'e
operand'sız `<> ` olarak giriyordu → PostgreSQL syntax hatası.

Bu test DB'siz çalışır; kaynak metni AST/metin düzeyinde denetler.
"""
from __future__ import annotations

import ast
from pathlib import Path

KAYNAK = Path(__file__).resolve().parents[1] / "src" / "company_master" / "search" / "engine.py"


def _kaynak() -> str:
    return KAYNAK.read_text(encoding="utf-8")


def test_sozdizimi_gecerli() -> None:
    ast.parse(_kaynak())


def test_bozuk_operand_yok() -> None:
    """`<> ""` → SQL'e boş operand olarak sızar; hiç bulunmamalı."""
    assert '<> ""' not in _kaynak()


def test_mukerrer_where_blogu_yok() -> None:
    """has_phone/has_email/has_web filtreleri birer kez eklenmeli."""
    src = _kaynak()
    assert src.count("c.primary_phone IS NOT NULL") == 1
    assert src.count("c.primary_email IS NOT NULL") == 1
    assert src.count("c.website_domain IS NOT NULL") == 1


def test_bos_string_karsilastirmasi_tek_tirnak() -> None:
    """SQL içinde boş string tek tırnakla yazılmalı: <> ''"""
    src = _kaynak()
    assert "<> ''" in src


if __name__ == "__main__":  # ponytail: framework yok, doğrudan çalıştırılabilir
    test_sozdizimi_gecerli()
    test_bozuk_operand_yok()
    test_mukerrer_where_blogu_yok()
    test_bos_string_karsilastirmasi_tek_tirnak()
    print("OK: 4/4 kontrol gecti")
