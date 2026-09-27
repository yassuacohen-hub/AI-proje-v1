# -*- coding: utf-8 -*-
"""Sessiz is emri kontrolu: pano 'aktif' ama ajanin postasinda tetik yok.

Kok neden vakasi (ae0fb2f): gorev panoya aktif yazildi, trigger.tetik_ekle
cagrilmadi. Ajan hic haber almadi, pano calisiyor gorundu.
"""
from __future__ import annotations

import json
from datetime import datetime

from scripts import pano_denetim as pd

SIMDI = datetime(2026, 9, 27, 18, 0)
SON = SIMDI.isoformat()  # stuck uyarisi uretmesin, tek sinyal olcsun


def _gorev(tid: str, durum: str, sahip: str = "utku") -> dict:
    return {"task_id": tid, "durum": durum, "sahip": sahip, "baslangic": SON}


def _tetik_tipleri(pano, tetikler):
    return [b["tip"] for b in pd.tara(pano, [], SIMDI, frozenset(), tetikler)]


def test_aktif_gorev_tetiksizse_hata():
    bulgular = pd.tara([_gorev("X-01", "aktif")], [], SIMDI, frozenset(), frozenset())
    tetik = [b for b in bulgular if b["tip"] == "tetik"]
    assert len(tetik) == 1, f"sessiz is emri yakalanmadi: {bulgular}"
    assert tetik[0]["seviye"] == "hata"
    assert "utku" in tetik[0]["mesaj"]


def test_tetigi_olan_aktif_gorev_temiz():
    tetikler = frozenset({("utku", "X-01")})
    assert "tetik" not in _tetik_tipleri([_gorev("X-01", "aktif")], tetikler)


def test_baska_ajanin_tetigi_sayilmaz():
    """Kanal ajana aittir: salih'in postasindaki kayit utku'nun gorevini kapatmaz."""
    tetikler = frozenset({("salih", "X-01")})
    assert "tetik" in _tetik_tipleri([_gorev("X-01", "aktif")], tetikler)


def test_plan_durumu_tetik_beklemez():
    """Henuz baslamamis gorev icin tetik olmamasi normaldir."""
    assert "tetik" not in _tetik_tipleri([_gorev("X-01", "plan")], frozenset())


def test_tetikler_yoksa_kontrol_kapali():
    """Geriye uyumluluk: tetikler=None verilmezse eski davranis surer."""
    assert "tetik" not in [b["tip"] for b in pd.tara([_gorev("X-01", "aktif")], [], SIMDI)]


def test_tetik_kimlikleri_kanal_ve_gorevi_cifter_okur(tmp_path, monkeypatch):
    kanal = tmp_path / "triggers"
    kanal.mkdir()
    (kanal / "utku.jsonl").write_text(
        json.dumps({"task_id": "A-01"}) + "\n\n" + json.dumps({"task_id": "A-02"}) + "\n",
        encoding="utf-8",
    )
    (kanal / "salih.jsonl").write_text(json.dumps({"task_id": "A-01"}) + "\n", encoding="utf-8")
    (kanal / "utku.ALARM.json").write_text('{"bozuk": 1}', encoding="utf-8")  # .jsonl degil: okunmaz
    monkeypatch.setattr(pd, "STATE", tmp_path)
    assert pd.tetik_kimlikleri() == frozenset(
        {("utku", "A-01"), ("utku", "A-02"), ("salih", "A-01")}
    )


def test_bozuk_satir_taramayi_kirmaz(tmp_path, monkeypatch):
    kanal = tmp_path / "triggers"
    kanal.mkdir()
    (kanal / "utku.jsonl").write_text(
        'bozuk json\n{"ajan": "utku"}\n' + json.dumps({"task_id": "A-01"}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pd, "STATE", tmp_path)
    assert pd.tetik_kimlikleri() == frozenset({("utku", "A-01")})


def test_canli_panoda_sessiz_is_emri_yok():
    """Gercek durum bekcisi: su an aktif her gorevin tetigi olmali."""
    pano = pd._json_oku(pd.PANO_DOSYA)
    eksik = [
        g["task_id"]
        for g in pano
        if g.get("durum") == "aktif"
        and g.get("sahip")
        and (g["sahip"], g["task_id"]) not in pd.tetik_kimlikleri()
    ]
    assert not eksik, f"tetigi gonderilmemis aktif gorevler: {eksik}"
