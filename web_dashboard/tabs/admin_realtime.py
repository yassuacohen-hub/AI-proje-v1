# -*- coding: utf-8 -*-
"""P7-45: Canli Veri Akisi (SSE) Admin Sekmesi.

SSE endpoint: http://localhost:8000/api/intelligence/dashboard/stream
Kullanim: streamlit run app.py -> Sistem sekmesi

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` -> ``SectionNav`` -> ``Section``. Renk, ikon ve tipografi
  secimleri **degismedi**; yalnizca hiyerarsi disipline edildi. Ekranin tek
  birincil butonu "Veriyi Yenile" dugmesidir.

ADMIN-ROO-01 (Aşama B):
  * Ham SQL string'i ``sqlalchemy.text()`` ile sarıldı (SQLAlchemy 2.x uyumu).
  * ``except Exception: pass`` kaldırıldı; hata metni kullanıcıya
    ``hata_kutusu`` ile gösterilir, log'a yazılır.
  * ``st.metric`` → ``kpi_karti`` (tek KPI dili, UI-CHART-01).
  * SSE ayrıştırma ve metrik çıkarımı saf fonksiyonlara ayrıldı (test edilebilir).
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
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

_load_env()

log = logging.getLogger(__name__)

SSE_URL = "http://localhost:8000/api/intelligence/dashboard/stream"
CACHE_TTL = 5
SSE_TIMEOUT = 10
SAGLIK_ESIK = 90

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section(
        "Canlı Metrikler",
        "Firma, sinyal, API çağrısı ve sistem sağlığı anlık değerleri.",
        ikon="📊",
        kimlik="canli-metrikler",
    ),
    Section(
        "Son 24 Saat Trend",
        "Aynı metriklerin zaman içindeki seyri.",
        ikon="📈",
        kimlik="trend-24s",
    ),
)

GIRIS_METNI = (
    "Gerçek zamanlı KPI ve sinyal akışını izleyin. Veri "
    f"{CACHE_TTL} saniyede bir otomatik yenilenir; SSE bağlantısı kesilirse "
    "son bilinen değerler gösterilir."
)

SSE_IPUCU = "API (8000) ayakta mı? `docker compose ps api` ile kontrol edin."
DB_IPUCU = "DATABASE_URL `.env` içinde doğru mu? `docker compose ps` ile servisi kontrol edin."


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


# ---------------------------------------------------------------------------
# Saf yardımcılar (Streamlit'siz, test edilebilir)
# ---------------------------------------------------------------------------

def _sse_ayristir(govde: str) -> dict[str, Any]:
    """SSE metninden ilk ``data:`` satırını JSON olarak döndürür; yoksa ``{}``.

    Bozuk JSON satırı atlanır, sonraki ``data:`` satırı denenir.
    """
    for satir in govde.splitlines():
        satir = satir.strip()
        if not satir.startswith("data:"):
            continue
        try:
            veri = json.loads(satir[5:].strip())
        except json.JSONDecodeError:
            continue
        if isinstance(veri, dict):
            return veri
    return {}


def _sse_metrikleri(sse: dict[str, Any]) -> dict[str, Any]:
    """SSE sözlüğünden 4 ana metriği takma adlarıyla birlikte çıkarır.

    İki isim şeması desteklenir (İngilizce API / Türkçe alias); ilk bulunan alınır.
    """
    def _al(*anahtarlar: str, varsayilan: Any = None) -> Any:
        for k in anahtarlar:
            if k in sse and sse[k] is not None:
                return sse[k]
        return varsayilan

    return {
        "total": _al("total", "total_firma", varsayilan=0),
        "signals": _al("signals", "sinyal_toplam", varsayilan=0),
        "api_calls": _al("api_calls", "api_cagri_toplam", varsayilan=0),
        "score": _al("quality_score", "saglik_skoru", varsayilan=100),
    }


def _saglik_durumu(skor: Any, esik: int = SAGLIK_ESIK) -> str:
    """Skoru insan diline çevirir: ``🟢 Sağlıklı`` / ``🟠 Dikkat``."""
    try:
        return "🟢 Sağlıklı" if float(skor) >= esik else "🟠 Dikkat"
    except (TypeError, ValueError):
        return "🟠 Dikkat"


def _sse_oku(url: str = SSE_URL, timeout: int = SSE_TIMEOUT) -> tuple[dict[str, Any], str | None]:
    """SSE endpoint'ini okur → ``(veri, hata)``. Hata varsa veri boştur."""
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("SSE okunamadı (%s): %s", url, exc)
        return {}, f"{type(exc).__name__}: {exc}"
    return _sse_ayristir(resp.text), None


def _db_kpi_oku() -> tuple[dict[str, Any], str | None]:
    """DB'den yedek KPI okur → ``(veri, hata)``; SQL ``text()`` ile sarılıdır."""
    sonuc: dict[str, Any] = {"total": 0, "signals": 0, "api_calls": 0}
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text("SELECT COUNT(*) AS cnt FROM companies")).mappings().first()
    except Exception as exc:  # noqa: BLE001 - sürücü/bağlantı hataları çeşitli
        log.warning("DB KPI okunamadı: %s", exc)
        return sonuc, f"{type(exc).__name__}: {exc}"
    if row:
        sonuc["total"] = row["cnt"] or 0
    return sonuc, None


# ---------------------------------------------------------------------------
# Önbellekli sarmalayıcılar
# ---------------------------------------------------------------------------

@st.cache_data(ttl=CACHE_TTL)
def load_sse_data() -> tuple[dict[str, Any], str | None]:
    """SSE endpoint'den canli veri al (önbellekli)."""
    return _sse_oku()


@st.cache_data(ttl=CACHE_TTL)
def load_kpi_from_db() -> tuple[dict[str, Any], str | None]:
    """DB'den KPI al (önbellekli)."""
    return _db_kpi_oku()


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _canli_metrikleri_ciz(sse: dict[str, Any]) -> None:
    """4 KPI kartı (kpi_karti) — tek KPI dili."""
    m = _sse_metrikleri(sse)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_karti(
            "Toplam Firma", m["total"], ikon="🏢", kategori="sistem",
            aciklama="📊 Arttı mı azaldı mı?", anahtar="rt-total",
        )
    with col2:
        kpi_karti(
            "Sinyal", m["signals"], ikon="📡", kategori="sistem",
            aciklama="📊 Spike var mı?", anahtar="rt-signals",
        )
    with col3:
        kpi_karti(
            "API Çağrı", m["api_calls"], ikon="🔌", kategori="sistem",
            aciklama="📊 Artış trendi?", anahtar="rt-api",
        )
    with col4:
        kpi_karti(
            "Sistem Sağlığı", _saglik_durumu(m["score"]), ikon="🩺", kategori="sistem",
            yardim=f"Skor: {m['score']}", aciklama="📊 Kritik uyarı var mı?", anahtar="rt-score",
        )


def _trend_ciz(sse: dict[str, Any]) -> None:
    trend = sse.get("trend") or {}
    trend_df = pd.DataFrame(trend) if trend else pd.DataFrame()
    if trend_df.empty:
        bos_durum("Trend verisi henüz oluşmadı.", ikon="📈", aksiyon="Birkaç dakika sonra tekrar bakın")
        return
    st.line_chart(trend_df, width="stretch")


def render_admin_realtime_tab() -> None:
    """Canli veri akisi sekmesi (ADMIN-UI-10 sayfa iskeletiyle)."""
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
            help="Önbelleği temizler ve canlı akışı yeniden okur.",
        )
    with col_rehber:
        rehber = st.toggle(
            "ℹ️ Sekme rehberi",
            key="realtime_rehber",
            help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.",
        )
    with col_zaman:
        st.caption(
            f"Son güncelleme: {son_guncelleme} · {CACHE_TTL}s aralıkla otomatik yenileniyor"
        )

    if yenile:
        st.cache_data.clear()
        st.rerun()

    if rehber:
        st.info(
            "**Bu ekran ne işe yarar?** Sistemin şu anki nabzını gösterir: yeni gelen "
            "firma sinyalleri, KPI değişimleri ve canlı olaylar burada akar. "
            "\"Şu an ne oluyor?\" sorusu için bakılacak yerdir.\n\n"
            "**Nasıl kullanılır?** Ekran kendiliğinden yenilenir; elle müdahale gerekmez. "
            "Son güncelleme saati sağ üstte görünür. Bağlantı koparsa uyarı çıkar ve "
            "son bilinen veriler gösterilmeye devam eder.\n\n"
            "**Veriler nereden gelir?** `/api/intelligence/dashboard/stream` canlı akışı "
            "(SSE). Akış kesilirse veritabanından yedek okuma yapılır.\n\n"
            f"**Dikkat:** Veriler {CACHE_TTL} saniyede bir yenilenir; bu süreden kısa "
            "değişimler ekrana yansımayabilir."
        )

    SectionNav(BOLUMLER, yatay=True).render()

    with st.spinner("Canlı veri yükleniyor..."):
        sse, sse_hata = load_sse_data()

    if sse:
        _bolum("canli-metrikler").render()
        _canli_metrikleri_ciz(sse)
        if sse.get("generated_at"):
            st.caption(f"Veri zamanı: {sse['generated_at']}")
        _bolum("trend-24s").render()
        _trend_ciz(sse)
        return

    # --- SSE yok: hata kutusu + DB yedeği ---
    if sse_hata:
        hata_kutusu("Canlı bağlantı kurulamadı", sse_hata, ipucu=SSE_IPUCU)
    else:
        bos_durum("SSE akışı boş yanıt döndürdü.", ikon="📡", aksiyon="Veriyi Yenile")

    _bolum("canli-metrikler").render()
    db, db_hata = load_kpi_from_db()
    if db_hata:
        hata_kutusu("Veritabanı yedeği okunamadı", db_hata, ipucu=DB_IPUCU)
        return
    if db.get("total"):
        kpi_karti(
            "DB Toplam Firma", db["total"], ikon="🗄️", kategori="sistem",
            aciklama="Veritabanından yedek okuma (SSE kapalı).", anahtar="rt-db-total",
        )
    else:
        bos_durum("Veritabanında firma kaydı yok.", ikon="🗄️", aksiyon="Veri ingest çalıştırın")


__all__ = [
    "BOLUMLER",
    "CACHE_TTL",
    "SSE_URL",
    "load_kpi_from_db",
    "load_sse_data",
    "render_admin_realtime_tab",
]
