# -*- coding: utf-8 -*-
"""MANDAL-YUTULAN-01 (D-301): yutulan hata "veri yok" diye sunulmasin.

Olculen olay: `load_risky_companies` SQL'i patladiginda bos df donuyor, panel de
`st.success("... risk yok")` yaziyordu. Kullanici kirik sorguyu **iyi haber**
olarak okuyordu -- D-249'un panel yuzeyindeki son kalintisi.

Kardes taramasi (D-301): ayni dosyada 7 loader `except` icinde bos veri donuyor.
Dordu yoklugu **belirsiz** sunuyor ("Skor dagilimi verisi bulunamadi") -- bu
D-249'a aykiri degil, dokunulmadi. Ikisi `st.success` ile yoklugu **olumluyordu**;
yalnizca onlar kesildi. Yani "bir tane bulduysan kardesleri var" dogruydu ama
sayi 6 degil 2: olcum, tahmini yariya indirdi.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from web_dashboard.tabs import admin_quality


class _PatlayanConn:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a, **k):
        raise RuntimeError("kolon yok: simulasyon")

    def rollback(self):
        pass


class _PatlayanEngine:
    def connect(self):
        return _PatlayanConn()


@pytest.fixture
def patlayan_db(monkeypatch):
    monkeypatch.setattr(admin_quality, "get_engine", lambda: _PatlayanEngine())
    monkeypatch.setattr(admin_quality._admin_quality_logger, "warning", lambda *a, **k: None)


def test_riskli_firmalar_hatayi_veriye_yaziyor(patlayan_db):
    admin_quality.load_risky_companies.clear()
    df = admin_quality.load_risky_companies(limit=5)
    assert df.empty
    assert admin_quality.olculemedi(df), (
        "SQL patladi ama df 'gercekten bos' gorunuyor -- panel 'risk yok' yazar"
    )


def test_eksik_alan_analizi_hatayi_veriye_yaziyor(patlayan_db):
    admin_quality.load_missing_field_analysis.clear()
    df = admin_quality.load_missing_field_analysis()
    assert admin_quality.olculemedi(df), (
        "SQL patladi ama df temiz gorunuyor -- panel 'kalite iyi durumda' yazar"
    )


def test_gercek_bos_sonuc_hata_isareti_tasimaz():
    """Isaret yanlis pozitif vermesin: gercekten bos veri 'olculemedi' degildir."""
    assert admin_quality.olculemedi(pd.DataFrame()) is None


def test_hata_isareti_cache_ustunden_sag_kaliyor(patlayan_db):
    """st.cache_data `df.attrs`'i koruyor -- D-301'de olculdu, varsayilmadi."""
    admin_quality.load_risky_companies.clear()
    ilk = admin_quality.load_risky_companies(limit=5)
    ikinci = admin_quality.load_risky_companies(limit=5)  # cache'ten
    assert admin_quality.olculemedi(ikinci) == admin_quality.olculemedi(ilk)


def test_olumlayan_yuzeyler_hata_kontrolsuz_kalmasin():
    """`st.success` yoklugu olumlar; once 'olculemedi' sorulmali.

    Bu mandal kod okur: gelecekte yeni bir `st.success(... bulunamadi)` eklenirse
    ve hata kontrolu yapilmazsa kirmizi verir.
    """
    satirlar = Path(admin_quality.__file__).read_text(encoding="utf-8").splitlines()
    basarili = [
        (i + 1, s.strip()) for i, s in enumerate(satirlar)
        if "st.success(" in s and not s.lstrip().startswith("#")
    ]
    # Olculen durum: 3 st.success var. Ikisi bos-veri dalinda (artik `olculemedi`
    # kontrolunden sonra), biri kaynak guvenilirligi ("Tum kaynaklar yesil") --
    # o bos listede degil, dolu listede kosuyor, yani yokluk olumlamiyor.
    assert len(basarili) == 3, (
        f"st.success sayisi degisti ({len(basarili)}): yeni yuzey yoklugu "
        f"olumluyor olabilir, 'olculemedi' kontrolu eklendi mi? {basarili}"
    )
    kaynak = "\n".join(satirlar)
    assert kaynak.count("olculemedi(") >= 3, (
        "Hata kontrolu kaldirilmis; bos veri yine iyi haber gibi sunulur"
    )
