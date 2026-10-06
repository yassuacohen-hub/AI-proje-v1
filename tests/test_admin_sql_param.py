# -*- coding: utf-8 -*-
"""ALTYAPI-ADMIN-SQL-PARAM-01: `_dolu_kosulu` kolon adi beyaz listesi.

`_dolu_kosulu` kolon adini dogrudan SQL'e gomer (bind parametresi degil).
Tek savunma: `_IZINLI_KOLONLAR` disindaki her deger ValueError ile
fail-closed reddedilmeli -- aksi halde cagiran kod sorgu enjeksiyonuna
acik olur.
"""
import pytest

from web_dashboard.tabs import admin_quality


def test_izinli_kolon_gecer():
    kosul = admin_quality._dolu_kosulu("website_domain")
    assert "website_domain" in kosul


def test_izinsiz_kolon_fail_closed():
    with pytest.raises(ValueError):
        admin_quality._dolu_kosulu("website_domain; DROP TABLE companies")


def test_izinli_kolonlar_quality_fields_ile_ayni():
    assert admin_quality._IZINLI_KOLONLAR == frozenset(admin_quality._QUALITY_FIELDS)
