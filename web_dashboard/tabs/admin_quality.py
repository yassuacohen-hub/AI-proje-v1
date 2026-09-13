# -*- coding: utf-8 -*-
"""P7-31 — Admin Panel Faz 2: Veri Kalitesi Özeti sekmesi.

Kapsam:
  - company.data_quality_score aggregation (toplam/ortalama/medyan/min/max)
  - Kalite skoru dağılımı (bucket bazlı: 0-19, 20-39, 40-59, 60-79, 80-100)
  - Eksik alan analizi (telefon, e-posta, web, VKN, NACE, adres, parsel)
  - Kural bazlı iyileştirme önerileri
  - Kalite riski (QS < 30) filtreleme — riskli firma listesi + eksik alan özeti

Kurallar:
  - st.cache_data ttl=60
  - Plotly fallback: st.bar_chart
  - st.metric kullanımı
"""
from __future__ import annotations

import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine

# Analiz edilecek alanlar: kolon adı -> okunabilir etiket
_QUALITY_FIELDS: dict[str, str] = {
    "primary_phone": "Telefon",
    "primary_email": "E-posta",
    "website_domain": "Web Sitesi",
    "tax_number": "VKN",
    "nace_code": "NACE",
    "adres": "Adres",
    "osb_parsel": "Parsel",
}

_RISK_ESIGI = 30  # Kalite riski (QS < 30) eşiği


# ---------------------------------------------------------------------------
# Veri Yükleme Fonksiyonları
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def load_quality_overview() -> dict[str, Any]:
    """Genel kalite skoru özeti: toplam, ortalama, medyan, min, max, riskli oran."""
    result: dict[str, Any] = {
        "toplam_firma": 0,
        "ortalama_skor": 0.0,
        "medyan_skor": 0.0,
        "min_skor": 0.0,
        "max_skor": 0.0,
        "riskli_sayisi": 0,
        "riskli_orani": 0.0,
    }
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT COUNT(*) as toplam, AVG(data_quality_score) as ort, "
                "MIN(data_quality_score) as min_s, MAX(data_quality_score) as max_s, "
                "SUM(CASE WHEN data_quality_score < :esik THEN 1 ELSE 0 END) as riskli "
                "FROM companies WHERE is_ankara=TRUE AND is_osb_member=TRUE"
            ), {"esik": _RISK_ESIGI}).mappings().first()
            if row and row["toplam"]:
                result["toplam_firma"] = row["toplam"]
                result["ortalama_skor"] = round(float(row["ort"] or 0), 1)
                result["min_skor"] = round(float(row["min_s"] or 0), 1)
                result["max_skor"] = round(float(row["max_s"] or 0), 1)
                result["riskli_sayisi"] = row["riskli"] or 0
                result["riskli_orani"] = round(
                    result["riskli_sayisi"] / max(result["toplam_firma"], 1) * 100, 1
                )

            # Medyan: cross-DB uyumluluk için Python tarafında hesapla
            scores = conn.execute(text(
                "SELECT data_quality_score FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE "
                "AND data_quality_score IS NOT NULL"
            )).scalars().all()
            if scores:
                scores_f = [float(s) for s in scores]
                result["medyan_skor"] = round(statistics.median(scores_f), 1)
    except Exception:
        pass
    return result


@st.cache_data(ttl=60)
def load_score_distribution() -> pd.DataFrame:
    """Kalite skoru dağılımı (bucket bazlı) — 8313+ firma için histogram verisi."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT CASE
                    WHEN data_quality_score >= 80 THEN '80-100'
                    WHEN data_quality_score >= 60 THEN '60-79'
                    WHEN data_quality_score >= 40 THEN '40-59'
                    WHEN data_quality_score >= 20 THEN '20-39'
                    ELSE '0-19'
                END as bucket, COUNT(*) as adet
                FROM companies
                WHERE is_ankara=TRUE AND is_osb_member=TRUE
                GROUP BY 1
            """)).mappings().all()
            if rows:
                df = pd.DataFrame([dict(r) for r in rows])
                sira = ["0-19", "20-39", "40-59", "60-79", "80-100"]
                df["bucket"] = pd.Categorical(df["bucket"], categories=sira, ordered=True)
                return df.sort_values("bucket").reset_index(drop=True)
    except Exception:
        pass
    return pd.DataFrame(columns=["bucket", "adet"])


@st.cache_data(ttl=60)
def load_missing_field_analysis() -> pd.DataFrame:
    """Eksik alan analizi: her alanın eksiklik oranı (doluluk analizinin tersi)."""
    result: list[dict[str, Any]] = []
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT COUNT(*) as total FROM companies "
                "WHERE is_ankara=TRUE AND is_osb_member=TRUE"
            )).mappings().first()
            total = (row["total"] or 1) if row else 1

            for col, label in _QUALITY_FIELDS.items():
                try:
                    cnt_row = conn.execute(text(
                        f"SELECT COUNT(*) as cnt FROM companies "
                        f"WHERE is_ankara=TRUE AND is_osb_member=TRUE "
                        f"AND ({col} IS NULL OR {col} = '')"
                    )).mappings().first()
                    eksik = cnt_row["cnt"] if cnt_row else 0
                except Exception:
                    eksik = 0
                result.append({
                    "Alan": label,
                    "Eksik": eksik,
                    "Toplam": total,
                    "Eksiklik (%)": round(eksik / max(total, 1) * 100, 1),
                })
    except Exception:
        for label in _QUALITY_FIELDS.values():
            result.append({"Alan": label, "Eksik": 0, "Toplam": 0, "Eksiklik (%)": 0})
    return pd.DataFrame(result)


@st.cache_data(ttl=60)
def load_risky_companies(limit: int = 100) -> pd.DataFrame:
    """Kalite riski (QS < 30) firmaları — eksik alan özetiyle birlikte."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT company_id, legal_name, trade_name, data_quality_score,
                       CASE WHEN primary_phone IS NULL OR primary_phone='' THEN 1 ELSE 0 END as e_tel,
                       CASE WHEN primary_email IS NULL OR primary_email='' THEN 1 ELSE 0 END as e_email,
                       CASE WHEN website_domain IS NULL OR website_domain='' THEN 1 ELSE 0 END as e_web,
                       CASE WHEN tax_number IS NULL OR tax_number='' THEN 1 ELSE 0 END as e_vkn,
                       CASE WHEN nace_code IS NULL OR nace_code='' THEN 1 ELSE 0 END as e_nace,
                       CASE WHEN adres IS NULL OR adres='' THEN 1 ELSE 0 END as e_adres
                FROM companies
                WHERE is_ankara=TRUE AND is_osb_member=TRUE
                  AND data_quality_score < :esik
                ORDER BY data_quality_score ASC
                LIMIT :limit
            """), {"esik": _RISK_ESIGI, "limit": limit}).mappings().all()
            if rows:
                df = pd.DataFrame([dict(r) for r in rows])

                def _eksik_ozet(r: pd.Series) -> str:
                    eksikler = []
                    if r["e_tel"]:
                        eksikler.append("Tel")
                    if r["e_email"]:
                        eksikler.append("Email")
                    if r["e_web"]:
                        eksikler.append("Web")
                    if r["e_vkn"]:
                        eksikler.append("VKN")
                    if r["e_nace"]:
                        eksikler.append("NACE")
                    if r["e_adres"]:
                        eksikler.append("Adres")
                    return ", ".join(eksikler) if eksikler else "-"

                df["Eksik Alanlar"] = df.apply(_eksik_ozet, axis=1)
                df = df.drop(columns=["e_tel", "e_email", "e_web", "e_vkn", "e_nace", "e_adres"])
                df["data_quality_score"] = df["data_quality_score"].apply(
                    lambda x: round(float(x), 1) if x is not None else 0
                )
                df = df.rename(columns={
                    "company_id": "Firma ID", "legal_name": "Unvan",
                    "trade_name": "Ticari Ad", "data_quality_score": "Kalite Skoru",
                })
                return df
    except Exception:
        pass
    return pd.DataFrame(columns=["Firma ID", "Unvan", "Ticari Ad", "Kalite Skoru", "Eksik Alanlar"])


def generate_improvement_suggestions(
    missing_df: pd.DataFrame, overview: dict[str, Any]
) -> list[dict[str, str]]:
    """Eksik alan oranlarına ve genel risk oranına göre kural bazlı iyileştirme önerileri üretir."""
    suggestions: list[dict[str, str]] = []
    if not missing_df.empty:
        for _, row in missing_df.sort_values("Eksiklik (%)", ascending=False).iterrows():
            oran = row["Eksiklik (%)"]
            if oran >= 50:
                oncelik = "🔴 Yüksek"
            elif oran >= 25:
                oncelik = "🟠 Orta"
            elif oran >= 10:
                oncelik = "🟡 Düşük"
            else:
                continue
            suggestions.append({
                "Öncelik": oncelik,
                "Alan": row["Alan"],
                "Eksiklik (%)": f"%{oran}",
                "Öneri": f"{row['Alan']} alanı firmaların %{oran}'inde eksik — "
                         f"zenginleştirme/scraping kaynağı önceliklendirilmeli.",
            })

    riskli_oran = overview.get("riskli_orani", 0)
    if riskli_oran >= 10:
        suggestions.insert(0, {
            "Öncelik": "🔴 Yüksek",
            "Alan": "Genel Kalite",
            "Eksiklik (%)": f"%{riskli_oran}",
            "Öneri": f"Firmaların %{riskli_oran}'i risk eşiğinin (QS<{_RISK_ESIGI}) altında — "
                     f"toplu yeniden zenginleştirme (recalc + scrape) planlanmalı.",
        })
    return suggestions


# ---------------------------------------------------------------------------
# Grafik Fonksiyonları
# ---------------------------------------------------------------------------

def _chart_distribution(dist_df: pd.DataFrame) -> None:
    if dist_df.empty:
        st.info("Skor dağılımı verisi bulunamadı.")
        return
    try:
        import plotly.express as px
        fig = px.bar(
            dist_df, x="bucket", y="adet",
            title="Kalite Skoru Dağılımı (Bucket Bazlı)",
            labels={"bucket": "Skor Aralığı", "adet": "Firma Sayısı"},
            color="adet", color_continuous_scale="RdYlGn",
        )
        fig.update_layout(height=320, margin=dict(t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        st.bar_chart(dist_df.set_index("bucket")["adet"], use_container_width=True)


def _chart_missing_fields(missing_df: pd.DataFrame) -> None:
    if missing_df.empty:
        st.info("Eksik alan verisi bulunamadı.")
        return
    col_table, col_chart = st.columns([1, 1])
    with col_table:
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
    with col_chart:
        try:
            import plotly.express as px
            fig = px.bar(
                missing_df, x="Alan", y="Eksiklik (%)",
                title="Alan Bazlı Eksiklik Oranları (%)",
                color="Eksiklik (%)", color_continuous_scale="Reds",
            )
            fig.update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.bar_chart(missing_df.set_index("Alan")["Eksiklik (%)"], use_container_width=True)


# ---------------------------------------------------------------------------
# Render Fonksiyonu
# ---------------------------------------------------------------------------

def render_quality_tab() -> None:
    """P7-31: Admin Panel Faz 2 — Veri Kalitesi Özeti sekmesi."""

    st.subheader("🧪 Veri Kalitesi Özeti")
    st.caption(
        "Kalite skoru dağılımı, eksik alan analizi, iyileştirme önerileri — "
        "Son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    if st.button("🔄 Yenile", key="admin-quality-refresh"):
        st.cache_data.clear()
        st.rerun()

    overview = load_quality_overview()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📦 Toplam Firma", f"{overview['toplam_firma']:,}")
    with c2:
        st.metric("📊 Ortalama Skor", f"{overview['ortalama_skor']:.1f}")
    with c3:
        st.metric("📐 Medyan Skor", f"{overview['medyan_skor']:.1f}")
    with c4:
        st.metric(
            "⚠️ Riskli Firma (QS<30)",
            f"{overview['riskli_sayisi']:,}",
            f"%{overview['riskli_orani']} oranında" if overview["riskli_sayisi"] else None,
        )

    st.divider()
    st.subheader("📈 Kalite Skoru Dağılımı")
    dist_df = load_score_distribution()
    _chart_distribution(dist_df)

    st.divider()
    st.subheader("🔍 Eksik Alan Analizi")
    missing_df = load_missing_field_analysis()
    _chart_missing_fields(missing_df)

    st.divider()
    st.subheader("💡 İyileştirme Önerileri")
    suggestions = generate_improvement_suggestions(missing_df, overview)
    if suggestions:
        st.dataframe(pd.DataFrame(suggestions), use_container_width=True, hide_index=True)
    else:
        st.success("Kritik eksiklik tespit edilmedi — veri kalitesi genel olarak iyi durumda.")

    st.divider()
    st.subheader(f"🚨 Kalite Riski Filtreleme (QS < {_RISK_ESIGI})")
    limit = st.slider(
        "Gösterilecek maksimum firma sayısı",
        min_value=10, max_value=500, value=100, step=10,
        key="quality_risk_limit",
    )
    risky_df = load_risky_companies(limit=limit)
    if risky_df.empty:
        st.success(f"QS<{_RISK_ESIGI} aralığında firma bulunamadı — risk yok.")
    else:
        st.caption(f"{len(risky_df)} firma listeleniyor (limit: {limit})")
        st.dataframe(risky_df, use_container_width=True, hide_index=True)
