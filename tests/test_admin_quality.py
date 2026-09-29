# -*- coding: utf-8 -*-
"""UI-ADMIN-GUNCELLIK-KOVA-10: updated_at yaş kovası dağılımı testleri."""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from web_dashboard.tabs import admin_quality


class _Conn:
    def __init__(self, rows):
        self._rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a, **k):
        return self

    def scalars(self):
        return self

    def all(self):
        return self._rows


class _Engine:
    def __init__(self, rows):
        self._rows = rows

    def connect(self):
        return _Conn(self._rows)


def test_load_freshness_distribution_bos_tabloda_hata_vermez(monkeypatch):
    monkeypatch.setattr(admin_quality, "get_engine", lambda: _Engine([]))
    admin_quality.load_freshness_distribution.clear()
    df = admin_quality.load_freshness_distribution()
    assert list(df.columns) == ["kova", "adet"]
    assert df.empty


def test_load_freshness_distribution_kova_dagilimi_dogru(monkeypatch):
    simdi = datetime.now()
    rows = [
        (simdi - timedelta(days=2)).isoformat(timespec="seconds"),  # 0-7g
        (simdi - timedelta(days=15)).isoformat(timespec="seconds"),  # 8-30g
        (simdi - timedelta(days=60)).isoformat(timespec="seconds"),  # 31-90g
        (simdi - timedelta(days=200)).isoformat(timespec="seconds"),  # 90g+
    ]
    monkeypatch.setattr(admin_quality, "get_engine", lambda: _Engine(rows))
    admin_quality.load_freshness_distribution.clear()
    df = admin_quality.load_freshness_distribution()
    sonuc = dict(zip(df["kova"], df["adet"]))
    assert sonuc == {"0-7g": 1, "8-30g": 1, "31-90g": 1, "90g+": 1}


def test_load_freshness_distribution_db_hatasinda_bos_doner(monkeypatch):
    def _patlar():
        raise RuntimeError("db down")

    monkeypatch.setattr(admin_quality, "get_engine", _patlar)
    admin_quality.load_freshness_distribution.clear()
    df = admin_quality.load_freshness_distribution()
    assert df.empty


def test_chart_freshness_bos_df_hata_vermez(monkeypatch):
    calls = []
    monkeypatch.setattr(admin_quality.st, "info", lambda msg: calls.append(msg))
    admin_quality._chart_freshness(admin_quality.pd.DataFrame(columns=["kova", "adet"]))
    assert calls


# ---------------------------------------------------------------------------
# D-299: `_QUALITY_FIELDS` anahtarlari SQL'e ad olarak gomulur; `adres` ve
# `osb_parsel` yaziliydi, canlida yok. Hata `except` ile yutulup `eksik = 0`
# yazildigi icin panel "%0 eksik" diyordu (gercek: adres %38,4 parsel %99,8).
# Tek gercek sema kaynagi canli DB -- schema/*.sql bayat.
# ---------------------------------------------------------------------------

def test_sablon_deger_dolu_sayilmaz():
    """D-299: `isim.org.tr` sablonu 2142 kayitta "dolu" sayiliyordu.

    Doluluk kosulu sablon listesini dislamali; yoksa panel bilgi tasimayan
    metni veri gibi sunar (D-292'nin panel yuzeyindeki esi).
    """
    kosul = admin_quality._dolu_kosulu("website_domain")
    assert "isim.org.tr" in kosul
    assert "NOT IN" in kosul
    assert "'' " in kosul or "<> ''" in kosul


def test_kpi_doluluk_kosulu_ayni_kapidan_gecer():
    """D-299: iki panel ayni sablon listesini kullanmali, kopya olmamali."""
    from web_dashboard.tabs import admin_kpi

    assert admin_kpi._dolu_kosulu is admin_quality._dolu_kosulu


def test_kpi_alan_sozlugu_kopya_degil():
    """D-299: `adres`/`osb_parsel` kirigi iki dosyada birden yasadi.

    Kopya sozluk geri gelirse kirik da geri gelir -- ayni nesne olmali.
    """
    from web_dashboard.tabs import admin_kpi

    assert admin_kpi._QUALITY_FIELDS is admin_quality._QUALITY_FIELDS


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


@pytest.mark.skipif(not _db_var(), reason="DATABASE_URL erisimi yok; canli sema mandali atlandi")
def test_quality_fields_canli_semada_var():
    """Her alan adi gercekten `companies`te olmali; yoksa panel sessizce yalan soyler."""
    from company_master.db.connection import get_engine
    from sqlalchemy import text

    with get_engine().connect() as conn:
        kolonlar = {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'companies'"
                )
            )
        }
    eksik = sorted(set(admin_quality._QUALITY_FIELDS) - kolonlar)
    assert not eksik, f"canli `companies`te olmayan alan adlari: {eksik}"


@pytest.mark.skipif(not _db_var(), reason="DATABASE_URL erisimi yok; canli sema mandali atlandi")
def test_riskli_firmalar_sorgusu_canlida_kosar():
    """SQL gercek semada kosar; kolon adi hatasi burada kirilir (yutulmaz)."""
    admin_quality.load_risky_companies.clear()
    df = admin_quality.load_risky_companies(limit=5)
    assert list(df.columns) == [
        "Firma ID", "Unvan", "Ticari Ad", "Kimlik Tamlığı", "Eksik Alanlar",
    ]


@pytest.mark.skipif(not _db_var(), reason="DATABASE_URL erisimi yok; canli sema mandali atlandi")
def test_eksik_alan_analizi_olculemeyeni_sifir_yazmaz():
    """D-249: olculemeyen alan satir uretmez; `%0 eksik` yalani donmez."""
    admin_quality.load_missing_field_analysis.clear()
    df = admin_quality.load_missing_field_analysis()
    assert len(df) == len(admin_quality._QUALITY_FIELDS)
    # adres canlida %0 degil (olculdu: 3611/9409); 0 gorunuyorsa sorgu patlamistir
    assert float(df.loc[df["Alan"] == "Adres", "Eksiklik (%)"].iloc[0]) > 0
