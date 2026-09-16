# -*- coding: utf-8 -*-
"""FIX-YONETIM-01: Yönetim › Veri Export Excel indirme regresyonu.

Sahip bulgusu: "Yönetim çizilirken hata oluştu: NDFrame.to_excel() missing 1
required positional argument: 'excel_writer'". `df.to_excel()` bir yazıcı
ister; `_excel_bytes` bunu BytesIO ile karşılar.
"""
from __future__ import annotations

import io

import pandas as pd
import pytest

from web_dashboard.tabs import admin_export


def test_excel_bytes_gecerli_xlsx_uretir():
    df = pd.DataFrame({"firma": ["Ağaç A.Ş.", "Çelik Ltd."], "skor": [80, 65]})
    veri = admin_export._excel_bytes(df)
    assert isinstance(veri, (bytes, bytearray))
    # xlsx = zip; PK imzasi ile baslar
    assert veri[:2] == b"PK"
    geri = pd.read_excel(io.BytesIO(veri), engine="openpyxl")
    assert list(geri["firma"]) == ["Ağaç A.Ş.", "Çelik Ltd."]


def test_excel_bytes_openpyxl_yoksa_none(monkeypatch):
    def _patlat(self, *a, **k):
        raise ImportError("openpyxl yok")

    monkeypatch.setattr(pd.DataFrame, "to_excel", _patlat)
    assert admin_export._excel_bytes(pd.DataFrame({"a": [1]})) is None


def test_render_export_tab_to_excel_hatasi_vermez(monkeypatch):
    """Tam render: download_button'a bytes gider, TypeError firlamaz."""
    st = admin_export.st
    df = pd.DataFrame({"a": [1, 2]})
    monkeypatch.setattr(admin_export, "load_export_data", lambda _t: df)
    monkeypatch.setattr(st, "subheader", lambda *a, **k: None)
    monkeypatch.setattr(st, "radio", lambda *a, **k: "KPI Metrikleri")
    monkeypatch.setattr(st, "success", lambda *a, **k: None)
    monkeypatch.setattr(st, "dataframe", lambda *a, **k: None)
    monkeypatch.setattr(st, "info", lambda *a, **k: None)
    monkeypatch.setattr(st, "warning", lambda *a, **k: None)

    class _Col:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(st, "columns", lambda n: [_Col() for _ in range(n)])
    gelen: list[dict] = []
    monkeypatch.setattr(st, "download_button", lambda **k: gelen.append(k))

    admin_export.render_export_tab()

    etiketler = [g["label"] for g in gelen]
    assert any("Excel" in e for e in etiketler), etiketler
    excel = next(g for g in gelen if "Excel" in g["label"])
    assert isinstance(excel["data"], (bytes, bytearray))
    assert excel["file_name"].endswith(".xlsx")


@pytest.mark.parametrize(
    "modul",
    ["admin_panel", "ana_kontrol", "paketler", "admin_musteriler", "admin_realtime", "pazarlama"],
)
def test_sekme_rehberi_metinleri_utf8_ve_yapili(modul):
    """Rehber metinleri 4 baslik tasir ve mojibake icermez."""
    from pathlib import Path

    kaynak = Path("web_dashboard/tabs") / f"{modul}.py"
    metin = kaynak.read_text(encoding="utf-8")
    for baslik in ("Bu ekran ne işe yarar?", "Nasıl kullanılır?", "Veriler nereden gelir?", "Dikkat:"):
        assert baslik in metin, f"{modul}: '{baslik}' eksik"
    assert "\u00c3" not in metin and "\u00e2\u20ac" not in metin, f"{modul}: mojibake"
