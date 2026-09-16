# -*- coding: utf-8 -*-
"""Müşteri Yönetimi ana sayfa — 6 alt sekme (NAV-IA-02).

Alt sekmeler:
1. Kullanıcılar & Onay (musteriler + kullanicilar)
2. Paket & Kredi (admin_extras kredi formu + tier selectbox)
3. Giriş Etkinliği (DATA-LOG-01 — yakında)
4. Aramalar (DATA-LOG-01 — yakında)
5. Destek (admin_destek.render_destek_tab)
6. Dışa Aktar (admin_export.render_export_tab)
"""
from __future__ import annotations

import streamlit as st
from company_master.ui import PageHeader
from company_master.ui.components.page import Section

from web_dashboard.tabs import admin_destek, admin_export
from web_dashboard.tabs.admin_extras import render_user_management, TIER_SECIMLERI


BOLUMLER = (
    Section("Kullanıcılar & Onay", "Onay bekleyen kullanıcılar ve paket/kredi.", ikon="👥"),
    Section("Paket & Kredi", "Paket tanımları, kredi yükleme ve tier seçimi.", ikon="📦"),
    Section("Giriş Etkinliği", "Kim ne zaman giriş yaptı — DATA-LOG-01.", ikon="🔑"),
    Section("Aramalar", "Arama kayıtları ve filtreleme — DATA-LOG-01.", ikon="🔍"),
    Section("Destek", "Ticket listesi, olusturma ve durum degistirme.", ikon="🎫"),
    Section("Dışa Aktar", "Veri dışa aktarma ve raporlar.", ikon="💾"),
)

__all__ = ["render_musteri_yonetimi_tab", "BOLUMLER"]


def render_musteri_yonetimi_tab() -> None:
    """Müşteri Yönetimi üst sayfası — 6 alt sekme."""
    PageHeader(
        "Müşteri Yönetimi",
        "Kullanıcı onayları, paket/kredi, giriş etkinliği, aramalar, destek ve dışa aktarma.",
        ust_etiket="İş · Yönetim",
        ikon="👥",
    ).render()

    sekme_basliklari = [b.baslik for b in BOLUMLER]
    secim = st.tabs(sekme_basliklari)

    with secim[0]:
        _kullanicilar_onay()
    with secim[1]:
        _paket_kredi()
    with secim[2]:
        _giris_aktinligi()
    with secim[3]:
        _aramalar()
    with secim[4]:
        _destek()
    with secim[5]:
        _dissa_aktar()


def _kullanicilar_onay() -> None:
    BOLUMLER[0].render()
    render_user_management()


def _paket_kredi() -> None:
    BOLUMLER[1].render()
    from web_dashboard.tabs.admin_extras import get_api, post_api  # noqa: F401

    try:
        data = get_api("/api/admin/categories")
        if isinstance(data, dict):
            items = data.get("items", [])
            if items:
                st.dataframe(data=items, width="stretch", hide_index=True)
            else:
                st.info("Kategori kaydı yok.")
    except Exception:
        st.info("Kategori verisi yüklenemedi.")

    st.divider()
    st.caption("Kredi yükleme — Kullanıcı ID'ye kredi atar.")
    with st.form("kredi_formu_musteri"):
        col1, col2 = st.columns(2)
        with col1:
            kredi_user_id = st.text_input("Kullanıcı ID", key="musteri_kredi_uid")
        with col2:
            kredi_miktar = st.number_input("Kredi Miktarı", min_value=1, value=50, key="musteri_kredi_miktar")
        tier_secili = st.selectbox(
            "Tier",
            options=TIER_SECIMLERI,
            index=0,
            key="musteri_tier_select",
            label_visibility="collapsed",
        )
        gönder = st.form_submit_button("Kredi Yükle")
        if gönder and kredi_user_id:
            try:
                post_api(
                    "/api/admin/credit",
                    json={"user_id": kredi_user_id, "amount": kredi_miktar, "tier": tier_secili},
                )
                st.success(f"{kredi_miktar} kredi yüklendi ({tier_secili}).")
            except Exception as exc:
                st.error(f"Kredi yükleme başarısız: {exc}")


def _giris_aktinligi() -> None:
    BOLUMLER[2].render()
    st.info("Yakında — DATA-LOG-01 login_events tablosu gelene kadar.")


def _aramalar() -> None:
    BOLUMLER[3].render()
    st.info("Yakında — DATA-LOG-01 search_log tablosu gelene kadar.")


def _destek() -> None:
    BOLUMLER[4].render()
    try:
        admin_destek.render_destek_tab()
    except Exception as exc:
        st.error(f"Destek yüklenemedi: {exc}")


def _dissa_aktar() -> None:
    BOLUMLER[5].render()
    try:
        admin_export.render_export_tab()
    except Exception as exc:
        st.error(f"Dışa aktarım yüklenemedi: {exc}")
