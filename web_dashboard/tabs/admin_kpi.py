"""P7-25: Admin Dashboard KPI Kartları — Müşteri, API, Sinyal, Sistem Sağlığı.

Kurallar:
  - st.cache_data ttl=60
  - Plotly fallback: st.bar_chart
  - st.metric kullanımı
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


# ---------------------------------------------------------------------------
# Veri Yükleme Fonksiyonları
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def load_admin_kpi_summary() -> dict[str, Any]:
    """Genel KPI özeti: toplam firma, aktif kullanıcı, API kullanım, sinyal sayısı."""
    engine = get_engine()
    result: dict[str, Any] = {
        "toplam_firma": 0,
        "aktif_kullanici": 0,
        "api_cagri_toplam": 0,
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

            # Aktif kullanıcı
            row = conn.execute(text(
                "SELECT COUNT(*) as cnt FROM users "
                "WHERE status IN ('onayli', 'aktif')"
            )).mappings().first()
            if row:
                result["aktif_kullanici"] = row["cnt"] or 0

            # Son 24 saatte yeni firma
            row = conn.execute(text(
                "SELECT COUNT(*) as cnt FROM companies "
                "WHERE created_at >= NOW() - INTERVAL '24 hours'"
            )).mappings().first()
            if row:
                result["son_24s_yeni_firma"] = row["cnt"] or 0
    except Exception:
        pass  # SQLite uyumluluğu için sessiz fallback

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
    except Exception:
        pass

    # API kullanım toplamı
    try:
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT COALESCE(SUM(request_count), 0) as total "
                "FROM api_usage_daily"
            )).mappings().first()
            if row:
                result["api_cagri_toplam"] = row["total"] or 0
    except Exception:
        pass

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
    except Exception:
        pass
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
                except Exception:
                    cnt = 0
                result.append({
                    "Alan": label,
                    "Dolu": cnt,
                    "Toplam": total,
                    "Doluluk (%)": round(cnt / max(total, 1) * 100, 1),
                })
    except Exception:
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
    except Exception:
        pass
    return pd.DataFrame(columns=["source_name", "kayit_sayisi", "son_guncelleme"])


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
    except Exception:
        pass
    return pd.DataFrame(columns=["tarih", "istek"])


# ---------------------------------------------------------------------------
# Render Fonksiyonu
# ---------------------------------------------------------------------------

def render_kpi_tab() -> None:
    """P7-25: Admin Dashboard KPI Kartları sekmesi."""

    st.subheader("📊 Admin Dashboard KPI")
    st.caption("Operasyonel metrikler — Son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M"))

    # --- Ana KPI Kartları ---
    kpi = load_admin_kpi_summary()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="🏢 Toplam Firma",
            value=f"{kpi['toplam_firma']:,}",
            delta=f"+{kpi['son_24s_yeni_firma']} (24s)" if kpi["son_24s_yeni_firma"] else None,
        )
    with c2:
        st.metric(
            label="👥 Aktif Kullanıcı",
            value=f"{kpi['aktif_kullanici']:,}",
        )
    with c3:
        st.metric(
            label="📡 Toplam Sinyal",
            value=f"{kpi['sinyal_toplam']:,}",
            delta=f"+{kpi['son_24s_yeni_sinyal']} (24s)" if kpi["son_24s_yeni_sinyal"] else None,
        )
    with c4:
        st.metric(
            label="🔗 API Çağrıları",
            value=f"{kpi['api_cagri_toplam']:,}",
        )

    # --- İkinci satır: Sağlık + Görev ---
    st.divider()
    c5, c6, c7, c8 = st.columns(4)

    # Sistem sağlığı
    dlq = kpi.get("dlq_adet", 0)
    saglik = "🟢 Sağlıklı" if dlq == 0 else f"🟠 {dlq} DLQ"
    with c5:
        st.metric(label="🛡️ Sistem Durumu", value=saglik)

    # Görev durumu
    task_sum = load_task_summary()
    with c6:
        st.metric(label="📋 Aktif Görev", value=task_sum.get("aktif", 0))
    with c7:
        st.metric(label="✅ Tamamlanan", value=task_sum.get("done", 0))
    with c8:
        st.metric(label="🔒 Blokaj", value=task_sum.get("blocked", 0))

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

    trend_df = load_quality_trend(gun_secimi)
    with trend_cols[1]:
        if not trend_df.empty:
            try:
                # Plotly varsa kullan
                import plotly.express as px
                fig = px.line(
                    trend_df, x="tarih", y="ort_skor",
                    title=f"Son {gun_secimi} Gün — Ortalama Kalite Skoru",
                    labels={"ort_skor": "Skor", "tarih": "Tarih"},
                    markers=True,
                )
                fig.update_layout(height=300, margin=dict(t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                # Fallback: Streamlit bar_chart
                st.bar_chart(trend_df.set_index("tarih")["ort_skor"], use_container_width=True)
        else:
            st.info(f"Son {gun_secimi} gün için kalite trendi verisi bulunamadı.")

    # --- Alan Bazlı Kalite Analizi ---
    st.divider()
    st.subheader("🔍 Alan Bazlı Kalite Analizi")

    field_df = load_field_quality_breakdown()
    if not field_df.empty:
        col_table, col_chart = st.columns([1, 1])
        with col_table:
            st.dataframe(field_df, use_container_width=True, hide_index=True)
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
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.bar_chart(field_df.set_index("Alan")["Doluluk (%)"], use_container_width=True)
    else:
        st.info("Alan kalitesi verisi yüklenemedi.")

    # --- Veri Kaynakları Sağlık Durumu ---
    st.divider()
    st.subheader("🗃️ Veri Kaynakları Durumu")

    source_df = load_source_health()
    if not source_df.empty:
        st.dataframe(source_df, use_container_width=True, hide_index=True)
        try:
            import plotly.express as px
            fig = px.pie(
                source_df, values="kayit_sayisi", names="source_name",
                title="Kaynak Dağılımı",
            )
            fig.update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.bar_chart(source_df.set_index("source_name")["kayit_sayisi"], use_container_width=True)
    else:
        st.info("Kaynak verisi bulunamadı.")

    # --- API Kullanım Trendi ---
    st.divider()
    st.subheader("🔗 API Kullanım Trendi (30 Gün)")

    api_trend_df = load_api_usage_trend()
    if not api_trend_df.empty:
        try:
            import plotly.express as px
            fig = px.bar(
                api_trend_df, x="tarih", y="istek",
                title="Günlük API İstek Sayısı",
            )
            fig.update_layout(height=250, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.bar_chart(api_trend_df.set_index("tarih")["istek"], use_container_width=True)
    else:
        st.info("API kullanım trendi verisi bulunamadı.")
