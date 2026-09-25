#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API-ADMIN-MFA-26 — MFA yardımcı fonksiyon testleri.

Kapsam (brief: "Test: tests/test_mfa.py (3 test)"):
    1. Backup kodu üretimi biçimi (8 kod, 4 karakter, base16/upper).
    2. Hash + doğrulama round-trip (küçük harf girdi normalize edilir).
    3. Bozuk/eksik JSON karşısında `_verify_backup_code` sessizce False döner.

Not: Bu testler DB/HTTP gerektirmez; yalnızca `web_app` içindeki saf
yardımcı fonksiyonları ölçer. Uçtan uca akış DB fixture'ı gerektirir.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _yol in (ROOT, ROOT / "src"):
    if str(_yol) not in sys.path:
        sys.path.insert(0, str(_yol))


def _web_app():
    """`web_app` modülünü test anında import eder (ağır import maliyeti izole)."""
    import web_app

    return web_app


def test_backup_kodlari_bicimi():
    """8 kod üretilir; her kod 4 karakter ve [0-9A-F] kümesinden olur."""
    wa = _web_app()

    kodlar = wa._generate_backup_codes(8)

    assert len(kodlar) == 8
    for kod in kodlar:
        assert isinstance(kod, str)
        assert len(kod) == 4, f"beklenen 4 karakter, gelen: {kod!r}"
        assert re.fullmatch(r"[0-9A-F]{4}", kod), f"beklenmeyen karakter: {kod!r}"


def test_hash_ve_dogrula_roundtrip():
    """Hash'lenen kod doğrulanır; küçük harf girdi normalize edilir; yanlış kod reddedilir."""
    wa = _web_app()

    kodlar = wa._generate_backup_codes(8)
    sakli_hash = wa._hash_backup_codes(kodlar)

    assert wa._verify_backup_code(sakli_hash, kodlar[0]) is True
    assert wa._verify_backup_code(sakli_hash, kodlar[0].lower()) is True
    assert wa._verify_backup_code(sakli_hash, "ZZZZ") is False


def test_bozuk_json_false_doner():
    """Bozuk veya boş backup-codes JSON'u istisna fırlatmaz, False döner."""
    wa = _web_app()

    assert wa._verify_backup_code("{bozuk-json", "ABCD") is False
    assert wa._verify_backup_code("", "ABCD") is False
    assert wa._verify_backup_code("null", "ABCD") is False
