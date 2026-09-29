# -*- coding: utf-8 -*-
"""ADMIN-EXEC-01: Executive Dashboard sekmesi (roo).

Kapsam:
* ``load_executive_ozet`` → hata yutulmaz: ``hata`` / ``tenant_hata`` alanları
  dolar, ``logger.warning`` yazılır, ``kaynak`` doğru işaretlenir.
* ``_tl`` / ``_mrr_delta`` / ``_firma_kayitlari`` saf yardımcılar.
* ``render_executive_tab`` tek KPI dili: 6 ``kpi_karti`` (MRR, ARR, Churn,
  🟢, 🟡, 🔴), benzersiz anahtar, ``st.metric`` hiç çağrılmaz; DB yoksa
  ``hata_kutusu`` çizilir.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from web_dashboard.tabs import admin_executive as ex


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

class _Col:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Sonuc:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _Conn(_Col):
    def __init__(self, rows=None, hata: Exception | None = None):
        self._rows = rows or []
        self._hata = hata

    def execute(self, *a, **k):
        if self._hata:
            raise self._hata
        return _Sonuc(self._rows)


class _Engine:
    def __init__(self, rows=None, hata: Exception | None = None):
        self._conn = _Conn(rows, hata)

    def connect(self):
        return self._conn


def _yukle_ham() -> Any:
    """``st.cache_data`` sarmalayıcısını atlayarak asıl fonksiyonu döndürür."""
    fn = getattr(ex.load_executive_ozet, "__wrapped__", None)
    if fn is None:  # pragma: no cover — streamlit sürümüne göre
        ex.load_executive_ozet.clear()
        fn = ex.load_executive_ozet
    return fn


# ---------------------------------------------------------------------------
# load_executive_ozet — sessiz except yok
# ---------------------------------------------------------------------------

def test_load_db_hatasi_hata_alanina_yazilir(monkeypatch, caplog):
    def _patlat():
        raise ConnectionError("postgres kapalı")

    monkeypatch.setattr(ex, "get_engine", _patlat)
    with caplog.at_level(logging.WARNING):
        veri = _yukle_ham()()

    assert veri["kaynak"] == "bos"
    assert veri["abonelikler"] == [] and veri["tenantlar"] == []
    assert "ConnectionError" in veri["hata"] and "postgres kapalı" in veri["hata"]
    assert veri["tenant_hata"] is None
    assert any("okunamadı" in r.getMessage() for r in caplog.records)


def test_load_db_basarili_tenant_hatasi_ayri_alanda(monkeypatch, caplog):
    rows = [{"paket": "Temel", "aylik_ucret": 500, "baslangic": "2026-01-01", "durum": "aktif"}]
    monkeypatch.setattr(ex, "get_engine", lambda: _Engine(rows))
    monkeypatch.setattr(ex, "_tenant_sagligi", lambda engine: (_ for _ in ()).throw(RuntimeError("companies yok")))

    with caplog.at_level(logging.WARNING):
        veri = _yukle_ham()()

    assert veri["kaynak"] == "db"
    assert veri["abonelikler"] == rows
    assert veri["hata"] is None
    assert "RuntimeError" in veri["tenant_hata"]
    assert veri["tenantlar"] == []


def test_load_tam_basari(monkeypatch):
    rows = [{"paket": "Pro", "aylik_ucret": 1200, "baslangic": "2026-02-01", "durum": "aktif"}]
    monkeypatch.setattr(ex, "get_engine", lambda: _Engine(rows))
    monkeypatch.setattr(ex, "_tenant_sagligi", lambda engine: {"score": 90, "band": "green"})

    veri = _yukle_ham()()

    assert veri == {
        "abonelikler": rows,
        "tenantlar": [{"score": 90, "band": "green"}],
        "kaynak": "db",
        "hata": None,
        "tenant_hata": None,
        "veri_yok": False,
    }


# ---------------------------------------------------------------------------
# Saf yardımcılar
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "deger, ondalik, beklenen",
    [
        (12345, 0, "12.345 ₺"),
        (1234.5, 2, "1.234,50 ₺"),
        (0, 0, "0 ₺"),
        (-750, 0, "-750 ₺"),
        (None, 0, "—"),
        ("abc", 0, "—"),
    ],
)
def test_tl_bicimi(deger, ondalik, beklenen):
    assert ex._tl(deger, ondalik) == beklenen


@pytest.mark.parametrize(
    "seri, beklenen",
    [
        ([], None),
        ([{"ay": "2026-08", "mrr": 100}], None),
        ([{"ay": "2026-07", "mrr": 100}, {"ay": "2026-08", "mrr": 1300}], "+1.200 ₺"),
        ([{"ay": "2026-07", "mrr": 1300}, {"ay": "2026-08", "mrr": 100}], "-1.200 ₺"),
        ([{"ay": "2026-07", "mrr": 500}, {"ay": "2026-08", "mrr": 500}], "0 ₺ (değişim yok)"),
        ([{"ay": "2026-07", "mrr": 0}, {"ay": "2026-08", "mrr": 0}], None),  # gelir yok → delta yok
        ([{"ay": "2026-07"}, {"ay": "2026-08", "mrr": 5}], None),  # KeyError
        ([{"ay": "2026-07", "mrr": "x"}, {"ay": "2026-08", "mrr": 5}], None),  # ValueError
    ],
)
def test_mrr_delta(seri, beklenen):
    assert ex._mrr_delta(seri) == beklenen


def test_churn_donemi_pencere():
    baslangic, bitis = ex._churn_donemi(30)
    fark = datetime.fromisoformat(bitis) - datetime.fromisoformat(baslangic)
    assert fark.days == 30


def test_firma_kayitlari_30_gun_esigi():
    # D-298: naive `datetime.now()` yerel saatti (UTC+3); kod naive girdiyi UTC
    # sayinca 3 gun 2'ye dusuyordu. Canli `updated_at` timestamptz -> aware.
    simdi = datetime.now(timezone.utc)
    rows = [
        {"identity_completeness": 6.5, "nace_code": "62.01", "adres": "Ankara",
         "updated_at": simdi - timedelta(days=3)},
        {"identity_completeness": None, "nace_code": None, "adres": None,
         "updated_at": (simdi - timedelta(days=60)).isoformat()},
        {"identity_completeness": 3.0, "nace_code": "x", "adres": "y",
         "updated_at": "bozuk"},
    ]
    kayitlar = ex._firma_kayitlari(_Engine(rows))

    assert len(kayitlar) == 3
    assert kayitlar[0]["son_guncelleme_gun"] == 3
    assert kayitlar[0]["adres"] == "Ankara"
    assert kayitlar[1]["son_guncelleme_gun"] is None  # 30 günden eski
    # D-249: olculmemis firma 0 puanli gibi saglik ortalamasina girmez
    assert kayitlar[1]["identity_completeness"] is None
    assert kayitlar[2]["son_guncelleme_gun"] is None  # parse edilemedi
    assert all("data_quality_score" not in k for k in kayitlar), \
        "terk edilmis kolon geri sizdi"


def test_firma_kayitlari_canli_tipleri_aware_ve_decimal():
    """D-298: canli DB `updated_at`i timestamptz (offset-aware),
    `identity_completeness`i NUMERIC (-> ``Decimal``) dondurur. Sahte engine
    naive datetime + float veriyordu, iki canli TypeError gizlendi. DB yokken
    de bu iki tip regresyonu yakalansin diye canli tipler taklit edilir.
    """
    simdi = datetime.now(timezone.utc)
    rows = [
        {"identity_completeness": Decimal("6.50"), "nace_code": "62.01",
         "adres": "Ankara", "updated_at": simdi - timedelta(days=3)},
    ]
    kayitlar = ex._firma_kayitlari(_Engine(rows))

    assert kayitlar[0]["son_guncelleme_gun"] == 3
    # health.py float ile boler; Decimal sizarsa canlida TypeError
    assert isinstance(kayitlar[0]["identity_completeness"], float)
    assert kayitlar[0]["identity_completeness"] == 6.5


# ---------------------------------------------------------------------------
# D-298: sahte engine SQL'i hic calistirmiyordu; uc canli ariza yesil gorundu.
# Tek gercek sema kaynagi canli DB (schema/*.sql bayat: `address` yok,
# `raw_address` yaziyor). DB yoksa atlanir.
# ---------------------------------------------------------------------------

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
def test_firma_kayitlari_canli_semaya_karsi_kosar():
    """SQL gercek semada kosar; kolon adi/tz/Decimal uclusu burada kirilir."""
    from company_master.db.connection import get_engine

    kayitlar = ex._firma_kayitlari(get_engine())

    assert isinstance(kayitlar, list)
    for k in kayitlar:
        assert set(k) == {
            "identity_completeness", "nace_code", "adres", "son_guncelleme_gun",
        }
        assert k["identity_completeness"] is None or isinstance(
            k["identity_completeness"], float
        )
        assert k["son_guncelleme_gun"] is None or isinstance(
            k["son_guncelleme_gun"], int
        )


# ---------------------------------------------------------------------------
# render_executive_tab — tek KPI dili
# ---------------------------------------------------------------------------

class _Cikti:
    def __init__(self):
        self.kpi: list[dict[str, Any]] = []
        self.hata: list[tuple[str, str, str | None]] = []
        self.caption: list[str] = []
        self.info: list[str] = []
        self.plotly = 0
        self.dataframe: list[dict[str, Any]] = []
        self.metric = 0


@pytest.fixture()
def cikti(monkeypatch):
    c = _Cikti()
    st = ex.st
    monkeypatch.setattr(st, "columns", lambda n, **k: [_Col() for _ in range(n if isinstance(n, int) else len(n))])
    monkeypatch.setattr(st, "caption", lambda m, *a, **k: c.caption.append(str(m)))
    monkeypatch.setattr(st, "info", lambda m, *a, **k: c.info.append(str(m)))
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(st, "metric", lambda *a, **k: setattr(c, "metric", c.metric + 1))
    monkeypatch.setattr(st, "plotly_chart", lambda *a, **k: setattr(c, "plotly", c.plotly + 1))
    monkeypatch.setattr(st, "line_chart", lambda *a, **k: setattr(c, "plotly", c.plotly + 1))
    monkeypatch.setattr(st, "dataframe", lambda df, **k: c.dataframe.append(k))
    monkeypatch.setattr(ex, "line_chart", lambda *a, **k: object())
    monkeypatch.setattr(ex.PageHeader, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(ex.Section, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(ex, "kpi_karti", lambda baslik, deger, **k: c.kpi.append({"baslik": baslik, "deger": deger, **k}))
    monkeypatch.setattr(ex, "hata_kutusu", lambda b, h, ipucu=None, **k: c.hata.append((b, h, ipucu)) or "")
    return c


def _abonelikler() -> list[dict[str, Any]]:
    bugun = datetime.now().date()
    return [
        {"paket": "Temel", "aylik_ucret": 500, "baslangic": (bugun - timedelta(days=200)).isoformat(), "durum": "aktif"},
        {"paket": "Pro", "aylik_ucret": 1500, "baslangic": (bugun - timedelta(days=100)).isoformat(), "durum": "aktif"},
    ]


def test_render_db_varsa_alti_kpi_karti_ve_hata_yok(monkeypatch, cikti):
    veri = {
        "abonelikler": _abonelikler(),
        "tenantlar": [{"score": 90, "band": "green"}, {"score": 70, "band": "yellow"}],
        "kaynak": "db",
        "hata": None,
        "tenant_hata": None,
    }
    monkeypatch.setattr(ex, "load_executive_ozet", lambda: veri)
    monkeypatch.setattr(ex, "health_dagilimi", lambda t: {"green": 1, "yellow": 1, "red": 0})

    ex.render_executive_tab()

    basliklar = [k["baslik"] for k in cikti.kpi]
    assert basliklar == [
        "MRR (Aylık Yinelenen Gelir)",
        "ARR (Yıllık Yinelenen Gelir)",
        f"Churn Oranı ({ex.CHURN_GUN} gün)",
        "🟢 Sağlıklı",
        "🟡 Uyarı",
        "🔴 Kritik",
    ]
    assert cikti.kpi[0]["deger"] == "2.000 ₺"
    assert cikti.kpi[1]["deger"] == "24.000 ₺"
    assert cikti.kpi[2]["deger"].startswith("%")
    assert [k["deger"] for k in cikti.kpi[3:]] == [1, 1, 0]
    assert [k["kategori"] for k in cikti.kpi[3:]] == ["basari", "uyari", "tehlike"]
    assert len({k["anahtar"] for k in cikti.kpi}) == 6
    assert cikti.metric == 0  # st.metric tamamen kalktı
    assert not cikti.hata
    assert cikti.plotly == 1
    assert cikti.dataframe and cikti.dataframe[0].get("width") == "stretch"
    assert any("Toplam 2 tenant" in m for m in cikti.caption)


def test_render_db_yoksa_hata_kutusu_ve_bos_kartlar(monkeypatch, cikti):
    veri = {"abonelikler": [], "tenantlar": [], "kaynak": "bos",
            "hata": "OperationalError: bağlantı reddedildi", "tenant_hata": None}
    monkeypatch.setattr(ex, "load_executive_ozet", lambda: veri)

    ex.render_executive_tab()

    assert len(cikti.hata) == 1
    baslik, hata, ipucu = cikti.hata[0]
    assert "Abonelik verisine" in baslik
    assert "OperationalError" in hata
    assert "DATABASE_URL" in ipucu
    assert len(cikti.kpi) == 6
    assert cikti.kpi[0]["deger"] == "0 ₺"
    assert cikti.kpi[0].get("delta") is None
    assert cikti.plotly == 0 and any("Trend" in m for m in cikti.info)
    assert any("bulunamadı" in m for m in cikti.caption)
    assert cikti.metric == 0


def test_render_tenant_hatasi_ikinci_hata_kutusu(monkeypatch, cikti):
    veri = {"abonelikler": _abonelikler(), "tenantlar": [], "kaynak": "db",
            "hata": None, "tenant_hata": "RuntimeError: companies yok"}
    monkeypatch.setattr(ex, "load_executive_ozet", lambda: veri)

    ex.render_executive_tab()

    assert [h[0] for h in cikti.hata] == ["Tenant sağlığı hesaplanamadı"]
    assert "RuntimeError" in cikti.hata[0][1]


def test_render_hata_yoksa_hata_metni_bos_kaynak_icin_varsayilan(monkeypatch, cikti):
    veri = {"abonelikler": [], "tenantlar": [], "kaynak": "bos", "hata": None, "tenant_hata": None}
    monkeypatch.setattr(ex, "load_executive_ozet", lambda: veri)

    ex.render_executive_tab()

    assert cikti.hata[0][1] == "DB bağlantısı kurulamadı"


def test_modul_st_metric_ve_use_container_width_icermez():
    from pathlib import Path

    kaynak = Path(ex.__file__).read_text(encoding="utf-8")
    assert "st.metric(" not in kaynak
    assert "use_container_width" not in kaynak
    assert "except Exception:\n        pass" not in kaynak
