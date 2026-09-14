# -*- coding: utf-8 -*-
"""ORCH-13: Pano sema dogrulama (S-05) + tetik_al pano fallback (S-06) testleri.

Kaynak elestiri kayitlari: docs/ROO_ELESTIRI_NOTLARI.md
- S-05: Tek bozuk pano kaydi (or. `oncelik` alani eksik WIKI-01) TUM ajanlarin
  pano yazimini KeyError ile cokertiyordu.
- S-06: `gorev_kutusu.py al` yalnizca posta kutusunda tetik varsa calisiyordu;
  panoya elle eklenen gorev alinamiyordu.
"""
from __future__ import annotations

import pytest

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger


@pytest.fixture(autouse=True)
def izole_pano(tmp_path, monkeypatch):
    """Pano + senkron dosyalarini tmp_path'e yonlendir (gercek panoya dokunma)."""
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "STATE_JSON", tmp_path / "state.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md")
    return tmp_path


# ---- S-05: sema dogrulama ----

def test_sema_dogrula_eksik_oncelik_reddeder():
    """WIKI-01 vakasi: `oncelik` alani olmayan kayit panoya girmemeli."""
    with pytest.raises(ValueError, match="eksik alan"):
        tb.sema_dogrula({"task_id": "X-1", "baslik": "b", "sahip": "roo",
                         "durum": "plan", "dosyalar": []})


def test_sema_dogrula_eksik_sahip_reddeder():
    with pytest.raises(ValueError, match="eksik alan"):
        tb.sema_dogrula({"task_id": "X-1", "baslik": "b", "oncelik": "P1",
                         "durum": "plan", "dosyalar": []})


def test_sema_dogrula_gecersiz_durum_reddeder():
    with pytest.raises(ValueError, match="Gecersiz durum"):
        tb.sema_dogrula({"task_id": "X-1", "baslik": "b", "sahip": "roo",
                         "oncelik": "P1", "durum": "uydurma", "dosyalar": []})


def test_sema_dogrula_dosyalar_liste_olmali():
    with pytest.raises(ValueError, match="liste olmali"):
        tb.sema_dogrula({"task_id": "X-1", "baslik": "b", "sahip": "roo",
                         "oncelik": "P1", "durum": "plan", "dosyalar": "a.py"})


def test_sema_dogrula_gecerli_kaydi_gecirir():
    tb.sema_dogrula({"task_id": "X-1", "baslik": "b", "sahip": "roo",
                     "oncelik": "P1", "durum": "plan", "dosyalar": []})


def test_gorev_normalize_eksikleri_doldurur():
    bozuk = {"task_id": "WIKI-01", "baslik": "Admin kilavuz", "sahip": "orkestrator",
             "durum": "done"}
    duzeltilmis = tb.gorev_normalize(bozuk)
    assert duzeltilmis["oncelik"] == "P2"
    assert duzeltilmis["dosyalar"] == []
    # task_id uydurulmaz, korunur
    assert duzeltilmis["task_id"] == "WIKI-01"


def test_gorev_normalize_bozuk_dosyalar_alanini_listeye_cevirir():
    duzeltilmis = tb.gorev_normalize({"task_id": "X-1", "dosyalar": "a.py"})
    assert duzeltilmis["dosyalar"] == []


def test_pano_normalize_onarilan_idleri_dondurur():
    board = [
        {"task_id": "OK-1", "baslik": "b", "sahip": "roo", "oncelik": "P1",
         "durum": "plan", "dosyalar": []},
        {"task_id": "BOZUK-1", "baslik": "b", "sahip": "roo", "durum": "plan"},
    ]
    _, onarilan = tb.pano_normalize(board)
    assert onarilan == ["BOZUK-1"]
    assert board[1]["oncelik"] == "P2"


def test_bozuk_kayit_pano_yazimini_cokertmez(tmp_path):
    """S-05 regresyon: eksik alanli kayit varken gorev_ekle/_md_yaz patlamamali."""
    tb._write_json(tb.TASK_BOARD, [
        {"task_id": "WIKI-01", "baslik": "Admin kilavuz", "sahip": "orkestrator",
         "durum": "done"},  # `oncelik` YOK -> eski kodda KeyError
    ])
    tb.gorev_ekle("YENI-1", "Yeni gorev", "roo", "P1")
    assert tb.gorev_getir("YENI-1")["durum"] == "plan"
    # markdown + AGENT_SYNC uretimi de ayakta kalmali
    tb._md_yaz(tb._read_json(tb.TASK_BOARD))
    assert "WIKI-01" in tb.agent_sync_olustur()


def test_gorev_guncelle_bozuk_kaydi_onarir(tmp_path):
    """Self-healing: her yazimda eski kayitlar semaya tamamlanir."""
    tb._write_json(tb.TASK_BOARD, [
        {"task_id": "WIKI-01", "baslik": "Admin kilavuz", "sahip": "orkestrator",
         "durum": "done"},
        {"task_id": "T-1", "baslik": "b", "sahip": "roo", "oncelik": "P1",
         "durum": "plan", "dosyalar": []},
    ])
    tb.gorev_guncelle("T-1", durum="aktif")
    assert tb.gorev_getir("WIKI-01")["oncelik"] == "P2"


def test_gorev_guncelle_olmayan_gorev_none_dondurur():
    tb.gorev_ekle("T-1", "b", "roo", "P1")
    assert tb.gorev_guncelle("YOK-9", durum="aktif") is None


# ---- S-06: tetik_al pano fallback ----

def test_tetiksiz_kendi_gorevini_panodan_alabilir(tmp_path):
    tb.gorev_ekle("PANO-1", "Panoya elle eklenmis gorev", "roo", "P1")
    sonuc = trigger.tetik_al("roo", "PANO-1", data_dir=tmp_path)
    assert sonuc["durum"] == "alindi"
    assert sonuc["kaynak"] == "pano"
    assert tb.gorev_getir("PANO-1")["durum"] == "aktif"


def test_baskasinin_gorevi_panodan_alinamaz(tmp_path):
    tb.gorev_ekle("PANO-2", "Copilot gorevi", "copilot", "P1")
    with pytest.raises(trigger.TriggerError, match="ajanına ait"):
        trigger.tetik_al("roo", "PANO-2", data_dir=tmp_path)
    assert tb.gorev_getir("PANO-2")["durum"] == "plan"


def test_zaten_aktif_gorev_tekrar_alinamaz(tmp_path):
    tb.gorev_ekle("PANO-3", "b", "roo", "P1")
    trigger.tetik_al("roo", "PANO-3", data_dir=tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.tetik_al("roo", "PANO-3", data_dir=tmp_path)


def test_panoda_olmayan_gorev_hala_reddedilir(tmp_path):
    with pytest.raises(trigger.TriggerError, match="panoda bulunamadı"):
        trigger.tetik_al("roo", "HIC-YOK", data_dir=tmp_path)


def test_tetik_varsa_kaynak_tetik_olur(tmp_path):
    tb.gorev_ekle("PANO-4", "b", "roo", "P1")
    trigger.tetik_ekle("PANO-4", "roo", data_dir=tmp_path)
    sonuc = trigger.tetik_al("roo", "PANO-4", data_dir=tmp_path)
    assert sonuc["kaynak"] == "tetik"
    assert trigger.bekleyen_tetikler("roo", tmp_path) == []
