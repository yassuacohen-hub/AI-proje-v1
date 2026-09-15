# -*- coding: utf-8 -*-
"""PO-BACK-04 — Paket fiyat kataloğu tekilleştirme testleri."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from company_master.paketler import (
    fiyat_katalogu,
    _ORJINAL_FIYATLAR,
    _ORJINAL_OZELLIKLER,
    _ORJINAL_SIRALAMA,
)


def test_fiyat_katalogu_tek_kaynak():
    """fiyat_katalogu() 4 tier döndürür."""
    katalog = fiyat_katalogu()

    assert [p["name"] for p in katalog] == ["Temel", "Standart", "Profesyonel", "Kurumsal"]
    assert [p["price"] for p in katalog] == [499.0, 2999.0, 7999.0, 19999.0]


def test_fiyat_katalogu_tier_siralama():
    """İlk tier Temel, son tier Kurumsal olmalı."""
    katalog = fiyat_katalogu()

    assert katalog[0]["name"] == "Temel"
    assert katalog[-1]["name"] == "Kurumsal"
    assert len(katalog) == 4


def test_fiyat_katalogu_features_tam():
    """Her tier'da features, description, icon olmalı."""
    katalog = fiyat_katalogu()

    assert all(p["features"] for p in katalog)
    assert all(p["description"] for p in katalog)
    assert all(p["icon"] for p in katalog)


# ---------------------------------------------------------------------------
# PO-BACK-04: Ek testler (≥5 yeni test)
# ---------------------------------------------------------------------------


def test_orjinal_fiyatlar_tam_sayi():
    """_ORJINAL_FIYATLAR'daki tüm değerler pozitif float."""
    for isim, price in _ORJINAL_FIYATLAR.items():
        assert isinstance(price, (int, float)), f"{isim} price tipi hatalı"
        assert price > 0, f"{isim} price negatif/sıfır"


def test_orjinal_ozellikler_listesi():
    """_ORJINAL_OZELLIKLER'daki tüm değerler list[str]."""
    for isim, ozellikler in _ORJINAL_OZELLIKLER.items():
        assert isinstance(ozellikler, list), f"{isim} ozellikler listesi değil"
        assert all(isinstance(o, str) for o in ozellikler), f"{isim} ozellikler string değil"
        assert len(ozellikler) > 0, f"{isim} ozellikler boş"


def test_orjinal_siralama_kapsam():
    """_ORJINAL_SIRALAMA 4 elemanlı ve doğru sıralı."""
    assert len(_ORJINAL_SIRALAMA) == 4
    assert _ORJINAL_SIRALAMA == ["Temel", "Standart", "Profesyonel", "Kurumsal"]


def test_fiyat_katalogu_fiyatlar_eslesir():
    """fiyat_katalogu() returned prices match _ORJINAL_FIYATLAR."""
    katalog = fiyat_katalogu()
    for entry in katalog:
        name = entry["name"]
        assert entry["price"] == _ORJINAL_FIYATLAR[name], f"{name} price eşleşmiyor"


def test_fiyat_katalogu_ozellikler_eslesir():
    """fiyat_katalogu() returned features match _ORJINAL_OZELLIKLER."""
    katalog = fiyat_katalogu()
    for entry in katalog:
        name = entry["name"]
        assert entry["features"] == _ORJINAL_OZELLIKLER[name], f"{name} features eşleşmiyor"


def test_fiyat_katalogu_icon_var():
    """Her tier'da icon var ve beklenen ikonlar."""
    expected_icons = {
        "Temel": "fa-tag",
        "Standart": "fa-box",
        "Profesyonel": "fa-shield",
        "Kurumsal": "fa-building",
    }
    katalog = fiyat_katalogu()
    for entry in katalog:
        name = entry["name"]
        assert entry["icon"] == expected_icons[name], f"{name} icon eşleşmiyor"


def test_fiyat_katalogu_description_var():
    """Her tier'da description var."""
    katalog = fiyat_katalogu()
    for entry in katalog:
        assert entry["description"], f"{entry['name']} description boş"


def test_sync_paket_fiyatlari_modul_elmeli():
    """scripts/sync_paket_fiyatlari.py var ve import edilebilir."""
    sync_path = Path(__file__).resolve().parent.parent / "scripts" / "sync_paket_fiyatlari.py"
    assert sync_path.exists(), f"scripts/sync_paket_fiyatlari.py yok: {sync_path}"

    # Modülü import edebilir miyiz?
    sys.path.insert(0, str(sync_path.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("sync_paket_fiyatlari", sync_path)
    assert spec is not None, "spec None"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "fiyat_katalogu")
    assert hasattr(mod, "check_katalog_uyumu")
    assert hasattr(mod, "katalogu_json_yaz")