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
from datetime import date

from company_master.db.connection import get_engine

from web_dashboard.tabs import admin_destek, admin_export
from web_dashboard.tabs.admin_extras import render_user_management

from company_master.settings.user_settings import kvkk_maske_acik  # noqa: E402
from scripts.dash04_api_client import get_api, post_api  # noqa: E402
from company_master.churn import risk_etiketi, risk_etiketi_3sinyal  # noqa: E402 (UI-ADMIN-CHURN-KOLON-07, API-ADMIN-CHURN-3SINYAL-16)

# UI-ADMIN-UPSELL-22: Upsell aday listesi
_UPSELL_DOYGUNLUK_ESIK = 0.85  # %85 doygunluk eşiği

# Tier kota limitleri (kredi bazlı)
_TIER_KOTALAR = {
    "terminal": 100,      # Terminal: 100 kredi/ay
    "strategic": 500,     # Strategic: 500 kredi/ay
    "enterprise": -1,     # Enterprise: sınırsız (credit_balance = -1)
}


BOLUMLER = (
    Section("Kullanıcılar & Onay", "Onay bekleyen kullanıcılar ve paket/kredi.", ikon="👥"),
    Section("Paket & Kredi", "Paket tanımları, kredi yükleme ve tier seçimi.", ikon="📦"),
    Section("Giriş Etkinliği", "Kim ne zaman giriş yaptı — DATA-LOG-01.", ikon="🔑"),
    Section("Aramalar", "Arama kayıtları ve filtreleme — DATA-LOG-01.", ikon="🔍"),
    Section("Destek", "Ticket listesi, olusturma ve durum degistirme.", ikon="🎫"),
    Section("Dışa Aktar", "Veri dışa aktarma ve raporlar.", ikon="💾"),
    Section("Upsell Adayları", "Kota doygunluğu yüksek, düşük churn riskli büyüyen müşteriler.", ikon="📈"),
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
    with secim[6]:
        _render_upsell_adaylari()


def _kullanicilar_onay() -> None:
    """Kullanıcılar & Onay — admin_extras.render_user_management'a yönlendirir.

    UI-ADMIN-KULLANICI-BIRLESTIR-09: burada onay bekleyen kullanıcı listesi,
    tier seçimi ve onaylama mantığının ikinci kopyası vardı; kanonik uygulama
    NAV-PLAN-01 §2.1 gereği admin_extras.render_user_management. Silme değil
    yönlendirme — çağrı noktası (bu fonksiyon, sekme 0) korunuyor.
    """
    BOLUMLER[0].render()
    token = st.session_state.get("admin_token")
    render_user_management(token)


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

    # UI-ADMIN-CHURN-KOLON-07: Churn risk listesi (3 sinyal: last_login + user_activity_log)
    st.divider()
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 3 sinyal için: last_login + son_arama + son_ai (user_activity_log)
            churn_rows = conn.execute(
                text(
                    """
                    SELECT u.email, u.last_login, u.created_at,
                           -- son_arama: user_activity_log'dan olay_tipi='arama' olan en son tarih
                           (SELECT MAX(olay_zamani)::date FROM user_activity_log
                            WHERE user_id = u.user_id AND olay_tipi = 'arama') as son_arama,
                           -- son_ai: user_activity_log'dan olay_tipi='ai_kullanim' olan en son tarih
                           (SELECT MAX(olay_zamani)::date FROM user_activity_log
                            WHERE user_id = u.user_id AND olay_tipi = 'ai_kullanim') as son_ai
                    FROM users u
                    ORDER BY u.last_login DESC NULLS LAST
                    """
                )
            ).mappings().all()
        if churn_rows:
            from datetime import date
            bugun = date.today()
            churn_data = []
            for r in churn_rows:
                # 3 sinyalli risk etiketi: last_login + son_arama + son_ai
                risk = risk_etiketi_3sinyal(
                    son_giris=r["last_login"],
                    son_arama=r["son_arama"],
                    son_ai=r["son_ai"],
                    bugun=bugun,
                )
                churn_data.append({
                    "E-posta": r["email"],
                    "Son Giriş": r["last_login"] or "—",
                    "Son Arama": r["son_arama"] or "—",
                    "Son AI": r["son_ai"] or "—",
                    "Kayıt Tarihi": r["created_at"],
                    "Churn Riski": risk,
                })
            st.caption("Churn Risk (3 sinyal): 'Yok'=3 sinyal de <14g, 'Düşük'=1 sinyal bayat, 'Orta'=2 sinyal bayat, 'Yüksek'=3 sinyal bayat")
            st.dataframe(churn_data, width="stretch", hide_index=True)
        else:
            st.info("Kullanıcı kaydı yok.")
    except Exception:
        st.info("Churn risk verisi yüklenemedi.")


# UI-ADMIN-UPSELL-22: Upsell aday listesi

def _doygunluk_hesapla(
    user_id: str,
    tier: str,
    engine,
) -> float | None:
    """Kullanıcının kota doygunluğunu hesapla.

    Doygunluk = tüketim / kota
    - kota = tier bazlı limit (enterprise = -1 -> sınırsız -> None)
    - tüketim = son 30 günde credit_ledger'dan negatif delta toplamı (mutlak değer)
    - kota 0/None -> None döner (müşteri listeden çıkarılır)

    Returns:
        float: 0.0-1.0 arası doygunluk oranı, None = hesaplanamaz (sınırsız/geçersiz)
    """
    kota = _TIER_KOTALAR.get(tier)
    if kota is None or kota <= 0:
        return None  # Sınırsız veya geçersiz tier

    try:
        with engine.connect() as conn:
            # Son 30 günde tüketim (negatif delta = kullanım)
            row = conn.execute(text("""
                SELECT COALESCE(SUM(CASE WHEN delta < 0 THEN -delta ELSE 0 END), 0) as tuketim
                FROM credit_ledger
                WHERE user_id = :uid
                  AND created_at >= (CURRENT_DATE - INTERVAL '30 days')
            """), {"uid": user_id}).scalar()
        tuketim = int(row or 0)
        return min(tuketim / kota, 1.0) if kota > 0 else 0.0
    except Exception:
        return None


def _buyume_hesapla(user_id: str, engine) -> float:
    """Son 30 günde kullanım büyümesi (tüketim artışı).

    Bu ayki tüketim - önceki ayki tüketim / önceki ayki tüketim
    Tarih alanı yoksa 0 döner.
    """
    try:
        with engine.connect() as conn:
            # Bu ay (son 30 gün)
            bu_ay = conn.execute(text("""
                SELECT COALESCE(SUM(CASE WHEN delta < 0 THEN -delta ELSE 0 END), 0)
                FROM credit_ledger
                WHERE user_id = :uid
                  AND created_at >= (CURRENT_DATE - INTERVAL '30 days')
            """), {"uid": user_id}).scalar()

            # Önceki ay (30-60 gün önce)
            onceki_ay = conn.execute(text("""
                SELECT COALESCE(SUM(CASE WHEN delta < 0 THEN -delta ELSE 0 END), 0)
                FROM credit_ledger
                WHERE user_id = :uid
                  AND created_at >= (CURRENT_DATE - INTERVAL '60 days')
                  AND created_at < (CURRENT_DATE - INTERVAL '30 days')
            """), {"uid": user_id}).scalar()

        bu_ay = int(bu_ay or 0)
        onceki_ay = int(onceki_ay or 0)

        if onceki_ay <= 0:
            return 0.0  # Büyüme hesaplanamaz
        return (bu_ay - onceki_ay) / onceki_ay
    except Exception:
        return 0.0


def _upsell_adaylari_yukle(engine) -> list[dict]:
    """Upsell adaylarını yükle: 3 koşul birlikte sağlanmalı.

    Koşullar (AND):
    1. doygunluk >= _UPSELL_DOYGUNLUK_ESIK (0.85)
    2. churn_etiketi ∈ {"Yok", "Düşük"} (risk_etiketi_3sinyal)
    3. son 30 gün büyüme > 0

    Returns:
        list[dict]: Aday listesi (doğrunluk oranına göre azalan)
    """
    from datetime import date
    bugun = date.today()

    try:
        with engine.connect() as conn:
            # credit_ledger tablosu var mı?
            if not _db_yardim.tablo_var_mi(conn, "credit_ledger"):
                return []

            rows = conn.execute(text("""
                SELECT u.user_id, u.email, u.company_name, u.tier, u.credit_balance,
                       u.last_login, u.created_at
                FROM users u
                WHERE u.status = 'onayli'
                  AND u.role = 'user'
                ORDER BY u.credit_balance DESC NULLS LAST
            """)).mappings().all()
    except Exception:
        return []

    if not rows:
        return []

    bugun = date.today()
    adaylar = []

    for r in rows:
        user_id = r["user_id"]
        tier = r["tier"]

        # 1. Doygunluk hesapla
        doygunluk = _doygunluk_hesapla(user_id, tier, engine)
        if doygunluk is None:
            continue  # Sınırsız kota (enterprise) veya geçersiz

        if doygunluk < _UPSELL_DOYGUNLUK_ESIK:
            continue  # Eşik altında

        # 2. Churn risk etiketi (3 sinyal)
        # last_login, son_arama, son_ai için subquery
        try:
            with engine.connect() as conn:
                son_arama = conn.execute(text("""
                    SELECT MAX(olay_zamani)::date FROM user_activity_log
                    WHERE user_id = :uid AND olay_tipi = 'arama'
                """), {"uid": user_id}).scalar()

                son_ai = conn.execute(text("""
                    SELECT MAX(olay_zamani)::date FROM user_activity_log
                    WHERE user_id = :uid AND olay_tipi = 'ai_kullanim'
                """), {"uid": user_id}).scalar()
        except Exception:
            son_arama = None
            son_ai = None

        churn = risk_etiketi_3sinyal(
            son_giris=r["last_login"],
            son_arama=son_arama,
            son_ai=son_ai,
            bugun=bugun,
        )
        if churn not in ("Yok", "Düşük"):
            continue  # Riskli müşteri

        # 3. Büyüme > 0
        buyume = _buyume_hesapla(user_id, engine)
        if buyume <= 0:
            continue  # Büyüme yok

        # Tüm koşullar sağlandı - aday
        adaylar.append({
            "musteri": r["company_name"] or r["email"],
            "email": r["email"],
            "doygunluk": round(doygunluk * 100, 1),
            "churn_etiketi": churn,
            "buyume": round(buyume * 100, 1),
            "tier": tier,
            "paket": f"{tier.title()} Paketi",
        })

    # Doygunluğa göre azalan sırala
    adaylar.sort(key=lambda x: x["doygunluk"], reverse=True)
    return adaylar


def _render_upsell_adaylari() -> None:
    """UI-ADMIN-UPSELL-22: Upsell Adayları bölümü."""
    Section("📈 Upsell Adayları", "Kota doygunluğu %85+, churn riski düşük, büyüme olan müşteriler.", ikon="📈").render()
    st.caption(
        "Kriterler (AND): Doygunluk ≥%85 · Churn ∈ {Yok,Düşük} · 30g büyüme>0. "
        f"Eşik: {int(_UPSELL_DOYGUNLUK_ESIK*100)}%. Enterprise (sınırsız) hariç."
    )

    try:
        engine = get_engine()
    except Exception:
        st.warning("Veritabanı bağlantısı kurulamadı.")
        return

    # credit_ledger tablosu var mı kontrolü
    try:
        with engine.connect() as conn:
            if not _db_yardim.tablo_var_mi(conn, "credit_ledger"):
                st.warning("⚠️ Veri kaynağı yok — credit_ledger tablosu bulunamadı.")
                return
    except Exception:
        st.warning("⚠️ Veri kaynağı yok — credit_ledger tablosu kontrol edilemedi.")
        return

    adaylar = _upsell_adaylari_yukle(engine)

    if not adaylar:
        st.info("Upsell kriterlerini sağlayan müşteri bulunamadı.")
        return

    # Metrik kartları
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📋 Toplam Aday", len(adaylar))
    with c2:
        ort_doygunluk = sum(a["doygunluk"] for a in adaylar) / len(adaylar)
        st.metric("📊 Ort. Doygunluk", f"%{ort_doygunluk:.1f}")
    with c3:
        ort_buyume = sum(a["buyume"] for a in adaylar) / len(adaylar)
        st.metric("📈 Ort. Büyüme", f"%{ort_buyume:.1f}")

    # Tablo
    display_df = pd.DataFrame(adaylar)[
        ["musteri", "email", "doygunluk", "churn_etiketi", "buyume", "tier", "paket"]
    ].rename(columns={
        "musteri": "Müşteri",
        "email": "E-posta",
        "doygunluk": "Doygunluk (%)",
        "churn_etiketi": "Churn Riski",
        "buyume": "Büyüme (%)",
        "tier": "Tier",
        "paket": "Mevcut Paket",
    })
    st.dataframe(display_df, width="stretch", hide_index=True)

    # CSV indirme
    csv = pd.DataFrame(adaylar).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 CSV İndir",
        data=csv,
        file_name=f"upsell_adaylari_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="upsell_download",
    )
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
