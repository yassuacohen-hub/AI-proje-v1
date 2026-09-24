# -*- coding: utf-8 -*-
"""UI-ADMIN-GUNCELLIK-KOVA-10: updated_at yaş kovası dağılımı testleri."""
from __future__ import annotations

from datetime import datetime, timedelta

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
