# -*- coding: utf-8 -*-
"""B-14 hafiza izi kapisi — `gorev_kutusu.py teslim` ve yardimcilari.

Karar: AGENTS.md D-198 / denetim bulgusu B-14 (kapanan is hub'a yansimiyor).
Kapsanan komut: `teslim` (cmd_teslim), yardimcilar `_hafiza_hedefleri`, `_hafiza_izi`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "scripts"))

import gorev_kutusu as gk  # noqa: E402

# DIKKAT: gorev_kutusu "src.company_master..." yolundan import eder; testte
# "company_master..." yazmak ayri bir modul nesnesi yaratir ve monkeypatch
# komutu etkilemez. Bu yuzden modul komutun kendi referansindan alinir.
tb = gk.tb


def _kurulum(tmp_path, monkeypatch, *, brief_metin: str | None = None,
             ssot_metin: str = "", hub_metin: str = "") -> dict:
    """Izole bir kok: SSOT, varsayilan hub ve istege bagli brief dosyasi."""
    (tmp_path / "hubs").mkdir(exist_ok=True)
    ssot = tmp_path / "ssot.md"
    ssot.write_text(ssot_metin, encoding="utf-8")
    hub = tmp_path / "hubs" / "ADMIN_DASHBOARD_HUB.md"
    hub.write_text(hub_metin, encoding="utf-8")

    gorev: dict = {"task_id": "TEST-B14-01", "durum": "in_progress"}
    if brief_metin is not None:
        (tmp_path / "plans").mkdir()
        (tmp_path / "plans" / "brief_test.md").write_text(brief_metin, encoding="utf-8")
        gorev["brief"] = "plans/brief_test.md"

    monkeypatch.setattr(gk, "_KOK", tmp_path)
    monkeypatch.setattr(gk, "_SSOT", ssot)
    monkeypatch.setattr(gk, "_HUB", hub)
    monkeypatch.setattr(tb, "gorev_getir", lambda tid: gorev if tid == gorev["task_id"] else None)
    return gorev


def _args(**ek) -> argparse.Namespace:
    temel = dict(task_id="TEST-B14-01", ajan="utku", ozet="test", cikti=None, zorla=False)
    temel.update(ek)
    return argparse.Namespace(**temel)


def test_izsiz_teslim_reddedilir(tmp_path, monkeypatch, capsys):
    """SSOT'ta da hub'da da task_id yoksa teslim 1 doner ve gerekce basar."""
    _kurulum(tmp_path, monkeypatch, ssot_metin="bos", hub_metin="bos")
    cagrildi = []
    monkeypatch.setattr(gk.trigger, "teslim_et", lambda *a, **k: cagrildi.append(a))

    assert gk.cmd_teslim(_args()) == 1
    assert not cagrildi, "reddedilen teslimde trigger.teslim_et cagrilmamali"
    hata = capsys.readouterr().err
    assert "hafiza izi yok" in hata and "B-14" in hata


def test_hub_izi_varsa_teslim_gecer(tmp_path, monkeypatch):
    """Hub'da task_id geciyorsa kapi acilir; teslim normal akisina devam eder."""
    _kurulum(tmp_path, monkeypatch, hub_metin="| TEST-B14-01 | kapandi | 2026-09-24 |")
    monkeypatch.setattr(gk.trigger, "teslim_et", lambda *a, **k: {"task_id": "TEST-B14-01"})

    assert gk.cmd_teslim(_args()) == 0


def test_zorla_gecerse_panoya_atlandi_islenir(tmp_path, monkeypatch):
    """--zorla kacis kapisi (D-65): is durmaz ama borc panoya yazilir."""
    _kurulum(tmp_path, monkeypatch, ssot_metin="bos", hub_metin="bos")
    monkeypatch.setattr(gk.trigger, "teslim_et", lambda *a, **k: {"task_id": "TEST-B14-01"})
    yazilan: dict = {}
    monkeypatch.setattr(tb, "gorev_guncelle", lambda tid, **f: yazilan.update({tid: f}))

    assert gk.cmd_teslim(_args(zorla=True)) == 0
    assert yazilan == {"TEST-B14-01": {"hafiza_izi": "atlandi"}}


def test_hedefler_briefteki_hubu_secer(tmp_path, monkeypatch):
    """Brief `hubs/XXX` yaziyorsa iz orada aranir, varsayilan hub'da degil."""
    _kurulum(tmp_path, monkeypatch,
             brief_metin="**Hub:** `hubs/ORKESTRASYON_AJANLAR_HUB.md` — kapanista yazilir.")
    (tmp_path / "hubs" / "ORKESTRASYON_AJANLAR_HUB.md").write_text("bos", encoding="utf-8")

    hedefler = gk._hafiza_hedefleri("TEST-B14-01")
    assert hedefler[0].name == "ssot.md"
    assert [y.name for y in hedefler[1:]] == ["ORKESTRASYON_AJANLAR_HUB.md"]


def test_briefsiz_gorev_varsayilan_huba_duser(tmp_path, monkeypatch):
    """Brief yoksa kapi yine calisir; hedef varsayilan hub'dir (belirsizlik yok)."""
    _kurulum(tmp_path, monkeypatch)
    assert [y.name for y in gk._hafiza_hedefleri("TEST-B14-01")] == [
        "ssot.md", "ADMIN_DASHBOARD_HUB.md"]
