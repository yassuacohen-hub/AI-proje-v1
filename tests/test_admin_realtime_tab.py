# -*- coding: utf-8 -*-
"""UI-ADMIN-SSE-IHLAL-03: Canlı Veri Akışı sekmesi (polling).

Kapsam:
* Sağlık durumu saf fonksiyonu
* ``_db_kpi_oku`` / ``_db_trend_oku`` ``(veri, hata)`` sözleşmesi; SQL ``text()``
* ``render_admin_realtime_tab`` yolları: veri var → kpi_karti ×3 + trend;
  DB hatası → hata_kutusu; boş DB → bos_durum
* **Mimari kural:** modülde SSE kalıntısı yok (ADR satır 81)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from sqlalchemy.sql.elements import TextClause

from web_dashboard.tabs import admin_realtime as rt


# ---------------------------------------------------------------------------
# Mimari kural — SSE kalıntısı yok
# ---------------------------------------------------------------------------

def test_sse_kalintisi_yok():
    """ADR satır 81: SSE yalnız müşteri panelinde; admin polling."""
    kaynak = Path(rt.__file__).read_text(encoding="utf-8")
    kod = "\n".join(
        s for s in kaynak.splitlines() if not s.lstrip().startswith("#")
    )
    for yasak in ("import requests", "requests.get", "_sse_oku", "SSE_URL", "load_sse_data"):
        assert yasak not in kod, f"admin_realtime.py hâlâ SSE kalıntısı içeriyor: {yasak}"
    assert not hasattr(rt, "load_sse_data")


# ---------------------------------------------------------------------------
# Saf fonksiyonlar
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "skor, beklenen",
    [(95, "🟢 Sağlıklı"), (90, "🟢 Sağlıklı"), (89.9, "🟠 Dikkat"), (None, "🟠 Dikkat"), ("x", "🟠 Dikkat")],
)
def test_saglik_durumu(skor, beklenen):
    assert rt._saglik_durumu(skor) == beklenen


# ---------------------------------------------------------------------------
# DB okuyucular
# ---------------------------------------------------------------------------

class _Row(dict):
    pass


class _Sonuc:
    def __init__(self, satirlar):
        self._satirlar = satirlar

    def mappings(self):
        return self

    def first(self):
        return self._satirlar[0] if self._satirlar else None

    def __iter__(self):
        return iter(self._satirlar)


class _Conn:
    def __init__(self, satirlar, kayit: list):
        self._satirlar = satirlar
        self._kayit = kayit

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, ifade):
        self._kayit.append(ifade)
        return _Sonuc(self._satirlar)


class _Engine:
    def __init__(self, satirlar, kayit):
        self._satirlar, self._kayit = satirlar, kayit

    def connect(self):
        return _Conn(self._satirlar, self._kayit)


def test_db_kpi_oku_text_ile_sarili(monkeypatch):
    kayit: list = []
    satir = _Row(total=42, signals=7, score=93)
    monkeypatch.setattr(rt, "get_engine", lambda: _Engine([satir], kayit))
    veri, hata = rt._db_kpi_oku()
    assert hata is None and veri == {"total": 42, "signals": 7, "score": 93}
    assert len(kayit) == 1 and isinstance(kayit[0], TextClause)
    assert "FROM companies" in str(kayit[0])


def test_db_kpi_oku_satir_yoksa_sifir(monkeypatch):
    monkeypatch.setattr(rt, "get_engine", lambda: _Engine([], []))
    veri, hata = rt._db_kpi_oku()
    assert hata is None and veri["total"] == 0


def test_db_kpi_oku_hata_metni(monkeypatch, caplog):
    def _patlat():
        raise RuntimeError("DB kapalı")

    monkeypatch.setattr(rt, "get_engine", _patlat)
    with caplog.at_level("WARNING"):
        veri, hata = rt._db_kpi_oku()
    assert veri["total"] == 0
    assert "RuntimeError" in hata and "DB kapalı" in hata
    assert "DB KPI okunamadı" in caplog.text


def test_db_trend_oku(monkeypatch):
    kayit: list = []
    satirlar = [_Row(saat="2026-09-24T01:00", sinyal=3)]
    monkeypatch.setattr(rt, "get_engine", lambda: _Engine(satirlar, kayit))
    df, hata = rt._db_trend_oku()
    assert hata is None and len(df) == 1 and list(df.columns) == ["saat", "sinyal"]
    assert isinstance(kayit[0], TextClause) and "company_signals" in str(kayit[0])


def test_db_trend_oku_hata_bos_df(monkeypatch, caplog):
    def _patlat():
        raise RuntimeError("yok")

    monkeypatch.setattr(rt, "get_engine", _patlat)
    with caplog.at_level("WARNING"):
        df, hata = rt._db_trend_oku()
    assert df.empty and "RuntimeError" in hata


# ---------------------------------------------------------------------------
# Render yolları
# ---------------------------------------------------------------------------

class _Col:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Cikti:
    """Render sırasında çağrılan bileşenleri toplar."""

    def __init__(self):
        self.kpi: list[dict[str, Any]] = []
        self.hata: list[tuple[str, str, str | None]] = []
        self.bos: list[str] = []
        self.line_chart = 0
        self.caption: list[str] = []


@pytest.fixture()
def cikti(monkeypatch):
    c = _Cikti()
    st = rt.st
    monkeypatch.setattr(st, "columns", lambda n, **k: [_Col() for _ in range(n if isinstance(n, int) else len(n))])
    monkeypatch.setattr(st, "button", lambda *a, **k: False)
    monkeypatch.setattr(st, "toggle", lambda *a, **k: False)
    monkeypatch.setattr(st, "caption", lambda m, *a, **k: c.caption.append(str(m)))
    monkeypatch.setattr(st, "info", lambda *a, **k: None)
    monkeypatch.setattr(st, "spinner", lambda *a, **k: _Col())
    monkeypatch.setattr(st, "line_chart", lambda *a, **k: setattr(c, "line_chart", c.line_chart + 1))
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(rt, "render_auto_refresh", lambda *a, **k: None)
    monkeypatch.setattr(rt.PageHeader, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(rt.SectionNav, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(rt.Section, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(rt, "kpi_karti", lambda baslik, deger, **k: c.kpi.append({"baslik": baslik, "deger": deger, **k}))
    monkeypatch.setattr(rt, "hata_kutusu", lambda b, h, ipucu=None, **k: c.hata.append((b, h, ipucu)) or "")
    monkeypatch.setattr(rt, "bos_durum", lambda m, **k: c.bos.append(m) or "")
    return c


def test_render_veri_varsa_uc_kpi_ve_trend(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: ({"total": 1500, "signals": 20, "score": 97}, None))
    monkeypatch.setattr(
        rt, "load_trend_from_db",
        lambda: (pd.DataFrame({"saat": ["01:00", "02:00"], "sinyal": [3, 4]}), None),
    )

    rt.render_admin_realtime_tab()

    assert [k["baslik"] for k in cikti.kpi] == ["Toplam Firma", "Sinyal", "Veri Sağlığı"]
    assert cikti.kpi[0]["deger"] == 1500
    assert cikti.kpi[2]["deger"] == "🟢 Sağlıklı"
    assert len({k["anahtar"] for k in cikti.kpi}) == 3  # widget anahtar çakışması yok
    assert cikti.line_chart == 1
    assert not cikti.hata and not cikti.bos


def test_render_trend_yoksa_bos_durum(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: ({"total": 5, "signals": 0, "score": 50}, None))
    monkeypatch.setattr(rt, "load_trend_from_db", lambda: (pd.DataFrame(), None))
    rt.render_admin_realtime_tab()
    assert cikti.line_chart == 0
    assert any("sinyal yok" in m for m in cikti.bos)


def test_render_db_hatasi_hata_kutusu(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: ({"total": 0}, "OperationalError: no db"))
    monkeypatch.setattr(rt, "load_trend_from_db", lambda: pytest.fail("trend çağrılmamalı"))

    rt.render_admin_realtime_tab()

    assert len(cikti.hata) == 1
    baslik, hata, ipucu = cikti.hata[0]
    assert "Veritabanı okunamadı" == baslik and "no db" in hata and "DATABASE_URL" in ipucu
    assert not cikti.kpi


def test_render_bos_db_bos_durum(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: ({"total": 0, "signals": 0, "score": 0}, None))
    monkeypatch.setattr(rt, "load_trend_from_db", lambda: pytest.fail("trend çağrılmamalı"))

    rt.render_admin_realtime_tab()

    assert not cikti.hata and not cikti.kpi
    assert len(cikti.bos) == 1


def test_modul_except_pass_icermez():
    """ADMIN-ROO-01 kuralı: sessiz yutma yok."""
    kaynak = Path(rt.__file__).read_text(encoding="utf-8")
    assert "except Exception:\n        pass" not in kaynak
    assert "st.metric(" not in kaynak
    assert "text(" in kaynak
