# -*- coding: utf-8 -*-
"""ORCH-12: Ajan işbirliği (isbirligi) testleri.

Gerçek pano/rapor dosyalarına dokunmaz: izole pano (tmp_path).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger
from src.company_master.orchestrator import duzen
from src.company_master.orchestrator import isbirligi


@pytest.fixture(autouse=True)
def izole(tmp_path, monkeypatch):
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    return tmp_path


# ---- bos_ajanlar ----

def test_bos_ajanlar_iki_azan_bosta(tmp_path):
    tb.gorev_ekle("T1", "ihsan is", "ihsan", "P1")
    tb.gorev_guncelle("T1", durum="aktif")
    tb.gorev_ekle("T2", "utku is", "utku", "P1")
    tb.gorev_guncelle("T2", durum="aktif")
    bosta = isbirligi.bos_ajanlar()
    assert "ihsan" not in bosta
    assert "utku" not in bosta
    assert "salih" in bosta
    assert "cline" in bosta


def test_bos_ajanlar_hepsi_mesgul(tmp_path):
    # D-60: kanonik ajanlar ihsan / utku / salih / cline.
    for ajan in ["ihsan", "utku", "salih", "cline"]:
        tid = f"T-{ajan}"
        tb.gorev_ekle(tid, f"{ajan} is", ajan, "P1")
        tb.gorev_guncelle(tid, durum="aktif")
    assert isbirligi.bos_ajanlar() == []


def test_bos_ajanlar_tek_bosta(tmp_path):
    tb.gorev_ekle("T1", "ihsan is", "ihsan", "P1")
    tb.gorev_guncelle("T1", durum="review")
    bosta = isbirligi.bos_ajanlar()
    assert "ihsan" not in bosta
    assert "utku" in bosta


# ---- yardim_edilebilir ----

def test_yardim_edilebilir_plan_gorevler(tmp_path):
    tb.gorev_ekle("T1", "api dosya duzeltme", "roo", "P1", dosyalar=["src/api.py"])
    tb.gorev_ekle("T2", "rapor yaz", "roo", "P2", dosyalar=["docs/rapor.md"])
    tb.gorev_ekle("T3", "kendi is", "kilo", "P1")
    sonuc = isbirligi.yardim_edilebilir("kilo")
    ids = [t["task_id"] for t in sonuc]
    assert "T1" in ids
    assert "T2" in ids
    assert "T3" not in ids


def test_yardim_edilebilir_kendi_gorevi_haric(tmp_path):
    tb.gorev_ekle("T1", "kilo is", "kilo", "P1")
    sonuc = isbirligi.yardim_edilebilir("kilo")
    assert not any(t["task_id"] == "T1" for t in sonuc)


def test_yardim_edilebilir_aktif_gorev_haric(tmp_path):
    tb.gorev_ekle("T1", "roo aktif", "roo", "P1")
    tb.gorev_guncelle("T1", durum="aktif")
    sonuc = isbirligi.yardim_edilebilir("kilo")
    assert len(sonuc) == 0


def test_yardim_edilebilir_rol_test_dosya_haritasi(tmp_path):
    tb.gorev_ekle("T1", "api duzelt", "roo", "P1", dosyalar=["src/api.py"])
    sonuc = isbirligi.yardim_edilebilir("kilo")
    t = sonuc[0]
    assert t["rol"] == "test"


def test_yardim_edilebilir_rol_arastirma_dosya_yok(tmp_path):
    tb.gorev_ekle("T1", "arastirma", "roo", "P1")
    sonuc = isbirligi.yardim_edilebilir("kilo")
    t = sonuc[0]
    assert t["rol"] == "arastirma"


# ---- destek_al ----

def test_destek_al_yeni_gorev_olusturur(tmp_path):
    tb.gorev_ekle("COP-15", "test yaz", "roo", "P1", dosyalar=["src/main.py"])
    sonuc = isbirligi.destek_al("kilo", "COP-15", "test")
    assert sonuc["hedef"] == "COP-15"
    gorev = sonuc["gorev"]
    assert gorev["task_id"] == "COP-15-DESTEK-KILO"
    assert gorev["sahip"] == "kilo"
    assert gorev.get("destek_icin") == "COP-15"
    assert gorev.get("rol") == "test"
    assert gorev.get("otomatik_onay") is True


def test_destek_al_hedef_yok_hata(tmp_path):
    with pytest.raises(ValueError):
        isbirligi.destek_al("kilo", "YOK", "test")


def test_destek_al_hedef_done_hata(tmp_path):
    tb.gorev_ekle("T1", "done gorev", "roo", "P1")
    tb.gorev_guncelle("T1", durum="done")
    with pytest.raises(ValueError):
        isbirligi.destek_al("kilo", "T1", "test")


def test_destek_al_kendi_goreve_destek_hata(tmp_path):
    tb.gorev_ekle("T1", "kilo is", "kilo", "P1")
    with pytest.raises(ValueError):
        isbirligi.destek_al("kilo", "T1", "test")


def test_destek_al_tekrar_olusturma_hata(tmp_path):
    tb.gorev_ekle("T1", "test", "roo", "P1")
    isbirligi.destek_al("kilo", "T1", "test")
    with pytest.raises(ValueError):
        isbirligi.destek_al("kilo", "T1", "test")


def test_destek_al_rol_gecersiz_hata(tmp_path):
    tb.gorev_ekle("T1", "test", "roo", "P1")
    with pytest.raises(ValueError):
        isbirligi.destek_al("kilo", "T1", "duzeltme")


def test_destek_al_tetik_duser(tmp_path):
    tb.gorev_ekle("T1", "test", "roo", "P1")
    isbirligi.destek_al("kilo", "T1", "test")
    bek = trigger.bekleyen_tetikler("kilo")
    assert any(k["task_id"] == "T1-DESTEK-KILO" for k in bek)


# ---- otomatik onay ----

def test_otomatik_onay_teslimleme(tmp_path):
    tb.gorev_ekle("COP-15", "test yaz", "roo", "P1")
    isbirligi.destek_al("kilo", "COP-15", "test")
    destek_id = "COP-15-DESTEK-KILO"
    trigger.teslim_et(destek_id, "kilo", "test tamamlandı", data_dir=tmp_path)
    gorev = tb.gorev_getir(destek_id)
    assert gorev["durum"] == "done"
    rapor_yol = tmp_path / "isbirligi_raporu.jsonl"
    assert rapor_yol.exists()
    satirlar = rapor_yol.read_text(encoding="utf-8").strip().splitlines()
    assert len(satirlar) == 1
    rapor = json.loads(satirlar[0])
    assert rapor["destek_task"] == destek_id
    assert rapor["ajan"] == "kilo"
    assert rapor["hedef"] == "COP-15"
    assert rapor["rol"] == "test"
    assert rapor["onaylayan"].startswith("oto:")


def test_otomatik_onay_hedef_not_guncellenir(tmp_path):
    tb.gorev_ekle("COP-15", "test yaz", "roo", "P1")
    isbirligi.destek_al("kilo", "COP-15", "test")
    trigger.teslim_et("COP-15-DESTEK-KILO", "kilo", "test tamamlandı", data_dir=tmp_path)
    hedef = tb.gorev_getir("COP-15")
    not_val = hedef.get("not", "")
    assert "DESTEK" in not_val
    assert "COP-15-DESTEK-KILO" in not_val


# ---- idempotency ----

def test_idempotency_done_goreve_tetik_dusmez(tmp_path):
    tb.gorev_ekle("T1", "test", "roo", "P1")
    tb.gorev_guncelle("T1", durum="done")
    with pytest.raises(trigger.TriggerError):
        trigger.tetik_ekle("T1", "kilo", data_dir=tmp_path)


def test_idempotency_destek_tekrar_hata(tmp_path):
    tb.gorev_ekle("T1", "test", "roo", "P1")
    isbirligi.destek_al("kilo", "T1", "test")
    with pytest.raises(ValueError):
        isbirligi.destek_al("kilo", "T1", "test")
