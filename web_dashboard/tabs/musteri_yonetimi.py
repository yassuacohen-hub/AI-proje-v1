# -*- coding: utf-8 -*-
"""Müşteri Yönetimi ana sayfa — 6 alt sekme (NAV-IA-02).

Alt sekmeler:
1. Kullanıcılar & Onay (musteriler + kullanicilar)
2. Paket & Kredi (admin_extras kredi formu + tier selectbox)
3. Giriş Etkinliği (DATA-LOG-01 — gerçek veri)
4. Aramalar (DATA-LOG-01 — gerçek veri)
5. Destek (admin_destek.render_destek_tab)
6. Dışa Aktar (admin_export.render_export_tab)
"""
from __future__ import annotations

import streamlit as st
from company_master.ui import PageHeader
from company_master.ui.components.page import Section
from sqlalchemy import text

from company_master.db.connection import get_engine

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
    st.info("Kullanıcılar & Onay — placeholder")


def _paket_kredi() -> None:
    BOLUMLER[1].render()
    from web_dashboard.tabs.admin_extras import get_api, post_api

    try:
        data = get_api("/api/admin/categories")
    except Exception:
        data = None
    if data:
        st.success(f"Kategoriler yüklendi: {len(data) if isinstance(data, list) else 'var'}")
    else:
        st.warning("Kategori yüklenemedi.")


def _giris_aktinligi() -> None:
    BOLUMLER[2].render()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT ts, email_masked, ip_masked, success, method, path "
                    "FROM login_events ORDER BY ts DESC LIMIT 50"
                )
            ).mappings().all()
        if rows:
            st.dataframe(
                [
                    {
                        "Zaman": r["ts"],
                        "E-posta": r["email_masked"],
                        "IP": r["ip_masked"],
                        "Basarili": "✅" if r["success"] else "❌",
                        "Yontem": r["method"],
                        "Yol": r["path"],
                    }
                    for r in rows
                ]
            )
        else:
            st.info("Henüz giriş kaydı yok.")
    except Exception:
        st.info("Giriş etkinliği tablosu henüz oluşturulmamış.")


def _aramalar() -> None:
    BOLUMLER[3].render()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT ts, email_masked, query, result_count "
                    "FROM search_events ORDER BY ts DESC LIMIT 50"
                )
            ).mappings().all()
        if rows:
            st.dataframe(
                [
                    {
                        "Zaman": r["ts"],
                        "E-posta": r["email_masked"],
                        "Sorgu": r["query"],
                        "Sonuc": r["result_count"],
                    }
                    for r in rows
                ]
            )
        else:
            st.info("Henüz arama kaydı yok.")
    except Exception:
        st.info("Arama kaydı tablosu henüz oluşturulmamış.")


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
