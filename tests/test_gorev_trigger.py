# -*- coding: utf-8 -*-
"""ORCH-08: Görev tetikleme + onay kuyruğu testleri.

Gerçek pano/AGENT_SYNC dosyalarına dokunmaz: task_board sabitleri tmp_path'e
yönlendirilir; tetik/onay dosyaları data_dir parametresiyle tmp dizinde tutulur.
"""
from __future__ import annotations

import pytest

from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator import trigger


@pytest.fixture(autouse=True)
def izole_pano(tmp_path, monkeypatch):
    """Pano + senkron dosyalarını tmp_path'e yönlendir."""
    monkeypatch.setattr(tb, "AUTO_SYNC", False)
    monkeypatch.setattr(tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(tb, "TASK_BOARD", tmp_path / "task_board.json")
    monkeypatch.setattr(tb, "FILE_LOCKS", tmp_path / "file_locks.json")
    monkeypatch.setattr(tb, "STATE_JSON", tmp_path / "state.json")
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "gorev_panosu.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD", tmp_path / "AGENT_SYNC.md")
    monkeypatch.setattr(tb, "AGENT_SYNC_MD_KOPYA", tmp_path / "AGENT_SYNC_kopya.md")
    return tmp_path


def _gorev_ac(task_id: str = "T-08", ajan: str = "kilo") -> None:
    tb.gorev_ekle(task_id=task_id, baslik=f"{task_id} test gorevi",
                  sahip=ajan, oncelik="P1")


# ---- Posta kutusu ----

def test_tetik_ekle_ve_listele(tmp_path):
    _gorev_ac()
    trigger.tetik_ekle("T-08", "kilo", talimat="test talimatı", data_dir=tmp_path)
    bekleyen = trigger.bekleyen_tetikler("kilo", data_dir=tmp_path)
    assert len(bekleyen) == 1
    assert bekleyen[0]["task_id"] == "T-08"
    assert bekleyen[0]["talimat"] == "test talimatı"


def test_tetik_ayni_gorev_cift_dusmez(tmp_path):
    _gorev_ac()
    trigger.tetik_ekle("T-08", "kilo", data_dir=tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.tetik_ekle("T-08", "kilo", data_dir=tmp_path)


def test_postalar_ajanlar_arasi_izole(tmp_path):
    _gorev_ac()
    _gorev_ac("T-09", "grok")
    trigger.tetik_ekle("T-08", "kilo", data_dir=tmp_path)
    trigger.tetik_ekle("T-09", "grok", data_dir=tmp_path)
    assert [k["task_id"] for k in trigger.bekleyen_tetikler("kilo", tmp_path)] == ["T-08"]
    assert [k["task_id"] for k in trigger.bekleyen_tetikler("grok", tmp_path)] == ["T-09"]


def test_tetik_al_gorevi_aktif_yapar(tmp_path):
    _gorev_ac()
    trigger.tetik_ekle("T-08", "kilo", data_dir=tmp_path)
    sonuc = trigger.tetik_al("kilo", "T-08", data_dir=tmp_path)
    assert sonuc["durum"] == "alindi"
    assert tb.gorev_getir("T-08")["durum"] == "aktif"
    assert trigger.bekleyen_tetikler("kilo", tmp_path) == []


def test_tetik_al_idempotent_degil(tmp_path):
    _gorev_ac()
    trigger.tetik_ekle("T-08", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-08", data_dir=tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.tetik_al("kilo", "T-08", data_dir=tmp_path)


def test_tetik_al_panoda_olmayan_gorev_red(tmp_path):
    trigger.tetik_ekle("YOK-1", "kilo", data_dir=tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.tetik_al("kilo", "YOK-1", data_dir=tmp_path)


# ---- Onay kuyruğu ----

def _ac_al_teslim(tmp_path, task_id="T-08", ajan="kilo"):
    _gorev_ac(task_id, ajan)
    trigger.tetik_ekle(task_id, ajan, data_dir=tmp_path)
    trigger.tetik_al(ajan, task_id, data_dir=tmp_path)
    return trigger.teslim_et(task_id, ajan, "iş tamamlandı", ["cikti.md"], data_dir=tmp_path)


def test_teslim_review_dusurur(tmp_path):
    sonuc = _ac_al_teslim(tmp_path)
    assert sonuc["durum"] == "review"
    assert tb.gorev_getir("T-08")["durum"] == "review"
    kuyruk = trigger.onay_bekleyenler(tmp_path)
    assert len(kuyruk) == 1
    assert kuyruk[0]["ozet"] == "iş tamamlandı"
    assert kuyruk[0]["ciktilar"] == ["cikti.md"]


def test_cift_teslim_engellenir(tmp_path):
    _ac_al_teslim(tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.teslim_et("T-08", "kilo", "tekrar", data_dir=tmp_path)


def test_bos_ozetli_teslim_engellenir(tmp_path):
    _gorev_ac()
    trigger.tetik_ekle("T-08", "kilo", data_dir=tmp_path)
    trigger.tetik_al("kilo", "T-08", data_dir=tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.teslim_et("T-08", "kilo", "   ", data_dir=tmp_path)


def test_onayla_done_yapar_ve_kilit_duser(tmp_path):
    import json as _json
    # T-K'nın kilidi T-08 onayında düşmemeli (yalnızca kendi görevinin kilidi düşer)
    tb.gorev_ekle("T-K", "kilit testi", "kilo", dosyalar=["src/x.py"])
    _ac_al_teslim(tmp_path)
    trigger.onayla("T-08", "orkestrator", data_dir=tmp_path)
    assert tb.gorev_getir("T-08")["durum"] == "done"
    assert tb.gorev_getir("T-08")["bitis"] is not None
    assert trigger.onay_bekleyenler(tmp_path) == []
    locks = _json.loads((tmp_path / "file_locks.json").read_text(encoding="utf-8"))
    assert "src/x.py" in locks  # T-K kilidi korunuyor


def test_onayla_yanlis_gorev_red(tmp_path):
    _ac_al_teslim(tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.onayla("YOK-9", "orkestrator", data_dir=tmp_path)


def test_reddet_aktife_geri_dondurur(tmp_path):
    _ac_al_teslim(tmp_path)
    trigger.reddet("T-08", "orkestrator", "testler kirmizi", data_dir=tmp_path)
    gorev = tb.gorev_getir("T-08")
    assert gorev["durum"] == "aktif"
    assert "testler kirmizi" in gorev["not"]


def test_reddet_nedensiz_engellenir(tmp_path):
    _ac_al_teslim(tmp_path)
    with pytest.raises(trigger.TriggerError):
        trigger.reddet("T-08", "orkestrator", "  ", data_dir=tmp_path)


def test_teslim_sonrasi_yeni_tetik_ile_duzeltme_dongusu(tmp_path):
    """Red -> ajan yeniden teslim -> onay: tam düzeltme döngüsü."""
    _ac_al_teslim(tmp_path)
    trigger.reddet("T-08", "orkestrator", "eksik test", data_dir=tmp_path)
    # Ajan düzeltip tekrar teslim eder (kuyruk kaydı yeni satır olarak eklenir)
    trigger.teslim_et("T-08", "kilo", "testler eklendi", data_dir=tmp_path)
    assert tb.gorev_getir("T-08")["durum"] == "review"
    trigger.onayla("T-08", "orkestrator", data_dir=tmp_path)
    assert tb.gorev_getir("T-08")["durum"] == "done"


def test_teslim_stale_bekliyor_kaydi_teslime_doner(tmp_path):
    """D-fix: `al` hiç çağrılmadan (kayıt "bekliyor"da kalmış) teslim edilirse
    tetik kaydı sonsuza dek "bekliyor" görünmemeli — "teslim"e geçmeli."""
    _gorev_ac()
    trigger.tetik_ekle("T-08", "kilo", data_dir=tmp_path)
    # DİKKAT: tetik_al() çağrılmadı — kayıt "bekliyor" durumunda kaldı.
    trigger.teslim_et("T-08", "kilo", "iş tamamlandı", data_dir=tmp_path)
    kayitlar = trigger._tetikleri_oku("kilo", tmp_path)
    hedef = [k for k in kayitlar if k["task_id"] == "T-08"]
    assert hedef and hedef[0]["durum"] == "teslim"
    assert trigger.bekleyen_tetikler("kilo", tmp_path) == []


def test_onay_bekleyenler_done_gorevi_kuyruktan_gizler(tmp_path):
    """D-fix: onay kuyruğunda "bekliyor" kalmış ama pano zaten "done" olan
    kayıt hayalet olarak gösterilmemeli (yalnızca tetik-kaynaklı dal değil)."""
    sonuc = _ac_al_teslim(tmp_path)
    assert sonuc["durum"] == "review"
    tb.gorev_guncelle("T-08", durum="done")  # kuyruk hâlâ "bekliyor" (stale)
    assert trigger.onay_bekleyenler(tmp_path) == []
