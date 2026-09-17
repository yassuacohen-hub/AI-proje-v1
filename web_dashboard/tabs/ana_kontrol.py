# -*- coding: utf-8 -*-
"""DASH-UX-01 Ana Kontrol Sekmesi — K4 (Mavi Müşteri + Turuncu Sistem).

Kapsam:
  - Müşteri metrikleri (mavi kart): toplam firma, aktif kullanıcı, sinyal, API çağrıları
  - Sistem metrikleri (turuncu kart): sistem durumu, DLQ, cache, query latency
  - Her metrik yanında "neyi gösterir" + operasyonel soru
  - K1 ortak şablonu: son güncelleme, yenile, "ℹ️ Bu sekme hakkında"

Kurallar:
  - kpi_karti(..., kategori=...) ile renk sınıflandırması (mavi müşteri / turuncu sistem)
  - st.cache_data(ttl=30)
  - Empty state → "Veri gelince X burada görünecek"

ADMIN-UI-09 (pilot ekran):
  Sayfa iskeleti Streamlit Playground dokümantasyon mantığına taşındı:
  ``PageHeader`` (üst etiket → H1 → giriş paragrafı) → ``SectionNav``
  ("Bu sayfada" gezinme) → ``Section`` (H2 + açıklama + ayraç) blokları.
  Renk paleti, ikon seti ve tipografi seçimleri **değişmedi**; yalnızca
  hiyerarşi disipline edildi. Aynı ekranda tek birincil buton kuralı gereği
  yalnız "Veriyi Yenile" birincil, diğer aksiyonlar ikincildir.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scripts.dash04_api_client import get_api, APIError  # noqa: E402

from company_master.i18n import t  # noqa: E402
from company_master.ui import PageHeader, Section, SectionNav  # noqa: E402
from web_dashboard.charts import donut, kpi_karti  # noqa: E402  (UI-CHART-01, KPI-EXA-02)


@st.cache_data(ttl=30)
def load_kpi_data() -> dict[str, Any]:
    """KPI verisi yükle (/api/kpi endpoint'inden)."""
    try:
        data = get_api("/api/kpi")
        if isinstance(data, dict):
            return data or {}
    except (APIError, Exception):
        pass
    return {}


@st.cache_data(ttl=30)
def load_kpi_history(days: int = 7) -> dict[str, Any]:
    """KPI tarih verisi yükle (/api/kpi/history endpoint'inden)."""
    try:
        data = get_api(f"/api/kpi/history?days={days}")
        if isinstance(data, dict):
            return data or {}
    except (APIError, Exception):
        pass
    return {}


@st.cache_data(ttl=30)
def load_webhook_stats() -> dict[str, Any]:
    """Webhook istatistikleri yükle."""
    try:
        # Placeholder: webhook monitor'dan veri çek
        # Gerçek impl: file log tarama veya /api/webhook-stats endpoint
        return {
            "basarili": 0,
            "hatali": 0,
            "calisan": 0,
            "dlq_toplam": 0,
            "son_olay": None,
            "olay_toplam": 0,
            "hata_turleri": {},
        }
    except Exception:
        pass
    return {}

#: ADMIN-UI-09 — Sayfa bölümleri tek yerde tanımlanır; hem `SectionNav`
#: hem de gövde aynı listeyi kullanır, böylece anchor'lar asla kaymaz.
# KPI-EXA-02 (sahip, 2026-09-15): Veri Akışı diyagramı "Teknik Altyapı" sayfasına
# taşındı; bölüm açıklama cümleleri ve küçük emojiler kaldırıldı (sade başlık).
BOLUMLER: tuple[Section, ...] = (
    Section("Müşteri", kimlik="musteri-metrikleri"),
    Section("Sistem", kimlik="sistem-metrikleri"),
    Section("Uyarılar", kimlik="anlik-uyarilar"),
    Section("Webhook Akışı", kimlik="webhook-akisi"),
)

GIRIS_METNI = t("huginn_dashboard_welcome")


def _bolum(kimlik: str) -> Section:
    """Kimliğe göre bölüm tanımını getirir (anchor tutarlılığı için)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def render_ana_kontrol_tab() -> None:
    """DASH-UX-01 Ana Kontrol sekmesi (ADMIN-UI-09 sayfa iskeletiyle)."""
    # --- ADMIN-UI-09: Playground kalıbı — üst etiket → H1 → giriş paragrafı ---
    PageHeader(
        "Ana Kontrol",
        giris=GIRIS_METNI,
        ust_etiket="İş · Operasyon",
    ).render()

    # --- K1: Aksiyon şeridi (tek birincil buton: Veriyi Yenile) ---
    col_refresh, col_info, col_time = st.columns([1, 1, 3], vertical_alignment="center")
    with col_refresh:
        yenile = st.button(
            "Veriyi Yenile",
            key="refresh_ana_kontrol",
            type="primary",
            width="stretch",
            help="Önbelleği temizler ve tüm kartları yeniden yükler.",
        )
    with col_info:
        bilgi = st.toggle(
            "Sekme rehberi",
            key="ana_kontrol_rehber",
            help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.",
        )
    with col_time:
        st.caption(
            f"Son güncelleme: {datetime.now().strftime('%H:%M')} · "
            "Önbellek ömrü 30 sn"
        )

    if yenile:
        st.cache_data.clear()
        st.rerun()

    if bilgi:
        st.info(
            "**Bu ekran ne işe yarar?** Müşteri tarafı (kayıt, onay, kredi) ve sistem tarafı "
            "(firma sayısı, kalite skoru, görev durumu) metriklerini tek bakışta gösterir. "
            "Güne başlarken \"her şey yolunda mı?\" sorusunun cevabı burada.\n\n"
            "**Nasıl kullanılır?** Kart konturu ve sol üstteki nokta kategoriyi gösterir: mavi müşteri, gri sistem. "
            "Sağ üstteki **Yenile** düğmesi önbelleği temizleyip verileri anında tazeler.\n\n"
            "**Veriler nereden gelir?** `/api/kpi` ve `/metrics` uç noktaları ile "
            "webhook izleme kayıtları.\n\n"
            "**Dikkat:** Veriler 30 saniyede bir otomatik yenilenir. Webhook istatistikleri "
            "şimdilik anlık değildir; canlı akış (SSE) Faz 2'de eklenecek."
        )

    # --- ADMIN-UI-09: "Bu sayfada" gezinmesi (uzun ekranı taranabilir yapar) ---
    SectionNav(BOLUMLER, yatay=True).render()

    # --- Veri yükleme ---
    with st.spinner("Veriler yükleniyor..."):
        kpi = load_kpi_data()
        kpi_history = load_kpi_history(7)
        webhook = load_webhook_stats()

    # --- K4: Müşteri Metrikleri (KPI-EXA-02: süreç diyagramı Teknik Altyapı sayfasında) ---
    _bolum("musteri-metrikleri").render()

    if kpi:
        series = kpi_history.get("series", {})
        _spark_login = series.get("login", [])
        _spark_search = series.get("search", [])
        _spark_yf = series.get("yeni_firma", [])

        # UI-CHART-01: st.metric yerine gradient KPI kartı (tema uyumlu, responsive)
        cust_c1, cust_c2, cust_c3, cust_c4 = st.columns(4)
        with cust_c1:
            kpi_karti(
                "Toplam Firma",
                kpi.get("total", 0) or None,
                sparkline=_spark_yf if _spark_yf else None,
                kategori="musteri",
                yardim="Veritabanında kayıtlı aktif firma sayısı",
            )
        with cust_c2:
            kpi_karti(
                "Aktif Kullanıcı",
                kpi.get("active_users", 0) or None,
                sparkline=_spark_login if _spark_login else None,
                kategori="musteri",
                yardim="Son 7 gün içinde api_key ile istek yapmış kullanıcılar",
            )
        with cust_c3:
            kpi_karti(
                "Sinyal Sayısı",
                kpi.get("signal_count", 0) or None,
                sparkline=_spark_search if _spark_search else None,
                kategori="musteri",
                yardim="Oluşturulmuş toplam ticari sinyal (purchase intent vb.)",
            )
        with cust_c4:
            kpi_karti(
                "API Çağrıları (24h)",
                kpi.get("api_calls_total", 0) or None,
                kategori="musteri",
                yardim="Son 24 saatte yapılmış API çağrı sayısı",
            )
    else:
        st.info("Müşteri metrikleri yükleniyor... Veriler 24 saat içinde görünecek.")

    # --- K4: Sistem Metrikleri ---
    _bolum("sistem-metrikleri").render()

    if webhook or kpi:
        sys_c1, sys_c2, sys_c3, sys_c4 = st.columns(4)
        with sys_c1:
            dlq_ok = webhook.get("dlq_toplam", 0) == 0
            kpi_karti(
                "Sistem Durumu",
                "Sağlıklı" if dlq_ok else "Uyarı",
                kategori="basari" if dlq_ok else "uyari",
                yardim="DLQ kuyruğu boş → sistem çalışıyor",
            )
        with sys_c2:
            dlq_count = webhook.get("dlq_toplam", 0)
            kpi_karti(
                "DLQ (Hata Kuyruğu)",
                dlq_count,
                kategori="tehlike" if dlq_count else "sistem",
                yardim="Webhook işlemesi başarısız olan kayıt sayısı",
            )
        with sys_c3:
            cache_hit = kpi.get("cache_hit_rate", 0)
            kpi_karti(
                "Cache Hit Oranı",
                f"%{cache_hit * 100:.1f}" if cache_hit else None,
                kategori="sistem",
                yardim="Veritabanı sorgusu yerine cache'den cevap %",
            )
        with sys_c4:
            query_ms = kpi.get("avg_query_latency_ms", 0)
            kpi_karti(
                "Ort. Query Latency",
                f"{query_ms:.0f} ms" if query_ms else None,
                kategori="sistem",
                yardim="Veritabanı sorgularının ortalama yanıt süresi",
            )
    else:
        st.info("Sistem metrikleri yükleniyor... Veriler kısa süre içinde görünecek.")

    # --- K2: Uyarılar (boş state örneği) ---
    _bolum("anlik-uyarilar").render()
    if webhook.get("dlq_toplam", 0) > 0:
        st.warning(f"{webhook['dlq_toplam']} işleme başarısız DLQ kaydı var. İncelemeyi gerektirir.")
    elif kpi.get("cache_hit_rate", 0) and kpi.get("cache_hit_rate", 0) < 0.3:
        st.warning("Cache hit oranı düşük (%30 altında). Veritabanı yükü yüksek olabilir.")
    else:
        st.success("Sistem iyi durumda. Kritik uyarı yok.")

    # --- İstatistik grafiği ---
    _bolum("webhook-akisi").render()
    if webhook and webhook.get("olay_toplam", 0) > 0:
        flow_df = pd.DataFrame({
            "Durum": ["Başarılı", "Hatalı", "DLQ"],
            "Adet": [
                webhook.get("basarili", 0),
                webhook.get("hatali", 0),
                webhook.get("dlq_toplam", 0),
            ],
        })
        if flow_df["Adet"].sum() > 0:
            # UI-CHART-01: bar → donut (merkezde toplam olay, hover tooltip)
            donut(flow_df, "Durum", "Adet", baslik="Webhook Akışı", merkez_metin="olay")
    else:
        st.info("Webhook verisi henüz toplanmadı. Sistem kullanılınca veriler burada görünecek.")
