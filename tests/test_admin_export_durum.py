# -*- coding: utf-8 -*-
"""ADMIN-ROO-01 Aşama C: admin_export veri okuyucu (df, hata) sözleşmesi testleri."""
from __future__ import annotations

import pandas as pd
import pytest

from web_dashboard.tabs import admin_export


# ---------------------------------------------------------------- _pano_oku
def test_pano_oku_dosya_yoksa_bos_df(tmp_path):
    df, hata = admin_export._pano_oku(tmp_path / "yok.json")
    assert hata is None
    assert df is not None and df.empty


def test_pano_oku_gecerli_json(tmp_path):
    yol = tmp_path / "task_board.json"
    yol.write_text('[{"id": "T-1", "durum": "done"}]', encoding="utf-8")
    df, hata = admin_export._pano_oku(yol)
    assert hata is None
    assert len(df) == 1 and df.iloc[0]["id"] == "T-1"


def test_pano_oku_bozuk_json_hata_doner(tmp_path):
    yol = tmp_path / "task_board.json"
    yol.write_text("{bozuk", encoding="utf-8")
    df, hata = admin_export._pano_oku(yol)
    assert df is None
    assert hata and "JSONDecodeError" in hata


# ---------------------------------------------------------- _db_sorgu_oku
class _Row(dict):
    pass


class _Sonuc:
    def __init__(self, kayitlar):
        self._kayitlar = kayitlar

    def mappings(self):
        return self

    def first(self):
        return self._kayitlar[0] if self._kayitlar else None

    def all(self):
        return self._kayitlar


class _Conn:
    def __init__(self, kayitlar):
        self._kayitlar = kayitlar
        self.sql = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql):
        self.sql = sql
        return _Sonuc(self._kayitlar)


class _Engine:
    def __init__(self, kayitlar):
        self.conn = _Conn(kayitlar)

    def connect(self):
        return self.conn


def test_db_sorgu_oku_kpi_tek_satir(monkeypatch):
    engine = _Engine([_Row(total_firma=42)])
    monkeypatch.setattr(admin_export, "get_engine", lambda: engine)
    df, hata = admin_export._db_sorgu_oku("kpi")
    assert hata is None
    assert df is not None and int(df.iloc[0]["total_firma"]) == 42


def test_db_sorgu_oku_companies_cok_satir(monkeypatch):
    engine = _Engine([_Row(company_id=1), _Row(company_id=2)])
    monkeypatch.setattr(admin_export, "get_engine", lambda: engine)
    df, hata = admin_export._db_sorgu_oku("companies")
    assert hata is None and len(df) == 2


def test_db_sorgu_oku_satir_yoksa_bos_df(monkeypatch):
    monkeypatch.setattr(admin_export, "get_engine", lambda: _Engine([]))
    df, hata = admin_export._db_sorgu_oku("audit")
    assert hata is None and df is not None and df.empty


def test_db_sorgu_oku_hata_yakalanir(monkeypatch):
    def _patla():
        raise RuntimeError("baglanti koptu")

    monkeypatch.setattr(admin_export, "get_engine", _patla)
    df, hata = admin_export._db_sorgu_oku("kpi")
    assert df is None
    assert hata and "RuntimeError" in hata and "baglanti koptu" in hata


def test_db_sorgu_oku_text_clause_kullanir(monkeypatch):
    from sqlalchemy.sql.elements import TextClause

    engine = _Engine([])
    monkeypatch.setattr(admin_export, "get_engine", lambda: engine)
    admin_export._db_sorgu_oku("kpi")
    assert isinstance(engine.conn.sql, TextClause)


# ------------------------------------------------------ _export_verisi_oku
@pytest.mark.parametrize("tur", ["kpi", "companies", "audit"])
def test_export_verisi_oku_db_turleri(monkeypatch, tur):
    monkeypatch.setattr(admin_export, "get_engine", lambda: _Engine([]))
    df, hata = admin_export._export_verisi_oku(tur)
    assert hata is None and df is not None


def test_export_verisi_oku_bilinmeyen_tur():
    df, hata = admin_export._export_verisi_oku("yok-boyle-tur")
    assert df is None
    assert hata and "Bilinmeyen export türü" in hata


# --------------------------------------------------------- kaynak taraması
def test_modul_sessiz_yutma_icermez():
    from pathlib import Path

    kaynak = Path("web_dashboard/tabs/admin_export.py").read_text(encoding="utf-8")
    assert "except Exception:\n            pass" not in kaynak
    assert "except Exception:\n            return None" not in kaynak
