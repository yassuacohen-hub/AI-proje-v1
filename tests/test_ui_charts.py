# -*- coding: utf-8 -*-
"""CHART-01/KR-2 regresyon testleri: `company_master.ui.charts` modulu.

Kapsam:
  - Kaynak dosyanin kodlama sagligi (UTF-8, BOM yok, NUL yok, derlenebilir docstring)
    -> KR-2 sinifi bozulmalarin (kacisli triple-quote / UTF-16 / BOM) tekrarini yakalar
  - `__all__` sozlesmesi ve gercek docstring'ler
  - plotly figur ureten yardimcilarin davranisi (DataFrame ile dict/list girdi)

Gereksinim: plotly + pandas (requirements-app.txt). Yoksa fonksiyonel testler atlanir;
kodlama sagligi testi bagimsiz calisir.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pandas as pd
import pytest

KOK = Path(__file__).resolve().parents[1]
MODUL_DOSYASI = KOK / "src" / "company_master" / "ui" / "charts" / "__init__.py"
BEKLENEN_API = ("line_chart", "bar_chart", "pie_chart", "scatter_chart", "fig_to_json")


@pytest.fixture(scope="module")
def charts():
    """Modulu import eder (plotly/pandas yoksa testleri atlar)."""
    pytest.importorskip("plotly")
    pytest.importorskip("pandas")
    return importlib.import_module("company_master.ui.charts")


@pytest.fixture()
def veri() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "tarih": ["2026-01", "2026-02", "2026-03"],
            "deger": [10.0, 25.5, 18.0],
            "kanal": ["web", "web", "mobil"],
            "adet": [3, 5, 2],
        }
    )


# ------------------------------------------------------------------ kodlama guard

def test_kaynak_dosyasi_kodlama_sagligi() -> None:
    """Kaynak UTF-8 olmali; BOM, NUL ya da kacisli triple-quote icermemeli."""
    ham = MODUL_DOSYASI.read_bytes()

    assert MODUL_DOSYASI.is_file(), f"modul dosyasi yok: {MODUL_DOSYASI}"
    assert not ham.startswith(b"\xef\xbb\xbf"), "UTF-8 BOM bulundu"
    assert b"\x00" not in ham, "NUL bayti bulundu (UTF-16 kacagi)"

    # derlenebilirlik: SyntaxError -> test kirmizi
    compile(ham, str(MODUL_DOSYASI), "exec")

    metin = ham.decode("utf-8")
    assert '\\"\\"\\"' not in metin, "docstring kacisli yazilmis (\\\"\\\"\\\")"
    assert '"""' in metin, "gercek triple-quote docstring yok"


# ------------------------------------------------------------------ API sozlesmesi

def test_all_sozlesmesi(charts) -> None:
    """`__all__` beklenen yardimci kumesini birebir vermeli."""
    assert set(charts.__all__) == set(BEKLENEN_API)
    for ad in BEKLENEN_API:
        assert callable(getattr(charts, ad)), f"{ad} cagrilabilir degil"


def test_docstring_gercek(charts) -> None:
    """Modul ve fonksiyon docstring'leri gercek triple-quote ile yazilmis olmali."""
    assert charts.__doc__ and "Charts module" in charts.__doc__
    for ad in BEKLENEN_API:
        belge = getattr(charts, ad).__doc__ or ""
        assert belge.strip(), f"{ad} docstring bos"
        assert "Returns:" in belge, f"{ad} docstring'inde Returns bolumu yok"


# ------------------------------------------------------------------ figur uretimi

def test_line_chart_figur_uretir(charts, veri) -> None:
    fig = charts.line_chart(veri, x="tarih", y="deger", title="Trend")
    assert fig.data, "iz (trace) uretilmedi"
    assert len(fig.data) == 1
    assert fig.layout.title.text == "Trend"
    assert fig.layout.legend.title.text in (None, "")


def test_bar_chart_ve_pie_chart(charts, veri) -> None:
    bar = charts.bar_chart(veri, x="tarih", y="deger", orientation="v")
    assert bar.data
    pie = charts.pie_chart(veri, names="kanal", values="adet")
    assert pie.data


def test_scatter_chart_dict_girdi_kabul_eder(charts) -> None:
    """DataFrame olmayan girdi (dict) DataFrame'e cevrilerek kabul edilmeli."""
    fig = charts.scatter_chart({"x": [1, 2, 3], "y": [4, 5, 6]}, x="x", y="y")
    assert fig.data


def test_color_kolonu_ile_coklu_iz(charts, veri) -> None:
    fig = charts.line_chart(veri, x="tarih", y="deger", color="kanal")
    assert len(fig.data) == 2  # web + mobil ayri iz


def test_fig_to_json_serilestirilebilir(charts, veri) -> None:
    fig = charts.line_chart(veri, x="tarih", y="deger")
    ham = charts.fig_to_json(fig)
    assert isinstance(ham, dict) and "data" in ham
    json.dumps(ham)


def test_gecersiz_kolon_hata_verir(charts, veri) -> None:
    with pytest.raises(Exception):
        charts.line_chart(veri, x="yok_boyle_kolon", y="deger")
