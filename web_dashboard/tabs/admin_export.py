# -*- coding: utf-8 -*-
"""P7-40: Export fonksiyonu — KPI ve veri tablolarindan CSV/Excel indir.

Kullanim:
    - KPI metriklerini CSV/Excel olarak indir
    - Veri tablolarini filtreli olarak export et
    - Audit log export
    - Task board export
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
def load_export_data(query_type: str) -> pd.DataFrame | None:
    """Farkli veri turleri icin DataFrame olustur."""
    engine = get_engine()

    if query_type == "kpi":
        try:
            with engine.connect() as conn:
                row = conn.execute(text("""
                    SELECT COUNT(*) as total_firma,
                           AVG(data_quality_score) as avg_quality,
                           SUM(CASE WHEN tax_number IS NOT NULL AND tax_number != '' THEN 1 ELSE 0 END) as with_vkn,
                           SUM(CASE WHEN website_domain IS NOT NULL AND website_domain != '' THEN 1 ELSE 0 END) as with_web,
                           SUM(CASE WHEN primary_phone IS NOT NULL AND primary_phone != '' THEN 1 ELSE 0 END) as with_phone,
                           SUM(CASE WHEN primary_email IS NOT NULL AND primary_email != '' THEN 1 ELSE 0 END) as with_email
                    FROM companies
                    WHERE is_ankara=TRUE
                """)).mappings().first()
                if row:
                    return pd.DataFrame([dict(row)])
        except Exception:
            pass
        return pd.DataFrame([{
            "toplam_firma": 0, "ortalama_kalite": 0,
            "vkn_var": 0, "web_var": 0, "telefon_var": 0, "email_var": 0,
        }])

    elif query_type == "companies":
        try:
            with engine.connect() as conn:
                rows = conn.execute(text("""
                    SELECT company_id, legal_name, tax_number, company_type, status,
                           data_quality_score, entity_confidence, is_ankara, is_osb_member,
                           primary_phone, primary_email, website_domain, nace_code,
                           establishment_date, updated_at
                    FROM companies
                    WHERE is_ankara=TRUE
                    LIMIT 5000
                """)).mappings().all()
                return pd.DataFrame([dict(r) for r in rows])
        except Exception:
            return None

    elif query_type == "audit":
        try:
            with engine.connect() as conn:
                rows = conn.execute(text("""
                    SELECT id, timestamp, level, logger_name, message, extra,
                           user_id, session_id, ip_address, action, resource_type,
                           resource_id, result, created_at
                    FROM audit_logs
                    ORDER BY timestamp DESC
                    LIMIT 10000
                """)).mappings().all()
                return pd.DataFrame([dict(r) for r in rows])
        except Exception:
            return None

    elif query_type == "tasks":
        try:
            import json
            board_path = ROOT / "data" / "orchestrator" / "task_board.json"
            if board_path.exists():
                tasks = json.loads(board_path.read_text(encoding="utf-8"))
                return pd.DataFrame(tasks)
        except Exception:
            pass
        return None

    return None


def render_export_tab() -> None:
    """Export sekmesini gosterir."""
    st.subheader("📥 Veri Export")

    export_type = st.radio(
        "Export Turu",
        ["KPI Metrikleri", "Firma Verileri", "Audit Log", "Gorev Panosu"],
        horizontal=True,
    )

    type_map = {
        "KPI Metrikleri": "kpi",
        "Firma Verileri": "companies",
        "Audit Log": "audit",
        "Gorev Panosu": "tasks",
    }

    query_type = type_map.get(export_type, "kpi")
    df = load_export_data(query_type)

    if df is not None and not df.empty:
        st.success(f"✅ {len(df)} kayit yuklendi")
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)

        col_csv, col_excel = st.columns(2)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with col_csv:
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📄 CSV İndir",
                data=csv,
                file_name=f"export_{query_type}_{timestamp}.csv",
                mime="text/csv",
            )

        with col_excel:
            try:
                excel_buffer = df.to_excel(index=False, engine="openpyxl")
                st.download_button(
                    label="📊 Excel İndir",
                    data=excel_buffer,
                    file_name=f"export_{query_type}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except ImportError:
                st.warning("openpyxl kurulu degil. CSV kullanin.")
    else:
        st.info("Export edilecek veri bulunamadi.")
