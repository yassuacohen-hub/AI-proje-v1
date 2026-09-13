# -*- coding: utf-8 -*-
"""ORCH-11: duzen.py (pano hijyeni + cakisima + blokaj) testleri.

Gercek dosyalara dokunmaz: izole pano (tmp_path).
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


@pytest.fixture(autouse=True)
def izole(tmp_path, monkeypatch):
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    return tmp_path


# ---- cakisirma_analizi ----

def test_cakisirma_aktif_gorev_dosyasi(tmp_path):
    tb.gorev_ekle("T-1", "roo is", "roo", "P1", dosyalar=["a.py"])
    tb.gorev_guncelle("T-1", durum="aktif")
    r = duzen.cakisirma_analizi("T-2", ["a.py", "b.py"])
    assert len(r["cakisan"]) == 1
    assert r["cakisan"][0]["dosya"] == "a.py"
    assert r["cakisan"][0]["tutan"] == "T-1"
    assert r["temiz"] == ["b.py"]


def test_cakisirma_kendi_dosyasi_degil(tmp_path):
    tb.gorev_ekle("T-1", "roo is", "roo", "P1", dosyalar=["a.py"])
    tb.gorev_guncelle("T-1", durum="aktif")
    r = duzen.cakisirma_analizi("T-1", ["a.py"])
    assert r["cakisan"] == []
    assert r["temiz"] == ["a.py"]


# ---- guvenli_gorev_ekle ----

def test_guvenli_ekle_kilit_atlar_uyari_verir(tmp_path):
    tb.gorev_ekle("T-1", "roo is", "roo", "P1", dosyalar=["a.py"])
    tb.gorev_guncelle("T-1", durum="aktif")
    r = duzen.guvenli_gorev_ekle("T-2", "kilo is", "kilo", dosyalar=["a.py"])
    assert len(r["uyarilar"]) == 1
    assert r["gorev"]["dosyalar"] == []  # cakisan dosya kilitlenmedi
    # kilitlenmedigini dogrula: FILE_LOCKS'ta a.py yok
    kilitler = json.loads((tmp_path / "file_locks.json").read_text(encoding="utf-8"))
    assert "a.py" not in kilitler


def test_guvenli_ekle_cift_id_hata(tmp_path):
    tb.gorev_ekle("T-1", "is", "roo")
    with pytest.raises(ValueError):
        duzen.guvenli_gorev_ekle("T-1", "tekrar", "kilo")


def test_guvenli_ekle_blokaj_yazar_tetikdusmez(tmp_path):
    tb.gorev_ekle("T-D", "bagimlilik", "roo")
    r = duzen.guvenli_gorev_ekle("T-B", "bloklu is", "kilo", blokaj=["T-D"], tetikle=True)
    assert r["gorev"]["blokaj"] == ["T-D"]
    # blokajli gorev icin tetik dusmez (bagimlilik bitince bakim dusurur)
    assert duzen.trigger.bekleyen_tetikler("kilo") == []


# ---- blokaj_guncelle ----

def test_blokaj_otomatik_kapanir(tmp_path):
    tb.gorev_ekle("T-D", "bagimlilik", "roo")   # plan (done degil)
    tb.gorev_ekle("T-B", "bloklu", "kilo")
    tb.gorev_guncelle("T-B", blokaj=["T-D"])
    r = duzen.blokaj_guncelle()
    assert r["kapanan"] == ["T-B"]
    assert tb.gorev_getir("T-B")["durum"] == "blocked"


def test_blokaj_otomatik_acilir_tetik_duser(tmp_path):
    tb.gorev_ekle("T-D", "bagimlilik", "roo")
    tb.gorev_guncelle("T-D", durum="done")
    tb.gorev_ekle("T-B", "bloklu", "kilo")
    tb.gorev_guncelle("T-B", durum="blocked", blokaj=["T-D"])
    r = duzen.blokaj_guncelle()
    assert r["acilan"] == ["T-B"]
    gorev = tb.gorev_getir("T-B")
    assert gorev["durum"] == "plan"
    # ajan posta kutusuna tetik dustu
    bek = trigger.bekleyen_tetikler("kilo")
    assert [k["task_id"] for k in bek] == ["T-B"]


def test_blokaj_plan_gorev_de_acilir(tmp_path):
    # Gorev olusturulurken bagimlilik zaten done: 'plan' durumda bekliyor,
    # 'blocked'a hic dusmemis. Kapilar yine de acilmali + tetik dusmeli.
    tb.gorev_ekle("T-D", "bagimlilik", "roo")
    tb.gorev_guncelle("T-D", durum="done")
    tb.gorev_ekle("T-P", "plan bekleyen", "kilo")
    tb.gorev_guncelle("T-P", blokaj=["T-D"])  # durum hala 'plan'
    r = duzen.blokaj_guncelle()
    assert r["acilan"] == ["T-P"]
    assert tb.gorev_getir("T-P")["durum"] == "plan"
    assert [k["task_id"] for k in trigger.bekleyen_tetikler("kilo")] == ["T-P"]


# ---- pano_bakim ----

def _ham_yaz(kayitlar):
    tb._write_json(tb.TASK_BOARD, kayitlar)


def test_bakim_cift_kayit_temizler(tmp_path):
    # COP-11 iki kez: biri plan, biri done (done kazanmali)
    _ham_yaz([
        {"task_id": "COP-11", "baslik": "cift plan", "sahip": "copilot", "oncelik": "P2", "durum": "plan"},
        {"task_id": "COP-11", "baslik": "gercek done", "sahip": "copilot", "oncelik": "P2", "durum": "done"},
    ])
    r = duzen.pano_bakim()
    assert r["dedupe"] == 1
    kalan = [t for t in tb.gorev_listesi() if t["task_id"] == "COP-11"]
    assert len(kalan) == 1
    assert kalan[0]["durum"] == "done"


def test_bakim_takili_tetik_esitler(tmp_path):
    tb.gorev_ekle("T-1", "is", "kilo")
    tb.gorev_guncelle("T-1", durum="done")
    # Bayat tetik: done goreve yine de 'bekliyor' kaydi dusmus (eski/harici)
    # Not: tetik_ekle artik idempotency nedeniyle done'a tetik dusurmez;
    # bayat kayit dogrudan dosyaya yazilarak simule edilir.
    trigger._tetikleri_yaz(
        [{"task_id": "T-1", "ajan": "kilo", "talimat": "bayat", "tarih": "2026-09-13",
          "durum": "bekliyor"}],
        "kilo")
    r = duzen.pano_bakim()
    assert r["tetik_esit"] >= 1
    tum = trigger._tetikleri_oku("kilo")
    assert tum[0]["durum"] == "done"
    # posta kutusu artik temiz
    assert trigger.bekleyen_tetikler("kilo") == []


def test_bakim_bayat_zincir_devam_ettirir(tmp_path):
    tb.gorev_ekle("Z-A", "once", "kilo")
    tb.gorev_ekle("Z-B", "sonra", "kilo")
    tb.gorev_guncelle("Z-A", durum="done")
    # elle zincir_bekleme kaydi yaz (A done olmus ama zincir ilerlememis)
    kayit = {"task_id": "Z-B", "ajan": "kilo", "talimat": "", "tarih": "2026-09-13",
             "durum": "zincir_bekleme", "onceki_gorev": "Z-A"}
    trigger._tetikleri_yaz([kayit], "kilo")
    r = duzen.pano_bakim()
    assert r["zincir"] == ["Z-A -> Z-B"]
    tum = trigger._tetikleri_oku("kilo")
    assert tum[0]["durum"] == "bekliyor"


# ---- ozet_rapor ----

def test_ozet_rapor_kisa_ve_bilgili(tmp_path):
    tb.gorev_ekle("T-1", "is", "roo")
    tb.gorev_guncelle("T-1", durum="aktif")
    s = duzen.ozet_rapor()
    assert "AKTIF:" in s and "T-1(roo)" in s
    assert "BLOCKED: 0" in s
    assert len(s) < 300  # token dostu: tek satir, kisa
