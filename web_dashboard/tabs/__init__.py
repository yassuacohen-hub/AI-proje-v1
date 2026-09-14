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
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Callable

from company_master.i18n import t

__all__ = [
    "TabTanimi",
    "SECTIONS",
    "GRUP_IS",
    "GRUP_SISTEM",
    "tab_getir",
    "tab_url_getir",
    "gruplar",
    "render_fonksiyonu",
    "varsayilan_tab",
]

GRUP_IS = "🏢 İş Operasyonları"
GRUP_SISTEM = "🔧 Sistem & Yönetim"


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
    """

    anahtar: str
    baslik: str
    ikon: str
    grup: str
    aciklama: str
    url_path: str
    modul: str | None = None
    fonksiyon: str | None = None
    hazir: bool = True
    bekleyen_gorev: str = ""

    @property
    def etiket(self) -> str:
        """Sidebar'da gösterilecek "ikon + başlık" metni."""
        return f"{self.ikon} {self.baslik}"


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
    ),
    TabTanimi(
        anahtar="musteriler",
        baslik=t("menu_m_musteriler"),
        ikon="👥",
        grup=GRUP_IS,
        aciklama="Firma listesi, filtreler ve kalite bildirimleri",
        url_path="musteriler",
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
        modul="web_dashboard.tabs.paketler",
        fonksiyon="render_paketler_tab",
    ),
    TabTanimi(
        anahtar="pazarlama",
        baslik=t("menu_h_pazarlama"),
        ikon="📢",
        grup=GRUP_IS,
        aciklama="Kampanyalar, segmentler ve segment kapsama analizi",
        url_path="pazarlama",
        modul="web_dashboard.tabs.pazarlama",
        fonksiyon="render_pazarlama_tab",
    ),
    TabTanimi(
        anahtar="abrakadabra",
        baslik=t("menu_m_abrakadabra"),
        ikon="🤖",
        grup=GRUP_IS,
        aciklama="9Router tabanlı AI sohbet ve analiz asistanı",
        url_path="abrakadabra",
        hazir=False,
        bekleyen_gorev="AI-CHAT-01",
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
    ),
    TabTanimi(
        anahtar="canli_veri",
        baslik=t("menu_m_canli_veri"),
        ikon="📡",
        grup=GRUP_SISTEM,
        aciklama="Gerçek zamanlı sinyal akışı (SSE)",
        url_path="canli-veri",
        modul="web_dashboard.tabs.admin_realtime",
        fonksiyon="render_admin_realtime_tab",
    ),
    TabTanimi(
        anahtar="denetim",
        baslik=t("menu_m_denetim"),
        ikon="📋",
        grup=GRUP_SISTEM,
        aciklama="Dosya kilitleri, handoff geçişleri ve tetikleyici günlüğü (DASH-08)",
        url_path="denetim",
        modul="web_dashboard.tabs.admin_audit",
        fonksiyon="render_audit_tab",
    ),
    TabTanimi(
        anahtar="yonetim",
        baslik=t("menu_yonetim"),
        ikon="👨‍💼",
        grup=GRUP_SISTEM,
        aciklama="Admin girişi, kullanıcı/API yönetimi, kalite ve karar defteri",
        url_path="yonetim",
        modul="web_dashboard.tabs.admin_yonetim",
        fonksiyon="render_yonetim_tab",
    ),
    TabTanimi(
        anahtar="ayarlar",
        baslik=t("menu_m_ayarlar"),
        ikon="🎛️",
        grup=GRUP_SISTEM,
        aciklama="Görünüm, veri, bildirim ve bölgesel kullanıcı tercihleri (P7-46)",
        url_path="ayarlar",
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_ayarlar_tab",
    ),
    TabTanimi(
        anahtar="yukleme",
        baslik=t("menu_loading"),
        ikon="⏳",
        grup=GRUP_SISTEM,
        aciklama="Loading state örnekleri ve skeleton gosterim (P7-42)",
        url_path="yukleme",
        modul="web_dashboard.tabs.admin_loading",
        fonksiyon="render_loading_tab",
    ),
)


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
    """URL parçasına göre bölüm tanımını döndürür (derin bağlantı)."""
    temiz = (url_path or "").strip().strip("/").lower()
    if not temiz:
        return None
    for tanim in SECTIONS:
        if tanim.url_path == temiz:
            return tanim
    return None


def gruplar() -> dict[str, list[TabTanimi]]:
    """Bölümleri sidebar gruplarına ayırır (tanım sırası korunur)."""
    cikti: dict[str, list[TabTanimi]] = {}
    for tanim in SECTIONS:
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
