#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERI-RISK-MOTORU-01: Risk motoru mandallari (D-256/4 — kirilarak dogrulanir).

Kapsam:
  A) Sema: 8 skor kolonu + CHECK kisiti + `DEFAULT 0` yasagi
  B) Hesaplayici: girdi yoksa None, payda duzeltmesi, kademe dogrulamasi
  C) D-256/2: tabloya yazan tek fonksiyon `risk_recalc()`

Bu dosya framework'suz calisir: `python -X utf8 tests/test_risk_skorlari.py`.
pytest altinda da toplanir (test_ oneki).
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

GOC = (
    PROJECT_ROOT
    / "src"
    / "company_master"
    / "schema"
    / "migrations"
    / "0046_risk_skorlari.sql"
)

from company_master.risk.skorlar import (  # noqa: E402
    AGIRLIKLAR,
    GENEL_SKOR,
    KADEMELER,
    SKORLAR,
    genel_guven,
    kademe,
    skorlari_hesapla,
)

# SSOT:791-822 — adlar birebir. Kaynak: plans/brief_utku_VERI-RISK-MOTORU-01.md
SSOT_SKORLAR: tuple[tuple[str, str, int], ...] = (
    ("corporateness_score", "Kurumsallık Skoru", 792),
    ("reliability_score", "Güvenilirlik Skoru", 796),
    ("reputation_score", "İtibar Skoru", 800),
    ("cyber_security_score", "Siber Güvenlik Skoru", 804),
    ("operational_power_score", "Operasyonel Güç Skoru", 808),
    ("transparency_score", "Şeffaflık Skoru", 812),
    ("fraud_risk_score", "Fraud Risk Skoru", 816),
    ("overall_trust_score", "Genel Güven Skoru", 820),
)


# --- A) Sema ---------------------------------------------------------------


def test_sekiz_skor_kolonu_goc_dosyasinda_geciyor():
    """8 kolonun tamami + SSOT satir numarasi COMMENT'te yazili olmali."""
    icerik = GOC.read_text(encoding="utf-8")
    for kolon, turkce_ad, satir_no in SSOT_SKORLAR:
        assert kolon in icerik, f"goc dosyasinda kolon yok: {kolon}"
        assert turkce_ad in icerik, f"COMMENT'te Turkce resmi ad yok: {turkce_ad}"
        assert f"SSOT:{satir_no}" in icerik, (
            f"COMMENT'te SSOT satir numarasi yok: {kolon} -> {satir_no}"
        )


def test_hicbir_skor_kolonunda_default_0_yok():
    """D-249: 'veri yok' ile '0 puan' ayri degerlerdir."""
    icerik = GOC.read_text(encoding="utf-8")
    assert "DEFAULT 0" not in icerik, (
        "goc dosyasinda 'DEFAULT 0' var — olculmemis skor 0 sayilir (D-249)"
    )


def test_oneri_kademesi_check_kisiti_dort_kademe_ile_sinirli():
    icerik = GOC.read_text(encoding="utf-8")
    assert "CHECK" in icerik.upper(), "recommendation_tier CHECK kisiti yok"
    for ad in KADEMELER:
        assert f"'{ad}'" in icerik, f"CHECK kisitinda kademe yok: {ad}"


def test_firma_basi_birincil_anahtar_ve_tablo_yazmaz():
    """company_risk_scores tek satir/firma tutar; companies FK'si company_id."""
    icerik = GOC.read_text(encoding="utf-8")
    assert "company_id UUID PRIMARY KEY" in icerik
    assert "REFERENCES companies(company_id)" in icerik, (
        "FK yanlis: companies PK'si company_id'dir (0001_core.sql:35)"
    )


# --- B) Hesaplayici -------------------------------------------------------


def test_bos_girdi_skor_none_tier_none_doner():
    """Girdisi olmayan firma -> skor None, tier None (0 degil)."""
    sonuc = skorlari_hesapla(None)
    for kolon, deger in sonuc.items():
        assert deger is None, f"{kolon} bos girdide None degil: {deger!r}"
    assert kademe(sonuc[GENEL_SKOR]) is None, "genel guven None iken tier None olmali"


def test_uc_skor_null_ise_ortalama_kalan_dordunden_hesaplaniyor():
    """D-249/3: olculmemis skor hem paydadan hem paydan duser."""
    dolu = {ad: 80.0 for ad in SKORLAR}
    eksik = dict(dolu)
    for ad in ("corporateness_score", "reputation_score", "cyber_security_score"):
        eksik[ad] = None

    tam = genel_guven(dolu)
    yarim = genel_guven(eksik)

    assert tam == 80.0, f"7 skorun tamami 80 iken 80 olmali, {tam} geldi"
    assert yarim == 80.0, (
        f"3 skor NULL iken kalan 4 ortalamasi alinmali, {yarim} geldi"
    )
    assert eksik["operational_power_score"] == 80.0, (
        "3 NULL olan skor disindaki 4 skor degismemis olmali"
    )
    # 3 skor NULL iken kalan 4un agirligi: 1.0 - (0.20+0.10+0.15) = 0.55
    kalan_agirlik = round(
        sum(
            AGIRLIKLAR[ad]
            for ad, deger in eksik.items()
            if deger is not None
        ),
        6,
    )
    assert kalan_agirlik == 0.55, f"kalan agirlik 0.55 olmali, {kalan_agirlik}"


def test_yedi_skorun_tumu_null_ise_genel_guven_none():
    hepsi_bos = {ad: None for ad in SKORLAR}
    assert genel_guven(hepsi_bos) is None, "7 skor NULL iken genel guven 0 olmamali"


def test_kademe_dort_kademe_disi_degerde_hata_veriyor():
    """CHK: yasak kademe degeri hata uretir (kademe() girdi dogrulamasi)."""
    assert kademe(95.0) == "calisilabilir"
    assert kademe(75.0) == "dikkatli_calisilmali"
    assert kademe(50.0) == "ek_inceleme_gerekli"
    assert kademe(10.0) == "yuksek_riskli"

    for yasak in ("calisilabilir ", "CALISILABILIR", "iyi", "", "100"):
        try:
            deger = kademe(yasak)  # type: ignore[arg-type]
        except (ValueError, TypeError):
            continue
        raise AssertionError(
            f"kademe() yasak degeri kabul etti: {yasak!r} -> {deger!r}"
        )


def test_agirliklar_toplami_bir():
    toplam = round(sum(AGIRLIKLAR.values()), 6)
    assert toplam == 1.0, f"agirlik toplami 1.0 olmali, {toplam} bulundu"


def test_bozuk_girdi_skoru_sifirlamaz():
    """Bozuk girdi 0 puan degil, olcum yoktur (D-249)."""
    sonuc = skorlari_hesapla({"employee_count": "cok"})
    assert sonuc["operational_power_score"] is None, (
        "bozuk girdi 0 puan uretti — olcum yoktur (D-249)"
    )


def test_kismi_skor_sifir_deger_gercek_olcumu_korur():
    """0 = olculdu ve sinyal yok; None ile karismaz (D-249/2)."""
    sonuc = skorlari_hesapla(
        {
            "legal_name": "X",
            "dogrulanmis_tckn": 1,
            "dogrulanmis_mersis": 1,
            "dogrulanmis_sicil": 1,
            "kimlik_verisi": 0,
            "kimlik_celiskisi": 0,
        }
    )
    assert sonuc["fraud_risk_score"] == 0.0, (
        "celiski olculdu ve 0 bulundu — bu gercek 0 olcumdur, None degil"
    )
    assert sonuc["transparency_score"] is None, "iletisim alani yoksa None olmali"


# --- C) Tek yazma kapisi (D-256/2) -----------------------------------------


def test_bu_modulde_tek_yazici_risk_recalc():
    """skorlar.py icinde INSERT/UPDATE yazan tek yer risk_recalc olmali."""
    kaynak = (
        PROJECT_ROOT / "src" / "company_master" / "risk" / "skorlar.py"
    ).read_text(encoding="utf-8")

    # Yazma ifadesi bir modul sabitidir (_YAZ); bu test onun **kosulmadan
    # tek yerde** kullanildigini olcer: yalnizca risk_recalc icinde.
    kullanim = [
        (no, satir)
        for no, satir in enumerate(kaynak.splitlines(), start=1)
        if "_YAZ" in satir and not satir.lstrip().startswith("_YAZ =")
        and not satir.lstrip().startswith("#")
    ]
    assert len(kullanim) == 1, (
        f"_YAZ yazma ifadesi birden fazla yerde kullaniliyor: {kullanim}"
    )
    assert "def risk_recalc" in kaynak, "risk_recalc tanimi yok"

    # Yazma ifadesinin **kosuldugu tek fonksiyon** risk_recalc olmali:
    # taniminin satirindan sonra ilk kullanim onun icinde olmalidir.
    risk_satiri = next(
        no for no, satir in enumerate(kaynak.splitlines(), start=1)
        if satir.startswith("def risk_recalc")
    )
    assert kullanim[0][0] > risk_satiri, (
        f"_YAZ ilk kez risk_recalc'ten once ({kullanim[0][0]}. satir) kullaniliyor "
        "— yazici dagilmis olabilir"
    )
    assert "ON CONFLICT (company_id) DO UPDATE" in kaynak, (
        "toplu yazma idempotent olmali (ON CONFLICT)"
    )


def _calistir() -> int:
    testler = [deger for ad, deger in sorted(globals().items()) if ad.startswith("test_")]
    gecen = 0
    for test in testler:
        try:
            test()
        except AssertionError as exc:
            print(f"KIRILDI - {test.__name__}: {exc}")
            return 1
        gecen += 1
    print(f"[OK] {gecen} risk skoru mandali gecti")
    return 0


if __name__ == "__main__":
    raise SystemExit(_calistir())
