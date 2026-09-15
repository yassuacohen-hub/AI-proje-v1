# -*- coding: utf-8 -*-
"""Tenant Health Score dashboard (Streamlit)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from company_master.tenant.health import esik_dokumani, hesapla
from company_master.tenant.model import TenantContext


def dashboard_kart(tenant_health: Any) -> None:
    """Tenant Health Score dashboard kartı (Streamlit)."""
    renk_map = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
    icon = renk_map.get(tenant_health.band, "⚪")

    st.markdown(f"### {icon} Tenant Health Score — {tenant_health.tenant_id}")
    st.metric(
        label="Genel Sağlık Skoru",
        value=f"{tenant_health.overall:.1f}",
        help=f"Bant: {tenant_health.band.upper()}",
    )

    cols = st.columns(4)
    component_labels = {
        "data_quality": "📊 Veri Kalitesi",
        "source_reliability": "🔗 Kaynak Güvenilirliği",
        "coverage": "📋 Segment Uygunluk",
        "activity": "⚡ Etkinlik Tazeliği",
    }
    for i, (key, label) in enumerate(component_labels.items()):
        cols[i].metric(label, f"{tenant_health.components.get(key, 0):.1f}")


def tenant_health_dashboard(tenant_ctx: TenantContext, companies: list[dict[str, Any]]) -> None:
    """Tam Tenant Health dashboard bileşeni (Streamlit)."""
    tenant_health = hesapla(tenant_ctx, companies)
    dashboard_kart(tenant_health)

    with st.expander("📐 Eşik Bilgileri"):
        st.text(esik_dokumani())
