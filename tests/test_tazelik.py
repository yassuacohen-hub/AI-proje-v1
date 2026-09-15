# -*- coding: utf-8 -*-
"""PO-BACK-05: Veri Tazelik Etiketi testleri."""

from datetime import datetime, timedelta, timezone

import pytest

from company_master.tazelik import tazelik_etiketi


def test_taze_30_dakika_alti():
    """≤30 dakika → taze, green."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    son = simdi + timedelta(minutes=10)
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "taze"
    assert r["renk"] == "green"
    assert r["saat_farki"] == 10.0


def test_eskiyor_30_120_arasi():
    """30-120 dakika → eskiyor, yellow."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    son = simdi + timedelta(minutes=60)
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "eskiyor"
    assert r["renk"] == "yellow"
    assert r["saat_farki"] == 60.0


def test_bayat_120_dakika_ustu():
    """>120 dakika → bayat, red."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    son = simdi + timedelta(minutes=200)
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "bayat"
    assert r["renk"] == "red"
    assert r["saat_farki"] == 200.0


def test_none_son_guncelleme():
    """None son_guncelleme → bayat, gray, saat_farki=None."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    r = tazelik_etiketi(None, simdi)
    assert r["etiketi"] == "bayat"
    assert r["renk"] == "gray"
    assert r["saat_farki"] is None


def test_zaman_dilimi_uyum():
    """TZ-aware + TZ-naive mixed → still works."""
    simdi = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)
    son = datetime(2026, 9, 15, 11, 55, 0)  # naive, 5 dk once
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "taze"
    assert r["renk"] == "green"
    assert r["saat_farki"] == 5.0


def test_sifir_dakika_ayni_zaman():
    """Sıfır dakika (aynı zaman) → taze."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    r = tazelik_etiketi(simdi, simdi)
    assert r["etiketi"] == "taze"
    assert r["renk"] == "green"
    assert r["saat_farki"] == 0.0


def test_tuzgun_format_string_hata():
    """String format → TypeError fırlatmalı."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    with pytest.raises((TypeError, AttributeError)):
        tazelik_etiketi("2026-09-15 12:00:00", simdi)


def test_negative_fark_future_timestamp():
    """Negative fark (future timestamp) → abs ile çalışır."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    son = simdi + timedelta(minutes=15)  # future
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "taze"
    assert r["renk"] == "green"
    assert r["saat_farki"] == 15.0


def test_eskiyor_sinir_30_dakika():
    """Tam 30 dakika → hala taze (≤)."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    son = simdi + timedelta(minutes=30)
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "taze"
    assert r["renk"] == "green"


def test_eskiyor_sinir_120_dakika():
    """Tam 120 dakika → eskiyor (≤)."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    son = simdi + timedelta(minutes=120)
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "eskiyor"
    assert r["renk"] == "yellow"


def test_31_dakika_taze_degil():
    """31 dakika → taze değil, eskiyor."""
    simdi = datetime(2026, 9, 15, 12, 0, 0)
    son = simdi + timedelta(minutes=31)
    r = tazelik_etiketi(son, simdi)
    assert r["etiketi"] == "eskiyor"
    assert r["renk"] == "yellow"
