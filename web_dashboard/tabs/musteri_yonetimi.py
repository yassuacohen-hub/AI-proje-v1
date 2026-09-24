# -*- coding: utf-8 -*-
"""Müşteri Yönetimi ana sayfa — 6 alt sekme (NAV-IA-02).

Alt sekmeler:
1. Kullanıcılar & Onay (musteriler + kullanicilar)
2. Paket & Kredi (admin_extras kredi formu + tier selectbox)
3. Giriş Etkinliği (DATA-LOG-01 — gerçek veri)
4. Aramalar (DATA-LOG-01 — gerçek veri)
5. Destek (admin_destek.render_destek_tab)
6. Dışa Aktar (admin_export.render_export_tab)

UI-ADMIN-CHURN-KOLON-07: Churn risk kolonu (SSOT §9 K1, API-ADMIN-CHURN-FONKSIYON-06).
"""
from __future__ import annotations

import streamlit as st
from company_master.ui import PageHeader
from company_master.ui.components.page import Section
from sqlalchemy import text

from company_master.db.connection import get_engine

from web_dashboard.tabs import admin_destek, admin_export
from web_dashboard.tabs.admin_extras import render_user_management, TIER_SECIMLERI

from company_master.settings.user_settings import kvkk_maske_acik  # noqa: E402
from scripts.dash04_api_client import get_api, post_api  # noqa: E402
from company_master.churn import risk_etiketi  # noqa: E402 (UI-ADMIN-CHURN-KOLON-07)


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
    """Kullanıcılar & Onay — onay bekleyen kullanıcılar listesi + tier seçimi + onaylama."""
    BOLUMLER[0].render()

    token = st.session_state.get("admin_token")
    if not token:
        st.warning("Lütfen giriş yapın")
        return

    try:
        # Onay bekleyen kullanıcıları ve kategorileri yükle
        pending = get_api("/api/admin/pending", token=token)
        categories = get_api("/api/admin/categories", token=token)
    except Exception as exc:
        st.error(f"Veri yüklenemedi: {exc}")
        return

    # Onay bekleyen kullanıcılar
    if isinstance(pending, dict):
        bekleyen = pending.get("bekleyen", [])
        if bekleyen:
            Section("Onay Bekleyen Kullanıcılar").render()
            for user in bekleyen:
                with st.container():
                    cols = st.columns([4, 1])
                    with cols[0]:
                        tiers = TIER_SECIMLERI
                        default_tier = user.get("tier", "terminal")
                        try:
                            default_index = tiers.index(default_tier)
                        except ValueError:
                            default_index = 0
                        selected_tier = st.selectbox(
                            "Tier",
                            options=tiers,
                            index=default_index,
                            key=f"tier_select_{user.get('user_id', '')}",
                            label_visibility="collapsed"
                        )
                        st.write(
                            f"**{user.get('email', '')}** — {user.get('company_name', '')} ({user.get('tier', '')})"
                        )
                    with cols[1]:
                        if st.button("Onayla", key=f"approve_{user.get('user_id', '')}", type="primary"):
                            try:
                                post_api(
                                    "/api/admin/approve",
                                    json={"user_id": user.get("user_id", ""), "tier": selected_tier},
                                    token=token,
                                )
                                st.success(f"{user.get('email', '')} onaylandı ({selected_tier} tier)")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Onaylama başarısız: {e}")
        else:
            st.info("Onay bekleyen kullanıcı yok.")

        # Son onaylı kullanıcılar
        onayli_son = pending.get("onayli_son", [])
        if onayli_son:
            Section("Son Onaylanan Kullanıcılar").render()
            import pandas as pd
            st.dataframe(pd.DataFrame(onayli_son), width="stretch", hide_index=True)
        else:
            st.info("Son onaylı kullanıcı yok.")

    # Kategoriler
    if isinstance(categories, dict):
        items = categories.get("items", [])
        if items:
            Section("Paket Kategorileri").render()
            import pandas as pd
            st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
        else:
            st.info("Kategori kaydı yok.")


def _paket_kredi() -> None:
    """Paket & Kredi — kredi yükleme formu + kategori yönetimi."""
    BOLUMLER[1].render()

    token = st.session_state.get("admin_token")
    if not token:
        st.warning("Lütfen giriş yapın")
        return

    Section("Kredi Yükleme").render()

    with st.form("kredi_formu"):
        col1, col2 = st.columns(2)
        with col1:
            kredi_user_id = st.text_input("Kullanıcı ID", placeholder="Örn: 123e4567-e89b-12d3-a456-426614174000")
        with col2:
            kredi_miktar = st.number_input("Kredi Miktarı", min_value=1, value=50)
        if st.form_submit_button("Kredi Yükle", type="primary") and kredi_user_id:
            try:
                post_api(
                    "/api/admin/credit",
                    json={"user_id": kredi_user_id, "amount": kredi_miktar},
                    token=token,
                )
                st.success(f"{kredi_miktar} kredi yüklendi.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Kredi yükleme başarısız: {e}")

    st.divider()
    Section("Kategori Yönetimi").render()

    try:
        categories = get_api("/api/admin/categories", token=token)
    except Exception as exc:
        st.error(f"Kategoriler yüklenemedi: {exc}")
        return

    if isinstance(categories, dict):
        items = categories.get("items", [])
        if items:
            import pandas as pd
            st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
        else:
            st.info("Kategori kaydı yok.")

    # Yeni kategori ekleme formu
    with st.expander("➕ Yeni Kategori Ekle"):
        with st.form("yeni_kategori_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                cat_name = st.text_input("Kategori Adı", placeholder="Örn: Premium Paket")
            with col2:
                cat_credits = st.number_input("Kredi Miktarı", min_value=1, value=100)
            with col3:
                cat_desc = st.text_input("Açıklama", placeholder="İsteğe bağlı")
            if st.form_submit_button("Kategori Oluştur", type="primary") and cat_name:
                try:
                    post_api(
                        "/api/admin/categories",
                        json={"name": cat_name, "credits": cat_credits, "description": cat_desc},
                        token=token,
                    )
                    st.success(f"Kategori '{cat_name}' oluşturuldu.")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Kategori oluşturma başarısız: {e}")


def _giris_aktinligi() -> None:
    BOLUMLER[2].render()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Giriş etkinliği (login_events)
            login_rows = conn.execute(
                text(
                    "SELECT ts, email_masked, ip_masked, success, method, path "
                    "FROM login_events ORDER BY ts DESC LIMIT 50"
                )
            ).mappings().all()
        
        if login_rows:
            _kullanici_id = st.session_state.get("kullanici_id", "misafir")
            if not isinstance(_kullanici_id, str) or not _kullanici_id.strip():
                _kullanici_id = "misafir"
            if not kvkk_maske_acik(_kullanici_id):
                st.caption("Maskeleme kapalı — yetki gerektirir")
            st.dataframe(
                [
                    {
                        "Zaman": r["ts"],
                        "E-posta": r["email_masked"],
                        "IP": r["ip_masked"],
                        "Başarılı": "✅" if r["success"] else "❌",
                        "Yöntem": r["method"],
                        "Yol": r["path"],
                    }
                    for r in login_rows
                ]
            )
        else:
            st.info("Henüz giriş kaydı yok.")
    except Exception:
        st.info("Giriş etkinliği tablosu henüz oluşturulmamış.")

    # UI-ADMIN-CHURN-KOLON-07: Churn risk listesi (users.last_login)
    st.divider()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            churn_rows = conn.execute(
                text(
                    "SELECT email, last_login, created_at "
                    "FROM users ORDER BY last_login DESC NULLS LAST"
                )
            ).mappings().all()
        if churn_rows:
            from datetime import date
            bugun = date.today()
            churn_data = []
            for r in churn_rows:
                risk = risk_etiketi(r["last_login"], bugun) if r["last_login"] else risk_etiketi(None, bugun)
                churn_data.append({
                    "E-posta": r["email"],
                    "Son Giriş": r["last_login"] or "—",
                    "Kayıt Tarihi": r["created_at"],
                    "Churn Riski": risk,
                })
            st.caption("Churn Risk: 'Yok' = son 14 günde giriş var, 'Düşük' = 14+ gün veya giriş yok (tek sinyal last_login)")
            st.dataframe(churn_data, width="stretch", hide_index=True)
        else:
            st.info("Kullanıcı kaydı yok.")
    except Exception:
        st.info("Churn risk verisi yüklenemedi.")


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
            _kullanici_id = st.session_state.get("kullanici_id", "misafir")
            if not isinstance(_kullanici_id, str) or not _kullanici_id.strip():
                _kullanici_id = "misafir"
            if not kvkk_maske_acik(_kullanici_id):
                st.caption("Maskeleme kapalı — yetki gerektirir")
            st.dataframe(
                [
                    {
                        "Zaman": r["ts"],
                        "E-posta": r["email_masked"],
                        "Sorgu": r["query"],
                        "Sonuç": r["result_count"],
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
