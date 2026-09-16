# -*- coding: utf-8 -*-
"""S-07 (sahip karari 2026-09-16): otomatik onay yalniz P2 ve alti.

P0/P1 gorevler oto-nobetci / hepsini-tamamla tarafindan onaylanmaz; roo elle onaylar.
Pano disi gorev (D-35 hayalet onay) de otomatik onaylanmaz.
"""
from __future__ import annotations

import pytest

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger


@pytest.fixture()
def pano(tmp_path, monkeypatch):
    """Izole pano (gercek panoya dokunmaz)."""
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "STATE_JSON", tmp_path / "state.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md")
    tb.gorev_ekle(task_id="S07-P0", baslik="Kritik", sahip="kilo", oncelik="P0")
    tb.gorev_ekle(task_id="S07-P1", baslik="Yuksek", sahip="kilo", oncelik="P1")
    tb.gorev_ekle(task_id="S07-P2", baslik="Normal", sahip="kilo", oncelik="P2")
    tb.gorev_ekle(task_id="S07-P3", baslik="Dusuk", sahip="kilo", oncelik="p3")
    return tmp_path


@pytest.mark.parametrize("task_id", ["S07-P0", "S07-P1"])
def test_p0_p1_elle_onay(pano, task_id):
    uygun, gerekce = trigger.otomatik_onaylanabilir(task_id)
    assert uygun is False
    assert "S-07" in gerekce


@pytest.mark.parametrize("task_id", ["S07-P2", "S07-P3"])
def test_p2_ve_alti_otomatik(pano, task_id):
    uygun, _ = trigger.otomatik_onaylanabilir(task_id)
    assert uygun is True


def test_pano_disi_gorev_otomatik_onaylanmaz(pano):
    uygun, gerekce = trigger.otomatik_onaylanabilir("HAYALET-99")
    assert uygun is False
    assert "D-35" in gerekce


def test_nobetci_dongusu_p1_atlar_p2_onaylar(pano, monkeypatch):
    """oto_nobetci/hepsini-tamamla ile ayni mantik: P1 kuyrukta kalir, P2 done olur."""
    for tid in ("S07-P1", "S07-P2"):
        trigger.teslim_et(tid, "kilo", "test teslim", data_dir=pano)
    kuyruk = trigger.onay_bekleyenler(pano)
    assert {k["task_id"] for k in kuyruk} == {"S07-P1", "S07-P2"}

    onaylanan: list[str] = []
    for k in kuyruk:
        uygun, _ = trigger.otomatik_onaylanabilir(k["task_id"])
        if not uygun:
            continue
        trigger.onayla(k["task_id"], "oto-nobetci", data_dir=pano)
        onaylanan.append(k["task_id"])

    assert onaylanan == ["S07-P2"]
    assert tb.gorev_getir("S07-P2")["durum"] == "done"
    assert tb.gorev_getir("S07-P1")["durum"] != "done"
    kalan = trigger.onay_bekleyenler(pano)
    assert [k["task_id"] for k in kalan] == ["S07-P1"]
