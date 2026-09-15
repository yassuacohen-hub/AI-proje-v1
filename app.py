#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Streamlit Dashboard â€” P7-44: Modern Navigasyon.

Ne deÄŸiÅŸti (P7-44):
    1. **Tek doÄŸru kaynak (SSOT):** Sekme listesi artÄ±k `app.py` iÃ§inde deÄŸil,
       `web_dashboard/tabs/__init__.py` â†’ `SECTIONS` kaydÄ±nda. Sidebar butonu ve
       yÃ¶nlendirme dalÄ± otomatik tÃ¼retilir; ikisi birbirinden kaÃ§amaz.
    2. **Placeholder'lar kaldÄ±rÄ±ldÄ±:** Paketler ve Pazarlama sekmeleri gerÃ§ek
       render fonksiyonlarÄ±na baÄŸlandÄ± (K-01 kapandÄ±).
    3. **Tembel (lazy) import:** Sadece gÃ¶rÃ¼ntÃ¼lenen bÃ¶lÃ¼mÃ¼n modÃ¼lÃ¼ yÃ¼klenir;
       aÃ§Ä±lÄ±ÅŸta 20+ modÃ¼l import edilmez.
    4. **Derin baÄŸlantÄ±:** `?bolum=paketler` ile doÄŸrudan bÃ¶lÃ¼me girilebilir,
       seÃ§im URL'e yazÄ±lÄ±r (yenileme/paylaÅŸÄ±m seÃ§imi korur).
    5. **Aktif durum vurgusu + breadcrumb:** KullanÄ±cÄ± nerede olduÄŸunu gÃ¶rÃ¼r.
    6. **HÄ±zlÄ± geÃ§iÅŸ:** Sidebar'daki arama kutusundan tÃ¼m bÃ¶lÃ¼mlere tek adÄ±mda.
    7. **Hata sÄ±nÄ±rÄ±:** Bir bÃ¶lÃ¼m patlarsa panel komple dÃ¼ÅŸmez; hata o bÃ¶lÃ¼mde
       gÃ¶sterilir, navigasyon Ã§alÄ±ÅŸmaya devam eder.

Navigasyon (BK5):
    Ä°ÅŸ OperasyonlarÄ± : Ana Kontrol Â· MÃ¼ÅŸteriler Â· Paketler Â· Pazarlama Â· Abrakadabra
    Sistem & YÃ¶netim : Sistem Â· CanlÄ± Veri Â· YÃ¶netim

Ã‡alÄ±ÅŸtÄ±rma:
    streamlit run app.py
"""
from __future__ import annotations

import sys
import time as _time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from web_dashboard.tabs import (  # noqa: E402
    ROL_ADMIN,
    ROL_ANON,
    SECTIONS,
    TabTanimi,
    erisebilir,
    gorunur_bolumler,
    gruplar,
    render_fonksiyonu,
    rol_normalize,
    tab_getir,
    tab_url_getir,
    varsayilan_tab,
)

from company_master.i18n import t  # noqa: E402
from company_master.ui import (  # noqa: E402
    ChatBubble,
    TopBar,
    stil_enjekte,
)

# UI-WIDE-01: ÃœrÃ¼n Sahibi kararÄ± â€” sayfa varsayÄ±lan olarak geniÅŸ (wide) aÃ§Ä±lÄ±r;
# `toolbarMode = "auto"` (.streamlit/config.toml) sayesinde saÄŸ Ã¼stteki â‹®
# Settings menÃ¼sÃ¼ hÃ¢lÃ¢ gÃ¶rÃ¼nÃ¼r ve kullanÄ±cÄ± dilerse "Wide mode"u kapatÄ±p
# tekrar "Centered" moda geÃ§ebilir (bu tercih tarayÄ±cÄ±da saklanÄ±r).
st.set_page_config(
    page_title="Huginn â€” Company Master Dashboard",
    page_icon="ğŸ¢",
    layout="wide",
    initial_sidebar_state="expanded",
)

URL_PARAM = "bolum"
SOHBET_PARAM = "sohbet"
ARAMA_KEY = "_hg_arama_sorgu"
TEMA_KEY = "_hg_tema"
SOHBET_KEY = "_hg_sohbet_acik"
#: Streamlit'in tema adlarÄ± â†’ iÃ§ tasarÄ±m sistemi anahtarlarÄ±mÄ±z.
STREAMLIT_TEMA_ESLEME = {"light": "aydinlik", "dark": "karanlik"}
#: `st.context.theme` okunamazsa kullanÄ±lacak deÄŸer; config.toml `base = "light"`.
VARSAYILAN_TEMA = "aydinlik"
ARAMA_MAKS_SONUC = 5
KOMPAKT_KEY = "_hg_menu_kompakt"
KOMPAKT_SUTUN = 4  # ikon-only modda satÄ±r baÅŸÄ±na dÃ¼ÅŸen ikon sayÄ±sÄ±
#: U-10: Oturum rolÃ¼. YazÄ±lÄ±rsa `admin_token` tÃ¼retimini ezer (test/gelecek RBAC).
ROL_KEY = "_hg_rol"

# --------------------------------------------------------------------------- #
# Oturum durumu
# --------------------------------------------------------------------------- #

if "perf_metrics" not in st.session_state:
    st.session_state["perf_metrics"] = {"page_load_start": None, "son_bolum": ""}
st.session_state["perf_metrics"]["page_load_start"] = _time.perf_counter()

if "current_section" not in st.session_state:
    st.session_state["current_section"] = varsayilan_tab().anahtar

# NAV-01: her bÃ¶lÃ¼mÃ¼n `st.Page` nesnesi. `sayfalari_uret()` her koÅŸuda doldurur;
# `bolum_sec()` ve eski adres Ã§evirici buradan sayfa nesnesine ulaÅŸÄ±r.
_SAYFA_KAYDI: dict[str, Any] = {}  # anahtar -> st.Page nesnesi


# --------------------------------------------------------------------------- #
# YÃ¶nlendirme (routing) yardÄ±mcÄ±larÄ±
# --------------------------------------------------------------------------- #


def _eski_adresi_cevir() -> None:
    """Eski `?bolum=...` adresini yeni `/{url_path}` yoluna taÅŸÄ±r.

    Geriye dÃ¶nÃ¼k uyum: dÄ±ÅŸarÄ±da paylaÅŸÄ±lmÄ±ÅŸ eski baÄŸlantÄ±lar bozulmasÄ±n.
    Parametre okunduktan sonra **temizlenir**; aksi hÃ¢lde her koÅŸuda yeniden
    yÃ¶nlendirme tetiklenir (sonsuz yenileme).
    """
    try:
        ham = st.query_params.get(URL_PARAM, "")
    except Exception:  # Streamlit sÃ¼rÃ¼m farkÄ± â€” URL yoksa sessizce geÃ§
        return
    if isinstance(ham, list):
        ham = ham[0] if ham else ""
    tanim = tab_url_getir(str(ham))
    if tanim is None:
        return
    try:
        st.query_params.pop(URL_PARAM, None)
    except Exception:
        pass
    sayfa = _SAYFA_KAYDI.get(tanim.anahtar)
    if sayfa is not None:
        st.switch_page(sayfa)


def aktif_rol() -> str:
    """U-10: Oturumun rolÃ¼nÃ¼ dÃ¶ndÃ¼rÃ¼r.

    Ã–ncelik: `st.session_state[ROL_KEY]` â†’ varsa `admin_token` â‡’ `admin`
    â†’ aksi hÃ¢lde `anon`. Bilinmeyen deÄŸerler `anon`a indirgenir.
    """
    acik = st.session_state.get(ROL_KEY)
    if acik:
        return rol_normalize(str(acik))
    return ROL_ADMIN if st.session_state.get("admin_token") else ROL_ANON


def aktif_tab() -> TabTanimi:
    """Oturumdaki bÃ¶lÃ¼mÃ¼ dÃ¶ndÃ¼rÃ¼r (geri uyum; yÃ¶nlendirme artÄ±k sayfa temelli)."""
    tanim = tab_getir(st.session_state.get("current_section", ""))
    return tanim or varsayilan_tab()


def bolum_sec(anahtar: str) -> None:
    """Sidebar/hÄ±zlÄ± geÃ§iÅŸ tÄ±klamasÄ±nda bÃ¶lÃ¼m sayfasÄ±na geÃ§er."""
    if st.session_state.get("current_section") == anahtar:
        return
    st.session_state["current_section"] = anahtar
    sayfa = _SAYFA_KAYDI.get(anahtar)
    if sayfa is None:  # sayfa Ã¼retilmemiÅŸse en azÄ±ndan yeniden Ã§iz
        st.rerun()
    st.switch_page(sayfa)


def _url_param_oku(ad: str) -> str:
    """Tek bir sorgu parametresini gÃ¼venli biÃ§imde metin olarak okur."""
    try:
        ham = st.query_params.get(ad, "")
    except Exception:
        return ""
    if isinstance(ham, list):
        ham = ham[0] if ham else ""
    return str(ham or "").strip().lower()


def _url_param_yaz(ad: str, deger: str) -> None:
    """Sorgu parametresini yalnÄ±zca deÄŸiÅŸtiyse yazar (gereksiz rerun yok)."""
    try:
        if st.query_params.get(ad) != deger:
            st.query_params[ad] = deger
    except Exception:
        pass


def aktif_tema() -> str:
    """GeÃ§erli temayÄ± **Streamlit'in kendi ayarÄ±ndan** okur.

    U-01: Sayfa iÃ§indeki ikinci gece/gÃ¼ndÃ¼z dÃ¼ÄŸmesi kaldÄ±rÄ±ldÄ±. Tek doÄŸru
    kaynak artÄ±k saÄŸ Ã¼st â‹® menÃ¼sÃ¼ â€º Settings â€º Appearance. `st.context.theme`
    kullanÄ±cÄ±nÄ±n seÃ§tiÄŸi temayÄ± verir; alan yoksa (eski sÃ¼rÃ¼m) varsayÄ±lana
    dÃ¼ÅŸÃ¼lÃ¼r ve uygulama kÄ±rÄ±lmaz.
    """
    tip = ""
    try:
        tema_ctx = getattr(st.context, "theme", None)
        tip = str(getattr(tema_ctx, "type", "") or "").strip().lower()
    except Exception:  # baÄŸlam yoksa (test/Ã§evrimdÄ±ÅŸÄ± Ã§alÄ±ÅŸtÄ±rma) sessizce geÃ§
        tip = ""
    tema = STREAMLIT_TEMA_ESLEME.get(tip, VARSAYILAN_TEMA)
    st.session_state[TEMA_KEY] = tema
    return tema


def sohbet_acik_mi() -> bool:
    """SaÄŸ alt sohbet panelinin aÃ§Ä±k/kapalÄ± durumu (URL > oturum)."""
    ham = _url_param_oku(SOHBET_PARAM)
    if ham in {"acik", "kapali"}:
        st.session_state[SOHBET_KEY] = ham == "acik"
    acik = bool(st.session_state.get(SOHBET_KEY, False))
    _url_param_yaz(SOHBET_PARAM, "acik" if acik else "kapali")
    return acik


def _baglanti(tanim: TabTanimi, **ek: str) -> str:
    """BÃ¶lÃ¼mÃ¼ koruyan sorgu baÄŸlantÄ±sÄ± Ã¼retir (`/{url_path}?tema=...&...`).

    NAV-01: st.navigation yÃ¶nlendirmesi kullanÄ±ldÄ±ÄŸÄ±ndan, `bolum` parametresi
    artÄ±k URL yolunda (`/{url_path}`). Tema/sohbet gibi ek parametreler sorgu
    satÄ±rÄ±na yazÄ±lÄ±r; sayfa geÃ§iÅŸi `st.switch_page()` ile yapÄ±lÄ±r.
    """
    ek_str = "&".join(f"{k}={v}" for k, v in ek.items()) if ek else ""
    taban = f"/{tanim.url_path}"
    return f"{taban}?{ek_str}" if ek_str else taban


def bolum_ara(sorgu: str) -> list[TabTanimi]:
    """Arama sorgusunu bÃ¶lÃ¼mlerle eÅŸler (baÅŸlÄ±k, etiket, aÃ§Ä±klama, anahtar)."""
    q = (sorgu or "").strip().casefold()
    if not q:
        return []
    sonuc: list[TabTanimi] = []
    for tanim in SECTIONS:
        alanlar = (tanim.baslik, tanim.etiket, tanim.aciklama, tanim.anahtar, tanim.grup)
        if any(q in (a or "").casefold() for a in alanlar):
            sonuc.append(tanim)
    return sonuc


# --------------------------------------------------------------------------- #
# app.py'ye Ã¶zgÃ¼ render'lar (YÃ¶netim bileÅŸimi)
# --------------------------------------------------------------------------- #


def render_karar_defteri() -> None:
    """OrkestratÃ¶r karar kayÄ±tlarÄ±nÄ±n defteri â€” render_decision_tab'a devrolundu.
    
    (MÃ¼kerrer fonksiyon â€” tabs/admin_panel.py::render_decision_tab() kullanÄ±lÄ±yor.)
    Eski implementasyon silinmiÅŸ, yÃ¶netim bÃ¶lÃ¼mÃ¼ tabs versiyonuna yÃ¶nlendirilmiÅŸ.
    """
    from web_dashboard.tabs.admin_panel import render_decision_tab
    
    render_decision_tab()


def render_yonetim_bilesik() -> None:
    """YÃ¶netim bÃ¶lÃ¼mÃ¼: admin giriÅŸi + yÃ¶netim panelleri + analitik alt sekmeler.

    `admin_yonetim.render_yonetim_tab()` yalnÄ±zca API/kullanÄ±cÄ±/export/arama
    panellerini iÃ§erir. Admin panelinin KPI, maliyet, kalite ve API analitiÄŸi
    ekranlarÄ± burada alt sekme olarak birleÅŸtirilir.
    """
    from web_dashboard.tabs.admin_api_analytics import render_api_analytics_tab
    from web_dashboard.tabs.admin_auth import (
        flash_goster,
        render_admin_cikis,
        render_admin_login,
        render_sifre_degistir,
    )
    from web_dashboard.tabs.admin_cost import render_cost_tab
    from web_dashboard.tabs.admin_errors import render_errors_tab
    from web_dashboard.tabs.admin_kpi import render_kpi_tab
    from web_dashboard.tabs.admin_quality import render_quality_tab
    from web_dashboard.tabs.admin_yonetim import render_yonetim_tab

    # ADMIN-RESET-01: giriÅŸ/Ã§Ä±kÄ±ÅŸ sonrasÄ± tek seferlik baÅŸarÄ± mesajÄ± (rerun'a dayanÄ±klÄ±)
    flash_goster()
    if not st.session_state.get("admin_token"):
        st.warning("ğŸ” YÃ¶netim iÅŸlemleri iÃ§in admin giriÅŸi gerekir.")
        render_admin_login()
        st.divider()
    else:
        render_admin_cikis()
        with st.expander("ğŸ”‘ Åifre deÄŸiÅŸtir", expanded=False):
            render_sifre_degistir()

    sekmeler = st.tabs(
        [
            "ğŸ› ï¸ YÃ¶netim AraÃ§larÄ±",
            "ğŸ“Š KPI KartlarÄ±",
            "ğŸ’° AI Maliyet",
            "ğŸ§ª Kalite Ã–zeti",
            "ğŸ”Œ API AnalitiÄŸi",
            "ğŸ“‹ Karar Defteri",
            "âŒ Hata YÃ¶netimi",
        ]
    )
    with sekmeler[0]:
        render_yonetim_tab()
    with sekmeler[1]:
        render_kpi_tab()
    with sekmeler[2]:
        render_cost_tab()
    with sekmeler[3]:
        render_quality_tab()
    with sekmeler[4]:
        render_api_analytics_tab()
    with sekmeler[5]:
        render_karar_defteri()
    with sekmeler[6]:
        render_errors_tab()


# KayÄ±ttaki modÃ¼l yerine app.py iÃ§indeki bileÅŸimi kullanacak bÃ¶lÃ¼mler.
RENDER_OVERRIDES: dict[str, Callable[[], None]] = {
    "yonetim": render_yonetim_bilesik,
}


# --------------------------------------------------------------------------- #
# st.navigation Sayfa Ãœreticisi (NAV-01)
# --------------------------------------------------------------------------- #


def _sayfa_cizici(tanim: TabTanimi) -> Callable[[], None]:
    """BÃ¶lÃ¼mÃ¼ hata sÄ±nÄ±rÄ± iÃ§inde Ã§izen, adÄ± olan bir sayfa fonksiyonu Ã¼retir.

    st.Page Ã§aÄŸrÄ±labilir nesnenin ``__name__`` Ã¶zelliÄŸine bakabildiÄŸi iÃ§in
    ``functools.partial`` yerine kapalÄ± fonksiyon (closure) kullanÄ±lÄ±r.
    Hata sÄ±nÄ±rÄ±, hazÄ±r-deÄŸil yer tutucu ve yÃ¼klenemedi mesajÄ± `render_icerik`
    iÃ§inde tek yerde durur.
    """

    def _sayfa() -> None:
        render_icerik(tanim)

    _sayfa.__name__ = f"sayfa_{tanim.anahtar}"
    _sayfa.__qualname__ = _sayfa.__name__
    return _sayfa


def sayfalari_uret() -> list:
    """SECTIONS'tan st.Page nesneleri Ã¼retir ve _SAYFA_KAYDI'ya kaydeder.

    Her sayfa `render_icerik(tanim)` Ã¼zerinden Ã§alÄ±ÅŸÄ±r; bÃ¶ylece
    RENDER_OVERRIDES > dinamik import > placeholder sÄ±rasÄ± ve hata sÄ±nÄ±rÄ±
    (bir bÃ¶lÃ¼m patlarsa panel dÃ¼ÅŸmez) tek noktada korunur.
    Default sayfa: `varsayilan_tab()`.
    """
    sayfalar = []
    varsayilan = varsayilan_tab()

    for tanim in SECTIONS:
        sayfa = st.Page(
            _sayfa_cizici(tanim),
            title=tanim.baslik,
            icon=tanim.ikon,
            url_path=tanim.url_path,
            default=(tanim.anahtar == varsayilan.anahtar),
        )
        _SAYFA_KAYDI[tanim.anahtar] = sayfa
        sayfalar.append(sayfa)

    return sayfalar


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #


def _nav_ipucu(tanim: TabTanimi, kompakt: bool) -> str:
    """MenÃ¼ dÃ¼ÄŸmesinin tooltip metni.

    Kompakt modda etiket gÃ¶rÃ¼nmediÄŸi iÃ§in baÅŸlÄ±k da tooltip'e taÅŸÄ±nÄ±r
    (eriÅŸilebilirlik: yalnÄ±z ikon bÄ±rakÄ±lmaz).
    """
    ek = "" if tanim.hazir else " Â· â³ yapÄ±m aÅŸamasÄ±nda"
    if kompakt:
        return f"{tanim.baslik} â€” {tanim.aciklama}{ek}"
    return f"{tanim.aciklama}{ek}"


def _nav_grubu_ciz(tanimlar: list[TabTanimi], secili: TabTanimi, kompakt: bool) -> None:
    """Tek bir menÃ¼ grubunu Ã§izer.

    ADMIN-UI-04: Ä°kon dizilimi ve sÄ±rasÄ± **deÄŸiÅŸmez**; kompakt modda yalnÄ±zca
    metin etiketi gizlenir, ikon ve sÄ±ra aynen korunur.
    """
    if kompakt:
        for bas in range(0, len(tanimlar), KOMPAKT_SUTUN):
            dilim = tanimlar[bas : bas + KOMPAKT_SUTUN]
            kolonlar = st.columns(KOMPAKT_SUTUN)
            for kolon, tanim in zip(kolonlar, dilim):
                aktif = tanim.anahtar == secili.anahtar
                with kolon:
                    if st.button(
                        tanim.ikon,
                        key=f"nav_{tanim.anahtar}",
                        width="stretch",
                        type="primary" if aktif else "secondary",
                        help=_nav_ipucu(tanim, True),
                        disabled=aktif,
                    ):
                        bolum_sec(tanim.anahtar)
        return

    for tanim in tanimlar:
        aktif = tanim.anahtar == secili.anahtar
        etiket = f"{tanim.etiket}{'' if tanim.hazir else ' â³'}"
        if st.button(
            etiket,
            key=f"nav_{tanim.anahtar}",
            width="stretch",
            type="primary" if aktif else "secondary",
            help=_nav_ipucu(tanim, False),
            disabled=aktif,
        ):
            bolum_sec(tanim.anahtar)


def render_sidebar(secili: TabTanimi) -> None:
    """Modern sidebar: marka başlığı, hızlı geçiş, gruplu navigasyon.

    ADMIN-UI-04: "Kompakt menü" anahtarı ikon-only görünümüne geçirir;
    ikon seti, sıra ve gruplama korunur, yalnızca metin gizlenir.
    """
    with st.sidebar:
        kompakt = bool(st.session_state.get(KOMPAKT_KEY, False))

        if kompakt:
            st.markdown("## 🏢")
        else:
            st.markdown("## 🏢 Huginn")
            st.caption(t("odin_command_center"))

        st.toggle(
            "Kompakt menü",
            key=KOMPAKT_KEY,
            help="Yalnız ikonlar görünür; başlıklar imleçle üzerine gelince çıkar.",
        )
        # UI-SIDEBAR-02: Marka blogu bölümü
        st.markdown("### 📝 Marka Blogu")
        st.caption("Bu bölümde marka ile ilgili blog yazıları yer alacaktır. (Placeholder)")
        st.divider()

        # U-10: yalnızca rolün görebildiği bölümler menüye girer.
        rol = aktif_rol()
        gorunur = list(gorunur_bolumler(rol))
        if secili not in gorunur:  # derin bağlantıyla gelinmiş yetkisiz sayfa
            gorunur.append(secili)

        # --- Hızlı geçiş: tek adımda herhangi bir bölüme ---
        if not kompakt:
            secenekler = gorunur
            secim = st.selectbox(
                "🔍 Hızlı geçiş",
                secenekler,
                index=secenekler.index(secili),
                format_func=lambda tanim: tanim.etiket,
                key="nav_hizli_gecis",
                help="Bölüm adını yazarak doğrudan geçiş yapın.",
            )
            if secim.anahtar != secili.anahtar:
                bolum_sec(secim.anahtar)

            st.divider()

        for grup_adi, tanimlar in gruplar(rol).items():
            if kompakt:
                st.caption(grup_adi.split(" ", 1)[0] if " " in grup_adi else grup_adi)
            else:
                st.markdown(f"##### {grup_adi}")
            _nav_grubu_ciz(tanimlar, secili, kompakt)
            st.write("")

        st.divider()
        gorunur_sayisi = len(gorunur_bolumler(rol))
        hazir_sayisi = sum(1 for tanim in gorunur_bolumler(rol) if tanim.hazir)
        gizli_sayisi = len(SECTIONS) - gorunur_sayisi
        if kompakt:
            st.caption(f"{hazir_sayisi}/{gorunur_sayisi}")
        else:
            gizli_notu = f" · 🔒 {gizli_sayisi} bölüm giriş gerektirir" if gizli_sayisi else ""
            st.caption(
                f"Bölüm: {hazir_sayisi}/{gorunur_sayisi} hazır · ⏳ = yapım aşamasında"
                f"{gizli_notu}\n\nP7-44 Modern Navigasyon"
            )
def render_topbar(tanim: TabTanimi) -> None:
    """ADMIN-UI-03 Ã¼st ÅŸerit: kÄ±rÄ±ntÄ± yolu + H1, saÄŸda bÃ¶lÃ¼m aramasÄ±.

    Arama alanÄ± hibrittir: gÃ¶rsel kabuk Streamlit `st.text_input`, eÅŸleÅŸme
    mantÄ±ÄŸÄ± `bolum_ara()`. Tek eÅŸleÅŸme â†’ doÄŸrudan geÃ§iÅŸ; Ã§oklu eÅŸleÅŸme â†’
    ikincil buton listesi (aynÄ± ekranda tek birincil buton kuralÄ± korunur).

    U-01: Tema dÃ¼ÄŸmesi buradan kaldÄ±rÄ±ldÄ± â€” Streamlit'in â‹® menÃ¼sÃ¼ndeki
    Appearance ayarÄ±yla mÃ¼kerrerdi ve iki ayrÄ± kaynak birbirini tutmuyordu.
    """
    sol, sag = st.columns([7, 3], vertical_alignment="center")
    with sol:
        # Bu sayfada breadcrumb
        breadcrumb_path = f"🏠 {t('menu_h_ana')} > {tanim.grup} > {tanim.baslik}"
        st.caption(breadcrumb_path)
        TopBar(
            tanim.baslik,
            ust_etiket=tanim.grup,  # Fixed: was hardcoded to "İş · Yönetim"
        ).render()
    with sag:
        sorgu = st.text_input(
            "BÃ¶lÃ¼m ara",
            key=ARAMA_KEY,
            placeholder="ğŸ” BÃ¶lÃ¼m araâ€¦  (Ã¶r. kalite, mÃ¼ÅŸteri)",
            label_visibility="collapsed",
        )

    # NOT: widget oluÅŸtuktan sonra st.session_state[ARAMA_KEY] yazÄ±lamaz
    # (StreamlitAPIException); bu yÃ¼zden sorgu temizlenmez, navigasyon
    # koÅŸullarÄ± dÃ¶ngÃ¼yÃ¼ kendiliÄŸinden keser (aktif bÃ¶lÃ¼m eÅŸleÅŸmesi atlanÄ±r).
    eslesenler = bolum_ara(sorgu)
    if sorgu and not eslesenler:
        st.caption(f"â€œ{sorgu}â€ iÃ§in bÃ¶lÃ¼m bulunamadÄ±.")
    elif len(eslesenler) == 1 and eslesenler[0].anahtar != tanim.anahtar:
        bolum_sec(eslesenler[0].anahtar)
    elif len(eslesenler) > 1:
        kolonlar = st.columns(min(len(eslesenler), ARAMA_MAKS_SONUC))
        for kolon, aday in zip(kolonlar, eslesenler[:ARAMA_MAKS_SONUC]):
            with kolon:
                if st.button(
                    aday.etiket,
                    key=f"ara_{aday.anahtar}",
                    width="stretch",
                    help=aday.aciklama,
                    disabled=aday.anahtar == tanim.anahtar,
                ):
                    bolum_sec(aday.anahtar)

    st.caption(f"{tanim.aciklama} Â· Son yÃ¼kleme: {datetime.now().strftime('%H:%M')}")
    st.divider()


def render_chat(tanim: TabTanimi, acik: bool) -> None:
    """SaÄŸ alt "AI MIMIR" sohbet balonu â€” UI kabuÄŸu.

    Motor baÄŸlantÄ±sÄ± ayrÄ± gÃ¶revdir; ÅŸimdilik panel aÃ§Ä±lÄ±r/kapanÄ±r ve
    kullanÄ±cÄ±ya "motor baÄŸlÄ± deÄŸil" notunu gÃ¶sterir.
    """
    ChatBubble(
        acik=acik,
        mesajlar=st.session_state.get("_hg_sohbet_mesajlar", []),
        ac_url=_baglanti(tanim, **{SOHBET_PARAM: "acik"}),
        kapat_url=_baglanti(tanim, **{SOHBET_PARAM: "kapali"}),
        not_metni=t("odin_ai_co_pilot"),
    ).render()


def render_placeholder(tanim: TabTanimi) -> None:
    """K2: hazÄ±r olmayan bÃ¶lÃ¼m iÃ§in boÅŸ ekran yerine aÃ§Ä±klayÄ±cÄ± bilgi."""
    st.info(
        f"â³ **{tanim.baslik}** bÃ¶lÃ¼mÃ¼ henÃ¼z hazÄ±r deÄŸil.\n\n"
        f"Bekleyen gÃ¶rev: `{tanim.bekleyen_gorev or 'planlanÄ±yor'}` â€” "
        f"tamamlandÄ±ÄŸÄ±nda {tanim.aciklama.lower()} burada gÃ¶rÃ¼necek."
    )


def render_yetki_uyarisi(tanim: TabTanimi) -> None:
    """U-10: Derin baÄŸlantÄ±yla gelinen yetkisiz bÃ¶lÃ¼m iÃ§in aÃ§Ä±klayÄ±cÄ± ekran."""
    st.warning(
        f"ğŸ”’ **{tanim.baslik}** bÃ¶lÃ¼mÃ¼ iÃ§in `{tanim.min_rol}` yetkisi gerekir. "
        "YÃ¶netim bÃ¶lÃ¼mÃ¼nden admin giriÅŸi yapÄ±n."
    )
    yonetim = tab_getir("yonetim")
    if yonetim is not None and st.button("ğŸ” YÃ¶netim â†’ Admin giriÅŸi", key="yetki_yonetim"):
        bolum_sec(yonetim.anahtar)


def render_musteri_onizleme(tanim: TabTanimi) -> None:
    """MIG-UI-01: Hedefi Huginn olan bÃ¶lÃ¼m iÃ§in geÃ§iÅŸ dÃ¶nemi ÅŸeridi.

    Tam gÃ¶Ã§ "Huginn tasarÄ±m turu" tamamlanÄ±nca yapÄ±lÄ±r; o zamana kadar bÃ¶lÃ¼m
    Muninn'de kalÄ±r ve iÃ§ ekibe mÃ¼ÅŸteri ekranÄ± olduÄŸu aÃ§Ä±kÃ§a bildirilir.
    """
    st.caption(
        f"ğŸ‘ **MÃ¼ÅŸteri Ã–nizleme** â€” *{tanim.baslik}* bir Huginn ğŸ¦… (mÃ¼ÅŸteri) "
        "ekranÄ±dÄ±r; tasarÄ±m turu sonrasÄ± 8000 portundaki arayÃ¼ze taÅŸÄ±nacak. "
        "Burada yalnÄ±zca iÃ§ ekip Ã¶nizlemesi iÃ§in gÃ¶rÃ¼nÃ¼r."
    )


def render_icerik(tanim: TabTanimi) -> None:
    """SeÃ§ili bÃ¶lÃ¼mÃ¼ hata sÄ±nÄ±rÄ± iÃ§inde Ã§izer."""
    if not erisebilir(tanim, aktif_rol()):
        render_yetki_uyarisi(tanim)
        return
    if not tanim.hazir:
        render_placeholder(tanim)
        return
    if tanim.musteri_onizleme:
        render_musteri_onizleme(tanim)

    fn = RENDER_OVERRIDES.get(tanim.anahtar) or render_fonksiyonu(tanim)
    if fn is None:
        st.error(
            f"âŒ **{tanim.baslik}** bÃ¶lÃ¼mÃ¼ yÃ¼klenemedi.\n\n"
            f"Beklenen: `{tanim.modul}.{tanim.fonksiyon}`. "
            "ModÃ¼l taÅŸÄ±nmÄ±ÅŸ veya fonksiyon adÄ± deÄŸiÅŸmiÅŸ olabilir."
        )
        return

    try:
        fn()
    except Exception as exc:  # hata sÄ±nÄ±rÄ±: navigasyon ayakta kalsÄ±n
        st.error(f"âŒ **{tanim.baslik}** Ã§izilirken hata oluÅŸtu: {exc}")
        with st.expander("ğŸ” Teknik ayrÄ±ntÄ±"):
            st.code(traceback.format_exc(), language="text")
        st.caption("DiÄŸer bÃ¶lÃ¼mler Ã§alÄ±ÅŸmaya devam ediyor; sol menÃ¼den geÃ§iÅŸ yapabilirsiniz.")


def render_footer(tanim: TabTanimi) -> None:
    """Alt bilgi: yÃ¼kleme sÃ¼resi, aktif bÃ¶lÃ¼m, cache Ã¶mrÃ¼.

    U-07: "Cache Temizle" dÃ¼ÄŸmesi kaldÄ±rÄ±ldÄ± â€” Streamlit'in â‹® menÃ¼sÃ¼ndeki
    "Clear cache" ile mÃ¼kerrerdi. MenÃ¼ `toolbarMode = "auto"` ile geri geldi.
    """
    st.divider()
    baslangic = st.session_state["perf_metrics"].get("page_load_start")
    if not baslangic:
        st.caption("Performans metrikleri bir sonraki yÃ¼klemede gÃ¶rÃ¼necek.")
        return
    yukleme_ms = (_time.perf_counter() - baslangic) * 1000
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Sayfa YÃ¼kleme", f"{yukleme_ms:.0f} ms")
    with c2:
        st.metric("Aktif BÃ¶lÃ¼m", tanim.baslik)
    with c3:
        st.metric("Cache TTL", "30 sn")
    st.caption("Ã–nbelleÄŸi temizlemek iÃ§in saÄŸ Ã¼st â‹® menÃ¼sÃ¼ â€º Clear cache.")


def main() -> None:
    """Uygulama giriÅŸ noktasÄ± â€” st.navigation + markalÄ± sidebar.
    
    NAV-01 hibrit multipage mimarisi:
    - st.navigation(..., position="hidden") â€” Streamlit'in kendi menÃ¼sÃ¼ Ã§izilmez,
      yÃ¶nlendirme ve "hangi sayfa Ã§alÄ±ÅŸÄ±yor" bilgisi saÄŸlanÄ±r.
    - render_sidebar() â€” MarkalÄ± sol menÃ¼ aynen yerinde kalÄ±r.
    - sayfa.run() â€” SeÃ§ili st.Page'nin render fonksiyonunu Ã§alÄ±ÅŸtÄ±rÄ±r.
    - render_footer/render_chat â€” Ana akÄ±ÅŸÄ±n parÃ§asÄ± (sayfa.run() sonrasÄ±).
    """
    stil_enjekte(tema=aktif_tema())

    # st.navigation() Ã§alÄ±ÅŸtÄ±rarak sayfa objesini al (Ã¶nce _SAYFA_KAYDI dolmalÄ±)
    sayfa = st.navigation(sayfalari_uret(), position="hidden")
    _eski_adresi_cevir()  # Eski ?bolum=... baÄŸlantÄ±larÄ±nÄ± /{url_path} olarak Ã§evir
    
    # SayfanÄ±n URL yolundan bÃ¶lÃ¼mÃ¼ bul; yoksa varsayÄ±lan
    if sayfa and hasattr(sayfa, "url_path"):
        secili = tab_url_getir(sayfa.url_path) or varsayilan_tab()
        st.session_state["current_section"] = secili.anahtar
    else:
        secili = aktif_tab()
    
    # MarkalÄ± sidebar + Ã¼st ÅŸerit (kÄ±rÄ±ntÄ± yolu, H1, bÃ¶lÃ¼m arama)
    render_sidebar(secili)
    render_topbar(secili)

    # Sayfa iÃ§eriÄŸini Ã§alÄ±ÅŸtÄ±r â€” render_icerik hata sÄ±nÄ±rÄ± iÃ§inde Ã§alÄ±ÅŸÄ±r
    sayfa.run()
    
    # SayfanÄ±n altÄ±nda footer ve sohbet balonu
    render_footer(secili)
    render_chat(secili, sohbet_acik_mi())


main()



