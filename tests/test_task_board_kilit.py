# -*- coding: utf-8 -*-
"""ALTYAPI-KILIT-OTOMATIK-01: toplu kilit birakma + stale tarama testleri.

Calistirma: python -m pytest tests/test_task_board_kilit.py -q
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from company_master.orchestrator import task_board as tb  # noqa: E402


@pytest.fixture
def izole(tmp_path, monkeypatch):
    """Gercek pano/kilit dosyalarina dokunmadan izole ortam."""
    pano = tmp_path / "task_board.json"
    kilit = tmp_path / "file_locks.json"
    pano.write_text("[]", encoding="utf-8")
    kilit.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(tb, "TASK_BOARD", pano)
    monkeypatch.setattr(tb, "FILE_LOCKS", kilit)
    monkeypatch.setattr(tb, "TASK_MD", tmp_path / "TASKS.md")
    monkeypatch.setattr(tb, "_sync_tetikle", lambda: None)
    monkeypatch.setattr(tb, "agent_sync_yaz", lambda: None)
    return tmp_path


def _kilit_yaz(izole, kayitlar: dict) -> None:
    (izole / "file_locks.json").write_text(
        json.dumps(kayitlar, ensure_ascii=False), encoding="utf-8")


def _kilitler(izole) -> dict:
    return json.loads((izole / "file_locks.json").read_text(encoding="utf-8"))


def test_toplu_birakma_sadece_kendi_gorevini_birakir(izole):
    _kilit_yaz(izole, {
        "a.py": {"sahip": "yasu", "task_id": "T-1", "kilitlendi": "2026-09-23T10:00:00"},
        "b.py": {"sahip": "utku", "task_id": "T-1", "kilitlendi": "2026-09-23T10:00:00"},
        "c.py": {"sahip": "yasu", "task_id": "T-2", "kilitlendi": "2026-09-23T10:00:00"},
    })
    birakilan = tb.lock_birak_gorev("T-1")
    assert sorted(birakilan) == ["a.py", "b.py"]     # sahip farki onemsiz
    assert list(_kilitler(izole)) == ["c.py"]        # baska gorev dokunulmadi


def test_kilidi_olmayan_gorev_bos_liste_doner(izole):
    _kilit_yaz(izole, {"c.py": {"sahip": "yasu", "task_id": "T-2",
                                "kilitlendi": "2026-09-23T10:00:00"}})
    assert tb.lock_birak_gorev("YOK-01") == []
    assert list(_kilitler(izole)) == ["c.py"]        # gereksiz yazim yok


def test_done_olunca_kilitler_otomatik_duser(izole):
    tb.gorev_ekle(task_id="T-9", baslik="test", sahip="yasu",
                  dosyalar=["x.py", "y.py"])
    assert set(_kilitler(izole)) == {"x.py", "y.py"}
    tb.gorev_guncelle("T-9", durum="done")
    assert _kilitler(izole) == {}


def test_aktif_durumda_kilit_dusmez(izole):
    tb.gorev_ekle(task_id="T-8", baslik="test", sahip="yasu", dosyalar=["z.py"])
    tb.gorev_guncelle("T-8", durum="aktif")
    assert "z.py" in _kilitler(izole)                # ORCH-05b regresyonu


def test_kilit_hatasi_pano_yazimini_cokertmez(izole, monkeypatch):
    tb.gorev_ekle(task_id="T-7", baslik="test", sahip="yasu", dosyalar=["q.py"])
    monkeypatch.setattr(tb, "lock_birak_gorev",
                        lambda tid: (_ for _ in ()).throw(OSError("disk dolu")))
    assert tb.gorev_guncelle("T-7", durum="done")["durum"] == "done"


def test_stale_listeler_silmez(izole):
    eski = (datetime.now() - timedelta(hours=48)).isoformat(timespec="seconds")
    yeni = datetime.now().isoformat(timespec="seconds")
    _kilit_yaz(izole, {
        "eski.py": {"sahip": "utku", "task_id": "T-ESKI", "kilitlendi": eski},
        "yeni.py": {"sahip": "utku", "task_id": "T-YENI", "kilitlendi": yeni},
    })
    bulgu = tb.stale_kilitler(saat=24)
    assert [b["dosya"] for b in bulgu] == ["eski.py"]
    assert bulgu[0]["gorev_durum"] == "PANODA YOK"   # oksuz kilit gorunur
    assert bulgu[0]["yas_saat"] >= 48
    assert set(_kilitler(izole)) == {"eski.py", "yeni.py"}   # SILME YOK


def test_stale_bozuk_tarihi_atlar(izole):
    _kilit_yaz(izole, {"bozuk.py": {"sahip": "utku", "task_id": "T-X",
                                    "kilitlendi": "cop-veri"}})
    assert tb.stale_kilitler(saat=1) == []           # cokmez, sessizce atlar
