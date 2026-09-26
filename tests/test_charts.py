# -*- coding: utf-8 -*-
"""UI-CHART-01: `web_dashboard.charts` birim testleri (Streamlit çalıştırılmadan).

Kapsam:
  - saf yardımcılar: sayi_formatla, delta_yonu, tema_normalize, tema_paleti, kategori_rengi
  - kpi_karti_html: XSS kaçışı, delta renk/ok, tema/kategori rengi, sabit px yok
  - plotly figürleri: sparkline/donut/alan yapısı + şeffaf arka plan (tema uyumu)
  - Streamlit sarmalayıcıları: MagicMock ile çağrı doğrulaması (fallback dahil)
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web_dashboard import charts  # noqa: E402
from web_dashboard.charts import (  # noqa: E402
    KATEGORI_RENK,
    alan_grafigi_fig,
    delta_yonu,
    donut_fig,
    kategori_rengi,
    kpi_karti_html,
    kpi_stil_css,
    sayi_formatla,
    sparkline_fig,
    tema_normalize,
    tema_paleti,
    veri_akisi_dot,
)

plotly = pytest.importorskip("plotly")


# ---------------------------------------------------------------------------
# KPI-EXA-01: sade kart CSS + süreç diyagramı (DOT)
# ---------------------------------------------------------------------------

def test_kpi_stil_css_sadece_cerceve_hover():
    css = kpi_stil_css("karanlik")
    assert ".hg-kpi:hover{border-color:" in css
    assert "box-shadow" not in css and "transform" not in css


def test_veri_akisi_dot_zincir_ve_tema():
    dot = veri_akisi_dot("karanlik")
    assert dot.startswith("digraph") and "rankdir=LR" in dot
    assert "kaynak -> etl -> db -> api -> panel;" in dot
    # KPI-EXA-02: kırık beyaz çerçeve, küçük düğüm, dolgu yok
    assert f'color="{charts.VERI_AKISI_CERCEVE}"' in dot and 'bgcolor="transparent"' in dot
    assert "penwidth=1" in dot and "fillcolor" not in dot
    assert "fontsize=9" in dot


def test_veri_akisi_dot_vurgu_marka_rengi():
    dot = veri_akisi_dot("karanlik", vurgu="db")
    marka = kategori_rengi("marka", "karanlik")
    assert f'db [label="VERİTABANI", color="{marka}"]' in dot
    assert f'api [label="API", color="{charts.VERI_AKISI_CERCEVE}"]' in dot


def test_veri_akisi_dugumler_buyuk_harf_ve_alt_satirsiz():
    for _, ad, alt in charts.VERI_AKISI_VARSAYILAN:
        assert ad == ad.upper() and alt == ""
    assert [ad for _, ad, _ in charts.VERI_AKISI_VARSAYILAN] == [
        "KAYNAK", "EŞLEŞTİRME", "VERİTABANI", "API", "DASHBOARD",
    ]


def test_veri_akisi_streamlit_fallback(sahte_st):
    sahte_st.graphviz_chart.side_effect = RuntimeError("graphviz yok")
    charts.veri_akisi()
    sahte_st.code.assert_called_once()
    assert "KAYNAK → EŞLEŞTİRME → VERİTABANI" in sahte_st.code.call_args.args[0]


def test_veri_akisi_streamlit_graphviz_cizer(sahte_st):
    charts.veri_akisi(vurgu="db")
    sahte_st.graphviz_chart.assert_called_once()
    assert "digraph" in sahte_st.graphviz_chart.call_args.args[0]
    sahte_st.code.assert_not_called()


# ---------------------------------------------------------------------------
# Saf yardımcılar
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "deger, ondalik, birim, beklenen",
    [
        (1234567, 0, "", "1.234.567"),
        (0, 0, "", "0"),
        (None, 0, "", "—"),
        ("", 0, "", "—"),
        ("🟢 Sağlıklı", 0, "", "🟢 Sağlıklı"),
        (87.456, 1, "%", "%87,5"),
        (12.3, 0, "ms", "12 ms"),
        (1234.5, 2, "", "1.234,50"),
    ],
)
def test_sayi_formatla_turkce_binlik_ve_birim(deger, ondalik, birim, beklenen):
    assert sayi_formatla(deger, ondalik, birim) == beklenen


@pytest.mark.parametrize(
    "delta, beklenen",
    [
        (5, "yukari"),
        (-2.5, "asagi"),
        (0, "duz"),
        (None, "duz"),
        ("", "duz"),
        ("+12 (24s)", "yukari"),
        ("-3%", "asagi"),
        ("7 adet", "yukari"),
        ("abc", "duz"),
    ],
)
def test_delta_yonu(delta, beklenen):
    assert delta_yonu(delta) == beklenen


@pytest.mark.parametrize(
    "girdi, beklenen",
    [("light", "aydinlik"), ("aydinlik", "aydinlik"), ("dark", "karanlik"), (None, "karanlik"), ("x", "karanlik")],
)
def test_tema_normalize(girdi, beklenen):
    assert tema_normalize(girdi) == beklenen


def test_tema_paleti_tokenlardan_gelir():
    karanlik = tema_paleti("karanlik")
    aydinlik = tema_paleti("light")
    assert karanlik["bg"] != aydinlik["bg"]
    assert karanlik["primary"] == aydinlik["primary"]  # marka rengi temadan bağımsız
    for anahtar in ("surface", "border", "text", "text-muted", "success-text", "danger-text"):
        assert anahtar in karanlik and anahtar in aydinlik


def test_kategori_rengi_eslesmesi():
    palet = tema_paleti("karanlik")
    for kategori, token_adi in KATEGORI_RENK.items():
        assert kategori_rengi(kategori) == palet[token_adi]
    assert kategori_rengi("bilinmeyen") == palet["primary"]


# ---------------------------------------------------------------------------
# KPI kartı HTML
# ---------------------------------------------------------------------------

def test_kpi_karti_html_xss_kacisi():
    html = kpi_karti_html("<script>x</script>", "<b>5</b>", delta="<i>+1</i>", yardim='a"b<c')
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<b>5</b>" not in html
    assert "<i>" not in html
    assert 'title="a&quot;b&lt;c"' in html


def test_kpi_karti_html_delta_renk_ve_ok():
    palet = tema_paleti("karanlik")
    yukari = kpi_karti_html("A", 10, delta=3)
    asagi = kpi_karti_html("A", 10, delta=-3)
    duz = kpi_karti_html("A", 10, delta="0")
    assert "▲ 3" in yukari and palet["success-text"] in yukari
    assert "▼ 3" in asagi and palet["danger-text"] in asagi
    assert "•" in duz and palet["text-muted"] in duz
    assert "hg-kpi-delta" not in kpi_karti_html("A", 10)  # delta yoksa satır yok


def test_kpi_karti_html_kategori_ve_tema():
    palet_k = tema_paleti("karanlik")
    palet_a = tema_paleti("aydinlik")
    musteri = kpi_karti_html("A", 1, kategori="musteri", tema="karanlik")
    sistem = kpi_karti_html("A", 1, kategori="sistem", tema="aydinlik")
    assert palet_k["metric-customer"] in musteri and palet_k["surface"] in musteri
    assert palet_a["metric-system"] in sistem and palet_a["surface"] in sistem
    # KPI-RENK-05 (KAHİN 2026-09-26; KPI-RENK-04'ü ezer): "bu kartın kenar
    # çizgileri kenar renkleri güzel, benzerlerini diğerlerine de yap" →
    # `_vurgu_paneli` reçetesi: nötr zemin + 1px nötr çerçeve + 3px kategori
    # renkli sol şerit. Gradient/gölge/renk **dolgusu** hâlâ yasak (gündüz
    # modunda patlıyordu); kategori rengi yalnız sol şerit ve 6px noktada.
    assert "linear-gradient" not in musteri and "box-shadow" not in musteri
    assert f"border-left:3px solid {palet_k['metric-customer']}" in musteri
    assert f"background:{palet_k['surface']}" in musteri
    assert f"border:1px solid {palet_k['border-strong']}" in musteri
    assert f"border:1px solid {palet_a['border-strong']}" in sistem
    # renk dolgusu yok: kategori rengi yalnız 2 yerde (sol şerit + nokta)
    assert musteri.count(palet_k["metric-customer"]) == 2
    assert "background:#fff" not in musteri.lower()  # beyaz zemin yok
    assert "1.234.567" in kpi_karti_html("A", 1234567)
    assert "—" in kpi_karti_html("A", None)


def test_kpi_karti_baslik_tek_satir_kalir():
    """K3-10f (KAHİN: "birbirlerine hizala"): uzun etiket sarmaz, kart boyu kaymaz."""
    html = kpi_karti_html("API Çağrıları (24 saat içinde)", 1234, yardim="tam ad ipuçta")
    assert "white-space:nowrap" in html
    assert "text-overflow:ellipsis" in html


def test_kpi_karti_html_sabit_genislik_yok():
    html = kpi_karti_html("A", 1, ikon="🏢")
    assert "width:" not in html.replace("min-width", "")  # responsive: sabit genişlik yok
    assert "🏢" in html


# ---------------------------------------------------------------------------
# Plotly figürleri
# ---------------------------------------------------------------------------

def _seffaf(fig) -> bool:
    return (
        fig.layout.paper_bgcolor == "rgba(0,0,0,0)"
        and fig.layout.plot_bgcolor == "rgba(0,0,0,0)"
    )


def test_sparkline_fig_eksensiz_ve_seffaf():
    fig = sparkline_fig([1, 3, 2, 5], kategori="musteri", yukseklik=56)
    assert len(fig.data) == 1
    assert fig.data[0].fill == "tozeroy"
    assert fig.layout.height == 56
    assert fig.layout.xaxis.visible is False and fig.layout.yaxis.visible is False
    assert _seffaf(fig)


def test_donut_fig_yapisi_ve_merkez_toplam():
    fig = donut_fig(["a", "b", "c"], [10, 20, 30], baslik="Dağılım", merkez_metin="kayıt")
    assert fig.data[0].type == "pie"
    assert fig.data[0].hole == pytest.approx(0.62)
    assert fig.layout.title.text == "Dağılım"
    metinler = [a.text for a in fig.layout.annotations]
    assert any("60" in m for m in metinler)  # toplam
    assert any("kayıt" in m for m in metinler)
    assert _seffaf(fig)


def test_donut_fig_renkler_temadan():
    fig = donut_fig(["a", "b"], [1, 2], tema="aydinlik")
    palet = tema_paleti("aydinlik")
    renkler = list(fig.data[0].marker.colors)
    assert renkler[0] == palet["primary"]


def test_alan_grafigi_fig_yapisi():
    fig = alan_grafigi_fig(["2026-01-01", "2026-01-02"], [1, 4], baslik="Trend", kategori="basari",
                           yukseklik=300, x_etiket="Tarih", y_etiket="Skor")
    assert fig.data[0].fill == "tozeroy"
    assert fig.layout.height == 300
    assert fig.layout.title.text == "Trend"
    assert fig.layout.xaxis.title.text == "Tarih"
    assert fig.layout.yaxis.title.text == "Skor"
    assert _seffaf(fig)


# ---------------------------------------------------------------------------
# Streamlit sarmalayıcıları (mock)
# ---------------------------------------------------------------------------

@pytest.fixture()
def sahte_st(monkeypatch):
    st = MagicMock()
    st.get_option.return_value = "dark"
    monkeypatch.setitem(sys.modules, "streamlit", st)
    return st


def test_aktif_tema_streamlit_ayarindan(sahte_st):
    # MagicMock context.theme.type str değil → get_option'a düşer
    sahte_st.get_option.return_value = "light"
    assert charts.aktif_tema() == "aydinlik"
    sahte_st.get_option.side_effect = RuntimeError("yok")
    assert charts.aktif_tema() == "karanlik"


def test_aktif_tema_context_oncelikli(sahte_st):
    # KPI-EXA-02: tarayıcının etkin teması (st.context.theme.type) ayarın önünde
    sahte_st.get_option.return_value = "dark"
    sahte_st.context.theme.type = "light"
    assert charts.aktif_tema() == "aydinlik"
    sahte_st.context.theme.type = ""
    assert charts.aktif_tema() == "karanlik"


def test_kpi_karti_markdown_ve_sparkline(sahte_st):
    charts.kpi_karti("Toplam", 1200, delta="+5 (24s)", sparkline=[1, 2, 3], aciklama="📊 not")
    sahte_st.markdown.assert_called_once()
    html, = sahte_st.markdown.call_args.args
    assert sahte_st.markdown.call_args.kwargs.get("unsafe_allow_html") is True
    assert "1.200" in html and "▲ +5 (24s)" in html
    sahte_st.plotly_chart.assert_called_once()
    assert sahte_st.plotly_chart.call_args.kwargs["key"] == "spark-Toplam"
    assert sahte_st.plotly_chart.call_args.kwargs["config"]["staticPlot"] is True
    sahte_st.caption.assert_called_once_with("📊 not")


def test_kpi_karti_sparkline_yoksa_grafik_cizmez(sahte_st):
    charts.kpi_karti("Tek", 1, sparkline=[1])
    sahte_st.plotly_chart.assert_not_called()
    sahte_st.area_chart.assert_not_called()


def test_kpi_karti_ozel_anahtar(sahte_st):
    charts.kpi_karti("Aynı", 1, sparkline=[1, 2], anahtar="spark-ozel")
    assert sahte_st.plotly_chart.call_args.kwargs["key"] == "spark-ozel"


def test_donut_bos_df_info(sahte_st):
    charts.donut(pd.DataFrame({"d": [], "a": []}), "d", "a")
    sahte_st.info.assert_called_once()
    sahte_st.plotly_chart.assert_not_called()


def test_donut_ve_alan_grafigi_plotly_cizer(sahte_st):
    df = pd.DataFrame({"Durum": ["Başarılı", "Hatalı"], "Adet": [8, 2]})
    charts.donut(df, "Durum", "Adet", baslik="Webhook")
    trend = pd.DataFrame({"tarih": ["2026-01-01", "2026-01-02"], "istek": [3, 7]})
    charts.alan_grafigi(trend, "tarih", "istek", baslik="API")
    assert sahte_st.plotly_chart.call_count == 2
    for cagri in sahte_st.plotly_chart.call_args_list:
        assert cagri.kwargs.get("width") == "stretch"


def test_plotly_yokken_fallback(sahte_st, monkeypatch):
    monkeypatch.setattr(charts, "go", None)
    df = pd.DataFrame({"Durum": ["a", "b"], "Adet": [1, 2]})
    charts.donut(df, "Durum", "Adet")
    trend = pd.DataFrame({"t": [1, 2], "y": [3, 4]})
    charts.alan_grafigi(trend, "t", "y")
    charts.kpi_karti("K", 1, sparkline=[1, 2])
    sahte_st.plotly_chart.assert_not_called()
    sahte_st.bar_chart.assert_called_once()
    assert sahte_st.area_chart.call_count == 2  # alan_grafigi + sparkline fallback
