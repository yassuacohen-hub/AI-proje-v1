# -*- coding: utf-8 -*-
"""PO-BACK-10: coverage_analitik saf fonksiyon testleri (DB yok)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from company_master.coverage_analitik import (
    BILINMEYEN_GRUP,
    NACE_HEDEF_DOSYASI,
    coverage_orani,
    coverage_ozeti,
    firma_nace_grubu,
    nace_hedeflerini_yukle,
    sektor_bazli_coverage,
)


def _firmalar(*gruplar: str) -> list[dict]:
    return [{"nace_grup": g} for g in gruplar]


# ---------------------------------------------------------------------------
# coverage_orani
# ---------------------------------------------------------------------------


def test_coverage_orani_bos_liste_sifir():
    assert coverage_orani([], 100) == 0.0


def test_coverage_orani_hedef_sifir_bolme_hatasi_yok():
    assert coverage_orani(_firmalar("62", "63"), 0) == 0.0
    assert coverage_orani(_firmalar("62"), -5) == 0.0


def test_coverage_orani_yuzde_yuz():
    assert coverage_orani(_firmalar("62", "63", "64"), 3) == 100.0


def test_coverage_orani_hedef_asimi_kirpilir():
    assert coverage_orani(_firmalar("62", "63", "64"), 2) == 100.0


def test_coverage_orani_yuvarlama_iki_ondalik():
    assert coverage_orani(_firmalar("a"), 3) == 33.33


def test_coverage_orani_none_girdiler():
    assert coverage_orani(None, None) == 0.0  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# firma_nace_grubu
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "firma, beklenen",
    [
        ({"nace_grup": "62"}, "62"),
        ({"nace_group": "63"}, "63"),
        ({"sektor": "Yazılım"}, "Yazılım"),
        ({"nace_kodu": "62.01"}, "62"),
        ({"nace_kodu": "6201"}, "62"),
        ({"nace_grup": "  "}, BILINMEYEN_GRUP),
        ({}, BILINMEYEN_GRUP),
        ("metin", BILINMEYEN_GRUP),
    ],
)
def test_firma_nace_grubu(firma, beklenen):
    assert firma_nace_grubu(firma) == beklenen


# ---------------------------------------------------------------------------
# sektor_bazli_coverage
# ---------------------------------------------------------------------------


def test_sektor_bazli_bos_liste_hedefler_sifir_oranla_doner():
    sonuc = sektor_bazli_coverage([], {"62": 10, "63": 5})
    assert {s["nace_grup"] for s in sonuc} == {"62", "63"}
    assert all(s["yakalanan"] == 0 and s["oran"] == 0.0 for s in sonuc)


def test_sektor_bazli_siralama_en_dusuk_once():
    firmalar = _firmalar("62", "62", "62", "63", "64")
    sonuc = sektor_bazli_coverage(firmalar, {"62": 3, "63": 4, "64": 2})
    assert [s["nace_grup"] for s in sonuc] == ["63", "64", "62"]
    assert sonuc[0]["oran"] == 25.0
    assert sonuc[1]["oran"] == 50.0
    assert sonuc[2]["oran"] == 100.0


def test_sektor_bazli_hedefsiz_grup_listede_kalir():
    sonuc = sektor_bazli_coverage(_firmalar("99"), {"62": 1})
    satir = next(s for s in sonuc if s["nace_grup"] == "99")
    assert satir == {"nace_grup": "99", "yakalanan": 1, "hedef": 0, "oran": 0.0}


def test_sektor_bazli_liste_tanimi_kabul_edilir():
    hedefler = [{"nace_grup": "62", "hedef": 2}, {"sektor": "63", "hedef": "4"}, {"x": 1}]
    sonuc = sektor_bazli_coverage(_firmalar("62", "63", "63"), hedefler)
    oranlar = {s["nace_grup"]: s["oran"] for s in sonuc}
    assert oranlar == {"62": 50.0, "63": 50.0}


def test_sektor_bazli_satir_anahtarlari():
    (satir,) = sektor_bazli_coverage(_firmalar("62"), {"62": 1})
    assert set(satir) == {"nace_grup", "yakalanan", "hedef", "oran"}


def test_sektor_bazli_gecersiz_hedef_sifir_sayilir():
    (satir,) = sektor_bazli_coverage([], {"62": "abc"})
    assert satir["hedef"] == 0 and satir["oran"] == 0.0


# ---------------------------------------------------------------------------
# coverage_ozeti
# ---------------------------------------------------------------------------


def test_coverage_ozeti_bos():
    ozet = coverage_ozeti([], 0)
    assert ozet["toplam"] == 0
    assert ozet["oran"] == 0.0
    assert ozet["sektorler"] == []
    assert ozet["en_dusuk_3_sektor"] == []
    assert ozet["veri_var"] is False


def test_coverage_ozeti_en_dusuk_3_sektor():
    firmalar = _firmalar("a", "b", "b", "c", "c", "c", "d", "d", "d", "d")
    hedefler = {"a": 10, "b": 10, "c": 10, "d": 10, "e": 0}
    ozet = coverage_ozeti(firmalar, 50, hedefler)
    assert ozet["toplam"] == 10
    assert ozet["hedef"] == 50
    assert ozet["oran"] == 20.0
    assert [s["nace_grup"] for s in ozet["en_dusuk_3_sektor"]] == ["a", "b", "c"]
    assert ozet["veri_var"] is True


def test_coverage_ozeti_hedefi_sifir_sektor_en_dusuk_listesine_girmez():
    ozet = coverage_ozeti(_firmalar("x"), 5, {"x": 2, "y": 0})
    assert [s["nace_grup"] for s in ozet["en_dusuk_3_sektor"]] == ["x"]


def test_coverage_ozeti_nace_gruplari_opsiyonel():
    ozet = coverage_ozeti(_firmalar("62"), 2)
    assert ozet["oran"] == 50.0
    assert ozet["sektorler"][0]["nace_grup"] == "62"


# ---------------------------------------------------------------------------
# HEDEF-NACE-01: nace_hedeflerini_yukle
# ---------------------------------------------------------------------------


def test_hedef_nace_dosya_yoksa_esit_paylasim(tmp_path: Path):
    hedefler, kaynak = nace_hedeflerini_yukle(tmp_path / "yok.json", ["62", "10", "46"], 900)
    assert kaynak == "esit_paylasim"
    assert hedefler == {"10": 300, "46": 300, "62": 300}


def test_hedef_nace_dosya_bozuksa_esit_paylasim(tmp_path: Path):
    dosya = tmp_path / "bozuk.json"
    dosya.write_text("{bozuk", encoding="utf-8")
    hedefler, kaynak = nace_hedeflerini_yukle(dosya, ["62"], 50)
    assert kaynak == "esit_paylasim"
    assert hedefler == {"62": 50}


def test_hedef_nace_dosya_bos_sozlukse_esit_paylasim(tmp_path: Path):
    dosya = tmp_path / "bos.json"
    dosya.write_text(json.dumps({"hedefler": {}}), encoding="utf-8")
    hedefler, kaynak = nace_hedeflerini_yukle(dosya, ["a", "b"], 10)
    assert kaynak == "esit_paylasim"
    assert hedefler == {"a": 5, "b": 5}


def test_hedef_nace_esit_paylasim_grup_yoksa_bos():
    hedefler, kaynak = nace_hedeflerini_yukle(Path("olmayan/yol.json"), [], 100)
    assert kaynak == "esit_paylasim"
    assert hedefler == {}


def test_hedef_nace_dosya_hedefler_sarmali(tmp_path: Path):
    dosya = tmp_path / "h.json"
    dosya.write_text(json.dumps({"_not": "x", "hedefler": {"62": 800, "10": "900"}}), encoding="utf-8")
    hedefler, kaynak = nace_hedeflerini_yukle(dosya, ["62"], 1)
    assert kaynak == "dosya"
    assert hedefler == {"62": 800, "10": 900}


def test_hedef_nace_dosya_duz_sozluk(tmp_path: Path):
    dosya = tmp_path / "h.json"
    dosya.write_text(json.dumps({"62": 5, "46": 7}), encoding="utf-8")
    hedefler, kaynak = nace_hedeflerini_yukle(dosya)
    assert kaynak == "dosya"
    assert hedefler == {"62": 5, "46": 7}


def test_hedef_nace_dosya_liste_bicimi(tmp_path: Path):
    dosya = tmp_path / "h.json"
    dosya.write_text(
        json.dumps([{"nace_grup": "62", "hedef": 3}, {"nace_grup": "10", "hedef": 4}]),
        encoding="utf-8",
    )
    hedefler, kaynak = nace_hedeflerini_yukle(dosya)
    assert kaynak == "dosya"
    assert hedefler == {"62": 3, "10": 4}


def test_hedef_nace_dosya_coverage_ozeti_ile_uyumlu(tmp_path: Path):
    dosya = tmp_path / "h.json"
    dosya.write_text(json.dumps({"hedefler": {"62": 4, "10": 4}}), encoding="utf-8")
    hedefler, _ = nace_hedeflerini_yukle(dosya)
    ozet = coverage_ozeti(_firmalar("62", "62", "10"), sum(hedefler.values()), hedefler)
    assert ozet["hedef"] == 8
    assert ozet["oran"] == 37.5
    assert [s["nace_grup"] for s in ozet["en_dusuk_3_sektor"]] == ["10", "62"]


def test_hedef_nace_repo_dosyasi_gecerli():
    """Repo icindeki gercek data/nace_hedefleri.json okunabilir ve pozitif hedefler icerir."""
    kok = Path(__file__).resolve().parents[1]
    dosya = kok / NACE_HEDEF_DOSYASI
    assert dosya.is_file(), f"eksik: {dosya}"
    hedefler, kaynak = nace_hedeflerini_yukle(dosya)
    assert kaynak == "dosya"
    assert hedefler and all(len(g) == 2 and g.isdigit() for g in hedefler)
    assert all(h > 0 for h in hedefler.values())
