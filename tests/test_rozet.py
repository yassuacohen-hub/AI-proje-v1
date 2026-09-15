# -*- coding: utf-8 -*-
"""Rozet modeli testleri."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.company_master.rozet.model import (
    UserProgress,
    karsilastir,
    rozet_ver,
)


# --- 1. rozet_ver() default (no db path) ---

def test_rozet_ver_default_ekler_rozet():
    sonuc = rozet_ver("u1", "rozet-ali")
    assert sonuc.kullanici_id == "u1"
    assert sonuc.rozetler == {"rozet-ali": 1}
    assert sonuc.toplam_puan == 1


# --- 2. rozet_ver() same rozet_id twice accumulates ---

def test_rozet_ver_tekrar_akumler():
    with tempfile.TemporaryDirectory() as tmp:
        yol = os.path.join(tmp, "test.json")
        sonuc = rozet_ver("u2", "rozet-merhaba", puan=3, veritabani_yol=yol)
        sonuc = rozet_ver("u2", "rozet-merhaba", puan=2, veritabani_yol=yol)
        assert sonuc.rozetler == {"rozet-merhaba": 5}
        assert sonuc.toplam_puan == 5


# --- 3. rozet_ver() negative puan treats as 0 ---

def test_rozet_ver_negatif_puan_sifir():
    sonuc = rozet_ver("u3", "rozet-eksi", puan=-5)
    assert sonuc.rozetler == {"rozet-eksi": 0}
    assert sonuc.toplam_puan == 0


# --- 4. karsilastir() returns dict with correct keys ---

def test_karsilastir_anahtarlar():
    bir = UserProgress(kullanici_id="a", rozetler={"x": 1, "y": 2}, toplam_puan=3)
    iki = UserProgress(kullanici_id="b", rozetler={"y": 1, "z": 3}, toplam_puan=4)
    sonuc = karsilastir(bir, iki)
    assert set(sonuc.keys()) == {
        "ortak_rozetler",
        "sadece_bir",
        "sadece_iki",
        "bir_toplam",
        "iki_toplam",
        "fark",
    }


# --- 5. karsilastir() ortak rozetler correct ---

def test_karsilastir_ortak_rozetler():
    bir = UserProgress(kullanici_id="a", rozetler={"x": 1, "y": 2}, toplam_puan=3)
    iki = UserProgress(kullanici_id="b", rozetler={"y": 1, "z": 3}, toplam_puan=4)
    sonuc = karsilastir(bir, iki)
    assert sonuc["ortak_rozetler"] == ["y"]
    assert sonuc["sadece_bir"] == ["x"]
    assert sonuc["sadece_iki"] == ["z"]


# --- 6. karsilastir() fark calculation correct ---

def test_karsilastir_fark():
    bir = UserProgress(kullanici_id="a", rozetler={"a": 10}, toplam_puan=10)
    iki = UserProgress(kullanici_id="b", rozetler={"b": 3}, toplam_puan=3)
    sonuc = karsilastir(bir, iki)
    assert sonuc["fark"] == 7
    assert sonuc["bir_toplam"] == 10
    assert sonuc["iki_toplam"] == 3


# --- 7. Rozetler empty dict default ---

def test_rozetler_bos_dict():
    kullanici = UserProgress(kullanici_id="boş")
    assert kullanici.rozetler == {}
    assert kullanici.toplam_puan == 0


# --- 8. Multiple users in same db file ---

def test_cok_kullanici_aynibdosya():
    with tempfile.TemporaryDirectory() as tmp:
        yol = Path(tmp) / "test.json"
        r1 = rozet_ver("alice", "rozet1", puan=3, veritabani_yol=yol)
        r2 = rozet_ver("bob", "rozet2", puan=5, veritabani_yol=yol)
        assert r1.rozetler == {"rozet1": 3}
        assert r2.rozetler == {"rozet2": 5}
        data = json.loads(yol.read_text(encoding="utf-8"))
        assert "alice" in data
        assert "bob" in data
        assert data["alice"]["rozetler"] == {"rozet1": 3}
        assert data["bob"]["rozetler"] == {"rozet2": 5}
