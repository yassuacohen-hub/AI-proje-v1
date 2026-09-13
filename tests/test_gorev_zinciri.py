# -*- coding: utf-8 -*-
"""ORCH-11: Gorev zinciri (otomatik ardisik tetikleme) testleri."""
from __future__ import annotations

import json

import pytest

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger


@pytest.fixture()
def zincir_ortami(tmp_path, monkeypatch):
    """Izole pano + tetik dizini (gercek panoya dokunmaz)."""
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "STATE_JSON", tmp_path / "state.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md")
    for tid, baslik in [("Z-1", "Birinci"), ("Z-2", "Ikinci"), ("Z-3", "Ucuncu")]:
        tb.gorev_ekle(task_id=tid, baslik=baslik, sahip="kilo", oncelik="P1")
    return tmp_path


def test_zincir_ilk_gorev_tetiklenir_digerleri_bekler(zincir_ortami):
    trigger.gorev_zinciri(["Z-1", "Z-2", "Z-3"], "kilo", "test", zincir_ortami)

    bekleyen = trigger.bekleyen_tetikler("kilo", zincir_ortami)
    assert [k["task_id"] for k in bekleyen] == ["Z-1"]

    tumu = trigger._tetikleri_oku("kilo", zincir_ortami)
    zincirde = [k for k in tumu if k["durum"] == "zincir_bekleme"]
    assert [k["task_id"] for k in zincirde] == ["Z-2", "Z-3"]
    assert zincirde[0]["onceki_gorev"] == "Z-1"
    assert zincirde[1]["onceki_gorev"] == "Z-2"


def test_teslim_sonraki_halkayi_otomatik_tetikler(zincir_ortami):
    trigger.gorev_zinciri(["Z-1", "Z-2", "Z-3"], "kilo", "test", zincir_ortami)

    trigger.tetik_al("kilo", "Z-1", zincir_ortami)
    trigger.teslim_et("Z-1", "kilo", "birinci bitti", None, zincir_ortami)

    # Z-2 artik bekliyor durumunda olmali (kullanici mudahalesi yok)
    bekleyen = trigger.bekleyen_tetikler("kilo", zincir_ortami)
    assert [k["task_id"] for k in bekleyen] == ["Z-2"]

    # Z-3 hala zincirde beklemeli
    tumu = trigger._tetikleri_oku("kilo", zincir_ortami)
    z3 = next(k for k in tumu if k["task_id"] == "Z-3")
    assert z3["durum"] == "zincir_bekleme"


def test_zincir_uctan_uca_tek_seferde_akar(zincir_ortami):
    trigger.gorev_zinciri(["Z-1", "Z-2", "Z-3"], "kilo", "test", zincir_ortami)

    for tid in ["Z-1", "Z-2", "Z-3"]:
        bekleyen = trigger.bekleyen_tetikler("kilo", zincir_ortami)
        assert [k["task_id"] for k in bekleyen] == [tid], f"{tid} otomatik tetiklenmedi"
        trigger.tetik_al("kilo", tid, zincir_ortami)
        trigger.teslim_et(tid, "kilo", f"{tid} bitti", None, zincir_ortami)

    assert trigger.bekleyen_tetikler("kilo", zincir_ortami) == []
    assert len(trigger.onay_bekleyenler(zincir_ortami)) == 3


def test_bos_liste_hata_verir(zincir_ortami):
    with pytest.raises(trigger.TriggerError):
        trigger.gorev_zinciri([], "kilo", "", zincir_ortami)


def test_zincir_disi_teslim_zinciri_bozmaz(zincir_ortami):
    """Zincirle ilgisiz bir gorev teslim edilirse zincir tetiklenmemeli."""
    tb.gorev_ekle("BAGIMSIZ", "Bagimsiz is", "kilo", "P2")
    trigger.gorev_zinciri(["Z-1", "Z-2"], "kilo", "test", zincir_ortami)

    trigger.tetik_ekle("BAGIMSIZ", "kilo", "", zincir_ortami)
    trigger.tetik_al("kilo", "BAGIMSIZ", zincir_ortami)
    trigger.teslim_et("BAGIMSIZ", "kilo", "bagimsiz bitti", None, zincir_ortami)

    tumu = trigger._tetikleri_oku("kilo", zincir_ortami)
    z2 = next(k for k in tumu if k["task_id"] == "Z-2")
    assert z2["durum"] == "zincir_bekleme"
