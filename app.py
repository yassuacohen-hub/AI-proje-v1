#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Streamlit Dashboard — P7-44: Modern Navigasyon.

Ne değişti (P7-44):
    1. **Tek doğru kaynak (SSOT):** Sekme listesi artık `app.py` içinde değil,
       `web_dashboard/tabs/__init__.py` → `SECTIONS` kaydında. Sidebar butonu ve
       yönlendirme dalı otomatik türetilir; ikisi birbirinden kaçamaz.
    2. **Placeholder'lar kaldırıldı:** Paketler ve Pazarlama sekmeleri gerçek
       render fonksiyonlarına bağlandı (K-01 kapandı).
    3. **Tembel (lazy) import:** Sadece görüntülenen bölümün modülü yüklenir;
       açılışta 20+ modül import edilmez.
    4. **Derin bağlantı:** `?bolum=paketler` ile doğrudan bölüme girilebilir,
       seçim URL'e yazılır (yenileme/paylaşım seçimi korur).
    5. **Aktif durum vurgusu + breadcrumb:** Kullanıcı nerede olduğunu görür.
    6. **Hızlı geçiş:** Sidebar'daki arama kutusundan tüm bölümlere tek adımda.
    7. **Hata sınırı:** Bir bölüm patlarsa panel komple düşmez; hata o bölümde
       gösterilir, navigasyon çalışmaya devam eder.

Navigasyon (BK5):
    İş Operasyonları : Ana Kontrol · Müşteriler · Paketler · Pazarlama · Abrakadabra
    Sistem & Yönetim : Sistem · Canlı Veri · Yönetim

Çalıştırma:
    streamlit run app.py
"""
from __future__ import annotations

import sys
import time as _time
import traceback
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
    alt_sekmeler,
    ust_sayfalar,
    render_fonksiyonu,
    rol_normalize,
    tab_getir,
    tab_url_getir,
    varsayilan_tab,
)

from company_master.i18n import t  # noqa: E402
from company_master.ui import (  # noqa: E402
    ChatBubble,
    stil_enjekte,
)
from company_master.ui.components.modal import Modal  # noqa: E402

# UI-WIDE-01: Ürün Sahibi kararı — sayfa varsayılan olarak geniş (wide) açılır;
# `toolbarMode = "auto"` (.streamlit/config.toml) sayesinde sağ üstteki ⋮
# Settings menüsü hâlâ görünür ve kullanıcı dilerse "Wide mode"u kapatıp
# tekrar "Centered" moda geçebilir (bu tercih tarayıcıda saklanır).
st.set_page_config(
    page_title="Huginn — Company Master Dashboard",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

URL_PARAM = "bolum"
SOHBET_PARAM = "sohbet"
ARAMA_KEY = "_hg_arama_sorgu"
TEMA_KEY = "_hg_tema"
SOHBET_KEY = "_hg_sohbet_acik"
#: Streamlit'in tema adları → iç tasarım sistemi anahtarlarımız.
STREAMLIT_TEMA_ESLEME = {"light": "aydinlik", "dark": "karanlik"}
#: `st.context.theme` okunamazsa kullanılacak değer; config.toml `base = "light"`.
VARSAYILAN_TEMA = "aydinlik"
ARAMA_MAKS_SONUC = 5
KOMPAKT_KEY = "_hg_menu_kompakt"
KOMPAKT_SUTUN = 4  # ikon-only modda satır başına düşen ikon sayısı
#: NAV-FIX-03: Menü tooltip'leri varsayılan KAPALI — Streamlit'in native
#: tooltip'i konumlandırılamaz ve butonların üzerine biner (sahip bulgusu,
#: 2026-09-16). Kullanıcı isterse sidebar'dan açar.
IPUCU_KEY = "_hg_menu_ipucu_ac"
#: U-10: Oturum rolü. Yazılırsa `admin_token` türetimini ezer (test/gelecek RBAC).
ROL_KEY = "_hg_rol"

# --------------------------------------------------------------------------- #
# Oturum durumu
# --------------------------------------------------------------------------- #

if "perf_metrics" not in st.session_state:
    st.session_state["perf_metrics"] = {"page_load_start": None, "son_bolum": ""}
st.session_state["perf_metrics"]["page_load_start"] = _time.perf_counter()

if "current_section" not in st.session_state:
    st.session_state["current_section"] = varsayilan_tab().anahtar

# NAV-01: her bölümün `st.Page` nesnesi. `sayfalari_uret()` her koşuda doldurur;
# `bolum_sec()` ve eski adres çevirici buradan sayfa nesnesine ulaşır.
_SAYFA_KAYDI: dict[str, Any] = {}  # anahtar -> st.Page nesnesi


# --------------------------------------------------------------------------- #
# Yönlendirme (routing) yardımcıları
# --------------------------------------------------------------------------- #


def _eski_adresi_cevir() -> None:
    """Eski `?bolum=...` adresini yeni `/{url_path}` yoluna taşır.

    Geriye dönük uyum: dışarıda paylaşılmış eski bağlantılar bozulmasın.
    Parametre okunduktan sonra **temizlenir**; aksi hâlde her koşuda yeniden
    yönlendirme tetiklenir (sonsuz yenileme).
    """
    try:
        ham = st.query_params.get(URL_PARAM, "")
    except Exception:  # Streamlit sürüm farkı — URL yoksa sessizce geç
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
    """U-10: Oturumun rolünü döndürür.

    Öncelik: `st.session_state[ROL_KEY]` → varsa `admin_token` ⇒ `admin`
    → aksi hâlde `anon`. Bilinmeyen değerler `anon`a indirgenir.
    """
    acik = st.session_state.get(ROL_KEY)
    if acik:
        return rol_normalize(str(acik))
    return ROL_ADMIN if st.session_state.get("admin_token") else ROL_ANON


def aktif_tab() -> TabTanimi:
    """Oturumdaki bölümü döndürür (geri uyum; yönlendirme artık sayfa temelli)."""
    tanim = tab_getir(st.session_state.get("current_section", ""))
    return tanim or varsayilan_tab()


def bolum_sec(anahtar: str) -> None:
    """Sidebar/hızlı geçiş tıklamasında bölüm sayfasına geçer."""
    if st.session_state.get("current_section") == anahtar:
        return
    st.session_state["current_section"] = anahtar
    sayfa = _SAYFA_KAYDI.get(anahtar)
    if sayfa is None:  # sayfa üretilmemişse en azından yeniden çiz
        st.rerun()
    st.switch_page(sayfa)


def _url_param_oku(ad: str) -> str:
    """Tek bir sorgu parametresini güvenli biçimde metin olarak okur."""
    try:
        ham = st.query_params.get(ad, "")
    except Exception:
        return ""
    if isinstance(ham, list):
        ham = ham[0] if ham else ""
    return str(ham or "").strip().lower()


def _url_param_yaz(ad: str, deger: str) -> None:
    """Sorgu parametresini yalnızca değiştiyse yazar (gereksiz rerun yok)."""
    try:
        if st.query_params.get(ad) != deger:
            st.query_params[ad] = deger
    except Exception:
        pass


def aktif_tema() -> str:
    """Geçerli temayı **Streamlit'in kendi ayarından** okur.

    U-01: Sayfa içindeki ikinci gece/gündüz düğmesi kaldırıldı. Tek doğru
    kaynak artık sağ üst ⋮ menüsü › Settings › Appearance. `st.context.theme`
    kullanıcının seçtiği temayı verir; alan yoksa (eski sürüm) varsayılana
    düşülür ve uygulama kırılmaz.
    """
    tip = ""
    try:
        tema_ctx = getattr(st.context, "theme", None)
        tip = str(getattr(tema_ctx, "type", "") or "").strip().lower()
    except Exception:  # bağlam yoksa (test/çevrimdışı çalıştırma) sessizce geç
        tip = ""
    tema = STREAMLIT_TEMA_ESLEME.get(tip, VARSAYILAN_TEMA)
    st.session_state[TEMA_KEY] = tema
    return tema


def sohbet_acik_mi() -> bool:
    """Sağ alt sohbet panelinin açık/kapalı durumu (URL > oturum)."""
    ham = _url_param_oku(SOHBET_PARAM)
    if ham in {"acik", "kapali"}:
        st.session_state[SOHBET_KEY] = ham == "acik"
    acik = bool(st.session_state.get(SOHBET_KEY, False))
    _url_param_yaz(SOHBET_PARAM, "acik" if acik else "kapali")
    return acik


def _baglanti(tanim: TabTanimi, **ek: str) -> str:
    """Bölümü koruyan sorgu bağlantısı üretir (`/{url_path}?tema=...&...`).

    NAV-01: st.navigation yönlendirmesi kullanıldığından, `bolum` parametresi
    artık URL yolunda (`/{url_path}`). Tema/sohbet gibi ek parametreler sorgu
    satırına yazılır; sayfa geçişi `st.switch_page()` ile yapılır.
    """
    ek_str = "&".join(f"{k}={v}" for k, v in ek.items()) if ek else ""
    taban = f"/{tanim.url_path}"
    return f"{taban}?{ek_str}" if ek_str else taban


def bolum_ara(sorgu: str) -> list[TabTanimi]:
    """Arama sorgusunu bölümlerle eşler (başlık, etiket, açıklama, anahtar)."""
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
# app.py'ye özgü render'lar (Yönetim bileşimi)
# --------------------------------------------------------------------------- #


def render_karar_defteri() -> None:
    """Orkestratör karar kayıtlarının defteri — render_decision_tab'a devrolundu.
    
    (Mükerrer fonksiyon — tabs/admin_panel.py::render_decision_tab() kullanılıyor.)
    Eski implementasyon silinmiş, yönetim bölümü tabs versiyonuna yönlendirilmiş.
    """
    from web_dashboard.tabs.admin_panel import render_decision_tab
    
    render_decision_tab()


# Kayıttaki modül yerine app.py içindeki bileşimi kullanacak bölümler.
RENDER_OVERRIDES: dict[str, Callable[[], None]] = {}


# --------------------------------------------------------------------------- #
# st.navigation Sayfa Üreticisi (NAV-01)
# --------------------------------------------------------------------------- #


def _sayfa_cizici(tanim: TabTanimi) -> Callable[[], None]:
    """Bölümü hata sınırı içinde çizen, adı olan bir sayfa fonksiyonu üretir.

    st.Page çağrılabilir nesnenin ``__name__`` özelliğine bakabildiği için
    ``functools.partial`` yerine kapalı fonksiyon (closure) kullanılır.
    Hata sınırı, hazır-değil yer tutucu ve yüklenemedi mesajı `render_icerik`
    içinde tek yerde durur.
    """

    def _sayfa() -> None:
        render_icerik(tanim)

    _sayfa.__name__ = f"sayfa_{tanim.anahtar}"
    _sayfa.__qualname__ = _sayfa.__name__
    return _sayfa


def sayfalari_uret() -> list:
    """SECTIONS'tan st.Page nesneleri üretir ve _SAYFA_KAYDI'ya kaydeder.

    Her sayfa `render_icerik(tanim)` üzerinden çalışır; böylece
    RENDER_OVERRIDES > dinamik import > placeholder sırası ve hata sınırı
    (bir bölüm patlarsa panel düşmez) tek noktada korunur.
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


def _nav_ipucu(tanim: TabTanimi, kompakt: bool) -> str | None:
    """NAV-FIX-02: Tooltip metni — her durumda None.

    Native Streamlit tooltip'leri menü butonlarının üzerine binip
    menüyü kullanılamaz hale getiriyordu. Kullanıcı isteği: bilgi
    yazıları menü dışında sağda gösterilsin. Bu fonksiyon geriye
    hiçbir şey döndürmez; bilgi sağ üstte (topbar) ve sadece toggle
    açıkken gösterilir.
    """
    return None


def _nav_grubu_ciz(tanimlar: list[TabTanimi], secili: TabTanimi, kompakt: bool) -> None:
    """Tek bir menü grubunu çizer.

    ADMIN-UI-04: İkon dizilimi ve sırası **değişmez**; kompakt modda yalnızca
    metin etiketi gizlenir, ikon ve sıra aynen korunur.
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
        etiket = f"{tanim.etiket}{'' if tanim.hazir else ' ⏳'}"
        if st.button(
            etiket,
            key=f"nav_{tanim.anahtar}",
            width="stretch",
            type="primary" if aktif else "secondary",
            help=_nav_ipucu(tanim, False),
            disabled=aktif,
        ):
            bolum_sec(tanim.anahtar)


def _hesap_karti_popover() -> None:
    """NAV-IA-04: Sol-alt hesap kartı popover.

    Admin: email, Çıkış, Şifre Değiştir.
    Misafir: Giriş yap (AUTH-GATE-01 modalını tetikler).
    """
    from web_dashboard.tabs.admin_auth import (
        get_admin_token,
        render_admin_cikis,
        render_admin_login,
        render_sifre_degistir,
    )

    token = get_admin_token()
    email = st.session_state.get("admin_email") or "Misafir"

    with st.popover(f"👤 {email}"):
        if token:
            st.caption("Rol: admin")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Şifre Değiştir", key="pop_sifre"):
                    render_sifre_degistir()
            with col2:
                if st.button("Çıkış", key="pop_cikis"):
                    render_admin_cikis()
                    st.rerun()
        else:
            if st.button("Giriş Yap", key="pop_giris"):
                st.session_state["_force_auth_gate"] = True
                st.rerun()


def render_sidebar(secili: TabTanimi) -> None:
    """Modern sidebar: marka başlığı, hızlı geçiş, 6 üst sayfa + alt sekmeler.

    NAV-IA-01: Sidebar artık grup değil 6 üst sayfaya göre listelenir.
    Aktif üst sayfanın alt sekmeleri altında gösterilir.
    `GRUP_IS/GRUP_SISTEM` geriye dönük korunur (testler için) ama
    sidebar artık `ust_sayfalar()` kullanır.
    NAV-IA-04: Alt kardeşte hesap kartı popover (👤 email|Misafir).
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
        st.toggle(
            "Bölüm açıklamasını göster",
            key=IPUCU_KEY,
            help="Seçili bölümün açıklaması sağ üstte, arama kutusunun altında görünür.",
        )
        # UI-SIDEBAR-02: Marka blogu bölümü
        st.markdown("### 📝 Marka Blogu")
        st.caption("Bu bölümde marka ile ilgili blog yazıları yer alacaktır. (Placeholder)")
        st.divider()

        # U-10: yalnızca rolün görebildiği bölümler menüde.
        rol = aktif_rol()
        gorunur = list(gorunur_bolumler(rol))
        if secili not in gorunur:  # derin bağlantıyla gelinmiş yetkisiz sayfa
            gorunur.append(secili)

        # --- Hızlı geçiş: tek adımda herhangi bir bölüme ---
        if not kompakt:
            secenekler = gorunur

            def _hizli_gecis_onchange():
                secim = st.session_state.get("nav_hizli_gecis")
                if secim is not None:
                    bolum_sec(secim)

            secim = st.selectbox(
                "🔍 Hızlı geçiş",
                secenekler,
                index=secenekler.index(secili) if secili in secenekler else 0,
                format_func=lambda tanim: tanim.etiket,
                key="nav_hizli_gecis",
                on_change=_hizli_gecis_onchange,
                help="Bölüm adını yazarak doğrudan geçiş yapın.",
            )

            st.divider()

        # --- NAV-IA-01: 6 üst sayfa + alt sekmeler ---
        ustlar = ust_sayfalar(rol)
        # Aktif üst sayfa anahtarı (alt sekme ise kendi üstüne bak)
        aktif_ust_key = secili.ust if secili.ust else secili.anahtar

        for key, tanim in ustlar.items():
            aktif = tanim.anahtar == aktif_ust_key or tanim.anahtar == secili.anahtar
            if kompakt:
                with st.columns(KOMPAKT_SUTUN)[0]:
                    if st.button(
                        tanim.ikon,
                        key=f"nav_{tanim.anahtar}",
                        width="stretch",
                        type="primary" if aktif else "secondary",
                        help=_nav_ipucu(tanim, True),
                        disabled=aktif,
                    ):
                        bolum_sec(tanim.anahtar)
            else:
                if st.button(
                    tanim.etiket,
                    key=f"nav_{tanim.anahtar}",
                    width="stretch",
                    type="primary" if aktif else "secondary",
                    help=_nav_ipucu(tanim, False),
                    disabled=aktif,
                ):
                    bolum_sec(tanim.anahtar)

                # Alt sekmeleri her zaman göster
                altlar = alt_sekmeler(tanim.anahtar, rol)
                for alt in altlar:
                    alt_aktif = alt.anahtar == secili.anahtar
                    if kompakt:
                        with st.columns(KOMPAKT_SUTUN)[0]:
                            if st.button(
                                f"  {alt.etiket}",
                                key=f"nav_{alt.anahtar}",
                                width="stretch",
                                type="primary" if alt_aktif else "secondary",
                                help=_nav_ipucu(alt, True) if kompakt else None,
                                disabled=alt_aktif,
                            ):
                                bolum_sec(alt.anahtar)
                    else:
                        if st.button(
                            f"  {alt.etiket}",
                            key=f"nav_{alt.anahtar}",
                            width="stretch",
                            type="primary" if alt_aktif else "secondary",
                            help=_nav_ipucu(alt, False),
                            disabled=alt_aktif,
                        ):
                            bolum_sec(alt.anahtar)

        st.divider()
        _hesap_karti_popover()
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
    """ADMIN-UI-03 üst şerit: tek kırıntı yolu, sağda bölüm araması.

    Arama alanı hibrittir: görsel kabuk Streamlit `st.text_input`, eşleşme
    mantığı `bolum_ara()`. Tek eşleşme → doğrudan geçiş; çoklu eşleşme →
    ikincil buton listesi (aynı ekranda tek birincil buton kuralı korunur).

    U-01: Tema düğmesi buradan kaldırıldı — Streamlit'in ⋮ menüsündeki
    Appearance ayarıyla mükerrerdi ve iki ayrı kaynak birbirini tutmuyordu.

    KPI-EXA-02: Sayfa H1'i her bölümün kendi `PageHeader`'ından gelir; buradaki
    `TopBar` H1'i ve açıklama satırı mükerrerdi, kaldırıldı. Kırıntı tek satır.
    """
    sol, sag = st.columns([7, 3], vertical_alignment="center")
    with sol:
        st.caption(f"{t('menu_h_ana')} › {tanim.grup} › {tanim.baslik}")
    with sag:
        sorgu = st.text_input(
            "Bölüm ara",
            key=ARAMA_KEY,
            placeholder="Bölüm ara…  (ör. kalite, müşteri)",
            label_visibility="collapsed",
        )
        if st.session_state.get(IPUCU_KEY, False):
            ek = "" if tanim.hazir else " · ⏳ yapım aşamasında"
            st.caption(f"ℹ️ {tanim.aciklama}{ek}")

    # Widget sonrası doğrudan session_state yazma serbesttir (yalnızca
    # widget'ın kendi internal state'i kısıtlı). Sorgu tek eşleşme
    # sonrası temizlenir; bolum_sec aynı rerun içinde çalışır.
    eslesenler = bolum_ara(sorgu)
    if sorgu and not eslesenler:
        st.caption(f"'{sorgu}' için bölüm bulunamadı.")
    elif len(eslesenler) == 1 and eslesenler[0].anahtar != tanim.anahtar:
        bolum_sec(eslesenler[0].anahtar)
        st.session_state[ARAMA_KEY] = ""
    elif len(eslesenler) > 1:
        kolonlar = st.columns(min(len(eslesenler), ARAMA_MAKS_SONUC))
        for kolon, aday in zip(kolonlar, eslesenler[:ARAMA_MAKS_SONUC]):
            with kolon:
                if st.button(
                    aday.etiket,
                    key=f"ara_{aday.anahtar}",
                    width="stretch",
                    disabled=aday.anahtar == tanim.anahtar,
                ):
                    bolum_sec(aday.anahtar)

    st.divider()


def render_chat(tanim: TabTanimi, acik: bool) -> None:
    """Sağ alt "AI MIMIR" sohbet balonu — UI kabuğu.

    Motor bağlantısı ayrı görevdir; şimdilik panel açılır/kapanır ve
    kullanıcıya "motor bağlı değil" notunu gösterir.
    """
    ChatBubble(
        acik=acik,
        mesajlar=st.session_state.get("_hg_sohbet_mesajlar", []),
        ac_url=_baglanti(tanim, **{SOHBET_PARAM: "acik"}),
        kapat_url=_baglanti(tanim, **{SOHBET_PARAM: "kapali"}),
        not_metni=t("odin_ai_co_pilot"),
    ).render()


def render_placeholder(tanim: TabTanimi) -> None:
    """K2: hazır olmayan bölüm için boş ekran yerine açıklayıcı bilgi."""
    st.info(
        f"⏳ **{tanim.baslik}** bölümü henüz hazır değil.\n\n"
        f"Bekleyen görev: `{tanim.bekleyen_gorev or 'planlanıyor'}` — "
        f"tamamlandığında {tanim.aciklama.lower()} burada görünecek."
    )


def render_yetki_uyarisi(tanim: TabTanimi) -> None:
    """U-10: Derin bağlantıyla gelinen yetkisiz bölüm için açıklayıcı ekran."""
    st.warning(
        f"**{tanim.baslik}** bölümü için `{tanim.min_rol}` yetkisi gerekir. "
        "Yönetim bölümünden admin girişi yapın."
    )
    yonetim = tab_getir("yonetim")
    if yonetim is not None and st.button("Yönetim → Admin girişi", key="yetki_yonetim"):
        bolum_sec(yonetim.anahtar)


def render_musteri_onizleme(tanim: TabTanimi) -> None:
    """MIG-UI-01: Hedefi Huginn olan bölüm için geçiş dönemi şeridi.

    KPI-EXA-02: Sahip kararıyla sayfa üstünden kaldırıldı (gürültü); bilgi
    yalnızca menü ipucunda (`_nav_ipucu`) kalır. Fonksiyon geriye dönük
    uyumluluk için korunur, `render_icerik` artık çağırmaz.
    """
    st.caption(
        f"**Müşteri Önizleme** — *{tanim.baslik}* bir Huginn (müşteri) "
        "ekranıdır; tasarım turu sonrası 8000 portundaki arayüze taşınacak. "
        "Burada yalnızca iç ekip önizlemesi için görünür."
    )


def render_icerik(tanim: TabTanimi) -> None:
    """Seçili bölümü hata sınırı içinde çizer."""
    if not erisebilir(tanim, aktif_rol()):
        render_yetki_uyarisi(tanim)
        return
    if not tanim.hazir:
        render_placeholder(tanim)
        return

    fn = RENDER_OVERRIDES.get(tanim.anahtar) or render_fonksiyonu(tanim)
    if fn is None:
        st.error(
            f"❌ **{tanim.baslik}** bölümü yüklenemedi.\n\n"
            f"Beklenen: `{tanim.modul}.{tanim.fonksiyon}`. "
            "Modül taşınmış veya fonksiyon adı değişmiş olabilir."
        )
        return

    try:
        fn()
    except Exception as exc:  # hata sınırı: navigasyon ayakta kalsın
        st.error(f"❌ **{tanim.baslik}** çizilirken hata oluştu: {exc}")
        with st.expander("Teknik ayrıntı"):
            st.code(traceback.format_exc(), language="text")
        st.caption("Diğer bölümler çalışmaya devam ediyor; sol menüden geçiş yapabilirsiniz.")


def render_footer(tanim: TabTanimi) -> None:
    """Alt bilgi: yükleme süresi, aktif bölüm, cache ömrü.

    U-07: "Cache Temizle" düğmesi kaldırıldı — Streamlit'in ⋮ menüsündeki
    "Clear cache" ile mükerrerdi. Menü `toolbarMode = "auto"` ile geri geldi.
    """
    st.divider()
    baslangic = st.session_state["perf_metrics"].get("page_load_start")
    if not baslangic:
        st.caption("Performans metrikleri bir sonraki yüklemede görünecek.")
        return
    yukleme_ms = (_time.perf_counter() - baslangic) * 1000
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Sayfa Yükleme", f"{yukleme_ms:.0f} ms")
    with c2:
        st.metric("Aktif Bölüm", tanim.baslik)
    with c3:
        st.metric("Cache TTL", "30 sn")
    st.caption("Önbelleği temizlemek için sağ üst ⋮ menüsü › Clear cache.")


def _auth_modal_icerik() -> None:
    """AUTH-GATE-01: Giriş kapısı modal içeriği.

    Akışlar: giriş yap, misafir olarak devam et, şifremi unuttum.
    """
    from web_dashboard.tabs.admin_auth import render_admin_login

    render_admin_login()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Misafir olarak devam et", key="misafir_gate_btn"):
            st.session_state["misafir"] = True
            st.session_state["admin_token"] = "guest"
            st.rerun()
    with col2:
        if st.button("Şifremi unuttum", key="sifre_unuttum_gate_btn"):
            st.session_state["_sifre_unuttum"] = True
            st.rerun()

    if st.session_state.get("_sifre_unuttum"):
        st.info("Sıfırlama için e-posta adresinizi girin.")
        with st.form("reset_form"):
            reset_email = st.text_input("E-posta", key="reset_email_gate")
            gönder = st.form_submit_button("Sıfırlama linki gönder")
            if gönder and reset_email:
                try:
                    from scripts.dash04_api_client import post_api as _p
                    _p("/api/admin/reset-request", json={"email": reset_email})
                    st.success("Sıfırlama linki gönderildi.")
                except Exception as exc:
                    st.error(f"Sıfırlama başarısız: {exc}")


def main() -> None:
    """Uygulama giriş noktası — st.navigation + markalı sidebar.
    
    NAV-01 hibrit multipage mimarisi:
    - st.navigation(..., position="hidden") — Streamlit'in kendi menüsü çizilmez,
      yönlendirme ve "hangi sayfa çalışıyor" bilgisi sağlanır.
    - render_sidebar() — Markalı sol menü aynen yerinde kalır.
    - sayfa.run() — Seçili st.Page'nin render fonksiyonunu çalıştırır.
    - render_footer/render_chat — Ana akışın parçası (sayfa.run() sonrası).
    """
    stil_enjekte(tema=aktif_tema())

    # AUTH-GATE-01: Admin token yoksa veya popover'dan giriş isteniyorsa giriş modalı
    if not st.session_state.get("admin_token") or st.session_state.get("_force_auth_gate"):
        Modal(
            "Admin Girişi",
            icerik="",
            kapatilabilir=False,
            aciklama="Giriş yap, misafir olarak devam et veya şifremi unuttum.",
        ).streamlit(govde_fn=_auth_modal_icerik)
        st.session_state.pop("_force_auth_gate", None)

    # st.navigation() çalıştırarak sayfa objesini al (önce _SAYFA_KAYDI dolmalı)
    sayfa = st.navigation(sayfalari_uret(), position="hidden")
    _eski_adresi_cevir()  # Eski ?bolum=... bağlantılarını /{url_path} olarak çevir

    # Sayfanın URL yolundan bölümü bul; yoksa varsayılan
    if sayfa and hasattr(sayfa, "url_path"):
        secili = tab_url_getir(sayfa.url_path) or varsayilan_tab()
        st.session_state["current_section"] = secili.anahtar
    else:
        secili = aktif_tab()

    render_sidebar(secili)
    render_topbar(secili)

    # Sayfa içeriğini çalıştır — render_icerik hata sınırı içinde çalışır
    sayfa.run()
    
    # Sayfanın altında footer ve sohbet balonu
    render_footer(secili)
    render_chat(secili, sohbet_acik_mi())


main()



