# -*- coding: utf-8 -*-
"""Proje Yönetimi sayfası — 5 alt sekme (NAV-IA-03).

Alt sekmeler (Karar Defteri üstte):
1. Karar Defteri (admin_panel)
2. 9Router / Abrakadabra (abrakadabra)
3. Denetim İzi (admin_audit)
4. Hata Yönetimi (admin_errors)
5. DLQ (admin_dlq)
"""
from __future__ import annotations

import streamlit as st
from company_master.ui import PageHeader
from company_master.ui.components.page import Section

import web_dashboard.tabs.admin_panel as admin_panel
import web_dashboard.tabs.abrakadabra as abrakadabra
import web_dashboard.tabs.admin_audit as admin_audit
import web_dashboard.tabs.admin_errors as admin_errors
import web_dashboard.tabs.admin_dlq as admin_dlq


BOLUMLER = (
    Section("Karar Defteri", "Sistem kararları ve denetim kayıtları.", ikon="📔"),
    Section("9Router / Abrakadabra", "AI sohbet ve analiz asistanı.", ikon="🤖"),
    Section("Denetim İzi", "Dosya kilitleri, handoff ve tetikleyici günlüğü.", ikon="📋"),
    Section("Hata Yönetimi", "Hata yönetimi ve sorun giderme.", ikon="⚠️"),
    Section("DLQ", "Kuyruk hataları ve ölü harf sırası.", ikon="⛔"),
)

__all__ = ["render_proje_yonetimi_tab", "BOLUMLER"]


def render_proje_yonetimi_tab() -> None:
    """Proje Yönetimi üst sayfası — 5 alt sekme."""
    PageHeader(
        "Proje Yönetimi",
        "Karar defteri, 9Router, denetim izi, hatalar ve DLQ.",
        ust_etiket="İş · Yönetim",
        ikon="📊",
    ).render()

    sekme_basliklari = [b.baslik for b in BOLUMLER]
    secim = st.tabs(sekme_basliklari)

    with secim[0]:
        BOLUMLER[0].render()
        admin_panel.render_decision_tab()
    with secim[1]:
        BOLUMLER[1].render()
        abrakadabra.render_abrakadabra_tab()
    with secim[2]:
        BOLUMLER[2].render()
        admin_audit.render_audit_tab()
    with secim[3]:
        BOLUMLER[3].render()
        admin_errors.render_errors_tab()
    with secim[4]:
        BOLUMLER[4].render()
        admin_dlq.render_dlq_tab()
