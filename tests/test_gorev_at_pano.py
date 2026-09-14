# -*- coding: utf-8 -*-
"""gorev_at.py cmd_pano cikti formati testleri.

Kapsam:
- Bekleyen tetik satirlarinda gorev basligi + kisa tarih gorunur
- Tam ISO tarih ciktida yer almaz (satir bolunmesi onlenir)
- task_id/tarih eksik tetiklerde cokmez ("?" / "-" duser)
- Onay kuyrugu ozeti kisaltilir
- Bos pano "(bos)" yazar

Calistirma: pytest tests/test_gorev_at_pano.py -q
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import gorev_at  # noqa: E402


def _args() -> argparse.Namespace:
    return argparse.Namespace()


def test_pano_baslik_ve_kisa_tarih_gosterir(capsys, monkeypatch):
    monkeypatch.setattr(gorev_at.tb, "gorev_listesi", lambda: [{"sahip": "kilo"}])
    monkeypatch.setattr(
        gorev_at.tb,
        "gorev_getir",
        lambda tid: {"baslik": "Kariyer.net Scraper"} if tid == "P7-6" else None,
    )
    monkeypatch.setattr(
        gorev_at.trigger,
        "bekleyen_tetikler",
        lambda ajan: [{"task_id": "P7-6", "tarih": "2026-09-14T00:00:00"}],
    )
    monkeypatch.setattr(gorev_at.trigger, "onay_bekleyenler", lambda: [])

    rc = gorev_at.cmd_pano(_args())
    out = capsys.readouterr().out

    assert rc == 0
    assert "Kariyer.net Scraper" in out
    assert "(09-14 00:00)" in out
    assert "T00:00:00" not in out  # tam ISO satiri bolumuyor
    assert "[kilo" in out


def test_pano_eksik_alanlarda_cokmez(capsys, monkeypatch):
    monkeypatch.setattr(gorev_at.tb, "gorev_listesi", lambda: [{"sahip": "roo"}])
    monkeypatch.setattr(gorev_at.tb, "gorev_getir", lambda tid: None)
    monkeypatch.setattr(
        gorev_at.trigger,
        "bekleyen_tetikler",
        lambda ajan: [{"task_id": None, "tarih": None}],
    )
    monkeypatch.setattr(
        gorev_at.trigger,
        "onay_bekleyenler",
        lambda: [{"task_id": "UX-99", "ajan": "roo", "teslim_tarihi": None, "ozet": "x" * 500}],
    )

    rc = gorev_at.cmd_pano(_args())
    out = capsys.readouterr().out

    assert rc == 0
    assert "None" not in out  # id alanı None yazmamali
    assert "?" in out  # task_id yok -> ?
    assert "  -  " in out or "(-)" in out or "(-" in out  # tarih yok -> -
    # ozet 500 karakter degil, kisaltilmis + '…'
    assert "…" in out
    assert len(out.splitlines()) <= 12


def test_pano_bos_ken_bos_yazar(capsys, monkeypatch):
    monkeypatch.setattr(gorev_at.tb, "gorev_listesi", lambda: [])
    monkeypatch.setattr(gorev_at.trigger, "bekleyen_tetikler", lambda ajan: [])
    monkeypatch.setattr(gorev_at.trigger, "onay_bekleyenler", lambda: [])

    rc = gorev_at.cmd_pano(_args())
    out = capsys.readouterr().out

    assert rc == 0
    assert out.count("(bos)") == 2


def test_pano_gecersiz_tarih_degil_ham_doner(capsys, monkeypatch):
    monkeypatch.setattr(gorev_at.tb, "gorev_listesi", lambda: [{"sahip": "kilo"}])
    monkeypatch.setattr(gorev_at.tb, "gorev_getir", lambda tid: {"baslik": "Baslik"})
    monkeypatch.setattr(
        gorev_at.trigger,
        "bekleyen_tetikler",
        lambda ajan: [{"task_id": "X-1", "tarih": "yarin-sabah"}],
    )
    monkeypatch.setattr(gorev_at.trigger, "onay_bekleyenler", lambda: [])

    gorev_at.cmd_pano(_args())
    out = capsys.readouterr().out

    assert "yarin-sabah" in out[:200]  # parse edilemeyen tarih ham kalir, cokmez