# -*- coding: utf-8 -*-
"""UI-CHART-01: Muninn admin paneli için modern KPI kartı ve grafik yardımcıları.

Tasarım ilkeleri:
  - Renkler `company_master.ui.tokens` jetonlarından gelir (ham hex yok, SSOT).
  - Tema `st.get_option("theme.base")` üzerinden okunur; plotly figürleri şeffaf
    arka planla çizilir, böylece koyu/açık temada bozulmaz.
  - Streamlit'siz test edilebilir çekirdek (`*_fig`, `kpi_karti_html`,
    `sayi_formatla`, `delta_yonu`, `tema_paleti`) + ince `st.*` sarmalayıcılar.
  - Plotly yoksa (`ImportError`) `st.metric` / `st.bar_chart` / `st.area_chart`
    fallback devreye girer.
  - Sabit piksel genişliği yok; yalnız yükseklik sabittir (responsive).

Kullanım (Streamlit içinde)::

    from web_dashboard.charts import kpi_karti, donut, alan_grafigi
    kpi_karti("Toplam Firma", 12_430, delta=+120, sparkline=[..], kategori="musteri")
"""
from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parent.parent
_SRC = ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from company_master.ui.tokens import RENKLER, RENKLER_AYDINLIK  # noqa: E402

try:  # plotly opsiyonel; yoksa fallback çalışır
    import plotly.graph_objects as go
except ImportError:  # pragma: no cover - CI'da plotly kurulu
    go = None  # type: ignore[assignment]

#: Kart kategorisi → token anahtarı (DASH-UX-01: mavi müşteri / turuncu sistem).
KATEGORI_RENK: dict[str, str] = {
    "musteri": "metric-customer",
    "sistem": "metric-system",
    "marka": "primary",
    "basari": "success",
    "uyari": "warning",
    "tehlike": "danger",
    "bilgi": "info",
}

_SEFFAF = "rgba(0,0,0,0)"


# ---------------------------------------------------------------------------
# Streamlit'siz saf yardımcılar
# ---------------------------------------------------------------------------

def sayi_formatla(deger: Any, ondalik: int = 0, birim: str = "") -> str:
    """Sayıyı Türkçe binlik ayracıyla biçimler; ``None``/boş → ``"—"``.

    >>> sayi_formatla(1234567)
    '1.234.567'
    >>> sayi_formatla(87.4, ondalik=1, birim="%")
    '%87,4'
    """
    if deger is None or deger == "":
        return "—"
    if isinstance(deger, str):
        return deger
    try:
        sayi = float(deger)
    except (TypeError, ValueError):
        return str(deger)
    if birim == "%":
        return f"%{sayi:,.{ondalik}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    metin = f"{sayi:,.{ondalik}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return f"{metin} {birim}".strip() if birim else metin


def delta_yonu(delta: Any) -> str:
    """Delta değerinin yönünü döndürür: ``yukari`` / ``asagi`` / ``duz``.

    Metin girdisi (``"+12 (24s)"``, ``"-3%"``) de desteklenir; ilk işaret bakılır.
    """
    if delta is None or delta == "":
        return "duz"
    if isinstance(delta, (int, float)):
        if delta > 0:
            return "yukari"
        if delta < 0:
            return "asagi"
        return "duz"
    metin = str(delta).strip()
    if metin.startswith("-"):
        return "asagi"
    if metin.startswith("+"):
        return "yukari"
    try:
        sayi = float(metin.split()[0].rstrip("%"))
    except (ValueError, IndexError):
        return "duz"
    return "yukari" if sayi > 0 else "asagi" if sayi < 0 else "duz"


def tema_normalize(tema: str | None) -> str:
    """Streamlit tema adını (``dark``/``light``) proje adına çevirir."""
    if tema in ("light", "aydinlik"):
        return "aydinlik"
    return "karanlik"


def tema_paleti(tema: str | None = "karanlik") -> dict[str, str]:
    """Tema için renk paleti (token sözlüğü üzerinden)."""
    renkler = dict(RENKLER)
    if tema_normalize(tema) == "aydinlik":
        renkler.update(RENKLER_AYDINLIK)
    return renkler


def kategori_rengi(kategori: str, tema: str | None = "karanlik") -> str:
    """Kategori adını (``musteri``, ``sistem`` …) hex renge çevirir."""
    palet = tema_paleti(tema)
    anahtar = KATEGORI_RENK.get(kategori, "primary")
    return palet.get(anahtar, palet["primary"])


def _hex_rgba(hex_renk: str, alfa: float) -> str:
    """``#rrggbb`` → ``rgba(r,g,b,alfa)``; hex değilse olduğu gibi döner."""
    h = hex_renk.lstrip("#")
    if len(h) != 6:
        return hex_renk
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alfa})"


def kpi_stil_css(tema: str | None = "karanlik") -> str:
    """KPI-EXA-01: Kart hover/odak stili — sayfada bir kez basılır (Exa tarzı: yalnız çerçeve koyulaşır)."""
    palet = tema_paleti(tema)
    return (
        "<style>"
        f".hg-kpi{{transition:border-color .15s ease}}"
        f".hg-kpi:hover{{border-color:{palet['text-muted']}}}"
        "</style>"
    )


def kpi_karti_html(
    baslik: str,
    deger: Any,
    delta: Any = None,
    ikon: str = "",
    kategori: str = "marka",
    tema: str | None = "karanlik",
    yardim: str | None = None,
    ondalik: int = 0,
    birim: str = "",
    donem: str | None = None,
    esik: tuple[float, float] | None = None,
    cta: tuple[str, str] | None = None,
    karsilastirma_serisi: Sequence[float] | None = None,
) -> str:
    """Sade (Claude Console / 9Router) KPI kartı HTML'i — Streamlit'siz, XSS güvenli.

    KPI-EXA-01/02 + KPI-RENK-04 (KAHİN, 2026-09-26: "kartların arka plan renklerini
    kaldır ... göz yoruyor, kurumsal değil, gündüz modunda hepsi patlar"):
    zemin **nötr tema yüzeyi**, çerçeve **nötr** 1px, gradient/gölge/renk dolgusu
    **yok**. Kategori rengi yalnızca etiket önündeki 6px noktada görünür; sayı nötr
    metin rengindedir. Böylece aydınlık/karanlık temada aynı kontrast korunur.

    Yeni parametreler (Faz B):
    - donem: "son 24 sa" gibi dönem etiketi; delta'nın yanında "önceki döneme göre" anlamı.
    - esik: (sari, kirmizi); değer eşiği aşınca kart kenarlığı + nokta rengi değişir.
    - cta: (etiket, session_state_anahtari); tıklanınca anahtar True yapılır.
    - karsilastirma_serisi: ikinci (önceki dönem) seri; sparkline iki çizgi.
    """
    palet = tema_paleti(tema)
    renk = kategori_rengi(kategori, tema)
    yon = delta_yonu(delta)
    ok = {"yukari": "▲", "asagi": "▼", "duz": "•"}[yon]
    delta_renk = {
        "yukari": palet["success-text"],
        "asagi": palet["danger-text"],
        "duz": palet["text-muted"],
    }[yon]
    delta_html = ""
    if delta is not None and delta != "":
        delta_metin = delta if isinstance(delta, str) else sayi_formatla(abs(delta), ondalik)
        donem_ek = f" (önceki döneme göre)" if donem else ""
        delta_html = (
            f'<div class="hg-kpi-delta" style="color:{delta_renk};font-size:0.8rem;'
            f'margin-top:6px;font-variant-numeric:tabular-nums;">'
            f"{ok} {html.escape(str(delta_metin))}{donem_ek}</div>"
        )
    yardim_attr = f' title="{html.escape(yardim)}"' if yardim else ""
    deger_metin = html.escape(sayi_formatla(deger, ondalik, birim))
    ikon_html = f"<span style=\"opacity:.85;margin-right:4px;\">{html.escape(ikon)}</span>" if ikon else ""

    # Eşik rengi hesapla
    kenar_renk = palet["border-strong"]
    nokta_renk = renk
    if esik is not None and isinstance(deger, (int, float)):
        sari, kirmizi = esik
        if deger >= kirmizi:
            kenar_renk = palet["danger"]
            nokta_renk = palet["danger"]
        elif deger >= sari:
            kenar_renk = palet["warning"]
            nokta_renk = palet["warning"]

    donem_html = f'<span style="color:{palet["text-muted"]};font-size:0.65rem;margin-left:8px;">{html.escape(donem)}</span>' if donem else ""

    return (
        f'<div class="hg-kpi" {yardim_attr} style="'
        f"background:{palet['surface']};"
        f"border:1px solid {kenar_renk};border-left:3px solid {nokta_renk};"
        f"border-radius:10px;"
        f'padding:14px 16px;min-height:92px;">'
        f'<div class="hg-kpi-baslik" style="display:flex;align-items:center;gap:6px;'
        f'color:{palet["text-muted"]};font-size:0.72rem;font-weight:500;'
        f'letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;'
        f'overflow:hidden;text-overflow:ellipsis;">'
        f'<span style="flex:0 0 6px;height:6px;border-radius:50%;background:{nokta_renk};"></span>'
        f"{ikon_html}{html.escape(baslik)}{donem_html}</div>"
        f'<div class="hg-kpi-deger" style="color:{palet["text"]};font-size:1.65rem;'
        f'font-weight:700;line-height:1.25;margin-top:6px;letter-spacing:-.01em;'
        f'font-variant-numeric:tabular-nums;">{deger_metin}</div>'
        f"{delta_html}</div>"
    )


# ---------------------------------------------------------------------------
# Süreç / veri akışı diyagramı (Graphviz DOT, Streamlit'siz)
# ---------------------------------------------------------------------------

# KPI-EXA-02 (sahip): düğümler kısa BÜYÜK HARF, alt satır yok; diyagram teknik sayfada.
VERI_AKISI_VARSAYILAN: tuple[tuple[str, str, str], ...] = (
    ("kaynak", "KAYNAK", ""),
    ("etl", "EŞLEŞTİRME", ""),
    ("db", "VERİTABANI", ""),
    ("api", "API", ""),
    ("panel", "DASHBOARD", ""),
)

#: Diyagram çerçevesi: hafif kırık beyaz (sahip talebi, temadan bağımsız).
VERI_AKISI_CERCEVE = "#E6E6E6"


def veri_akisi_dot(
    tema: str | None = "karanlik",
    dugumler: tuple[tuple[str, str, str], ...] = VERI_AKISI_VARSAYILAN,
    vurgu: str | None = None,
) -> str:
    """KPI-EXA-01/02: Sade süreç diyagramı (KAYNAK → EŞLEŞTİRME → VERİTABANI → API → DASHBOARD).

    Exa/developer tarzı: 1px **kırık beyaz** çerçeve, dolgu yok, gölge yok, küçük
    düğümler; yalnız ``vurgu`` düğümünün çerçevesi marka rengiyle çizilir.
    Graphviz DOT metni döner.
    """
    palet = tema_paleti(tema)
    marka = kategori_rengi("marka", tema)
    satirlar = [
        "digraph veri_akisi {",
        "rankdir=LR; bgcolor=\"transparent\"; nodesep=0.25; ranksep=0.4; pad=0.05;",
        f'node [shape=box, style="rounded", penwidth=1, color="{VERI_AKISI_CERCEVE}",'
        f' fontcolor="{palet["text"]}", fontname="Inter,Segoe UI,Arial", fontsize=9, margin="0.12,0.06"];',
        f'edge [color="{palet["text-muted"]}", penwidth=1, arrowsize=0.5];',
    ]
    for kimlik, ad, alt in dugumler:
        renk = marka if kimlik == vurgu else VERI_AKISI_CERCEVE
        etiket = html.escape(ad) + (f"\\n{html.escape(alt)}" if alt else "")
        satirlar.append(f'{kimlik} [label="{etiket}", color="{renk}"];')
    zincir = " -> ".join(k for k, _, _ in dugumler)
    satirlar.append(f"{zincir};")
    satirlar.append("}")
    return "\n".join(satirlar)


# ---------------------------------------------------------------------------
# Plotly figür üreticileri (Streamlit'siz)
# ---------------------------------------------------------------------------

def _plotly_gerekli() -> None:
    if go is None:
        raise ImportError("plotly kurulu değil")


def _seffaf_layout(fig: "go.Figure", palet: dict[str, str], yukseklik: int, baslik: str | None = None) -> "go.Figure":
    fig.update_layout(
        paper_bgcolor=_SEFFAF,
        plot_bgcolor=_SEFFAF,
        font=dict(color=palet["text"], family="Inter, system-ui, sans-serif"),
        height=yukseklik,
        margin=dict(t=44 if baslik else 8, b=8, l=8, r=8),
        title=dict(text=baslik, x=0.01, font=dict(size=15)) if baslik else None,
        hoverlabel=dict(bgcolor=palet["surface-2"], font_color=palet["text"], bordercolor=palet["border"]),
        legend=dict(bgcolor=_SEFFAF, orientation="h", y=-0.12),
    )
    fig.update_xaxes(gridcolor=palet["border"], zerolinecolor=palet["border"], linecolor=palet["border"])
    fig.update_yaxes(gridcolor=palet["border"], zerolinecolor=palet["border"], linecolor=palet["border"])
    return fig


def sparkline_fig(
    degerler: Sequence[float],
    kategori: str = "marka",
    tema: str | None = "karanlik",
    yukseklik: int = 56,
) -> "go.Figure":
    """Eksensiz mini alan grafiği (kart altı sparkline)."""
    _plotly_gerekli()
    palet = tema_paleti(tema)
    renk = kategori_rengi(kategori, tema)
    y = [float(v) for v in degerler]
    fig = go.Figure(
        go.Scatter(
            x=list(range(len(y))),
            y=y,
            mode="lines",
            line=dict(color=renk, width=2, shape="spline"),
            fill="tozeroy",
            fillcolor=_hex_rgba(renk, 0.18),
            hovertemplate="%{y}<extra></extra>",
        )
    )
    fig.update_layout(
        paper_bgcolor=_SEFFAF,
        plot_bgcolor=_SEFFAF,
        height=yukseklik,
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=False,
        hoverlabel=dict(bgcolor=palet["surface-2"], font_color=palet["text"]),
    )
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig


def donut_fig(
    etiketler: Sequence[str],
    degerler: Sequence[float],
    baslik: str | None = None,
    tema: str | None = "karanlik",
    yukseklik: int = 280,
    merkez_metin: str | None = None,
    renkler: Sequence[str] | None = None,
) -> "go.Figure":
    """Merkezinde toplam yazan donut grafik."""
    _plotly_gerekli()
    palet = tema_paleti(tema)
    if renkler is None:
        renkler = [
            palet["primary"], palet["info"], palet["success"],
            palet["warning"], palet["danger"], palet["metric-system"],
        ]
    toplam = sum(float(v) for v in degerler)
    fig = go.Figure(
        go.Pie(
            labels=list(etiketler),
            values=list(degerler),
            hole=0.62,
            marker=dict(colors=list(renkler), line=dict(color=palet["surface"], width=2)),
            textinfo="percent",
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
            sort=False,
        )
    )
    # Merkez: toplam (büyük) + isteğe bağlı alt etiket (küçük, ör. "kayıt"/"olay").
    merkez = f"<b>{sayi_formatla(toplam)}</b>"
    if merkez_metin:
        merkez += (
            f"<br><span style='font-size:12px;color:{palet['text-muted']}'>"
            f"{html.escape(str(merkez_metin))}</span>"
        )
    fig.add_annotation(
        text=merkez,
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22, color=palet["text"]),
    )
    return _seffaf_layout(fig, palet, yukseklik, baslik)


def alan_grafigi_fig(
    x: Sequence[Any],
    y: Sequence[float],
    baslik: str | None = None,
    kategori: str = "marka",
    tema: str | None = "karanlik",
    yukseklik: int = 280,
    x_etiket: str = "",
    y_etiket: str = "",
) -> "go.Figure":
    """Spline çizgili, dolgulu alan grafiği (trend)."""
    _plotly_gerekli()
    palet = tema_paleti(tema)
    renk = kategori_rengi(kategori, tema)
    fig = go.Figure(
        go.Scatter(
            x=list(x),
            y=[float(v) for v in y],
            mode="lines+markers",
            line=dict(color=renk, width=2.5, shape="spline"),
            marker=dict(size=6, color=renk),
            fill="tozeroy",
            fillcolor=_hex_rgba(renk, 0.16),
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    )
    fig.update_layout(showlegend=False, xaxis_title=x_etiket or None, yaxis_title=y_etiket or None)
    return _seffaf_layout(fig, palet, yukseklik, baslik)


# ---------------------------------------------------------------------------
# Streamlit sarmalayıcıları
# ---------------------------------------------------------------------------

def aktif_tema() -> str:
    """Streamlit'in **etkin** temasını proje tema adına çevirir.

    KPI-EXA-02: önce ``st.context.theme.type`` (kullanıcının tarayıcıda gerçekten
    gördüğü tema; 1.62+), yoksa ``theme.base`` ayarı. Böylece ``app.aktif_tema()``
    ile aynı kaynağı kullanır; kart zemini/kontur tema ile uyumsuz kalmaz.
    """
    try:
        import streamlit as st
        try:
            tip = st.context.theme.type
        except Exception:  # noqa: BLE001 - eski sürüm / test sahtesi
            tip = None
        if isinstance(tip, str) and tip.strip():
            return tema_normalize(tip)
        return tema_normalize(st.get_option("theme.base"))
    except Exception:  # noqa: BLE001 - Streamlit dışı çağrı
        return "karanlik"


def kpi_karti(
    baslik: str,
    deger: Any,
    delta: Any = None,
    sparkline: Iterable[float] | None = None,
    ikon: str = "",
    kategori: str = "marka",
    yardim: str | None = None,
    ondalik: int = 0,
    birim: str = "",
    aciklama: str | None = None,
    anahtar: str | None = None,
    donem: str | None = None,
    esik: tuple[float, float] | None = None,
    cta: tuple[str, str] | None = None,
    karsilastirma_serisi: Sequence[float] | None = None,
) -> None:
    """Sade KPI kartı + isteğe bağlı sparkline çizer (Streamlit).

    ``anahtar``: aynı sayfada aynı başlık iki kez kullanılırsa sparkline
    widget anahtarı çakışmasın diye verilir (varsayılan: ``spark-{baslik}``).

    Yeni parametreler (Faz B):
    - donem: dönem etiketi (örn. "son 24 sa")
    - esik: (sari, kirmizi) eşik değerleri
    - cta: (etiket, session_state_anahtarı) call-to-action
    - karsilastirma_serisi: önceki dönem seri (sparkline iki çizgi için)
    """
    import streamlit as st

    tema = aktif_tema()
    if not st.session_state.get("_hg_kpi_css"):
        st.markdown(kpi_stil_css(tema), unsafe_allow_html=True)
        st.session_state["_hg_kpi_css"] = True
    st.markdown(
        kpi_karti_html(baslik, deger, delta, ikon, kategori, tema, yardim, ondalik, birim, donem, esik, cta, karsilastirma_serisi),
        unsafe_allow_html=True,
    )
    seri = list(sparkline) if sparkline is not None else []
    if len(seri) >= 2:
        try:
            st.plotly_chart(
                sparkline_fig(seri, kategori, tema),
                width="stretch",
                config={"displayModeBar": False, "staticPlot": True},
                key=anahtar or f"spark-{baslik}",
            )
        except ImportError:
            st.area_chart(seri, height=56, width="stretch")
    if aciklama:
        st.caption(aciklama)


def donut(
    df: Any,
    etiket_kolonu: str,
    deger_kolonu: str,
    baslik: str | None = None,
    merkez_metin: str | None = None,
    yukseklik: int = 280,
) -> None:
    """DataFrame'den donut grafiği çizer; plotly yoksa ``st.bar_chart``."""
    import streamlit as st

    if df is None or len(df) == 0:
        st.info("Grafik için veri yok.")
        return
    try:
        fig = donut_fig(
            list(df[etiket_kolonu]), list(df[deger_kolonu]),
            baslik=baslik, tema=aktif_tema(), yukseklik=yukseklik, merkez_metin=merkez_metin,
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except ImportError:
        st.bar_chart(df.set_index(etiket_kolonu)[deger_kolonu], width="stretch")


def alan_grafigi(
    df: Any,
    x: str,
    y: str,
    baslik: str | None = None,
    kategori: str = "marka",
    yukseklik: int = 280,
    x_etiket: str = "",
    y_etiket: str = "",
) -> None:
    """DataFrame'den alan/trend grafiği çizer; plotly yoksa ``st.area_chart``."""
    import streamlit as st

    if df is None or len(df) == 0:
        st.info("Grafik için veri yok.")
        return
    try:
        fig = alan_grafigi_fig(
            list(df[x]), list(df[y]), baslik=baslik, kategori=kategori,
            tema=aktif_tema(), yukseklik=yukseklik, x_etiket=x_etiket, y_etiket=y_etiket,
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except ImportError:
        st.area_chart(df.set_index(x)[y], width="stretch")


def veri_akisi(vurgu: str | None = None, dugumler=VERI_AKISI_VARSAYILAN) -> None:
    """Süreç diyagramını çizer (``st.graphviz_chart``); graphviz yoksa metin zinciri."""
    import streamlit as st

    try:
        st.graphviz_chart(veri_akisi_dot(aktif_tema(), dugumler, vurgu), width="stretch")
    except Exception:  # noqa: BLE001 — graphviz eksik/uyumsuz sürüm
        st.code(" → ".join(ad for _, ad, _ in dugumler), language=None)


__all__ = [
    "VERI_AKISI_VARSAYILAN",
    "veri_akisi_dot",
    "veri_akisi",
    "kpi_stil_css",
    "KATEGORI_RENK",
    "sayi_formatla",
    "delta_yonu",
    "tema_normalize",
    "tema_paleti",
    "kategori_rengi",
    "kpi_karti_html",
    "sparkline_fig",
    "donut_fig",
    "alan_grafigi_fig",
    "aktif_tema",
    "kpi_karti",
    "donut",
    "alan_grafigi",
    # ECharts opts (Faz B)
    "_echarts_taban",
    "kart_sparkline_opts",
    "gosterge_opts",
    "cizgi_opts",
    "yatay_bar_opts",
    "huni_opts",
    "ic_ice_pasta_opts",
    "treemap_opts",
    "agac_opts",
    "sankey_opts",
    "matris_sparkline_opts",
]
