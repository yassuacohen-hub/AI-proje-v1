"""P7-25: Admin Dashboard KPI Kartları — Müşteri, API, Sinyal, Sistem Sağlığı.

Kurallar:
  - st.cache_data ttl=60
  - Plotly fallback: st.bar_chart / st.area_chart (web_dashboard.charts içinde)
  - UI-CHART-01: KPI kartları `web_dashboard.charts.kpi_karti`, dağılımlar `donut`,
    trendler `alan_grafigi` ile çizilir (tema uyumlu, responsive)
  - 7/30/90 gün trend desteği
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine

from company_master.tenant.model import TenantContext as _TenantContext
from web_dashboard.charts import alan_grafigi, donut, kpi_karti  # noqa: E402  (UI-CHART-01)
from web_dashboard.tabs.tenant_health_dashboard import (
    tenant_health_dashboard as _tenant_health_dashboard,
)
from web_dashboard.tabs.admin_error_handling import AdminErrorHandler
from web_dashboard.tabs._db_yardim import tablo_var_mi

# Admin KPI logger
_admin_kpi_logger = AdminErrorHandler("admin_kpi")

# ---------------------------------------------------------------------------
# Veri Yükleme Fonksiyonları
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def load_admin_kpi_summary() -> dict[str, Any]:
    """Genel KPI özeti: toplam firma, MAU, API kullanım, sinyal sayısı."""
    engine = get_engine()
    result: dict[str, Any] = {
        "toplam_firma": 0,
        "mau": 0,
        "api_cagri_toplam": 0,
        "api_veri_yok": False,
        "sinyal_toplam": 0,
        "saglik_skoru": 100,
        "dlq_adet": 0,
        "son_24s_yeni_firma": 0,
        "son_24s_yeni_sinyal": 0,
    }
    try:
        with engine.connect() as conn:
            # Toplam firma
            row = conn.execute(text(
                "SELECT COUNT(*) as cnt FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE"
            )).mappings().first()
            if row:
                result["toplam_firma"] = row["cnt"] or 0

            # MAU (Monthly Active Users) — last_login son 30 gün içinde
            row = conn.execute(text(
                "SELECT COUNT(*) as cnt FROM users "
                "WHERE last_login >= NOW() - INTERVAL '30 days'"
            )).mappings().first()
            if row:
                result["mau"] = row["cnt"] or 0

            # Son 24 saatte yeni firma
            row = conn.execute(text(
                "SELECT COUNT(*) as cnt FROM companies "
                "WHERE created_at >= NOW() - INTERVAL '24 hours'"
            )).mappings().first()
            if row:
                result["son_24s_yeni_firma"] = row["cnt"] or 0
    except Exception as exc:
        _admin_kpi_logger.warning("KPI özeti yüklenemedi", exc)

    # Sinyal sayısı
    try:
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT COUNT(*) as cnt FROM company_signals"
            )).mappings().first()
            if row:
                result["sinyal_toplam"] = row["cnt"] or 0

            # Son 24 saatte yeni sinyal
            row = conn.execute(text(
                "SELECT COUNT(*) as cnt FROM company_signals "
                "WHERE detected_at >= NOW() - INTERVAL '24 hours'"
            )).mappings().first()
            if row:
                result["son_24s_yeni_sinyal"] = row["cnt"] or 0
    except Exception as exc:
        _admin_kpi_logger.warning("Sinyal sayısı yüklenemedi", exc)

    # API kullanım toplamı — UI-ADMIN-SAHTE-KPI-01: tablo yoksa 0 değil rozet
    if not tablo_var_mi("api_usage_daily", engine):
        result["api_veri_yok"] = True
    else:
        try:
            with engine.connect() as conn:
                row = conn.execute(text(
                    "SELECT COALESCE(SUM(request_count), 0) as total "
                    "FROM api_usage_daily"
                )).mappings().first()
                if row:
                    result["api_cagri_toplam"] = row["total"] or 0
        except Exception as exc:
            _admin_kpi_logger.warning("API kullanım toplamı yüklenemedi", exc)

    return result


@st.cache_data(ttl=60)
def load_quality_trend(gun: int = 30) -> pd.DataFrame:
    """Son N gün için kalite skoru trendi (gunluk ortalama)."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT DATE(created_at) as tarih, "
                "       AVG(data_quality_score) as ort_skor, "
                "       COUNT(*) as firma_sayisi "
                "FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE "
                "  AND created_at >= NOW() - :gun || ' days' "
                "GROUP BY DATE(created_at) "
                "ORDER BY tarih"
            ), {"gun": gun}).mappings().all()
            if rows:
                return pd.DataFrame([dict(r) for r in rows])
    except Exception as exc:
        _admin_kpi_logger.warning("Kalite trendi yüklenemedi", exc)
    return pd.DataFrame(columns=["tarih", "ort_skor", "firma_sayisi"])


@st.cache_data(ttl=60)
def load_field_quality_breakdown() -> pd.DataFrame:
    """Alan bazlı kalite analizi: her alanın doluluk oranı."""
    engine = get_engine()
    result = []
    fields = {
        "primary_phone": "Telefon",
        "primary_email": "E-posta",
        "website_domain": "Web Sitesi",
        "tax_number": "VKN",
        "nace_code": "NACE",
        "adres": "Adres",
        "osb_parsel": "Parsel",
    }
    try:
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT COUNT(*) as total FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE"
            )).mappings().first()
            total = (row["total"] or 1) if row else 1

            for col, label in fields.items():
                try:
                    cnt_row = conn.execute(text(
                        f"SELECT COUNT(*) as cnt FROM companies "
                        f"WHERE is_ankara=TRUE AND is_osb_member=TRUE "
                        f"AND {col} IS NOT NULL AND {col} != ''"
                    )).mappings().first()
                    cnt = cnt_row["cnt"] if cnt_row else 0
                except Exception as exc:
                    _admin_kpi_logger.warning(f"Alan {label} sayımı başarısız", exc)
                    cnt = 0
                result.append({
                    "Alan": label,
                    "Dolu": cnt,
                    "Toplam": total,
                    "Doluluk (%)": round(cnt / max(total, 1) * 100, 1),
                })
    except Exception as exc:
        _admin_kpi_logger.warning("Alan kalite analizi yüklenemedi", exc)
        for col, label in fields.items():
            result.append({
                "Alan": label, "Dolu": 0, "Toplam": 0, "Doluluk (%)": 0,
            })
    return pd.DataFrame(result)


@st.cache_data(ttl=60)
def load_source_health() -> pd.DataFrame:
    """Veri kaynaklarının sağlık durumu."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT s.source_name, "
                "       COUNT(sr.source_record_id) as kayit_sayisi, "
                "       MAX(sr.created_at) as son_guncelleme "
                "FROM sources s "
                "LEFT JOIN source_records sr ON sr.source_id = s.source_id "
                "GROUP BY s.source_id, s.source_name "
                "ORDER BY kayit_sayisi DESC"
            )).mappings().all()
            if rows:
                return pd.DataFrame([dict(r) for r in rows])
    except Exception as exc:
        _admin_kpi_logger.warning("Kaynak sağlık durumu yüklenemedi", exc)
    return pd.DataFrame(columns=["source_name", "kayit_sayisi", "son_guncelleme"])


@st.cache_data(ttl=60)
def load_ai_cost_kpi() -> dict[str, Any]:
    """P7-27: 9Router optimizer JSON'undan günlük AI maliyet özeti.

    admin_cost.py ile aynı kaynağı (data/router/optimizer_latest.json) kullanır;
    burada sadece KPI panosu için özet metrikler çıkarılır.
    """
    import json

    result: dict[str, Any] = {
        "gunluk_maliyet_usd": 0.0,
        "aylik_tahmini_usd": 0.0,
        "problemli_provider": 0,
        "anomali_sayisi": 0,
    }
    try:
        json_path = Path("data/router/optimizer_latest.json")
        if not json_path.exists():
            return result
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        combo = data.get("combo_istatistik", {})
        usage = combo.get("usageHistory", {})
        gunluk = float(usage.get("toplam_maliyet_usd", 0.0))
        result["gunluk_maliyet_usd"] = gunluk
        result["aylik_tahmini_usd"] = gunluk * 30
        result["anomali_sayisi"] = len(data.get("anomaliler", []))

        providerlar = data.get("saglik", {}).get("providerlar", [])
        problemli = 0
        for p in providerlar:
            d = p.get("durum", {})
            if (d.get("backoffLevel") or 0) >= 3 or (d.get("modelLockSayisi") or 0) > 5 or d.get("errorCode"):
                problemli += 1
        result["problemli_provider"] = problemli
    except Exception as exc:
        _admin_kpi_logger.warning("AI maliyet KPI yüklenemedi", exc)
    return result


@st.cache_data(ttl=60)
def load_task_summary() -> dict[str, Any]:
    """Görev durumu özeti."""
    from company_master.orchestrator import task_board as tb
    board = tb.gorev_listesi()
    summary = {
        "toplam": 0, "done": 0, "aktif": 0, "review": 0,
        "plan": 0, "blocked": 0,
    }
    if not board:
        return summary
    summary["toplam"] = len(board)
    for t in board:
        durum = t.get("durum", "")
        if durum in summary:
            summary[durum] += 1
    return summary


@st.cache_data(ttl=60)
def load_api_usage_trend() -> pd.DataFrame:
    """Son 30 günlük API kullanım trendi."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT date as tarih, SUM(request_count) as istek "
                "FROM api_usage_daily "
                "WHERE date >= CURRENT_DATE - INTERVAL '30 days' "
                "GROUP BY date ORDER BY date"
            )).mappings().all()
            if rows:
                return pd.DataFrame([dict(r) for r in rows])
    except Exception as exc:
        _admin_kpi_logger.warning("API kullanım trendi yüklenemedi", exc)
    return pd.DataFrame(columns=["tarih", "istek"])


def _render_kpi_card(
    label: str,
    value: str,
    delta: str | None = None,
    icon: str = "",
    kategori: str = "marka",
) -> None:
    """UI-CHART-01: imza korunur; çizim `charts.kpi_karti`'ye delege edilir."""
    kpi_karti(label, value, delta=delta, ikon=icon, kategori=kategori)


def _render_quality_trend(gun_secimi: int) -> None:
    trend_df = load_quality_trend(gun_secimi)
    if trend_df.empty:
        st.info(f"Son {gun_secimi} gün için kalite trendi verisi bulunamadı.")
        return
    alan_grafigi(
        trend_df, "tarih", "ort_skor",
        baslik=f"Son {gun_secimi} Gün — Ortalama Kalite Skoru",
        kategori="basari", yukseklik=300, x_etiket="Tarih", y_etiket="Skor",
    )


def _render_field_quality(field_df: pd.DataFrame) -> None:
    if field_df.empty:
        st.info("Alan kalitesi verisi yüklenemedi.")
        return
    col_table, col_chart = st.columns([1, 1])
    with col_table:
        st.dataframe(field_df, width="stretch", hide_index=True)
    with col_chart:
        try:
            import plotly.express as px
            fig = px.bar(
                field_df, x="Alan", y="Doluluk (%)",
                title="Alan Doluluk Oranları (%)",
                color="Doluluk (%)",
                color_continuous_scale="RdYlGn",
            )
            fig.update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig, width="stretch")
        except ImportError:
            st.bar_chart(field_df.set_index("Alan")["Doluluk (%)"], width="stretch")


def _render_source_health(source_df: pd.DataFrame) -> None:
    if source_df.empty:
        st.info("Kaynak verisi bulunamadı.")
        return
    st.dataframe(source_df, width="stretch", hide_index=True)
    donut(
        source_df, "source_name", "kayit_sayisi",
        baslik="Kaynak Dağılımı", merkez_metin="kayıt", yukseklik=300,
    )


def _render_api_trend(api_df: pd.DataFrame) -> None:
    if api_df.empty:
        st.info("API kullanım trendi verisi bulunamadı.")
        return
    alan_grafigi(
        api_df, "tarih", "istek",
        baslik="Günlük API İstek Sayısı",
        kategori="bilgi", yukseklik=250, x_etiket="Tarih", y_etiket="İstek",
    )


# ---------------------------------------------------------------------------
# Render Fonksiyonu
# ---------------------------------------------------------------------------

def render_kpi_tab() -> None:
    """P7-25: Admin Dashboard KPI Kartları sekmesi."""

    st.subheader("📊 Admin Dashboard KPI")
    st.caption("Operasyonel metrikler — Son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    if st.button("🔄 Yenile", key="admin-kpi-refresh"):
        st.cache_data.clear()
        st.rerun()

    # --- Ana KPI Kartları ---
    kpi = load_admin_kpi_summary()
    if not kpi:
        with st.spinner("Veri yukleniyor..."):
            cols = st.columns(4)
            for col in cols:
                with col:
                    st.empty()
                    st.empty()
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _render_kpi_card(
            "Toplam Firma",
            f"{kpi['toplam_firma']:,}",
            f"+{kpi['son_24s_yeni_firma']} (24s)" if kpi["son_24s_yeni_firma"] else None,
            "🏢",
        )
    with c2:
        _render_kpi_card("MAU (30 Gün)", f"{kpi['mau']:,}", icon="👥")
    with c3:
        _render_kpi_card(
            "Toplam Sinyal",
            f"{kpi['sinyal_toplam']:,}",
            f"+{kpi['son_24s_yeni_sinyal']} (24s)" if kpi["son_24s_yeni_sinyal"] else None,
            "📡",
        )
    with c4:
        if kpi.get("api_veri_yok"):
            _render_kpi_card("API Çağrıları", "veri kaynağı yok", icon="⚠️")
        else:
            _render_kpi_card("API Çağrıları", f"{kpi['api_cagri_toplam']:,}", icon="🔗")

    # --- İkinci satır: Sağlık + Görev ---
    st.divider()
    c5, c6, c7, c8 = st.columns(4)

    dlq = kpi.get("dlq_adet", 0)
    saglik = "🟢 Sağlıklı" if dlq == 0 else f"🟠 {dlq} DLQ"
    with c5:
        _render_kpi_card("Sistem Durumu", saglik, icon="🛡️")

    task_sum = load_task_summary()
    with c6:
        _render_kpi_card("Aktif Görev", task_sum.get("aktif", 0), icon="📋")
    with c7:
        _render_kpi_card("Tamamlanan", task_sum.get("done", 0), icon="✅")
    with c8:
        _render_kpi_card("Blokaj", task_sum.get("blocked", 0), icon="🔒")

    # --- Tenant Sağlığı ---
    st.divider()
    st.subheader("🏥 Tenant Sağlığı")
    try:
        _tenant_health_dashboard(
            tenant_ctx=_TenantContext("huginn", "Huginn Data", "kurumsal"),
            companies=[],
        )
    except Exception as exc:
        _admin_kpi_logger.warning("Tenant sağlığı yüklenemedi", exc)
        st.warning("Tenant sağlığı yüklenemedi.")

    # --- Üçüncü satır: P7-27 AI Maliyet Özeti (9Router) ---
    st.divider()
    ai_cost = load_ai_cost_kpi()
    c9, c10, c11, c12 = st.columns(4)
    with c9:
        _render_kpi_card("Günlük AI Maliyet", f"${ai_cost['gunluk_maliyet_usd']:.4f}", icon="💰")
    with c10:
        _render_kpi_card("Aylık Tahmini Maliyet", f"${ai_cost['aylik_tahmini_usd']:.2f}", icon="📅")
    with c11:
        _render_kpi_card("Anomali Sayısı", ai_cost["anomali_sayisi"], icon="⚠️")
    with c12:
        _render_kpi_card("Problemli Provider", ai_cost["problemli_provider"], icon="🔴")

    # --- Trend Bölümü (7/30/90 Gün) ---
    st.divider()
    st.subheader("📈 Kalite Skoru Trendi")

    trend_cols = st.columns([1, 3])
    with trend_cols[0]:
        gun_secimi = st.radio(
            "Periyot",
            options=[7, 30, 90],
            index=1,
            format_func=lambda x: f"{x} Gün",
            key="kpi_trend_period",
        )
    _render_quality_trend(gun_secimi)

    # --- Alan Bazlı Kalite Analizi ---
    st.divider()
    st.subheader("🔍 Alan Bazlı Kalite Analizi")
    _render_field_quality(load_field_quality_breakdown())

    # --- Veri Kaynakları Sağlık Durumu ---
    st.divider()
    st.subheader("🗃️ Veri Kaynakları Durumu")
    _render_source_health(load_source_health())

    # --- API Kullanım Trendi ---
    st.divider()
    st.subheader("🔗 API Kullanım Trendi (30 Gün)")
    _render_api_trend(load_api_usage_trend())
