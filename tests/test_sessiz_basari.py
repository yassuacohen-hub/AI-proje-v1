# -*- coding: utf-8 -*-
"""Sessiz basari yasagi: is yapmadan 0 donen komut yoktur.

Iki tuzak kapatiliyor:
- tetik_senk: yanlis dizin -> hic dosya bulunmaz -> eskiden exit 0 ("basarili").
- pano_denetim --uygula: duzeltme adayi var, hicbiri yazilamadi -> eskiden exit 0.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]


def _yukle(ad: str):
    """scripts/ paket degil; dosya yolundan modul yukler."""
    spec = importlib.util.spec_from_file_location(ad, KOK / "scripts" / f"{ad}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[ad] = mod
    spec.loader.exec_module(mod)
    return mod


def test_tetik_senk_dosya_yoksa_sifir_donmez(tmp_path, monkeypatch):
    ts = _yukle("tetik_senk")
    monkeypatch.setattr(ts.tb, "STATE_DIR", tmp_path)  # triggers/ alt klasoru yok
    monkeypatch.setattr(ts.tb, "TASK_BOARD", tmp_path / "pano.json")
    (tmp_path / "pano.json").write_text("[]", encoding="utf-8")
    rapor = ts.tetik_senk()
    assert rapor["bulunan_dosya"] == 0, "dosya yokken sayac artmamali"
    assert rapor["hata"] == 0, "eski davranis: hata=0 -> yanlisliktan exit 0"
    # Kapi tam da burada: hata=0 olmasina ragmen komut basarili sayilmamali.


def test_tetik_senk_dosya_varsa_sayar(tmp_path, monkeypatch):
    ts = _yukle("tetik_senk")
    tetikler = tmp_path / "triggers"
    tetikler.mkdir()
    (tetikler / "yasu.jsonl").write_text("", encoding="utf-8")
    monkeypatch.setattr(ts.tb, "STATE_DIR", tmp_path)
    monkeypatch.setattr(ts.tb, "TASK_BOARD", tmp_path / "pano.json")
    (tmp_path / "pano.json").write_text("[]", encoding="utf-8")
    assert ts.tetik_senk()["bulunan_dosya"] == 1


def test_pano_denetim_uygula_adayi_yazamazsa_iki_doner(tmp_path, monkeypatch, capsys):
    pd = _yukle("pano_denetim")
    monkeypatch.setattr(pd, "RAPOR_DOSYA", tmp_path / "rapor.json")
    monkeypatch.setattr(pd, "_kanonik_yol_kontrol", lambda: None)
    monkeypatch.setattr(pd, "_json_oku", lambda yol: [])
    monkeypatch.setattr(pd, "ithalat_kontrol", lambda: None)
    monkeypatch.setattr(pd, "arsivlenebilir", lambda *a: [])
    # Aday var ama uygula() hicbirini yazamiyor -> sessiz basari tuzagi.
    monkeypatch.setattr(pd, "tara", lambda *a: [
        {"seviye": "uyari", "tip": "stuck", "task_id": "X-01",
         "mesaj": "takildi", "duzeltme": "plana_ac"}])
    monkeypatch.setattr(pd, "uygula", lambda *a: [])
    assert pd.main(["--uygula"]) == 2
    assert "hicbiri yazilamadi" in capsys.readouterr().err


def test_pano_denetim_temiz_ise_sifir(tmp_path, monkeypatch):
    pd = _yukle("pano_denetim")
    monkeypatch.setattr(pd, "RAPOR_DOSYA", tmp_path / "rapor.json")
    monkeypatch.setattr(pd, "_kanonik_yol_kontrol", lambda: None)
    monkeypatch.setattr(pd, "_json_oku", lambda yol: [])
    monkeypatch.setattr(pd, "ithalat_kontrol", lambda: None)
    monkeypatch.setattr(pd, "tara", lambda *a: [])
    assert pd.main([]) == 0
