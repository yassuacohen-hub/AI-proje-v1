# -*- coding: utf-8 -*-
"""P7-41: Arama ve filtreleme — Tum sekmelerde global arama.

Tum dashboard sekmelerinde ortak arama/filtreleme:
- Global arama (firma adi, VKN, telefon, e-posta)
- Kalite skoru araligi filtresi
- Kaynak tipi filtresi
- Sonuc sayisi gosterimi
"""
from __future__ import annotations

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


@st.cache_data(ttl=60)
def search_companies(
    query: str = "",
    score_min: int = 0,
    score_max: int = 100,
    source: str = "",
    limit: int = 100,
) -> pd.DataFrame | None:
    """Global arama — tum alanlarda arama yap."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            where: list[str] = []
            params: dict[str, Any] = {}

            if query:
                where.append(
                    "(legal_name ILIKE :q OR tax_number ILIKE :q OR primary_email ILIKE :q "
                    "OR primary_phone ILIKE :q OR description ILIKE :q OR nace_code ILIKE :q)"
                )
                params["q"] = f"%{query}%"

            where.append("data_quality_score >= :score_min")
            params["score_min"] = score_min
            where.append("data_quality_score <= :score_max")
            params["score_max"] = score_max

            if source:
                where.append("source_record_id IN (SELECT source_record_id FROM source_records WHERE source_name = :src)")
                params["src"] = source

            where_sql = f" WHERE {' AND '.join(where)}" if where else ""
            sql = f"""
                SELECT company_id, legal_name, trade_name, tax_number, company_type,
                       status, data_quality_score, entity_confidence, primary_phone,
                       primary_email, website_domain, nace_code, is_ankara, is_osb_member,
                       updated_at
                FROM companies
                {where_sql}
                ORDER BY data_quality_score DESC
                LIMIT :limit
            """
            params["limit"] = limit

            rows = conn.execute(text(sql), params).mappings().all()
            if rows:
                df = pd.DataFrame([dict(r) for r in rows])
                df["data_quality_score"] = df["data_quality_score"].apply(lambda x: round(float(x), 1) if x is not None else 0)
                return df
    except Exception as e:
        st.warning(f"Arama hatasi: {e}")

    return None


@st.cache_data(ttl=300)
def get_source_names() -> list[str]:
    """Kaynak isimlerini getir."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT source_name FROM sources ORDER BY source_name
            """)).mappings().all()
            return [r["source_name"] for r in rows]
    except Exception:
        return []


def render_search_tab() -> None:
    """Global arama/filtreleme sekmesini gosterir."""
    st.subheader("🔍 Global Arama ve Filtreleme")

    sources = get_source_names()

    col_search, col_filter = st.columns([3, 2])
    with col_search:
        query = st.text_input(
            "🔍 Firma Ara",
            placeholder="Firma adi, VKN, telefon, e-posta, NACE, aciklama...",
            key="global_search",
        )

    with col_filter:
        score_range = st.slider(
            "Kalite Skoru Araligi",
            0, 100, (0, 100),
        )

    col_source, col_limit = st.columns(2)
    with col_source:
        source = st.selectbox("Kaynak Tipi", ["Tümü"] + sources, key="source_filter")
    with col_limit:
        limit = st.selectbox("Sonuc Sayisi", [50, 100, 200, 500], index=1, key="limit_filter")

    if query or score_range != (0, 100) or source != "Tümü":
        df = search_companies(
            query=query,
            score_min=score_range[0],
            score_max=score_range[1],
            source=source if source != "Tümü" else "",
            limit=limit,
        )
        if df is not None and not df.empty:
            st.success(f"✅ {len(df)} sonuc bulundu")

            col1, col2 = st.columns([3, 1])
            with col1:
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col2:
                st.metric("Toplam Sonuc", len(df))
                avg_qs = df["data_quality_score"].mean()
                st.metric("Ort. Kalite", f"{avg_qs:.1f}/100")
                low_qs = len(df[df["data_quality_score"] < 30])
                st.metric("Dusuk Kalite", f"{low_qs}")

            st.divider()
            qs_buckets = {
                "80-100 (Yüksek)": len(df[df["data_quality_score"] >= 80]),
                "60-79 (Iyi)": len(df[(df["data_quality_score"] >= 60) & (df["data_quality_score"] < 80)]),
                "40-59 (Orta)": len(df[(df["data_quality_score"] >= 40) & (df["data_quality_score"] < 60)]),
                "20-39 (Düşük)": len(df[(df["data_quality_score"] >= 20) & (df["data_quality_score"] < 40)]),
                "0-19 (Çok Düşük)": len(df[df["data_quality_score"] < 20]),
            }
            st.bar_chart(pd.Series(qs_buckets), use_container_width=True)
        elif df is not None:
            st.info("Sonuc bulunamadi.")
    else:
        st.info("🔍 Arama veya filtreleme yapin...")
