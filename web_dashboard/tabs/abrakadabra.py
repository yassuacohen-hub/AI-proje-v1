# -*- coding: utf-8 -*-
"""AI-CHAT-01 — MIMIR sohbet ekranı (Muninn 🛡️ iç ekip yüzeyi).

S11: görünen ad **MIMIR**; url/anahtar ``abrakadabra`` sabit kalır (BK5).
``abrakadabra`` aynı zamanda sohbet içindeki **kilit sözü**dür: kullanıcı
mesajında veya kilit kutusunda geçmedikçe teklif onayı kapalı kalır.

Streamlit ``st.chat_message`` tabanlı orkestratör asistanı. Tüm iş mantığı
``company_master.ai_chat`` içindedir; bu dosya yalnızca sunum katmanıdır.

Güvenlik kapıları:
* Admin token yoksa sohbet açılmaz (``require_admin_token``).
* Model doğrudan pano yazamaz; ``TEKLIF:`` satırları ayıklanır ve
  yalnızca **Onayla** düğmesiyle ``teklif_uygula`` çağrılır.
* Onayla düğmesi **kilit sözü** doğrulanmadan pasiftir (ikinci kapı).

Karar: [[D-182]] — Orkestratör Asistanı İki Seviye (seviye-bağımlı display name)
Test: [[tests/test_d182_mimir.py]]
"""
from __future__ import annotations

import streamlit as st

from company_master import ai_chat
from company_master.ai_chat import AiChatHatasi, Mesaj, Teklif
from company_master.ui import PageHeader, Section, SectionNav
from web_dashboard.tabs.admin_auth import render_admin_login, require_admin_token

#: Bölümler tek yerde tanımlanır (anchor tutarlılığı).
BOLUMLER: tuple[Section, ...] = (
    Section("Bağlam", "Modele verilen görev panosu ve posta kutusu özeti (salt okunur).",
            ikon="📋", kimlik="abrakadabra-baglam"),
    Section("Sohbet", "Orkestratör asistanı ile konuşun; yanıtlar 9Router üzerinden gelir.",
            ikon="💬", kimlik="abrakadabra-sohbet"),
    Section("Bekleyen Teklifler", "Modelin önerdiği pano komutları; kilit sözü + onay olmadan uygulanmaz.",
            ikon="✅", kimlik="abrakadabra-teklifler"),
)

#: D-182 — ad seviye-bağımlı; getir() çağrısıyla alınır, statik değer yok.
GIRIS_METNI = (
    "MIMIR, görev panosunu ve posta kutusunu okuyarak orkestrasyon "
    "önerileri üretir. Panoda değişiklik yalnızca kilit sözü ve sizin onayınızla yapılır."
)

_GECMIS_KEY = "abrakadabra_gecmis"
_TEKLIF_KEY = "abrakadabra_teklifler"
_HATA_KEY = "abrakadabra_hatalar"
_KILIT_KEY = "abrakadabra_kilit"

#: D-182 — iki seviye rozeti. Ad da seviyeyle değişir: MIMIR (Seviye 0) → ODIN (Seviye 1).
_ROZETLER = {0: "🔒 Orkestratör Asistanı", 1: "🔓 Orkestratör"}


def _mimir_seviyesi() -> int:
    """Aktif orkestratör 'mimir' ise 1, değilse 0 (D-182).

    ponytail: orchestrator.json doğrudan okunur; devir CLI'dan
    (`gorev_at.py abrakadabra`) yapılır. UI'dan devralma gerekirse
    cmd_abrakadabra bir servis fonksiyonuna çıkarılıp buradan çağrılır.
    """
    try:
        from scripts.gorev_at import _orkestrator_oku
    except ImportError:
        return 0
    try:
        return 1 if _orkestrator_oku().get("ajan") == "mimir" else 0
    except OSError:
        return 0


def _bolum(kimlik: str) -> Section:
    """Kimliğe göre bölüm tanımını getirir."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def _gecmis() -> list[Mesaj]:
    return st.session_state.setdefault(_GECMIS_KEY, [])


def _teklifler() -> list[Teklif]:
    return st.session_state.setdefault(_TEKLIF_KEY, [])


def _kilit_acik() -> bool:
    """Oturumda kilit sözü doğrulandı mı?"""
    return bool(st.session_state.get(_KILIT_KEY))


def _render_baslik() -> None:
    seviye = _mimir_seviyesi()
    PageHeader(f"{ai_chat.gorunen_ad(seviye)} — {_ROZETLER[seviye]}", giris=GIRIS_METNI,
               ust_etiket="İş · AI Asistan", ikon="🤖").render()

    col_temizle, col_model, col_bos = st.columns([1, 2, 2], vertical_alignment="center")
    with col_temizle:
        temizle = st.button("🧹 Sohbeti Temizle", key="abrakadabra_temizle",
                            type="primary", width="stretch",
                            help="Geçmişi ve bekleyen teklifleri siler.")
    with col_model:
        st.caption("Model zinciri: " + " → ".join(ai_chat.model_zinciri()))
    if temizle:
        for key in (_GECMIS_KEY, _TEKLIF_KEY, _HATA_KEY, _KILIT_KEY):
            st.session_state.pop(key, None)
        st.rerun()

    SectionNav(BOLUMLER, yatay=True).render()


def _render_baglam() -> None:
    _bolum("abrakadabra-baglam").render()
    try:
        baglam = ai_chat.baglam_metni()
    except Exception as exc:  # noqa: BLE001 — pano okunamazsa ekran çökmesin
        st.warning(f"Bağlam okunamadı: {exc}")
        return
    with st.expander("Modele verilen bağlam", expanded=False):
        st.code(baglam, language="text")


def _render_kilit() -> None:
    """Kilit sözü kutusu: doğrulanınca oturum boyunca ayrıcalıklı işlemler açılır."""
    if _kilit_acik():
        col_durum, col_kapat = st.columns([4, 1], vertical_alignment="center")
        with col_durum:
            st.caption("🔓 Kilit açık — teklifler onaylanabilir.")
        with col_kapat:
            if st.button("🔒 Kilitle", key="abrakadabra_kilitle"):
                st.session_state.pop(_KILIT_KEY, None)
                st.rerun()
        return
    girdi = st.text_input("Kilit sözü", key="abrakadabra_kilit_girdi", type="password",
                          placeholder="Ayrıcalıklı işlemler için kilit sözünü yazın",
                          help="Kilit sözü olmadan Onayla düğmesi pasif kalır.")
    if girdi and ai_chat.kilit_acik(girdi):
        st.session_state[_KILIT_KEY] = True
        st.rerun()
    elif girdi:
        st.caption("🔒 Kilit sözü eşleşmedi.")


def _render_teklifler() -> None:
    _bolum("abrakadabra-teklifler").render()
    _render_kilit()
    teklifler = _teklifler()
    if not teklifler:
        st.caption("Bekleyen teklif yok.")
        return
    acik = _kilit_acik()
    for idx, teklif in enumerate(list(teklifler)):
        col_metin, col_onay, col_red = st.columns([4, 1, 1], vertical_alignment="center")
        with col_metin:
            st.code(teklif.metin, language="text")
        with col_onay:
            onay = st.button("Onayla", key=f"abrakadabra_onay_{idx}", type="secondary",
                             disabled=not acik, help=None if acik else "Önce kilit sözünü girin.")
        with col_red:
            red = st.button("Reddet", key=f"abrakadabra_red_{idx}")
        if onay:
            try:
                sonuc = ai_chat.teklif_uygula(teklif, kilit=ai_chat.kilit_sozu())
            except AiChatHatasi as exc:
                st.error(f"Teklif uygulanamadı: {exc}")
            else:
                st.success(f"Uygulandı: {sonuc}")
                teklifler.remove(teklif)
                st.rerun()
        elif red:
            teklifler.remove(teklif)
            st.rerun()


def _render_sohbet(token: str) -> None:
    _bolum("abrakadabra-sohbet").render()
    gecmis = _gecmis()
    for mesaj in gecmis:
        with st.chat_message(mesaj.rol):
            st.markdown(mesaj.icerik)

    hatalar: list[str] = st.session_state.get(_HATA_KEY, [])
    if hatalar:
        st.caption("Sağlayıcı düşüşleri: " + "; ".join(hatalar))

    girdi = st.chat_input(f"{ai_chat.gorunen_ad(_mimir_seviyesi())}'e yaz…", key="abrakadabra_girdi")
    if not girdi:
        return

    # Kilit sözü sohbette geçerse oturumu aç; modele maskelenmiş hâli gider.
    if ai_chat.kilit_acik(girdi):
        st.session_state[_KILIT_KEY] = True
        st.toast("🔓 Kilit sözü tanındı — teklif onayı açıldı.")
    gecmis.append(Mesaj("user", girdi))
    with st.chat_message("user"):
        st.markdown(ai_chat.kilit_maskele(girdi))

    dusen: list[str] = []
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor…"):
            try:
                yanit, model = ai_chat.sohbet(
                    gecmis, token,
                    hata_kaydi=lambda m, h: dusen.append(f"{m}: {h}"),
                )
            except AiChatHatasi as exc:
                st.error(str(exc))
                st.session_state[_HATA_KEY] = dusen
                return
        st.markdown(yanit)
        st.caption(f"Model: {model}")

    gecmis.append(Mesaj("assistant", yanit))
    st.session_state[_HATA_KEY] = dusen
    yeni = ai_chat.teklif_ayikla(yanit)
    if yeni:
        _teklifler().extend(yeni)
        st.info(f"{len(yeni)} teklif onay bekliyor (aşağıdaki bölüme bakın).")
        st.rerun()


def render_abrakadabra_tab() -> None:
    """MIMIR sohbet ekranını çizer; admin token yoksa giriş formu gösterir."""
    _render_baslik()
    token = require_admin_token()
    if not token:
        st.warning(f"{ai_chat.gorunen_ad(_mimir_seviyesi())} yalnızca admin oturumunda kullanılabilir.")
        render_admin_login()
        return
    _render_baglam()
    _render_sohbet(token)
    _render_teklifler()
