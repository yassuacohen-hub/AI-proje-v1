# -*- coding: utf-8 -*-
"""ADMIN-ROO-01 Aşama B: Canlı Veri Akışı sekmesi.

Kapsam:
* SSE ayrıştırma / metrik çıkarımı / sağlık durumu saf fonksiyonları
* ``_sse_oku`` ve ``_db_kpi_oku`` ``(veri, hata)`` sözleşmesi; SQL ``text()``
* ``render_admin_realtime_tab`` üç yol: SSE var → kpi_karti ×4; SSE yok →
  hata_kutusu + DB yedeği; DB de yok → ikinci hata_kutusu.
"""
from __future__ import annotations

import json
from typing import Any

import pytest
import requests
from sqlalchemy.sql.elements import TextClause

from web_dashboard.tabs import admin_realtime as rt


# ---------------------------------------------------------------------------
# Saf fonksiyonlar
# ---------------------------------------------------------------------------

def test_sse_ayristir_ilk_data_satiri():
    govde = "event: kpi\ndata: {\"total\": 5}\n\ndata: {\"total\": 9}\n"
    assert rt._sse_ayristir(govde) == {"total": 5}


def test_sse_ayristir_bozuk_json_atlanir():
    govde = "data: {bozuk\ndata: {\"signals\": 3}\n"
    assert rt._sse_ayristir(govde) == {"signals": 3}


def test_sse_ayristir_data_yoksa_bos():
    assert rt._sse_ayristir("event: ping\n\n") == {}
    assert rt._sse_ayristir("data: [1,2]\n") == {}  # dict değil


@pytest.mark.parametrize(
    "sse, beklenen",
    [
        ({}, {"total": 0, "signals": 0, "api_calls": 0, "score": 100}),
        (
            {"total_firma": 12, "sinyal_toplam": 4, "api_cagri_toplam": 7, "saglik_skoru": 55},
            {"total": 12, "signals": 4, "api_calls": 7, "score": 55},
        ),
        (
            {"total": 1, "total_firma": 99, "quality_score": None, "saglik_skoru": 80},
            {"total": 1, "signals": 0, "api_calls": 0, "score": 80},
        ),
    ],
)
def test_sse_metrikleri_takma_adlar(sse, beklenen):
    assert rt._sse_metrikleri(sse) == beklenen


@pytest.mark.parametrize(
    "skor, beklenen",
    [(95, "🟢 Sağlıklı"), (90, "🟢 Sağlıklı"), (89.9, "🟠 Dikkat"), (None, "🟠 Dikkat"), ("x", "🟠 Dikkat")],
)
def test_saglik_durumu(skor, beklenen):
    assert rt._saglik_durumu(skor) == beklenen


# ---------------------------------------------------------------------------
# Kaynak okuyucular
# ---------------------------------------------------------------------------

class _Yanit:
    def __init__(self, text: str, hata: Exception | None = None):
        self.text = text
        self._hata = hata

    def raise_for_status(self):
        if self._hata:
            raise self._hata


def test_sse_oku_basari(monkeypatch):
    monkeypatch.setattr(rt.requests, "get", lambda url, timeout: _Yanit('data: {"total": 3}\n'))
    veri, hata = rt._sse_oku()
    assert veri == {"total": 3} and hata is None


def test_sse_oku_baglanti_hatasi_metin_doner(monkeypatch, caplog):
    def _patlat(url, timeout):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(rt.requests, "get", _patlat)
    with caplog.at_level("WARNING"):
        veri, hata = rt._sse_oku()
    assert veri == {}
    assert hata is not None and "ConnectionError" in hata and "refused" in hata
    assert "SSE okunamadı" in caplog.text


def test_sse_oku_http_hatasi(monkeypatch):
    monkeypatch.setattr(
        rt.requests, "get", lambda url, timeout: _Yanit("", requests.HTTPError("503"))
    )
    veri, hata = rt._sse_oku()
    assert veri == {} and "HTTPError" in hata


class _Row(dict):
    pass


class _Sonuc:
    def __init__(self, row):
        self._row = row

    def mappings(self):
        return self

    def first(self):
        return self._row


class _Conn:
    def __init__(self, row, kayit: list):
        self._row = row
        self._kayit = kayit

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, ifade):
        self._kayit.append(ifade)
        return _Sonuc(self._row)


class _Engine:
    def __init__(self, row, kayit):
        self._row, self._kayit = row, kayit

    def connect(self):
        return _Conn(self._row, self._kayit)


def test_db_kpi_oku_text_ile_sarili(monkeypatch):
    kayit: list = []
    monkeypatch.setattr(rt, "get_engine", lambda: _Engine(_Row(cnt=42), kayit))
    veri, hata = rt._db_kpi_oku()
    assert hata is None and veri["total"] == 42
    assert len(kayit) == 1 and isinstance(kayit[0], TextClause)
    assert "FROM companies" in str(kayit[0])


def test_db_kpi_oku_satir_yoksa_sifir(monkeypatch):
    monkeypatch.setattr(rt, "get_engine", lambda: _Engine(None, []))
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


# ---------------------------------------------------------------------------
# Render yolları
# ---------------------------------------------------------------------------

class _Col:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Spinner(_Col):
    pass


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
    monkeypatch.setattr(st, "spinner", lambda *a, **k: _Spinner())
    monkeypatch.setattr(st, "line_chart", lambda *a, **k: setattr(c, "line_chart", c.line_chart + 1))
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(rt.PageHeader, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(rt.SectionNav, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(rt.Section, "render", lambda self, *a, **k: "")
    monkeypatch.setattr(rt, "kpi_karti", lambda baslik, deger, **k: c.kpi.append({"baslik": baslik, "deger": deger, **k}))
    monkeypatch.setattr(rt, "hata_kutusu", lambda b, h, ipucu=None, **k: c.hata.append((b, h, ipucu)) or "")
    monkeypatch.setattr(rt, "bos_durum", lambda m, **k: c.bos.append(m) or "")
    return c


def test_render_sse_varsa_dort_kpi_karti(monkeypatch, cikti):
    sse = {"total": 1500, "signals": 20, "api_calls": 300, "quality_score": 97,
           "generated_at": "2026-09-17T05:00", "trend": {"t": [1, 2], "v": [3, 4]}}
    monkeypatch.setattr(rt, "load_sse_data", lambda: (sse, None))
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: pytest.fail("DB yedeği çağrılmamalı"))

    rt.render_admin_realtime_tab()

    basliklar = [k["baslik"] for k in cikti.kpi]
    assert basliklar == ["Toplam Firma", "Sinyal", "API Çağrı", "Sistem Sağlığı"]
    assert cikti.kpi[0]["deger"] == 1500
    assert cikti.kpi[3]["deger"] == "🟢 Sağlıklı"
    anahtarlar = {k["anahtar"] for k in cikti.kpi}
    assert len(anahtarlar) == 4  # widget anahtar çakışması yok
    assert cikti.line_chart == 1
    assert not cikti.hata and not cikti.bos
    assert any("Veri zamanı" in m for m in cikti.caption)


def test_render_sse_trend_yoksa_bos_durum(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_sse_data", lambda: ({"total": 1}, None))
    rt.render_admin_realtime_tab()
    assert cikti.line_chart == 0
    assert any("Trend" in m for m in cikti.bos)


def test_render_sse_hatasi_hata_kutusu_ve_db_yedegi(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_sse_data", lambda: ({}, "ConnectionError: refused"))
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: ({"total": 77}, None))

    rt.render_admin_realtime_tab()

    assert len(cikti.hata) == 1
    baslik, hata, ipucu = cikti.hata[0]
    assert "Canlı bağlantı" in baslik and "refused" in hata and "docker compose ps api" in ipucu
    assert [k["baslik"] for k in cikti.kpi] == ["DB Toplam Firma"]
    assert cikti.kpi[0]["deger"] == 77


def test_render_sse_ve_db_hatali_iki_hata_kutusu(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_sse_data", lambda: ({}, "ConnectionError: refused"))
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: ({"total": 0}, "OperationalError: no db"))

    rt.render_admin_realtime_tab()

    assert [h[0] for h in cikti.hata] == ["Canlı bağlantı kurulamadı", "Veritabanı yedeği okunamadı"]
    assert "DATABASE_URL" in cikti.hata[1][2]
    assert not cikti.kpi


def test_render_sse_bos_ve_db_bos_iki_bos_durum(monkeypatch, cikti):
    monkeypatch.setattr(rt, "load_sse_data", lambda: ({}, None))
    monkeypatch.setattr(rt, "load_kpi_from_db", lambda: ({"total": 0}, None))

    rt.render_admin_realtime_tab()

    assert not cikti.hata and not cikti.kpi
    assert len(cikti.bos) == 2


def test_modul_except_pass_icermez():
    """ADMIN-ROO-01 kuralı: sessiz yutma yok."""
    from pathlib import Path

    kaynak = Path(rt.__file__).read_text(encoding="utf-8")
    assert "except Exception:\n        pass" not in kaynak
    assert "st.metric(" not in kaynak
    assert "text(" in kaynak
