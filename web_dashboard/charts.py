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
) -> str:
    """Gradient KPI kartının HTML'ini üretir (Streamlit'siz, XSS güvenli)."""
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
        delta_html = (
            f'<div class="hg-kpi-delta" style="color:{delta_renk}">'
            f"{ok} {html.escape(str(delta_metin))}</div>"
        )
    yardim_attr = f' title="{html.escape(yardim)}"' if yardim else ""
    deger_metin = html.escape(sayi_formatla(deger, ondalik, birim))
    return (
        f'<div class="hg-kpi" {yardim_attr} style="'
        f"background:linear-gradient(135deg,{_hex_rgba(renk, 0.22)} 0%,{palet['surface']} 65%);"
        f"border:1px solid {palet['border']};border-left:4px solid {renk};"
        f"border-radius:14px;padding:14px 16px 10px 16px;min-height:96px;"
        f"box-shadow:0 4px 14px {_hex_rgba(renk, 0.12)};\">"
        f'<div class="hg-kpi-baslik" style="color:{palet["text-muted"]};font-size:0.78rem;'
        f'letter-spacing:.04em;text-transform:uppercase;">{html.escape(ikon)} {html.escape(baslik)}</div>'
        f'<div class="hg-kpi-deger" style="color:{palet["text"]};font-size:1.7rem;'
        f'font-weight:700;line-height:1.2;margin-top:4px;">{deger_metin}</div>'
        f"{delta_html}</div>"
    )


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
    """Streamlit'in kendi tema ayarını proje tema adına çevirir."""
    try:
        import streamlit as st
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
) -> None:
    """Gradient KPI kartı + isteğe bağlı sparkline çizer (Streamlit).

    ``anahtar``: aynı sayfada aynı başlık iki kez kullanılırsa sparkline
    widget anahtarı çakışmasın diye verilir (varsayılan: ``spark-{baslik}``).
    """
    import streamlit as st

    tema = aktif_tema()
    st.markdown(
        kpi_karti_html(baslik, deger, delta, ikon, kategori, tema, yardim, ondalik, birim),
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


__all__ = [
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
]
