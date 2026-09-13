# -*- coding: utf-8 -*-
"""ORCH-09: Otomatik tetikleme nobetcisi testleri."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import nobetci, trigger


@pytest.fixture(autouse=True)
def izole_pano(tmp_path, monkeypatch):
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    for name, suf in [("TASK_BOARD",".json"),("FILE_LOCKS",".json"),
                       ("STATE_JSON",".json"),("TASK_MD",".md"),
                       ("AGENT_SYNC_MD",".md"),("AGENT_SYNC_MD_KOPYA",".md")]:
        monkeypatch.setattr(tb, name, tmp_path / f"{name.lower()}{suf}")
    return tmp_path


def _gorev_ac(task_id="T-09", ajan="kilo"):
    tb.gorev_ekle(task_id, f"{task_id} tetik testi", ajan, "P1")


def _tetik_gec_kim(ajan="kilo", task_id="T-09", sure_sn=120):
    _gorev_ac(task_id, ajan)
    trigger.tetik_ekle(task_id, ajan, talimat="tetik testi", data_dir=None)
    nobetci.tetik_gecikmis_yap(ajan, task_id, sure_sn)
    return trigger.bekleyen_tetikler(ajan)[0]


def test_geciken_tetikler_bos(izole_pano):
    assert nobetci.geciken_tetikler(izole_pano) == []


def test_geciken_tetikler_gelir(izole_pano):
    _tetik_gec_kim()
    gecen = nobetci.geciken_tetikler(izole_pano, kademe_sn=60)
    assert len(gecen) == 1
    assert gecen[0]["task_id"] == "T-09"
    assert gecen[0]["gecikme_dk"] >= 2


def test_geciken_tetikler_yok_gercek(izole_pano):
    _tetik_gec_kim()
    assert nobetci.geciken_tetikler(izole_pano, kademe_sn=99999) == []


def test_tetik_uyari_ekle(izole_pano):
    trigger.tetik_ekle("T-09", "kilo", talimat="tetik", data_dir=None)
    nobetci.tetik_uyari_ekle("kilo", "T-09")
    k = trigger.bekleyen_tetikler("kilo")[0]
    assert k["uyari_sayisi"] == 1
    assert "uyari_tarihi" in k


def test_tetik_firlat_olusturur_alarm_log(izole_pano):
    k = _tetik_gec_kim()
    ayar = nobetci.nobetci_ayar_oku(izole_pano)
    nobetci.tetik_firlat(k, ayar, izole_pano)
    logline = (izole_pano / "trigger_log.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1]
    log = json.loads(logline)
    assert log["kaynak"] == "nobetci"
    assert log["task_id"] == "T-09"
    alarm = json.loads((izole_pano / "triggers" / "kilo.ALARM.json").read_text(encoding="utf-8-sig"))
    assert any(a["task_id"] == "T-09" for a in alarm)


def test_geciken_tetikler_cok_geciken(izole_pano):
    _tetik_gec_kim(task_id="T-09", sure_sn=120)
    _tetik_gec_kim(task_id="T-10", sure_sn=120)
    _tetik_gec_kim(task_id="T-11", sure_sn=120)
    gecen = nobetci.geciken_tetikler(izole_pano, kademe_sn=60)
    assert len(gecen) == 3
    task_ids = [g["task_id"] for g in gecen]
    assert "T-09" in task_ids and "T-10" in task_ids and "T-11" in task_ids


def test_nobet_tut_firlatir(izole_pano):
    _tetik_gec_kim()
    sonuc = nobetci.nobet_tut(
        ayar={"kademe_sn": 60, "kanallar": ["log"], "telegram": False},
        data_dir=izole_pano,
    )
    assert len(sonuc) == 1
    assert trigger.bekleyen_tetikler("kilo")[0].get("uyari_tarihi")


def test_nobet_tut_devre_disi(izole_pano):
    nobetci.nobetci_ayar_yaz({"devre_disi": True, "kademe_sn": 60}, izole_pano)
    assert nobetci.nobet_tut(data_dir=izole_pano) == []


def test_ayar_oku_default(izole_pano):
    ayar = nobetci.nobetci_ayar_oku(izole_pano)
    assert ayar["kademe_sn"] == 600
    assert "log" in ayar["kanallar"]


def test_ayar_yaz_yukler(izole_pano):
    nobetci.nobetci_ayar_yaz({"kademe_sn": 300, "kanallar": ["ses"]}, izole_pano)
    assert nobetci.nobetci_ayar_oku(izole_pano)["kademe_sn"] == 300


def test_tetik_gecikmis_yap_tarih_ceker(izole_pano):
    trigger.tetik_ekle("T-09", "kilo", data_dir=None)
    nobetci.tetik_gecikmis_yap("kilo", "T-09", 300)
    from datetime import datetime as _dt
    t = _dt.fromisoformat(trigger.bekleyen_tetikler("kilo")[0]["tarih"])
    assert (_dt.now() - t).total_seconds() >= 290
