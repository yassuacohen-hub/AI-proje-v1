# -*- coding: utf-8 -*-
"""web_dashboard sekme paketi + merkezi navigasyon kaydı (P7-44).

Neden burada?
    Önceki tasarımda sekme listesi `app.py` içine gömülüydü: her yeni sekme
    için hem sidebar butonu hem de `if/elif` dalı elle ekleniyordu. İki yer
    birbirinden kaçtığı anda kullanıcı "hazırlanıyor" placeholder'ı görüyordu
    (bkz. `docs/ROO_ELESTIRI_NOTLARI.md` → K-01).

    Artık tek doğru kaynak (SSOT) aşağıdaki `SECTIONS` demetidir. `app.py`
    yalnızca bu kaydı okur; sidebar, yönlendirme ve derin bağlantı (URL)
    otomatik türetilir.

Tasarım kararları:
    - **Tembel (lazy) import:** Sekme modülü ancak kullanıcı o bölüme
      geçtiğinde import edilir. Açılışta 20+ modül yüklenmediği için ilk
      sayfa yükleme süresi belirgin düşer.
    - **Saf veri:** `SECTIONS` içinde Streamlit çağrısı yoktur; bu sayede
      navigasyon yapısı Streamlit runtime'ı olmadan test edilebilir.
    - **BK5:** 7 ana bölüm + Canlı Veri (P7-45 kapsamı) korunur.
    - **U-10 Rol filtresi:** Her bölümün `min_rol` alanı vardır. `SECTIONS`
      hiçbir zaman filtrelenmez (SSOT sabit kalır); `gorunur_bolumler(rol)`
      ve `gruplar(rol)` türetilmiş görünümü döndürür. Rol seviyeleri
      `company_master.auth.rbac.ROLE_HIERARCHY` ile birebir aynıdır; burada
      kopya tutulmasının nedeni bu modülün FastAPI'ye bağımlı `auth` paketini
      import etmeden saf veri kalmasıdır (test: `test_dashboard_nav`).
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Callable

import streamlit as st
from company_master.i18n import t

__all__ = [
    "TabTanimi",
    "SECTIONS",
    "GRUP_IS",
    "GRUP_SISTEM",
    "YUZEY_MUNINN",
    "YUZEY_HUGINN",
    "YUZEYLER",
    "musteri_onizleme_bolumleri",
    "ROL_ANON",
    "ROL_USER",
    "ROL_ANALYST",
    "ROL_ADMIN",
    "ROL_SEVIYE",
    "rol_normalize",
    "erisebilir",
    "gorunur_bolumler",
    "tab_getir",
    "tab_url_getir",
    "eski_url_yonlendir",
    "ust_sayfalar",
    "alt_sekmeler",
    "yenile",
    "gruplar",
    "render_fonksiyonu",
    "varsayilan_tab",
    "ESKI_URL",
]

GRUP_IS = "🏢 İş Operasyonları"
GRUP_SISTEM = "🔧 Sistem & Yönetim"

# --- MIG-UI-01: Ürün yüzeyleri (hedef arayüz) -------------------------------
# Muninn 🛡️ = iç ekip (8501 Streamlit), Huginn 🦅 = müşteri (8000 HTML).
# Hedefi Huginn olan bölümler tasarım turu bitene kadar Streamlit'te
# "Müşteri Önizleme" etiketiyle kalır (bkz. V10/14_urun_yuzeyleri_sitemap.md).
YUZEY_MUNINN = "muninn"
YUZEY_HUGINN = "huginn"
YUZEYLER: frozenset[str] = frozenset({YUZEY_MUNINN, YUZEY_HUGINN})

# --- U-10: Rol seviyeleri (rbac.ROLE_HIERARCHY aynası) ---------------------
ROL_ANON = "anon"
ROL_USER = "user"
ROL_ANALYST = "analyst"
ROL_ADMIN = "admin"

ROL_SEVIYE: dict[str, int] = {
    ROL_ANON: 0,
    ROL_USER: 1,
    ROL_ANALYST: 2,
    ROL_ADMIN: 3,
}


def rol_normalize(rol: str | None) -> str:
    """Bilinmeyen/boş rolü en düşük yetkiye (`anon`) indirger."""
    temiz = (rol or "").strip().lower()
    return temiz if temiz in ROL_SEVIYE else ROL_ANON


def erisebilir(tanim: TabTanimi, rol: str | None) -> bool:
    """Verilen rol bu bölümü görebilir mi? (seviye karşılaştırması)."""
    return ROL_SEVIYE[rol_normalize(rol)] >= ROL_SEVIYE.get(tanim.min_rol, 0)


@dataclass(frozen=True)
class TabTanimi:
    """Tek bir dashboard bölümünün navigasyon tanımı.

    Attributes:
        anahtar: Kod içi benzersiz kimlik (session_state ve override sözlüğü).
        baslik: Kullanıcıya gösterilen Türkçe başlık.
        ikon: Sidebar ikonu (emoji).
        grup: Sidebar başlığı — `GRUP_IS` veya `GRUP_SISTEM`.
        aciklama: Tek satır "bu bölüm ne işe yarar" açıklaması (K3).
        url_path: Derin bağlantı için URL parçası (`?/paketler`).
        modul: Render fonksiyonunu barındıran modül yolu (lazy import).
        fonksiyon: Modül içindeki render fonksiyonunun adı.
        hazir: False ise bölüm henüz kodlanmamıştır; placeholder gösterilir.
        bekleyen_gorev: Hazır olmayan bölümün beklediği görev kimliği.
        min_rol: Bölümü görmek için gereken en düşük rol (U-10). Varsayılan
            `anon` → herkes görür. `ROL_SEVIYE` anahtarlarından biri olmalı.
        yuzey: Bölümün **hedef ürün yüzeyi** (MIG-UI-01). `YUZEY_MUNINN`
            (8501, iç ekip) varsayılandır. `YUZEY_HUGINN` işaretli bölümler
            müşteri ekranıdır; Huginn tasarım turu tamamlanana kadar
            Streamlit'te "Müşteri Önizleme" etiketiyle kalırlar.
    """

    anahtar: str
    baslik: str
    ikon: str
    grup: str
    aciklama: str
    url_path: str
    ust: str | None = None
    sira: int = 0
    modul: str | None = None
    fonksiyon: str | None = None
    hazir: bool = True
    bekleyen_gorev: str = ""
    min_rol: str = "anon"
    yuzey: str = YUZEY_MUNINN

    def __post_init__(self) -> None:
        if self.min_rol not in ROL_SEVIYE:
            raise ValueError(
                f"{self.anahtar}: bilinmeyen min_rol={self.min_rol!r}; "
                f"izinli: {sorted(ROL_SEVIYE)}"
            )
        if self.yuzey not in YUZEYLER:
            raise ValueError(
                f"{self.anahtar}: bilinmeyen yuzey={self.yuzey!r}; "
                f"izinli: {sorted(YUZEYLER)}"
            )

    @property
    def etiket(self) -> str:
        """Sidebar'da gösterilecek "ikon + başlık" metni."""
        return f"{self.ikon} {self.baslik}"

    @property
    def musteri_onizleme(self) -> bool:
        """MIG-UI-01: Hedefi Huginn olan bölüm Muninn'de önizleme modundadır."""
        return self.yuzey == YUZEY_HUGINN


SECTIONS: tuple[TabTanimi, ...] = (
    TabTanimi(
        anahtar="ana_kontrol",
        baslik=t("menu_h_ana"),
        ikon="🏠",
        grup=GRUP_IS,
        aciklama="KPI'lar, müşteri ve sistem sağlığı tek bakışta",
        url_path="ana-kontrol",
        modul="web_dashboard.tabs.ana_kontrol",
        fonksiyon="render_ana_kontrol_tab",
        yuzey=YUZEY_HUGINN,
    ),
    TabTanimi(
        anahtar="musteriler",
        baslik=t("menu_m_musteriler"),
        ikon="👥",
        grup=GRUP_IS,
        aciklama="Firma listesi, filtreler ve kalite bildirimleri",
        url_path="musteriler",
        ust="musteri_yonetimi", sira=0,
        modul="web_dashboard.tabs.admin_musteriler",
        fonksiyon="render_musteriler_tab",
    ),
    TabTanimi(
        anahtar="paketler",
        baslik=t("menu_h_paketler"),
        ikon="📦",
        grup=GRUP_IS,
        aciklama="Paket kataloğu, fiyatlar ve çapraz satış önerileri",
        url_path="paketler",
        ust="musteri_onizleme", sira=0,
        modul="web_dashboard.tabs.paketler",
        fonksiyon="render_paketler_tab",
        yuzey=YUZEY_HUGINN,
    ),
    TabTanimi(
        anahtar="pazarlama",
        baslik=t("menu_h_pazarlama"),
        ikon="📢",
        grup=GRUP_IS,
        aciklama="Kampanyalar, segmentler ve segment kapsama analizi",
        url_path="pazarlama",
        ust="musteri_onizleme", sira=1,
        modul="web_dashboard.tabs.pazarlama",
        fonksiyon="render_pazarlama_tab",
        yuzey=YUZEY_HUGINN,
    ),
    TabTanimi(
        anahtar="abrakadabra",
        baslik=t("menu_m_abrakadabra"),
        ikon="🤖",
        grup=GRUP_IS,
        aciklama="9Router tabanlı AI sohbet ve analiz asistanı",
        url_path="abrakadabra",
        ust="proje_yonetimi", sira=1,
        modul="web_dashboard.tabs.abrakadabra",
        fonksiyon="render_abrakadabra_tab",
        min_rol="admin",
    ),
    # --- U-11: Yeni kısayol sekmeleri (sitemap Bölüm 3 menü ağacı dağıtımı) ---
    TabTanimi(
        anahtar="kpi",
        baslik=t("menu_kpi"),
        ikon="📊",
        grup=GRUP_IS,
        aciklama="KPI kartları ve özet metrikler",
        url_path="kpi",
        ust="veri_kalite", sira=0,
        modul="web_dashboard.tabs.admin_kpi",
        fonksiyon="render_kpi_tab",
        min_rol="analyst",
    ),
    # --- PO-BACK-08: Executive Dashboard (MRR/ARR + churn + tenant sağlığı) ---
    TabTanimi(
        anahtar="executive",
        baslik="Executive Dashboard",
        ikon="📈",
        grup=GRUP_IS,
        aciklama="MRR/ARR, churn oranı ve tenant sağlık dağılımı — yönetici özeti",
        url_path="executive",
        ust="veri_kalite", sira=3,
        modul="web_dashboard.tabs.admin_executive",
        fonksiyon="render_executive_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="destek",
        baslik="Destek Merkezi",
        ikon="🎫",
        grup=GRUP_IS,
        aciklama="Ticket listesi, olusturma ve durum degistirme",
        url_path="destek",
        ust="musteri_yonetimi", sira=2,
        modul="web_dashboard.tabs.admin_destek",
        fonksiyon="render_destek_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="hatalar",
        baslik=t("menu_hatalar"),
        ikon="⚠️",
        grup=GRUP_IS,
        aciklama="Hata yönetimi ve sorun giderme",
        url_path="hatalar",
        ust="proje_yonetimi", sira=3,
        modul="web_dashboard.tabs.admin_errors",
        fonksiyon="render_errors_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="kullanicilar",
        baslik=t("menu_kullanicilar"),
        ikon="👤",
        grup=GRUP_IS,
        aciklama="Kullanıcı yönetimi ve izin denetimi",
        url_path="kullanicilar",
        ust="musteri_yonetimi", sira=1,
        modul="web_dashboard.tabs.admin_extras",
        fonksiyon="render_user_management",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="karar_defteri",
        baslik=t("menu_karar_defteri"),
        ikon="📔",
        grup=GRUP_IS,
        aciklama="Sistem kararları ve denetim kayıtları",
        url_path="karar-defteri",
        ust="proje_yonetimi", sira=0,
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_decision_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="kalite",
        baslik=t("menu_kalite"),
        ikon="✅",
        grup=GRUP_IS,
        aciklama="Veri kalitesi ve uyum skoru",
        url_path="kalite",
        ust="veri_kalite", sira=1,
        modul="web_dashboard.tabs.admin_quality",
        fonksiyon="render_quality_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="arama",
        baslik=t("menu_arama"),
        ikon="🔍",
        grup=GRUP_IS,
        aciklama="Global arama ve filtreleme",
        url_path="arama",
        ust="veri_kalite", sira=2,
        modul="web_dashboard.tabs.admin_search",
        fonksiyon="render_search_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="export",
        baslik=t("menu_export"),
        ikon="💾",
        grup=GRUP_IS,
        aciklama="Veri dışa aktarma ve raporlar",
        url_path="export",
        ust="musteri_yonetimi", sira=3,
        modul="web_dashboard.tabs.admin_export",
        fonksiyon="render_export_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="maliyet",
        baslik=t("menu_maliyet"),
        ikon="💰",
        grup=GRUP_SISTEM,
        aciklama="AI ve sistem maliyeti analizi",
        url_path="maliyet",
        ust="sistem", sira=4,
        modul="web_dashboard.tabs.admin_cost",
        fonksiyon="render_cost_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="teknik_altyapi",
        baslik="Teknik Altyapı",
        ikon="🧭",
        grup=GRUP_SISTEM,
        aciklama="Süreç diyagramı ve servis haritası (KPI-EXA-02)",
        url_path="teknik-altyapi",
        ust="sistem", sira=0,
        modul="web_dashboard.tabs.teknik_altyapi",
        fonksiyon="render_teknik_altyapi_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="performans",
        baslik=t("menu_performans"),
        ikon="⚡",
        grup=GRUP_SISTEM,
        aciklama="Sistem performansı ve gecikme metriği",
        url_path="performans",
        ust="sistem", sira=1,
        modul="web_dashboard.tabs.admin_performance",
        fonksiyon="render_performance_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="api",
        baslik=t("menu_api"),
        ikon="🔌",
        grup=GRUP_SISTEM,
        aciklama="API analitiği ve kullanım",
        url_path="api",
        ust="sistem", sira=2,
        modul="web_dashboard.tabs.admin_api_analytics",
        fonksiyon="render_api_analytics_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="webhook",
        baslik=t("menu_webhook"),
        ikon="🔗",
        grup=GRUP_SISTEM,
        aciklama="Webhook izleme ve durum",
        url_path="webhook",
        ust="sistem", sira=3,
        modul="web_dashboard.tabs.webhook_monitor",
        fonksiyon="render_webhook_monitor_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="dlq",
        baslik=t("menu_dlq"),
        ikon="⛔",
        grup=GRUP_SISTEM,
        aciklama="Kuyruk hataları ve ölü harf sırası",
        url_path="dlq",
        ust="proje_yonetimi", sira=4,
        modul="web_dashboard.tabs.admin_dlq",
        fonksiyon="render_dlq_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="yenileme",
        baslik=t("menu_yenileme"),
        ikon="🔄",
        grup=GRUP_SISTEM,
        aciklama="Otomatik yenileme ayarları",
        url_path="yenileme",
        ust="sistem", sira=6,
        modul="web_dashboard.tabs.admin_auto_refresh",
        fonksiyon="render_auto_refresh",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="sistem",
        baslik=t("menu_sistem_bilesik"),
        ikon="⚙️",
        grup=GRUP_SISTEM,
        aciklama="Performans, maliyet, webhook, DLQ ve denetim izi",
        url_path="sistem",
        modul="web_dashboard.tabs.admin_sistem",
        fonksiyon="render_sistem_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="canli_veri",
        baslik=t("menu_m_canli_veri"),
        ikon="📡",
        grup=GRUP_SISTEM,
        aciklama="Gerçek zamanlı sinyal akışı (SSE)",
        url_path="canli-veri",
        ust="sistem", sira=5,
        modul="web_dashboard.tabs.admin_realtime",
        fonksiyon="render_admin_realtime_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="denetim",
        baslik=t("menu_m_denetim"),
        ikon="📋",
        grup=GRUP_SISTEM,
        aciklama="Dosya kilitleri, handoff geçişleri ve tetikleyici günlüğü (DASH-08)",
        url_path="denetim",
        ust="proje_yonetimi", sira=2,
        modul="web_dashboard.tabs.admin_audit",
        fonksiyon="render_audit_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="ayarlar",
        baslik=t("menu_m_ayarlar"),
        ikon="🎛️",
        grup=GRUP_SISTEM,
        aciklama="Görünüm, veri, bildirim ve bölgesel kullanıcı tercihleri (P7-46)",
        url_path="ayarlar",
        ust="sistem", sira=7,
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_ayarlar_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="yukleme",
        baslik=t("menu_loading"),
        ikon="⏳",
        grup=GRUP_SISTEM,
        aciklama="Loading state örnekleri ve skeleton gosterim (P7-42)",
        url_path="yukleme",
        ust="sistem", sira=8,
        modul="web_dashboard.tabs.admin_loading",
        fonksiyon="render_loading_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="musteri_yonetimi",
        baslik="Müşteri Yönetimi",
        ikon="👥",
        grup=GRUP_IS,
        aciklama="Müşteri yönetim, paket, giriş ve destek ana sayfa",
        url_path="musteri-yonetimi",
        modul="web_dashboard.tabs.musteri_yonetimi",
        fonksiyon="render_musteri_yonetimi_tab",
        hazir=True,
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="proje_yonetimi",
        baslik="Proje Yönetimi",
        ikon="📊",
        grup=GRUP_IS,
        aciklama="Karar defteri, açık işler, denetim izi ve hatalar",
        url_path="proje-yonetimi",
        modul="web_dashboard.tabs.proje_yonetimi",
        fonksiyon="render_proje_yonetimi_tab",
        hazir=True,
        min_rol="admin",
    ),
TabTanimi(
    anahtar="veri_kalite",
    baslik="Veri & Kalite",
    ikon="✅",
    grup=GRUP_IS,
    aciklama="KPI, kalite, arama ve executive özeti",
    url_path="veri-kalite",
    hazir=False,
    bekleyen_gorev="NAV-IA-01",
    min_rol="analyst",
),
    TabTanimi(
        anahtar="musteri_onizleme",
        baslik="Müşteri Önizleme",
        ikon="🦅",
        grup=GRUP_IS,
        aciklama="Paketler ve pazarlama müşteri ekranı (Huginn önizleme)",
        url_path="musteri-onizleme",
        hazir=False,
        bekleyen_gorev="NAV-IA-02",
        min_rol="anon",
        yuzey=YUZEY_MUNINN,
    ),
)


ESKI_URL: dict[str, tuple[str, str]] = {
    "kullanicilar": ("musteri_yonetimi", "kullanicilar"),
    "yonetim": ("admin_yonetim", ""),
    "kimlik": ("admin_auth", ""),
}


def eski_url_yonlendir(yol: str) -> tuple[str, str] | None:
    """Eski url_path -> (ust_sayfa_anahtari, alt_sekme_anahtari) veya None.

    NAV-IA-01: `tab_url_getir` ESki_URL bulamazsa buraya bakar.
    """
    temiz = (yol or "").strip().strip("/").lower()
    return ESKI_URL.get(temiz)


def ust_sayfalar(rol: str | None = None) -> dict[str, TabTanimi]:
    """Sidebar'da gorunen 6 ust sayfa (kimlik/yonetim/sistem cikmistir).

    Sadece `ust is None` OLAN ve `UST_SAYFA_ANAHTARLARI` listesinde
    olan bolumler doner. `GRUP_IS/GRUP_SISTEM` geriye donuk korunur.
    """
    UST_SAYFA_ANAHTARLARI: frozenset[str] = frozenset({
        "ana_kontrol", "musteri_yonetimi", "proje_yonetimi",
        "veri_kalite", "sistem", "musteri_onizleme",
    })
    sonuc: dict[str, TabTanimi] = {}
    for tanim in SECTIONS:
        if tanim.anahtar not in UST_SAYFA_ANAHTARLARI:
            continue
        if tanim.ust is not None:
            continue
        if rol is None or erisebilir(tanim, rol):
            sonuc[tanim.anahtar] = tanim
    return sonuc


def alt_sekmeler(ust: str, rol: str | None = None) -> tuple[TabTanimi, ...]:
    """Bir ust sayfanin alt sekmelerini sira sirasiyla dondurur.

    `ust` bos/hylif -> bos tuple.
    """
    if not ust:
        return ()
    return tuple(
        sorted(
            (tanim for tanim in SECTIONS if tanim.ust == ust and (rol is None or erisebilir(tanim, rol))),
            key=lambda tanim: tanim.sira,
        )
    )


def yenile() -> None:
    """Ortak yenile: cache temizle + rerun (D-1).

    `admin_kpi.py` ve `ana_kontrol.py` paylasma ici kullanilir.
    """
    st.cache_data.clear()
    st.rerun()


def varsayilan_tab() -> TabTanimi:
    """Uygulama ilk açıldığında gösterilecek bölüm."""
    return SECTIONS[0]


def tab_getir(anahtar: str) -> TabTanimi | None:
    """Anahtara göre bölüm tanımını döndürür; yoksa None."""
    for tanim in SECTIONS:
        if tanim.anahtar == anahtar:
            return tanim
    return None


def tab_url_getir(url_path: str) -> TabTanimi | None:
    """URL parçasına göre bölüm tanımını döndürür (derin bağlantı).

    SEC-AUTH-01 O-1: ESKI_URL once bakilir; eski yol SECTIONS'ta kalsa da
    dogru ust/alt sekmeye yonlendirilir (eski sayfa acilmaz).
    """
    temiz = (url_path or "").strip().strip("/").lower()
    if not temiz:
        return None
    # SEC-AUTH-01 O-1: ESKI_URL ONCELIKLI - eski yollar (kimlik/yonetim/kullanicilar)
    # halen SECTIONS'ta durdugu icin once eski haritaya bakilmali; aksi halde
    # SECTIONS eslesmesi fallback'i gecersiz kilar ve yonlendirme olu kod olur.
    eskiler = eski_url_yonlendir(temiz)
    if eskiler is not None:
        ust_anahtar, alt_anahtar = eskiler
        if alt_anahtar:
            tanim = tab_getir(alt_anahtar)
        else:
            tanim = tab_getir(ust_anahtar)
        if tanim is not None:
            try:
                import streamlit as st
                st.session_state["alt_sekme"] = alt_anahtar or ust_anahtar
            except Exception:
                pass
        return tanim
    for tanim in SECTIONS:
        if tanim.url_path == temiz:
            return tanim
    return None


def gorunur_bolumler(rol: str | None = None) -> tuple[TabTanimi, ...]:
    """U-10: Role göre görünür bölümler (tanım sırası korunur).

    `rol=None` → filtre yok (geriye uyumluluk; tüm `SECTIONS`).
    `SECTIONS` hiçbir zaman değiştirilmez; yeni bir demet döner.
    """
    if rol is None:
        return SECTIONS
    return tuple(tanim for tanim in SECTIONS if erisebilir(tanim, rol))


def musteri_onizleme_bolumleri() -> tuple[TabTanimi, ...]:
    """MIG-UI-01: Hedefi Huginn olan (önizleme modundaki) bölümler."""
    return tuple(tanim for tanim in SECTIONS if tanim.musteri_onizleme)


def gruplar(rol: str | None = None) -> dict[str, list[TabTanimi]]:
    """Bölümleri sidebar gruplarına ayırır (tanım sırası korunur).

    `rol` verilirse yalnızca o rolün görebildiği bölümler gruplanır; boş
    kalan grup sözlükte yer almaz (sidebar'da boş başlık çizilmez).
    """
    cikti: dict[str, list[TabTanimi]] = {}
    for tanim in gorunur_bolumler(rol):
        cikti.setdefault(tanim.grup, []).append(tanim)
    return cikti


def render_fonksiyonu(tanim: TabTanimi) -> Callable[[], None] | None:
    """Bölümün render fonksiyonunu tembel (lazy) import ile getirir.

    Modül bulunamazsa veya fonksiyon eksikse `None` döner; çağıran taraf
    kullanıcıya anlaşılır bir uyarı gösterir. Böylece tek bir bozuk sekme
    tüm paneli düşürmez.
    """
    if not tanim.hazir or not tanim.modul or not tanim.fonksiyon:
        return None
    try:
        modul = importlib.import_module(tanim.modul)
    except Exception:
        return None
    fn = getattr(modul, tanim.fonksiyon, None)
    return fn if callable(fn) else None
