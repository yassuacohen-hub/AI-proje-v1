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

st.set_page_config(
    page_title="Huginn — Company Master Dashboard",
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded",
)

URL_PARAM = "bolum"

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


def render_sidebar(secili: TabTanimi) -> None:
    """Modern sidebar: marka başlığı, hızlı geçiş, gruplu navigasyon."""
    with st.sidebar:
        st.markdown("## 🏢 Huginn")
        st.caption("Company Master · Veri Zekâsı Paneli")
        st.divider()

        # --- Hızlı geçiş: tek adımda herhangi bir bölüme ---
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
            st.markdown(f"##### {grup_adi}")
            for tanim in tanimlar:
                aktif = tanim.anahtar == secili.anahtar
                etiket = f"{tanim.etiket}{'' if tanim.hazir else ' ⏳'}"
                if st.button(
                    etiket,
                    key=f"nav_{tanim.anahtar}",
                    use_container_width=True,
                    type="primary" if aktif else "secondary",
                    help=tanim.aciklama,
                    disabled=aktif,
                ):
                    bolum_sec(tanim.anahtar)
            st.write("")

        st.divider()
        hazir_sayisi = sum(1 for t in SECTIONS if t.hazir)
        st.caption(
            f"Bölüm: {hazir_sayisi}/{len(SECTIONS)} hazır · ⏳ = yapım aşamasında\n\n"
            "P7-44 Modern Navigasyon"
        )


# --------------------------------------------------------------------------- #
# Ana içerik
# --------------------------------------------------------------------------- #


def render_breadcrumb(tanim: TabTanimi) -> None:
    """Üst kırıntı yolu: kullanıcı nerede olduğunu ve ne göreceğini bilir."""
    st.markdown(f"##### 🏠 Panel › {tanim.grup} › **{tanim.baslik}**")
    st.caption(f"{tanim.aciklama} · Son yükleme: {datetime.now().strftime('%H:%M')}")
    st.divider()


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
    render_sidebar(secili)
    render_breadcrumb(secili)
    render_icerik(secili)
    render_footer(secili)


main()
