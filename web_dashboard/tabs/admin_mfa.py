# UI-ADMIN-MFA-26 B-05: MFA Yönetim Sekmesi

import streamlit as st
import requests
from datetime import datetime

def _mfa_api_token() -> str | None:
    """Oturumdan admin token al."""
    try:
        oturum = dict(st.session_state)
        return oturum.get("admin_token") or oturum.get("user_token")
    except Exception:
        return None


def _mfa_durum_getir() -> dict | None:
    """MFA durumunu API'den getir."""
    token = _mfa_api_token()
    if not token:
        return None
    try:
        resp = requests.get(
            "/api/admin/mfa/status",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return None


def _mfa_kur(request, mfa_token: str, code: str) -> dict:
    """MFA kurulum doğrulama API çağrısı."""
    token = _mfa_api_token()
    if not token:
        return {"ok": False, "error": "Token bulunamadı"}
    try:
        resp = requests.post(
            "/api/admin/mfa/verify",
            json={"mfa_token": mfa_token, "code": code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return {"ok": False, "error": "API hatası"}


def _mfa_devre_disi_birak(request, password: str) -> dict:
    """MFA devre dışı bırakma API çağrısı."""
    token = _mfa_api_token()
    if not token:
        return {"ok": False, "error": "Token bulunamadı"}
    try:
        resp = requests.post(
            "/api/admin/mfa/disable",
            json={"password": password},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return {"ok": False, "error": "API hatası"}


def _mfa_backup_codes_getir(request) -> dict:
    """Backup codes API çağrısı."""
    token = _mfa_api_token()
    if not token:
        return {"ok": False, "error": "Token bulunamadı"}
    try:
        resp = requests.post(
            "/api/admin/mfa/backup-codes",
            json={},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return {"ok": False, "error": "API hatası"}


def _mfa_kurulum_baslat() -> dict | None:
    """MFA kurulum başlatma API çağrısı."""
    token = _mfa_api_token()
    if not token:
        return None
    try:
        resp = requests.post(
            "/api/admin/mfa/setup",
            json={},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return None


def render_mfa_tab() -> None:
    """UI-ADMIN-MFA-26 B-05: MFA Yönetim Sekmesi.
    
    - MFA durumu (aktif/pasif)
    - MFA kurulum (QR kod + secret + token)
    - MFA devre dışı bırakma (şifre ile)
    - Backup kodları yönetimi
    """
    from company_master.ui import PageHeader
    from company_master.ui.components.page import Section
    
    PageHeader(
        "MFA Yönetimi", ust_etiket="Güvenlik · Yönetim", ikon="🔐",
        giris="Çok faktörlü kimlik doğrulama (TOTP) ayarlarını yönetin. Sadece admin rolü erişebilir.",
    ).render()

    # Admin rol kontrolü
    try:
        session = dict(st.session_state)
        user_email = session.get("admin_email") or session.get("user_email")
        user_role = session.get("user_role", "anon")
    except Exception:
        user_email = None
        user_role = "anon"

    if user_role != "admin":
        st.error("Bu sekmeye sadece admin rolü erişebilir.")
        return

    # MFA durumu
    veri = _mfa_durum_getir()
    
    if not veri:
        st.warning("⚠️ Veri kaynağı yok — API endpoint çalışmıyor veya token bulunamadı.")
        return

    # Mevcut durum
    col1, col2, col3 = st.columns(3)
    with col1:
        if veri.get("enabled"):
            st.metric("🔐 MFA Durumu", "AKTİF", delta="Korunuyor")
        else:
            st.metric("🔓 MFA Durumu", "PASİF", delta="Açık")
    with col2:
        st.metric("Oluşturma", veri.get("created_at", "—")[:16] if veri.get("created_at") else "—")
    with col3:
        st.metric("Son Kullanım", veri.get("last_used_at", "—")[:16] if veri.get("last_used_at") else "—")

    st.divider()

    # MFA aktifse: devre dışı bırakma + backup codes
    if veri.get("enabled"):
        Section(
            "MFA Aktif — Yönetim",
            "MFA açık. Buradan devre dışı bırakabilir veya backup kodlarını yenileyebilirsiniz.",
            kimlik="mfa-yonetim",
        ).render()
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**MFA Aktif** - Hesabınız korumalı.")
            if st.button("🔴 MFA Devre Dışı Bırak", type="secondary"):
                with st.form("mfa_disable_form"):
                    st.write("MFA devre dışı bırakmak için mevcut şifrenizi girin:")
                    password = st.text_input("Mevcut Şifre", type="password")
                    submitted = st.form_submit_button("Devre Dışı Bırak", type="primary")
                    if submitted and password:
                        # Session'dan request objesi al
                        try:
                            from streamlit.runtime.scriptrunner import get_script_run_ctx
                            ctx = get_script_run_ctx()
                            if ctx and hasattr(ctx, 'request'):
                                request_obj = ctx.request
                                result = _mfa_devre_disi_birak(request_obj, password)
                            else:
                                result = {"ok": False, "error": "Request objesi alınamadı"}
                        except Exception:
                            result = {"ok": False, "error": "Request objesi alınamadı"}
                        
                        if result.get("ok"):
                            st.success("MFA devre dışı bırakıldı")
                            st.rerun()
                        else:
                            st.error(f"Hata: {result.get('error', 'Bilinmeyen hata')}")
        
        with col2:
            st.write("**Backup Kodları**")
            if veri.get("has_backup_codes"):
                if st.button("🔄 Yeni Backup Kodları Üret"):
                    try:
                        from streamlit.runtime.scriptrunner import get_script_run_ctx
                        ctx = get_script_run_ctx()
                        if ctx and hasattr(ctx, 'request'):
                            request_obj = ctx.request
                            result = _mfa_backup_codes_getir(request_obj)
                        else:
                            result = {"ok": False, "error": "Request objesi alınamadı"}
                    except Exception:
                        result = {"ok": False, "error": "Request objesi alınamadı"}
                    
                    if result.get("ok"):
                        st.success("Yeni backup kodları üretildi")
                        st.code("\n".join(result.get("backup_codes", [])), language=None)
                        st.warning("Bu kodları güvenli bir yere kaydedin! Her kod tek kullanımlıktır.")
                    else:
                        st.error(f"Hata: {result.get('error', 'Bilinmeyen hata')}")
            else:
                st.info("Backup kodları henüz üretilmemiş.")

    else:
        # MFA pasifse: kurulum
        Section(
            "MFA Kurulumu",
            "MFA henüz aktif değil. Aşağıdaki butonla kurulumu başlatın.",
            kimlik="mfa-kurulum",
        ).render()
        
        if st.button("🔐 MFA Kurulumu Başlat", type="primary"):
            result = _mfa_kurulum_baslat()
            if result:
                st.success("MFA kurulumu başlatıldı! Authenticator uygulamasıyla QR kodu tarayın.")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f"data:image/png;base64,{result.get('qr_code_base64', '')}", caption="QR Kod")
                with col2:
                    st.write("**Secret Key (Manuel Giriş):**")
                    st.code(result.get("secret_key", ""), language=None)
                    st.write("**MFA Token:**")
                    st.code(result.get("mfa_token", ""), language=None)
                    st.write(f"**Geçerlilik:** {result.get('expires_at', '')[:16]}")
                
                st.write("---")
                st.write("**Doğrulama:**")
                with st.form("mfa_verify_form"):
                    code = st.text_input("Authenticator'dan 6 haneli kodu girin", max_chars=6)
                    submitted = st.form_submit_button("Doğrula ve Aktifleştir", type="primary")
                    if submitted and code:
                        result = _mfa_kur(st.session_state.get("request"), result.get("mfa_token", ""), code)
                        if result.get("ok"):
                            st.success("MFA başarıyla aktifleştirildi!")
                            st.write("**Backup Kodlarınız (güvenli yere kaydedin):**")
                            st.code("\n".join(result.get("backup_codes", [])), language=None)
                            st.warning("Bu kodları güvenli bir yere kaydedin! Her kod tek kullanımlıktır.")
                            st.rerun()
                        else:
                            st.error(f"Hata: {result.get('error', 'Geçersiz kod')}")
            else:
                st.error(f"Kurulum başlatılamadı: {result.get('error', 'Bilinmeyen hata')}")

    st.caption("Not: MFA TOTP standardı (RFC 6238). Desteklenen uygulamalar: Google Authenticator, Authy, Microsoft Authenticator, 1Password, Bitwarden.")