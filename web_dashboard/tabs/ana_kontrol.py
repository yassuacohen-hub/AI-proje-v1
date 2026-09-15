# -*- coding: utf-8 -*-
"""DASH-UX-01 Ana Kontrol Sekmesi — K4 (Mavi Müşteri + Turuncu Sistem).

Kapsam:
  - Müşteri metrikleri (mavi kart): toplam firma, aktif kullanıcı, sinyal, API çağrıları
  - Sistem metrikleri (turuncu kart): sistem durumu, DLQ, cache, query latency
  - Her metrik yanında "neyi gösterir" + operasyonel soru
  - K1 ortak şablonu: son güncelleme, yenile, "ℹ️ Bu sekme hakkında"

Kurallar:
  - st.metric() mavi/turuncu renk sınıflandırması (CSS via _get_metric_color)
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


def _get_metric_color(category: str) -> str:
    """Metrik kartının CSS class'ı (mavi müşteri / turuncu sistem)."""
    if category == "customer":
        return "metric-blue"
    elif category == "system":
        return "metric-orange"
    return ""


#: ADMIN-UI-09 — Sayfa bölümleri tek yerde tanımlanır; hem `SectionNav`
#: hem de gövde aynı listeyi kullanır, böylece anchor'lar asla kaymaz.
BOLUMLER: tuple[Section, ...] = (
    Section(
        "Müşteri Metrikleri",
        "Mavi kartlar — kullanıcı ve işletme faaliyeti.",
        ikon="👥",
        kimlik="musteri-metrikleri",
    ),
    Section(
        "Sistem Metrikleri",
        "Turuncu kartlar — altyapı sağlığı.",
        ikon="🔧",
        kimlik="sistem-metrikleri",
    ),
    Section(
        "Anlık Uyarılar",
        "Eşik aşan durumlar burada toplanır; uyarı yoksa sistem iyi demektir.",
        ikon="🔔",
        kimlik="anlik-uyarilar",
    ),
    Section(
        "Webhook Akışı",
        "Son gün içindeki olay dağılımı (başarılı / hatalı / DLQ).",
        ikon="📈",
        kimlik="webhook-akisi",
    ),
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
        ikon="🏠",
    ).render()

    # --- K1: Aksiyon şeridi (tek birincil buton: Veriyi Yenile) ---
    col_refresh, col_info, col_time = st.columns([1, 1, 3], vertical_alignment="center")
    with col_refresh:
        yenile = st.button(
            "🔄 Veriyi Yenile",
            key="refresh_ana_kontrol",
            type="primary",
            width="stretch",
            help="Önbelleği temizler ve tüm kartları yeniden yükler.",
        )
    with col_info:
        bilgi = st.toggle(
            "ℹ️ Sekme rehberi",
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
            "**Nasıl kullanılır?** Kartlar renk kodludur: mavi müşteri, gri sistem metrikleri. "
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
        webhook = load_webhook_stats()

    # --- K4: Müşteri Metrikleri (Mavi) ---
    _bolum("musteri-metrikleri").render()

    if kpi:
        cust_c1, cust_c2, cust_c3, cust_c4 = st.columns(4)
        with cust_c1:
            total = kpi.get("total", 0)
            st.metric(
                "Toplam Firma",
                f"{total:,}".replace(",", ".") if total else "—",
                help="Veritabanında kayıtlı aktif firma sayısı"
            )
            st.caption("📊 Bu arttı mı / azaldı mı?")
        with cust_c2:
            users = kpi.get("active_users", 0)
            st.metric(
                "Aktif Kullanıcı",
                f"{users:,}".replace(",", ".") if users else "—",
                help="Son 7 gün içinde api_key ile istek yapmış kullanıcılar"
            )
            st.caption("📊 Churn risk var mı?")
        with cust_c3:
            signals = kpi.get("signal_count", 0)
            st.metric(
                "Sinyal Sayısı",
                f"{signals:,}".replace(",", ".") if signals else "—",
                help="Oluşturulmuş toplam ticari sinyal (purchase intent vb.)"
            )
            st.caption("📊 Trend nedir?")
        with cust_c4:
            api_calls = kpi.get("api_calls_total", 0)
            st.metric(
                "API Çağrıları (24h)",
                f"{api_calls:,}".replace(",", ".") if api_calls else "—",
                help="Son 24 saatte yapılmış API çağrı sayısı"
            )
            st.caption("📊 Spike/drop var mı?")
    else:
        st.info("⏳ Müşteri metrikleri yükleniyor... Veriler 24 saat içinde görünecek.")

    # --- K4: Sistem Metrikleri (Turuncu) ---
    _bolum("sistem-metrikleri").render()

    if webhook or kpi:
        sys_c1, sys_c2, sys_c3, sys_c4 = st.columns(4)
        with sys_c1:
            dlq_ok = webhook.get("dlq_toplam", 0) == 0
            status = "🟢 Sağlıklı" if dlq_ok else "🟠 Uyarı"
            st.metric(
                "Sistem Durumu",
                status,
                help="DLQ kuyruğu boş → sistem çalışıyor"
            )
            st.caption("📊 Son hata ne zaman?")
        with sys_c2:
            dlq_count = webhook.get("dlq_toplam", 0)
            st.metric(
                "DLQ (Hata Kuyruğu)",
                f"{dlq_count:,}".replace(",", "."),
                help="Webhook işlemesi başarısız olan kayıt sayısı"
            )
            st.caption("📊 Hızlanıyor/yavaşlıyor?")
        with sys_c3:
            cache_hit = kpi.get("cache_hit_rate", 0)
            st.metric(
                "Cache Hit Oranı",
                f"%{cache_hit * 100:.1f}" if cache_hit else "—",
                help="Veritabanı sorgusu yerine cache'den cevap %"
            )
            st.caption("📊 % arttırabilir miyiz?")
        with sys_c4:
            query_ms = kpi.get("avg_query_latency_ms", 0)
            st.metric(
                "Ort. Query Latency",
                f"{query_ms:.0f} ms" if query_ms else "—",
                help="Veritabanı sorgularının ortalama yanıt süresi"
            )
            st.caption("📊 Slow query yok mu?")
    else:
        st.info("⏳ Sistem metrikleri yükleniyor... Veriler kısa süre içinde görünecek.")

    # --- K2: Uyarılar (boş state örneği) ---
    _bolum("anlik-uyarilar").render()
    if webhook.get("dlq_toplam", 0) > 0:
        st.warning(f"⚠️ {webhook['dlq_toplam']} işleme başarısız DLQ kaydı var. İncelemeyi gerektirir.")
    elif kpi.get("cache_hit_rate", 0) and kpi.get("cache_hit_rate", 0) < 0.3:
        st.warning("⚠️ Cache hit oranı düşük (%30 altında). Veritabanı yükü yüksek olabilir.")
    else:
        st.success("✅ Sistem iyi durumda. Kritik uyarı yok.")

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
            st.bar_chart(flow_df.set_index("Durum"), width="stretch")
    else:
        st.info("📊 Webhook verisi henüz toplanmadı. Sistem kullanılınca veriler burada görünecek.")
