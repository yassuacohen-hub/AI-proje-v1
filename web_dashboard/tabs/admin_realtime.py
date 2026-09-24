# -*- coding: utf-8 -*-
"""P7-45: Canli Veri Akisi Admin Sekmesi (polling).

Kullanim: streamlit run app.py -> Sistem sekmesi

UI-ADMIN-SSE-IHLAL-03 (KK-1 karari, 2026-09-24):
  SSE okuyucu **kaldirildi**. Mimari demir kural (ADR satir 81 /
  V9 §16.4 kural 4): "SSE yalnizca musteri panelinde kullanilir; admin
  paneli polling ile calisir." Veri artik dogrudan DB'den okunur; periyodik
  tazeleme ``admin_auto_refresh.render_auto_refresh()`` ile yapilir.
  Musteri panelindeki SSE (P7-19b, FastAPI) etkilenmedi.

ADMIN-UI-10:
  Sayfa iskeleti ``PageHeader`` -> ``SectionNav`` -> ``Section``.

ADMIN-ROO-01 (Asama B):
  Ham SQL ``sqlalchemy.text()`` ile sarili; sessiz ``except: pass`` yok;
  KPI tek dil (``kpi_karti``).
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import _load_env, get_engine  # noqa: E402
from company_master.ui import (  # noqa: E402
    PageHeader,
    Section,
    SectionNav,
    bos_durum,
    hata_kutusu,
)
from web_dashboard.charts import kpi_karti  # noqa: E402  (ADMIN-ROO-01)
from web_dashboard.tabs.admin_auto_refresh import render_auto_refresh  # noqa: E402

_load_env()

log = logging.getLogger(__name__)

CACHE_TTL = 5
SAGLIK_ESIK = 90

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section(
        "Canlı Metrikler",
        "Firma, sinyal ve veri kalitesi anlık değerleri.",
        ikon="📊",
        kimlik="canli-metrikler",
    ),
    Section(
        "Son 24 Saat Trend",
        "Saatlik sinyal akışı.",
        ikon="📈",
        kimlik="trend-24s",
    ),
)

GIRIS_METNI = (
    "Sistemin anlık nabzı. Veriler veritabanından "
    f"{CACHE_TTL} saniyelik önbellekle okunur; periyodik tazeleme için "
    "aşağıdaki otomatik yenileme kontrolünü kullanın (polling — admin "
    "panelinde SSE kullanılmaz)."
)

DB_IPUCU = "DATABASE_URL `.env` içinde doğru mu? `docker compose ps` ile servisi kontrol edin."

_KPI_SQL = text(
    """
    SELECT
        (SELECT COUNT(*) FROM companies) AS total,
        (SELECT COUNT(*) FROM company_signals) AS signals,
        (SELECT COALESCE(ROUND(AVG(data_quality_score)), 0) FROM companies) AS score
    """
)

_TREND_SQL = text(
    """
    SELECT date_trunc('hour', detected_at) AS saat, COUNT(*) AS sinyal
    FROM company_signals
    WHERE detected_at >= NOW() - INTERVAL '24 hours'
    GROUP BY 1
    ORDER BY 1
    """
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


# ---------------------------------------------------------------------------
# Saf yardımcılar (Streamlit'siz, test edilebilir)
# ---------------------------------------------------------------------------

def _saglik_durumu(skor: Any, esik: int = SAGLIK_ESIK) -> str:
    """Skoru insan diline çevirir: ``🟢 Sağlıklı`` / ``🟠 Dikkat``."""
    try:
        return "🟢 Sağlıklı" if float(skor) >= esik else "🟠 Dikkat"
    except (TypeError, ValueError):
        return "🟠 Dikkat"


def _db_kpi_oku() -> tuple[dict[str, Any], str | None]:
    """DB'den KPI okur → ``(veri, hata)``; SQL ``text()`` ile sarılıdır."""
    sonuc: dict[str, Any] = {"total": 0, "signals": 0, "score": 0}
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(_KPI_SQL).mappings().first()
    except Exception as exc:  # noqa: BLE001 - sürücü/bağlantı hataları çeşitli
        log.warning("DB KPI okunamadı: %s", exc)
        return sonuc, f"{type(exc).__name__}: {exc}"
    if row:
        sonuc.update({k: row[k] or 0 for k in ("total", "signals", "score")})
    return sonuc, None


def _db_trend_oku() -> tuple[pd.DataFrame, str | None]:
    """Son 24 saatin saatlik sinyal sayısı → ``(df, hata)``."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            satirlar = [dict(r) for r in conn.execute(_TREND_SQL).mappings()]
    except Exception as exc:  # noqa: BLE001
        log.warning("DB trend okunamadı: %s", exc)
        return pd.DataFrame(), f"{type(exc).__name__}: {exc}"
    return pd.DataFrame(satirlar), None


# ---------------------------------------------------------------------------
# Önbellekli sarmalayıcılar
# ---------------------------------------------------------------------------

@st.cache_data(ttl=CACHE_TTL)
def load_kpi_from_db() -> tuple[dict[str, Any], str | None]:
    """DB'den KPI al (önbellekli)."""
    return _db_kpi_oku()


@st.cache_data(ttl=CACHE_TTL)
def load_trend_from_db() -> tuple[pd.DataFrame, str | None]:
    """DB'den 24 saatlik trend al (önbellekli)."""
    return _db_trend_oku()


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _canli_metrikleri_ciz(kpi: dict[str, Any]) -> None:
    """3 KPI kartı (kpi_karti) — tek KPI dili."""
    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_karti(
            "Toplam Firma", kpi["total"], ikon="🏢", kategori="sistem",
            aciklama="📊 Arttı mı azaldı mı?", anahtar="rt-total",
        )
    with col2:
        kpi_karti(
            "Sinyal", kpi["signals"], ikon="📡", kategori="sistem",
            aciklama="📊 Spike var mı?", anahtar="rt-signals",
        )
    with col3:
        kpi_karti(
            "Veri Sağlığı", _saglik_durumu(kpi["score"]), ikon="🩺", kategori="sistem",
            yardim=f"Ortalama kalite skoru: {kpi['score']}",
            aciklama="📊 Kritik uyarı var mı?", anahtar="rt-score",
        )


def _trend_ciz(trend_df: pd.DataFrame) -> None:
    if trend_df.empty:
        bos_durum("Son 24 saatte sinyal yok.", ikon="📈", aksiyon="Birkaç dakika sonra tekrar bakın")
        return
    st.line_chart(trend_df.set_index("saat"), width="stretch")


def render_admin_realtime_tab() -> None:
    """Canli veri akisi sekmesi (polling — UI-ADMIN-SSE-IHLAL-03)."""
    PageHeader(
        "Canlı Veri Akışı",
        giris=GIRIS_METNI,
        ust_etiket="Sistem · Canlı",
        ikon="📡",
    ).render()

    son_guncelleme = datetime.now().strftime("%H:%M:%S")
    col_btn, col_rehber, col_zaman = st.columns([1, 1, 3], vertical_alignment="center")
    with col_btn:
        yenile = st.button(
            "🔄 Veriyi Yenile",
            key="refresh_realtime",
            type="primary",
            width="stretch",
            help="Önbelleği temizler ve veritabanını yeniden okur.",
        )
    with col_rehber:
        rehber = st.toggle(
            "ℹ️ Sekme rehberi",
            key="realtime_rehber",
            help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.",
        )
    with col_zaman:
        st.caption(f"Son güncelleme: {son_guncelleme} · önbellek {CACHE_TTL}s")

    if yenile:
        st.cache_data.clear()
        st.rerun()

    if rehber:
        st.info(
            "**Bu ekran ne işe yarar?** Sistemin şu anki nabzını gösterir: firma "
            "sayısı, sinyal hacmi ve veri kalitesi. \"Şu an ne oluyor?\" sorusu "
            "için bakılacak yerdir.\n\n"
            "**Nasıl kullanılır?** Otomatik yenilemeyi açarsanız seçtiğiniz "
            "aralıkta sayfa tazelenir; kapalıyken 🔄 Veriyi Yenile ile elle "
            "tazelersiniz.\n\n"
            "**Veriler nereden gelir?** Doğrudan veritabanından (`companies`, "
            "`company_signals`). Admin panelinde SSE kullanılmaz — mimari kural "
            "gereği canlı akış yalnız müşteri panelindedir.\n\n"
            f"**Dikkat:** Değerler {CACHE_TTL} saniyelik önbellekten okunur."
        )

    render_auto_refresh()

    SectionNav(BOLUMLER, yatay=True).render()

    with st.spinner("Veriler yükleniyor..."):
        kpi, kpi_hata = load_kpi_from_db()

    _bolum("canli-metrikler").render()
    if kpi_hata:
        hata_kutusu("Veritabanı okunamadı", kpi_hata, ipucu=DB_IPUCU)
        return
    if not kpi["total"]:
        bos_durum("Veritabanında firma kaydı yok.", ikon="🗄️", aksiyon="Veri ingest çalıştırın")
        return

    _canli_metrikleri_ciz(kpi)

    _bolum("trend-24s").render()
    trend_df, trend_hata = load_trend_from_db()
    if trend_hata:
        hata_kutusu("Trend okunamadı", trend_hata, ipucu=DB_IPUCU)
        return
    _trend_ciz(trend_df)


__all__ = [
    "BOLUMLER",
    "CACHE_TTL",
    "load_kpi_from_db",
    "load_trend_from_db",
    "render_admin_realtime_tab",
]
