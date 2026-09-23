# -*- coding: utf-8 -*-
"""ALTYAPI-DURUM-SOZLUK-01: durum sozlugu tek kaynaktan gelir.

Kok neden: uc modul kendi listesini tutuyordu; "iptal" semada yoktu ama
panoda kullaniliyordu, denetim betikleri 5 sahte uyari uretiyordu.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))

from src.company_master.orchestrator import task_board as tb  # noqa: E402


def _betik(ad: str):
    """scripts/ altindaki betigi modul olarak yukler (paket degil)."""
    yol = KOK / "scripts" / f"{ad}.py"
    spec = importlib.util.spec_from_file_location(ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_iptal_gecerli_durumdur():
    assert "iptal" in tb.GOREV_DURUMLARI


def test_kapali_durumlar_gorev_durumlarinin_alt_kumesi():
    assert set(tb.KAPALI_DURUMLAR) <= set(tb.GOREV_DURUMLARI)


def test_sema_iptal_durumunu_kabul_eder():
    tb.sema_dogrula({
        "task_id": "T-1", "baslik": "x", "sahip": "ihsan",
        "oncelik": "P2", "durum": "iptal", "dosyalar": [], "mod": "code",
    })


def test_sema_uydurma_durumu_reddeder():
    with pytest.raises(ValueError):
        tb.sema_dogrula({
            "task_id": "T-1", "baslik": "x", "sahip": "ihsan",
            "oncelik": "P2", "durum": "cancelled", "dosyalar": [], "mod": "code",
        })


@pytest.mark.parametrize("betik", ["pano_denetim", "orkestrator_kontrol"])
def test_betikler_ayni_kapali_listesini_gorur(betik):
    assert _betik(betik).KAPALI_DURUMLAR == tb.KAPALI_DURUMLAR


def test_olu_cancelled_durumu_kalmadi():
    assert "cancelled" not in tb.GOREV_DURUMLARI
    assert "cancelled" not in tb.KAPALI_DURUMLAR
