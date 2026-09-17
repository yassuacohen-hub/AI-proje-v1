# -*- coding: utf-8 -*-
"""ADMIN-SEARCH-01: admin_search.py admin sekme kalıbı testleri.

Kapsam:
- ``_firma_ara`` / ``_kaynak_adlari`` → ``(veri, hata)`` sözleşmesi
- ``_sorgu_kur`` parametreli SQL üretimi
- ``kalite_bantlari`` dağılımı
- geriye dönük ``search_companies`` / ``get_source_names``
- ``render_search_tab`` senaryoları (kpi_karti / hata_kutusu / bos_durum / info)
- kaynak guard: ``st.metric`` ve sessiz ``except`` yok
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from web_dashboard.tabs import admin_search as modul

# ---------------------------------------------------------------------------
# Sahte DB
# ---------------------------------------------------------------------------


class _Sonuc:
    def __init__(self, kayitlar: list[dict[str, Any]]):
        self._kayitlar = kayitlar

    def mappings(self):
        return self

    def all(self):
        return list(self._kayitlar)


class _Conn:
    def __init__(self, rows: list[dict[str, Any]] | None = None, hata: Exception | None = None):
        self.rows = rows or []
        self.hata = hata
        self.sorgular: list[tuple[Any, Any]] = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        if self.hata is not None:
            raise self.hata
        self.sorgular.append((sql, params))
        return _Sonuc(self.rows)


class _Engine:
    def __init__(self, conn: _Conn):
        self._conn = conn

    def connect(self):
        return self._conn


def _engine_kur(monkeypatch, rows=None, hata=None) -> _Conn:
    conn = _Conn(rows=rows, hata=hata)
    monkeypatch.setattr(modul, "get_engine", lambda: _Engine(conn))
    return conn


def _satir(skor: float, cid: Any | None = None) -> dict[str, Any]:
    return {
        "company_id": cid if cid is not None else uuid.uuid4(),
        "legal_name": "Firma",
        "data_quality_score": skor,
    }


# ---------------------------------------------------------------------------
# _sorgu_kur
# ---------------------------------------------------------------------------


def test_sorgu_kur_filtresiz_sadece_skor_ve_limit():
    sql, params = modul._sorgu_kur("", 0, 100, "", 50)
    assert "ILIKE" not in sql
    assert "source_records" not in sql
    assert params == {"score_min": 0, "score_max": 100, "limit": 50}
    assert "ORDER BY data_quality_score DESC LIMIT :limit" in sql


def test_sorgu_kur_tum_filtreler_parametreli():
    sql, params = modul._sorgu_kur("abc", 10, 90, "ostim", 20)
    assert "legal_name ILIKE :q" in sql
    assert "source_name = :src" in sql
    assert params["q"] == "%abc%"
    assert params["src"] == "ostim"
    assert "abc" not in sql  # kullanıcı girdisi SQL'e gömülmez


# ---------------------------------------------------------------------------
# _firma_ara / _kaynak_adlari
# ---------------------------------------------------------------------------


def test_firma_ara_basarili_company_id_str_ve_skor_yuvarlanir(monkeypatch):
    cid = uuid.uuid4()
    conn = _engine_kur(monkeypatch, rows=[_satir(87.456, cid)])
    df, hata = modul._firma_ara(query="x")
    assert hata is None
    assert isinstance(df, pd.DataFrame)
    assert df.loc[0, "company_id"] == str(cid)
    assert df.loc[0, "data_quality_score"] == 87.5
    assert len(conn.sorgular) == 1


def test_firma_ara_satir_yoksa_bos_df_hata_yok(monkeypatch):
    _engine_kur(monkeypatch, rows=[])
    df, hata = modul._firma_ara()
    assert hata is None
    assert df is not None and df.empty


def test_firma_ara_hata_yakalanir_ve_loglanir(monkeypatch, caplog):
    _engine_kur(monkeypatch, hata=RuntimeError("baglanti yok"))
    with caplog.at_level(logging.WARNING):
        df, hata = modul._firma_ara()
    assert df is None
    assert hata == "RuntimeError: baglanti yok"
    assert "firma arama" in caplog.text


def test_firma_ara_none_skor_sifira_cevrilir(monkeypatch):
    _engine_kur(monkeypatch, rows=[_satir(None)])
    df, _ = modul._firma_ara()
    assert df.loc[0, "data_quality_score"] == 0


def test_kaynak_adlari_basarili(monkeypatch):
    _engine_kur(monkeypatch, rows=[{"source_name": "a"}, {"source_name": "b"}])
    assert modul._kaynak_adlari() == (["a", "b"], None)


def test_kaynak_adlari_hata_bos_liste_ve_metin(monkeypatch, caplog):
    _engine_kur(monkeypatch, hata=ValueError("tablo yok"))
    with caplog.at_level(logging.WARNING):
        kaynaklar, hata = modul._kaynak_adlari()
    assert kaynaklar == []
    assert hata == "ValueError: tablo yok"
    assert "kaynak listesi" in caplog.text


# ---------------------------------------------------------------------------
# kalite_bantlari
# ---------------------------------------------------------------------------


def test_kalite_bantlari_dagilim():
    df = pd.DataFrame({"data_quality_score": [95, 80, 79.9, 60, 45, 20, 5, 0]})
    bant = modul.kalite_bantlari(df)
    assert bant["80-100 (Yüksek)"] == 2
    assert bant["60-79 (İyi)"] == 2
    assert bant["40-59 (Orta)"] == 1
    assert bant["20-39 (Düşük)"] == 1
    assert bant["0-19 (Çok Düşük)"] == 2
    assert sum(bant.values()) == len(df)


@pytest.mark.parametrize("df", [None, pd.DataFrame(), pd.DataFrame({"x": [1]})])
def test_kalite_bantlari_bos_girdi_sifir(df):
    bant = modul.kalite_bantlari(df)
    assert len(bant) == 5 and all(v == 0 for v in bant.values())


# ---------------------------------------------------------------------------
# Geriye dönük uyumluluk (admin_musteriler kullanır)
# ---------------------------------------------------------------------------


def test_search_companies_df_doner(monkeypatch):
    frame = pd.DataFrame({"a": [1]})
    monkeypatch.setattr(modul, "firma_ara", lambda *a, **k: (frame, None))
    assert modul.search_companies(query="x") is frame


def test_search_companies_hatada_none(monkeypatch):
    monkeypatch.setattr(modul, "firma_ara", lambda *a, **k: (None, "hata"))
    assert modul.search_companies() is None


def test_get_source_names_hatada_bos_liste(monkeypatch):
    monkeypatch.setattr(modul, "kaynak_adlari", lambda: ([], "hata"))
    assert modul.get_source_names() == []


def test_cache_sarmalayicilar_saf_fonksiyona_delege_eder(monkeypatch):
    _engine_kur(monkeypatch, rows=[{"source_name": "z"}])
    assert modul.kaynak_adlari.__wrapped__() == (["z"], None)
    _engine_kur(monkeypatch, rows=[_satir(50)])
    df, hata = modul.firma_ara.__wrapped__(query="q")
    assert hata is None and len(df) == 1


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


class _Col:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Cikti:
    def __init__(self):
        self.kpi: list[dict[str, Any]] = []
        self.hata: list[tuple[str, Any, Any]] = []
        self.bos: list[str] = []
        self.info: list[str] = []
        self.success: list[str] = []
        self.dataframe = 0
        self.bar_chart = 0
        self.metric = 0


@pytest.fixture()
def cikti(monkeypatch):
    c = _Cikti()
    st = modul.st
    monkeypatch.setattr(st, "subheader", lambda *a, **k: None)
    monkeypatch.setattr(st, "columns", lambda n, **k: [_Col() for _ in range(n if isinstance(n, int) else len(n))])
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "")
    monkeypatch.setattr(st, "slider", lambda *a, **k: (0, 100))
    monkeypatch.setattr(st, "selectbox", lambda label, opts, **k: opts[k.get("index", 0)])
    monkeypatch.setattr(st, "info", lambda m, **k: c.info.append(m))
    monkeypatch.setattr(st, "success", lambda m, **k: c.success.append(m))
    monkeypatch.setattr(st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(st, "divider", lambda *a, **k: None)
    monkeypatch.setattr(st, "dataframe", lambda *a, **k: setattr(c, "dataframe", c.dataframe + 1))
    monkeypatch.setattr(st, "bar_chart", lambda *a, **k: setattr(c, "bar_chart", c.bar_chart + 1))
    monkeypatch.setattr(st, "metric", lambda *a, **k: setattr(c, "metric", c.metric + 1))
    monkeypatch.setattr(modul, "kpi_karti", lambda baslik, deger, **k: c.kpi.append({"baslik": baslik, "deger": deger, **k}))
    monkeypatch.setattr(modul, "hata_kutusu", lambda b, h, ipucu=None, **k: c.hata.append((b, h, ipucu)) or "")
    monkeypatch.setattr(modul, "bos_durum", lambda m, **k: c.bos.append(m) or "")
    monkeypatch.setattr(modul, "kaynak_adlari", lambda: (["ostim"], None))
    return c


def test_render_filtre_yoksa_yalniz_bilgi(monkeypatch, cikti):
    monkeypatch.setattr(modul, "firma_ara", lambda **k: pytest.fail("filtre yokken sorgu atılmamalı"))
    modul.render_search_tab()
    assert len(cikti.info) == 1 and "Arama yapın" in cikti.info[0]
    assert cikti.kpi == [] and cikti.hata == []


def test_render_sonuc_varsa_uc_kpi_karti_ve_metric_yok(monkeypatch, cikti):
    monkeypatch.setattr(modul.st, "text_input", lambda *a, **k: "firma")
    df = pd.DataFrame({"data_quality_score": [90.0, 20.0, 50.0]})
    monkeypatch.setattr(modul, "firma_ara", lambda **k: (df, None))
    modul.render_search_tab()
    assert [k["baslik"] for k in cikti.kpi] == ["Toplam Sonuç", "Ort. Kalite", "Düşük Kalite"]
    assert cikti.kpi[0]["deger"] == 3
    assert cikti.kpi[1]["deger"] == pytest.approx(53.333, abs=0.01)
    assert cikti.kpi[2]["deger"] == 1 and cikti.kpi[2]["kategori"] == "uyari"
    assert {k["anahtar"] for k in cikti.kpi} == {"search-toplam", "search-ortalama", "search-dusuk"}
    assert cikti.metric == 0
    assert cikti.dataframe == 1 and cikti.bar_chart == 1
    assert cikti.hata == [] and cikti.bos == []


def test_render_dusuk_kalite_yoksa_basari_kategorisi(monkeypatch, cikti):
    monkeypatch.setattr(modul.st, "text_input", lambda *a, **k: "x")
    monkeypatch.setattr(modul, "firma_ara", lambda **k: (pd.DataFrame({"data_quality_score": [80.0]}), None))
    modul.render_search_tab()
    assert cikti.kpi[2]["kategori"] == "basari"


def test_render_db_hatasi_hata_kutusu(monkeypatch, cikti):
    monkeypatch.setattr(modul.st, "text_input", lambda *a, **k: "x")
    monkeypatch.setattr(modul, "firma_ara", lambda **k: (None, "OperationalError: down"))
    modul.render_search_tab()
    assert cikti.hata == [("Arama sorgusu çalıştırılamadı", "OperationalError: down", modul.DB_IPUCU)]
    assert cikti.kpi == [] and cikti.dataframe == 0


def test_render_bos_sonuc_bos_durum(monkeypatch, cikti):
    monkeypatch.setattr(modul.st, "text_input", lambda *a, **k: "yok")
    monkeypatch.setattr(modul, "firma_ara", lambda **k: (pd.DataFrame(), None))
    modul.render_search_tab()
    assert len(cikti.bos) == 1 and "eşleşen firma yok" in cikti.bos[0]
    assert cikti.kpi == [] and cikti.hata == []


def test_render_kaynak_hatasi_kucuk_hata_kutusu_ama_arama_surer(monkeypatch, cikti):
    monkeypatch.setattr(modul, "kaynak_adlari", lambda: ([], "ValueError: tablo yok"))
    monkeypatch.setattr(modul.st, "text_input", lambda *a, **k: "x")
    monkeypatch.setattr(modul, "firma_ara", lambda **k: (pd.DataFrame({"data_quality_score": [70.0]}), None))
    modul.render_search_tab()
    assert cikti.hata[0][0] == "Kaynak listesi okunamadı"
    assert len(cikti.kpi) == 3


def test_render_filtre_parametreleri_dogru_iletilir(monkeypatch, cikti):
    yakalanan: dict[str, Any] = {}
    monkeypatch.setattr(modul.st, "text_input", lambda *a, **k: "abc")
    monkeypatch.setattr(modul.st, "slider", lambda *a, **k: (30, 70))
    monkeypatch.setattr(modul.st, "selectbox", lambda label, opts, **k: "ostim" if "Kaynak" in label else 200)

    def _ara(**k):
        yakalanan.update(k)
        return pd.DataFrame(), None

    monkeypatch.setattr(modul, "firma_ara", _ara)
    modul.render_search_tab()
    assert yakalanan == {"query": "abc", "score_min": 30, "score_max": 70, "source": "ostim", "limit": 200}


# ---------------------------------------------------------------------------
# Kaynak guard
# ---------------------------------------------------------------------------


def test_modul_st_metric_sessiz_except_ve_use_container_width_icermez():
    kaynak = Path(modul.__file__).read_text(encoding="utf-8")
    assert "st.metric(" not in kaynak
    assert "use_container_width" not in kaynak
    assert "st.warning(" not in kaynak
    assert "except Exception:\n        return []" not in kaynak
    assert "\ufeff" not in kaynak
