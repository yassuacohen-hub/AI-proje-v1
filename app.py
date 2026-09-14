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

import json
import sys
import time as _time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from web_dashboard.tabs import (  # noqa: E402
    SECTIONS,
    TabTanimi,
    gruplar,
    render_fonksiyonu,
    tab_getir,
    tab_url_getir,
    varsayilan_tab,
)

from company_master.ui import (  # noqa: E402
    ChatBubble,
    ThemeToggle,
    TopBar,
    stil_enjekte,
    tema_dogrula,
    tema_karsiti,
)

st.set_page_config(
    page_title="Huginn — Company Master Dashboard",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

URL_PARAM = "bolum"
TEMA_PARAM = "tema"
SOHBET_PARAM = "sohbet"
ARAMA_KEY = "_hg_arama_sorgu"
TEMA_KEY = "_hg_tema"
SOHBET_KEY = "_hg_sohbet_acik"
VARSAYILAN_TEMA = "karanlik"
ARAMA_MAKS_SONUC = 5
KOMPAKT_KEY = "_hg_menu_kompakt"
KOMPAKT_SUTUN = 4  # ikon-only modda satır başına düşen ikon sayısı

# --------------------------------------------------------------------------- #
# Oturum durumu
# --------------------------------------------------------------------------- #

if "perf_metrics" not in st.session_state:
    st.session_state["perf_metrics"] = {"page_load_start": None, "son_bolum": ""}
st.session_state["perf_metrics"]["page_load_start"] = _time.perf_counter()

if "current_section" not in st.session_state:
    st.session_state["current_section"] = varsayilan_tab().anahtar


# --------------------------------------------------------------------------- #
# Yönlendirme (routing) yardımcıları
# --------------------------------------------------------------------------- #


def _url_bolum_oku() -> TabTanimi | None:
    """URL'deki `?bolum=...` parametresini bölüm tanımına çevirir."""
    try:
        ham = st.query_params.get(URL_PARAM, "")
    except Exception:  # Streamlit sürüm farkı — URL yoksa sessizce geç
        return None
    if isinstance(ham, list):
        ham = ham[0] if ham else ""
    return tab_url_getir(str(ham))


def _url_bolum_yaz(tanim: TabTanimi) -> None:
    """Seçili bölümü URL'e yazar (yenilemede seçim korunur)."""
    try:
        if st.query_params.get(URL_PARAM) != tanim.url_path:
            st.query_params[URL_PARAM] = tanim.url_path
    except Exception:
        pass


def aktif_tab() -> TabTanimi:
    """Geçerli bölümü belirler: URL > oturum > varsayılan."""
    url_tanim = _url_bolum_oku()
    if url_tanim and url_tanim.anahtar != st.session_state.get("current_section"):
        st.session_state["current_section"] = url_tanim.anahtar
    tanim = tab_getir(st.session_state.get("current_section", ""))
    return tanim or varsayilan_tab()


def bolum_sec(anahtar: str) -> None:
    """Sidebar/hızlı geçiş tıklamasında bölümü değiştirir."""
    if st.session_state.get("current_section") != anahtar:
        st.session_state["current_section"] = anahtar
        st.rerun()


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
    """Geçerli temayı belirler: URL > oturum > varsayılan.

    ADMIN-UI-03: Sağ üstteki düğme `?tema=` bağlantısıdır (Streamlit'te JS
    çalışmaz). Tam sayfa yenilemesinde oturum sıfırlanabileceği için tema
    hem oturuma hem URL'e yazılır.
    """
    ham = _url_param_oku(TEMA_PARAM)
    try:
        tema = tema_dogrula(ham) if ham else ""
    except Exception:
        tema = ""
    if not tema:
        tema = st.session_state.get(TEMA_KEY) or VARSAYILAN_TEMA
    st.session_state[TEMA_KEY] = tema
    _url_param_yaz(TEMA_PARAM, tema)
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
    """Bölümü koruyan sorgu bağlantısı üretir (`?bolum=...&tema=...`).

    `bolum` taşınmazsa tema/sohbet tıklaması kullanıcıyı varsayılan bölüme
    fırlatır (aktif_tab önceliği URL > oturum).
    """
    parcalar = {URL_PARAM: tanim.url_path, **ek}
    return "?" + "&".join(f"{k}={v}" for k, v in parcalar.items())


def bolum_ara(sorgu: str) -> list[TabTanimi]:
    """Arama sorgusunu bölümlerle eşler (başlık, etiket, açıklama, anahtar)."""
    q = (sorgu or "").strip().casefold()
    if not q:
        return []
    sonuc: list[TabTanimi] = []
    for t in SECTIONS:
        alanlar = (t.baslik, t.etiket, t.aciklama, t.anahtar, t.grup)
        if any(q in (a or "").casefold() for a in alanlar):
            sonuc.append(t)
    return sonuc


# --------------------------------------------------------------------------- #
# app.py'ye özgü render'lar (Yönetim bileşimi)
# --------------------------------------------------------------------------- #


def render_karar_defteri() -> None:
    """Orkestratör karar kayıtlarının son 10 satırı."""
    st.subheader("📋 Karar Defteri")
    kayit_yolu = ROOT / "data" / "orchestrator" / "decision_log.jsonl"
    if not kayit_yolu.exists():
        st.info("📭 Karar defteri henüz oluşturulmadı. İlk karar yazıldığında burada görünecek.")
        return
    try:
        satirlar = [s for s in kayit_yolu.read_text(encoding="utf-8").splitlines() if s.strip()]
    except OSError as exc:
        st.error(f"Karar defteri okunamadı: {exc}")
        return
    if not satirlar:
        st.info("📭 Karar kaydı henüz yok.")
        return
    st.caption(f"Toplam karar: {len(satirlar)} · son 10 kayıt gösteriliyor")
    for satir in satirlar[-10:]:
        try:
            kayit = json.loads(satir)
        except json.JSONDecodeError:
            continue
        st.caption(f"{kayit.get('ts', '—')} · {kayit.get('op') or kayit.get('action', '—')}")


def render_yonetim_bilesik() -> None:
    """Yönetim bölümü: admin girişi + yönetim panelleri + analitik alt sekmeler.

    `admin_yonetim.render_yonetim_tab()` yalnızca API/kullanıcı/export/arama
    panellerini içerir. Admin panelinin KPI, maliyet, kalite ve API analitiği
    ekranları burada alt sekme olarak birleştirilir.
    """
    from web_dashboard.tabs.admin_api_analytics import render_api_analytics_tab
    from web_dashboard.tabs.admin_auth import render_admin_login
    from web_dashboard.tabs.admin_cost import render_cost_tab
    from web_dashboard.tabs.admin_errors import render_errors_tab
    from web_dashboard.tabs.admin_kpi import render_kpi_tab
    from web_dashboard.tabs.admin_quality import render_quality_tab
    from web_dashboard.tabs.admin_yonetim import render_yonetim_tab

    if not st.session_state.get("admin_token"):
        st.warning("🔐 Yönetim işlemleri için admin girişi gerekir.")
        render_admin_login()
        st.divider()

    sekmeler = st.tabs(
        [
            "🛠️ Yönetim Araçları",
            "📊 KPI Kartları",
            "💰 AI Maliyet",
            "🧪 Kalite Özeti",
            "🔌 API Analitiği",
            "📋 Karar Defteri",
            "❌ Hata Yönetimi",
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


# Kayıttaki modül yerine app.py içindeki bileşimi kullanacak bölümler.
RENDER_OVERRIDES: dict[str, Callable[[], None]] = {
    "yonetim": render_yonetim_bilesik,
}


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #


def _nav_ipucu(tanim: TabTanimi, kompakt: bool) -> str:
    """Menü düğmesinin tooltip metni.

    Kompakt modda etiket görünmediği için başlık da tooltip'e taşınır
    (erişilebilirlik: yalnız ikon bırakılmaz).
    """
    ek = "" if tanim.hazir else " · ⏳ yapım aşamasında"
    if kompakt:
        return f"{tanim.baslik} — {tanim.aciklama}{ek}"
    return f"{tanim.aciklama}{ek}"


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
                        use_container_width=True,
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
            use_container_width=True,
            type="primary" if aktif else "secondary",
            help=_nav_ipucu(tanim, False),
            disabled=aktif,
        ):
            bolum_sec(tanim.anahtar)


def render_sidebar(secili: TabTanimi) -> None:
    """Modern sidebar: marka başlığı, hızlı geçiş, gruplu navigasyon.

    ADMIN-UI-04: "Kompakt menü" anahtarı ikon-only görünüme geçirir;
    ikon seti, sıra ve gruplama korunur, yalnızca metin gizlenir.
    """
    with st.sidebar:
        kompakt = bool(st.session_state.get(KOMPAKT_KEY, False))

        if kompakt:
            st.markdown("## 🏢")
        else:
            st.markdown("## 🏢 Huginn")
            st.caption("Company Master · Veri Zekâsı Paneli")

        st.toggle(
            "Kompakt menü",
            key=KOMPAKT_KEY,
            help="Yalnız ikonlar görünür; başlıklar imleçle üzerine gelince çıkar.",
        )
        st.divider()

        # --- Hızlı geçiş: tek adımda herhangi bir bölüme ---
        if not kompakt:
            secenekler = list(SECTIONS)
            secim = st.selectbox(
                "🔍 Hızlı geçiş",
                secenekler,
                index=secenekler.index(secili),
                format_func=lambda t: t.etiket,
                key="nav_hizli_gecis",
                help="Bölüm adını yazarak doğrudan geçiş yapın.",
            )
            if secim.anahtar != secili.anahtar:
                bolum_sec(secim.anahtar)

            st.divider()

        for grup_adi, tanimlar in gruplar().items():
            if kompakt:
                st.caption(grup_adi.split(" ", 1)[0] if " " in grup_adi else grup_adi)
            else:
                st.markdown(f"##### {grup_adi}")
            _nav_grubu_ciz(tanimlar, secili, kompakt)
            st.write("")

        st.divider()
        hazir_sayisi = sum(1 for t in SECTIONS if t.hazir)
        if kompakt:
            st.caption(f"{hazir_sayisi}/{len(SECTIONS)}")
        else:
            st.caption(
                f"Bölüm: {hazir_sayisi}/{len(SECTIONS)} hazır · ⏳ = yapım aşamasında\n\n"
                "P7-44 Modern Navigasyon"
            )


# --------------------------------------------------------------------------- #
# Ana içerik
# --------------------------------------------------------------------------- #


def render_topbar(tanim: TabTanimi, tema: str) -> None:
    """ADMIN-UI-03 üst şerit: kırıntı yolu + H1, sağda arama ve tema düğmesi.

    Arama alanı hibrittir: görsel kabuk Streamlit `st.text_input`, eşleşme
    mantığı `bolum_ara()`. Tek eşleşme → doğrudan geçiş; çoklu eşleşme →
    ikincil buton listesi (aynı ekranda tek birincil buton kuralı korunur).
    """
    sol, sag = st.columns([7, 3], vertical_alignment="center")
    with sol:
        TopBar(
            tanim.baslik,
            ust_etiket=f"🏠 Panel › {tanim.grup}",
            sag=[
                ThemeToggle(
                    tema=tema,
                    hedef_url=_baglanti(tanim, **{TEMA_PARAM: tema_karsiti(tema)}),
                )
            ],
        ).render()
    with sag:
        sorgu = st.text_input(
            "Bölüm ara",
            key=ARAMA_KEY,
            placeholder="🔍 Bölüm ara…  (ör. kalite, müşteri)",
            label_visibility="collapsed",
        )

    # NOT: widget oluştuktan sonra st.session_state[ARAMA_KEY] yazılamaz
    # (StreamlitAPIException); bu yüzden sorgu temizlenmez, navigasyon
    # koşulları döngüyü kendiliğinden keser (aktif bölüm eşleşmesi atlanır).
    eslesenler = bolum_ara(sorgu)
    if sorgu and not eslesenler:
        st.caption(f"“{sorgu}” için bölüm bulunamadı.")
    elif len(eslesenler) == 1 and eslesenler[0].anahtar != tanim.anahtar:
        bolum_sec(eslesenler[0].anahtar)
    elif len(eslesenler) > 1:
        kolonlar = st.columns(min(len(eslesenler), ARAMA_MAKS_SONUC))
        for kolon, aday in zip(kolonlar, eslesenler[:ARAMA_MAKS_SONUC]):
            with kolon:
                if st.button(
                    aday.etiket,
                    key=f"ara_{aday.anahtar}",
                    use_container_width=True,
                    help=aday.aciklama,
                    disabled=aday.anahtar == tanim.anahtar,
                ):
                    bolum_sec(aday.anahtar)

    st.caption(f"{tanim.aciklama} · Son yükleme: {datetime.now().strftime('%H:%M')}")
    st.divider()


def render_chat(tanim: TabTanimi, acik: bool) -> None:
    """Sağ alt "AI Abrakadabra" sohbet balonu — UI kabuğu.

    Motor bağlantısı ayrı görevdir; şimdilik panel açılır/kapanır ve
    kullanıcıya "motor bağlı değil" notunu gösterir.
    """
    ChatBubble(
        acik=acik,
        mesajlar=st.session_state.get("_hg_sohbet_mesajlar", []),
        ac_url=_baglanti(tanim, **{SOHBET_PARAM: "acik"}),
        kapat_url=_baglanti(tanim, **{SOHBET_PARAM: "kapali"}),
    ).render()


def render_placeholder(tanim: TabTanimi) -> None:
    """K2: hazır olmayan bölüm için boş ekran yerine açıklayıcı bilgi."""
    st.info(
        f"⏳ **{tanim.baslik}** bölümü henüz hazır değil.\n\n"
        f"Bekleyen görev: `{tanim.bekleyen_gorev or 'planlanıyor'}` — "
        f"tamamlandığında {tanim.aciklama.lower()} burada görünecek."
    )


def render_icerik(tanim: TabTanimi) -> None:
    """Seçili bölümü hata sınırı içinde çizer."""
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
        with st.expander("🔎 Teknik ayrıntı"):
            st.code(traceback.format_exc(), language="text")
        st.caption("Diğer bölümler çalışmaya devam ediyor; sol menüden geçiş yapabilirsiniz.")


def render_footer(tanim: TabTanimi) -> None:
    """Alt bilgi: yükleme süresi, aktif bölüm, cache kontrolü."""
    st.divider()
    baslangic = st.session_state["perf_metrics"].get("page_load_start")
    if not baslangic:
        st.caption("Performans metrikleri bir sonraki yüklemede görünecek.")
        return
    yukleme_ms = (_time.perf_counter() - baslangic) * 1000
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Sayfa Yükleme", f"{yukleme_ms:.0f} ms")
    with c2:
        st.metric("Aktif Bölüm", tanim.baslik)
    with c3:
        st.metric("Cache TTL", "30 sn")
    with c4:
        if st.button("🔄 Cache Temizle", key="footer_cache_temizle", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


def main() -> None:
    """Uygulama giriş noktası."""
    secili = aktif_tab()
    _url_bolum_yaz(secili)
    tema = aktif_tema()
    stil_enjekte(tema=tema)
    render_sidebar(secili)
    render_topbar(secili, tema)
    render_icerik(secili)
    render_footer(secili)
    render_chat(secili, sohbet_acik_mi())


main()
