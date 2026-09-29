# -*- coding: utf-8 -*-
"""MANDAL-KPI-01 (D-301): Admin KPI sekmesinin SQL'leri canliya karsi kosuyor mu?

Neden bu dosya var: D-299 uc ayri canli hatayi (kolon adi, naive/aware datetime,
Decimal/float) **elle** yakaladi. Panelin en gorunur sekmesi testsizdi.

Neden sahte engine yok (D-288 dersi): sahte engine SQL'i hic calistirmaz, yani
`NOW() - :gun || ' days'` gibi bir Postgres hatasini yesil gosterir. Bu dosyanin
olctugu ilk kirik tam buydu -- `load_quality_trend` canlida **her zaman**
patliyordu, kalite trendi grafigi hic calismamisti.

Yutulan hatayi nasil yakaliyoruz: loader'lar `except` icinde `warning` cagirip
bos veri donuyor. "Bos df" ile "hata yedi" ayni gorunur. Bu yuzden testler
`_admin_kpi_logger.warning`'i dinliyor: cagrildiysa SQL patladi, kirmizi.
Boylece mandal veri **varligina** degil, sorgunun **kosabilirligine** bakar.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from web_dashboard.tabs import admin_kpi


def _db_var() -> bool:
    if not os.getenv("DATABASE_URL") and not (Path(__file__).resolve().parents[1] / ".env").exists():
        return False
    try:
        from company_master.db.connection import get_engine
        with get_engine().connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False


_ATLA = pytest.mark.skipif(
    not _db_var(), reason="DATABASE_URL erisimi yok; canli sema mandali atlandi"
)


@pytest.fixture
def yutulan(monkeypatch):
    """Loader'in yuttugu hatalari toplar. Bos liste = SQL gercekten kostu."""
    kayit: list[str] = []
    monkeypatch.setattr(
        admin_kpi._admin_kpi_logger,
        "warning",
        lambda msg, exc=None: kayit.append(f"{msg}: {exc}"),
    )
    return kayit


# --- DB'siz mandal: olculen kirigin deseni geri gelmesin --------------------

def test_interval_parametresi_yanlis_baglanmiyor():
    """`NOW() - :gun || ' days'` Postgres'te `timestamp - smallint` olur ve patlar.

    D-301'de olculdu. DB olmayan CI'da da kosar; desenin geri donusunu engeller.

    Kendi hatam (D-260): ilk surum tum dosyayi tarayinca hatayi *anlatan yorumu*
    kirik sandi. Yorum satirlari atlanir; mandal koda bakar, aciklamaya bakmaz.
    """
    kod = [
        s for s in Path(admin_kpi.__file__).read_text(encoding="utf-8").splitlines()
        if not s.lstrip().startswith("#")
    ]
    kirik = [s.strip() for s in kod if "- :gun || " in s]
    assert not kirik, (
        "Interval parametresi yine string birlestirmeye baglanmis; "
        f"dogrusu: NOW() - (:gun * INTERVAL '1 day'). Satir: {kirik}"
    )


# --- Canli sema mandallari ---------------------------------------------------

@_ATLA
def test_kpi_ozeti_canlida_hata_yutmuyor(yutulan):
    admin_kpi.load_admin_kpi_summary.clear()
    ozet = admin_kpi.load_admin_kpi_summary()
    assert yutulan == [], f"KPI ozeti SQL'i canlida patladi: {yutulan}"
    assert ozet["toplam_firma"] > 0, "Firma sayisi 0 -- sorgu kostu ama sema degismis olabilir"


@_ATLA
@pytest.mark.parametrize("gun", [7, 30, 90])
def test_kalite_trendi_canlida_kosuyor(yutulan, gun):
    """D-301'in bulduğu kirik: bu sorgu canlida hic kosmamisti."""
    admin_kpi.load_quality_trend.clear()
    df = admin_kpi.load_quality_trend(gun=gun)
    assert yutulan == [], f"Kalite trendi SQL'i {gun} gun icin patladi: {yutulan}"
    assert list(df.columns) == ["tarih", "ort_skor", "firma_sayisi"]


@_ATLA
def test_alan_kalitesi_canlida_hata_yutmuyor(yutulan):
    """Her alan icin ayri sorgu kosuyor; biri patlarsa D-249 gerekce bos kalir."""
    admin_kpi.load_field_quality_breakdown.clear()
    df = admin_kpi.load_field_quality_breakdown()
    assert yutulan == [], f"Alan kalitesi sorgusu patladi: {yutulan}"
    assert len(df) == len(admin_kpi._QUALITY_FIELDS), (
        "Bazi alanlar tabloya girmemis -- olculemeyen alan sessizce dusuruldu"
    )
    assert (df["Doluluk (%)"] <= 100).all(), "Doluluk %100'u asiyor: sayim/toplam uyusmuyor"


@_ATLA
def test_kaynak_sagligi_canlida_kosuyor(yutulan):
    admin_kpi.load_source_health.clear()
    df = admin_kpi.load_source_health()
    assert yutulan == [], f"Kaynak saglik sorgusu patladi: {yutulan}"
    assert list(df.columns) == ["source_name", "kayit_sayisi", "son_guncelleme"]


@_ATLA
def test_kaynak_sagligi_zaman_damgasi_aware(yutulan):
    """D-299 elle yakaladi: naive/aware karsilastirmasi canlida TypeError atiyor."""
    admin_kpi.load_source_health.clear()
    df = admin_kpi.load_source_health()
    damgalar = [t for t in df.get("son_guncelleme", []) if t is not None]
    if not damgalar:
        pytest.skip("Hic kaynak kaydi yok; zaman damgasi olculemez (D-249: 0 yazmiyoruz)")
    assert all(getattr(t, "tzinfo", None) is not None for t in damgalar), (
        "son_guncelleme naive dondu; datetime.now(timezone.utc) ile kiyas TypeError verir"
    )
