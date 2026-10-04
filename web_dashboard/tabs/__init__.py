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
import logging
from dataclasses import dataclass
from typing import Callable

import streamlit as st
from company_master.i18n import t

_LOG = logging.getLogger(__name__)

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
GRUP_GELIR = "💰 Gelir & Paketler"

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
        rehber: Uzun "bu ekran ne yarar / nasıl kullanılır / veri nereden
            gelir / dikkat" metni. Tek kapı `app.render_icerik` içinde
            `st.info` olarak basılır; sekme dosyası okumaz (D-211).
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
    rehber: str = ""

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
        aciklama="Müşteri ve sistem sağlığı, ana göstergeler tek bakışta",
        url_path="ana-kontrol",
        sira=0,  # NAV-AGAC-01: kök sıralaması
        modul="web_dashboard.tabs.ana_kontrol",
        fonksiyon="render_ana_kontrol_tab",
        yuzey=YUZEY_HUGINN,
        rehber=        "**Bu ekran ne işe yarar?** Müşteri tarafı (kayıt, onay, kredi) ve sistem tarafı "
                "(firma sayısı, kalite skoru, görev durumu) metriklerini tek bakışta gösterir.\n\n"
                "**Nasıl kullanılır?** Kartlar veri geldikçe kendiliğinden açılır. Bölüm "
                "başlıklarından ilgili panele atlayın.\n\n"
                "**Veriler nereden gelir?** `/api/kpi` ve `/metrics` uç noktaları ile "
                "webhook izleme kayıtları. 30 saniyede bir yenilenir.\n\n"
                "**Dikkat:** Verisi henüz gelmemiş kutular yer tutucu değerle çizilir ve "
                "hemen altlarında **SAHTE VERİ** uyarısı bulunur. Gerçek veri geldiğinde "
                "kutu otomatik olarak gerçek değere geçer, uyarı kendiliğinden kaybolur."

    ),
    TabTanimi(
        anahtar="musteriler",
        baslik="Firmalar",
        ikon="🏢",
        grup=GRUP_IS,
        aciklama="Firma listesi, filtreler ve kalite bildirimleri",
        url_path="musteriler",
        ust="musteri_yonetimi", sira=0,
        modul="web_dashboard.tabs.admin_musteriler",
        fonksiyon="render_musteriler_tab",
        rehber=        "**Bu ekran ne işe yarar?** Veritabanındaki firma kayıtlarını arar, kalite "
                "skoruna göre süzer ve eksik bilgi taşıyan (telefon, e-posta, web sitesi olmayan) "
                "kayıtları öne çıkarır. Veri temizliği ve müşteri araştırması için başlangıç "
                "noktasıdır.\n\n"
                "**Nasıl kullanılır?** Arama kutusuna firma adı veya NACE kodu yazın; kalite "
                "eşiğini kaydırıcıdan seçin. Sonuç tablosunda sütun başlığına tıklayarak "
                "sıralama yapabilirsiniz.\n\n"
                "**Veriler nereden gelir?** `companies` tablosu "
                "(`admin_search.search_companies` sorgusu).\n\n"
                "**Dikkat:** Liste, seçtiğiniz satır sayısı kadar kayıt gösterir. Tüm sonuçları "
                "indirmek için **Yönetim › Veri Export** ekranını kullanın."

    ),
    TabTanimi(
        anahtar="pazarlama",
        baslik=t("menu_h_pazarlama"),
        ikon="📢",
        grup=GRUP_IS,
        aciklama="Kampanyalar, segmentler ve segment kapsama analizi",
        url_path="pazarlama",
        ust="musteri_onizleme", sira=0,
        modul="web_dashboard.tabs.pazarlama",
        fonksiyon="render_pazarlama_tab",
        yuzey=YUZEY_HUGINN,
        rehber=        "**Bu ekran ne işe yarar?** Pazarlama kampanyalarını ve müşteri segmentlerini "
                "tek ekrandan izler. Hangi segmentin hangi kampanyayla beslendiğini, hangisinin "
                "boşta kaldığını ve hedef pazarın ne kadarını kapsadığımızı gösterir.\n\n"
                "**Nasıl kullanılır?** Üstteki özet kartlar aktif kampanya ve segment sayısını "
                "verir. **Kampanyalar**, **Segmentler** ve **Kapsam** sekmeleri arasında geçiş "
                "yaparak ayrıntılara inebilirsiniz. Segment başlığına tıklayınca kriterleri "
                "ve içindeki firmalar açılır.\n\n"
                "**Veriler nereden gelir?** `company_master.pazarlama` modülü (kampanya ve "
                "segment tabloları). Bağlantı yoksa `data/demo/` altındaki örnek veri gösterilir "
                "ve ekranda **Demo** rozeti belirir.\n\n"
                "**Dikkat:** Demo modda kampanya oluşturma ve düzenleme kapalıdır. "
                "Gösterim/tıklama/dönüşüm metrikleri yalnızca kaynakta kayıtlıysa hesaplanır."

    ),
    TabTanimi(
        anahtar="abrakadabra",
        baslik=t("menu_m_abrakadabra"),
        ikon="🤖",
        grup=GRUP_IS,
        aciklama="Yapay zekâ asistanı: sohbet ve analiz",
        url_path="abrakadabra",
        ust="proje_yonetimi", sira=1,  # D-215: denetim/kvkk_mode çıktı, yeniden sıralandı
        modul="web_dashboard.tabs.abrakadabra",
        fonksiyon="render_abrakadabra_tab",
        min_rol="admin",
    ),
    # --- PO-BACK-08: Executive Dashboard (MRR/ARR + churn + tenant sağlığı) ---
    # NAV-AGAC-01: Metrikler başlığı altında birleşti (eskiden menüden düşüyordu).
    TabTanimi(
        anahtar="executive",
        baslik="Executive Dashboard",
        # NAV-AGAC-01: menüye girince `veri_kalite` (📈) ile aynı ikonu taşıyordu;
        # iki kardeş düğme aynı ikonla ayırt edilemez → 💹 (yönetici/gelir özeti).
        ikon="💹",
        grup=GRUP_GELIR,
        aciklama="Aylık gelir, müşteri kaybı ve sağlık dağılımı",
        url_path="executive",
        ust="veri_kalite", sira=1,
        modul="web_dashboard.tabs.admin_executive",
        fonksiyon="render_executive_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="destek",
        baslik="Destek Merkezi",
        ikon="🎫",
        grup=GRUP_IS,
        aciklama="Destek talepleri: açma ve durum değiştirme",
        url_path="destek",
        ust="musteri_yonetimi", sira=2,
        modul="web_dashboard.tabs.admin_destek",
        fonksiyon="render_destek_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="hatalar",
        baslik="Olaylar & Hatalar",
        ikon="⚠️",
        grup=GRUP_SISTEM,
        aciklama="Hatalar, dış sistemden gelen haberler, takılan işler",
        url_path="hatalar",
        ust="sistem", sira=2,
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
    # NAV-AGAC-01: Proje başlığı altında birleşti.
    TabTanimi(
        anahtar="ajan_sohbet",
        baslik="Ajan Chat",
        ikon="💬",
        grup=GRUP_IS,
        aciklama="Ajan sorunları: açık, önerilen çözüm ve kapananlar",
        url_path="ajan-sohbet",
        ust="proje_yonetimi", sira=2,  # D-215
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_chat_summary",
        min_rol="admin",
        hazir=True,
    ),
    TabTanimi(
        anahtar="gorev_panosu",
        baslik="Görev Panosu",
        ikon="🗂️",
        grup=GRUP_IS,
        aciklama="Ajan görevlerinin dört bölümlü panosu",
        url_path="gorev-panosu",
        ust="proje_yonetimi", sira=3,  # D-215
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_task_board_tab",
        min_rol="admin",
        hazir=True,
    ),
    # NAV-AGAC-01: Proje başlığı altında birleşti.
    TabTanimi(
        anahtar="rapor_listesi",
        baslik="MIMIR Raporları",
        ikon="📑",
        grup=GRUP_IS,
        aciklama="MIMIR mimari raporları: otomatik üretilir, herkese açık",
        url_path="rapor-listesi",
        ust="proje_yonetimi", sira=4,  # D-215
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_rapor_listesi_tab",
    ),
    TabTanimi(
        anahtar="kalite",
        baslik=t("menu_kalite"),
        ikon="✅",
        grup=GRUP_IS,
        aciklama="Veri kalitesi ve uyum skoru",
        url_path="kalite",
        ust="veri_kalite", sira=0,
        modul="web_dashboard.tabs.admin_quality",
        fonksiyon="render_quality_tab",
        min_rol="analyst",
    ),
    # NAV-AGAC-01: Metrikler başlığı altında birleşti (üst şerit araması ayrıca duruyor).
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
        grup=GRUP_GELIR,
        aciklama="Yapay zekâ ve sistem maliyeti analizi",
        url_path="maliyet",
        ust="veri_kalite", sira=4,  # D-215: Metrikler'e taşındı (ölçüm sorumluluğu)
        modul="web_dashboard.tabs.admin_cost",
        fonksiyon="render_cost_tab",
        min_rol="analyst",
    ),
    # UI-ADMIN-KAYNAKLAR-SAYFA-34: 0050 kazıma tablolarının tek okuyucusu (D-236).
    TabTanimi(
        anahtar="kaynaklar",
        baslik="Veri Kaynakları",
        ikon="🕷️",
        grup=GRUP_IS,
        aciklama="Kazıma kaynakları: son çalışma, hata ve toplanan sayfa",
        url_path="kaynaklar",
        ust="veri_kalite", sira=5,
        modul="web_dashboard.tabs.admin_kaynaklar",
        fonksiyon="render_kaynaklar_tab",
        min_rol="admin",
        rehber=        "**Bu ekran ne işe yarar?** OSINT kazıma kaynaklarının sağlığını gösterir: "
                "kaynak başına toplam ve başarılı çekiş, son çalışma zamanı, son hatalar ve "
                "toplanan sayfa adedi. Ayrıca crawl'ı başlatma/durdurma kontrolü buradadır "
                "(eski Webhook Monitor ekranından taşındı).\n\n"
                "**Veriler nereden gelir?** Üç 0050 tablosu: `scrape_audit_log` (çekiş "
                "denemeleri), `scrape_errors` (hata kayıtları), `scrape_pages` (ham sayfa "
                "içeriği). Hepsi salt okunur; bu ekran hiçbir kayıt yazmaz.\n\n"
                "**Dikkat:** Kayıt yoksa ekran “Henüz kazıma yapılmadı” der — bu, sıfır "
                "başarısız çekiş anlamına gelmez."

    ),
    TabTanimi(
        anahtar="teknik_altyapi",
        baslik="Altyapı",
        ikon="🧭",
        grup=GRUP_SISTEM,
        aciklama="Süreç diyagramı, servis haritası ve performans metrikleri",
        url_path="teknik-altyapi",
        ust="sistem", sira=0,
        modul="web_dashboard.tabs.teknik_altyapi",
        fonksiyon="render_teknik_altyapi_tab",
        min_rol="analyst",
    ),
    # NAV-AGAC-01: Sistem başlığı altında birleşti.
    TabTanimi(
        anahtar="performans",
        baslik=t("menu_performans"),
        ikon="⚡",
        grup=GRUP_SISTEM,
        aciklama="Sistem performansı ve gecikme metriği",
        url_path="performans",
        ust="sistem", sira=4,
        modul="web_dashboard.tabs.admin_performance",
        fonksiyon="render_performance_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="api",
        baslik=t("menu_api"),
        ikon="🔌",
        grup=GRUP_SISTEM,
        aciklama="Sunucu isteği analizi ve kullanımı",
        url_path="api",
        ust="sistem", sira=1,
        modul="web_dashboard.tabs.admin_api_analytics",
        fonksiyon="render_api_analytics_tab",
        min_rol="analyst",
    ),
    TabTanimi(
        anahtar="webhook",
        baslik=t("menu_webhook"),
        ikon="🔗",
        grup=GRUP_SISTEM,
        aciklama="Dış sistemden gelen haberlerin durumu",
        url_path="webhook",
        ust="sistem", sira=5,
        modul="web_dashboard.tabs.webhook_monitor",
        fonksiyon="render_webhook_monitor_tab",
        min_rol="analyst",
    ),
    # NAV-AGAC-01: Sistem başlığı altında birleşti (Ana Kontrol kısayolu da duruyor).
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
        aciklama="Performans, maliyet, takılan işler ve denetim izi",
        url_path="sistem",
        sira=6,  # NAV-AGAC-01: kök sıralaması (D-215: mfa Güvenlik Kapısı'na taşındı)
        modul="web_dashboard.tabs.admin_sistem",
        fonksiyon="render_sistem_tab",
        min_rol="analyst",
        rehber="**Bu ekran ne işe yarar?** Sistemin operasyonel durumunu tek yerde toplar: webhook ve işlenemeyen kayıt kuyruğu (DLQ), sorgu gecikmesi ile AI maliyeti, uç nokta kullanımı ve tüketim dağılımı."
        "Üstteki **Yenile** düğmesi önbelleği temizleyip tüm panelleri yeniden yükler. Boş bölümler, ilgili veri kaynağı ilk verisini ürettiğinde otomatik dolar; boş görünen bir bölüm hata değildir."
    ),
    TabTanimi(
        anahtar="canli_veri",
        baslik=t("menu_m_canli_veri"),
        ikon="📡",
        grup=GRUP_SISTEM,
        aciklama="Gerçek zamanlı sinyal akışı",
        url_path="canli-veri",
        ust="sistem", sira=3,
        modul="web_dashboard.tabs.admin_realtime",
        fonksiyon="render_admin_realtime_tab",
        min_rol="analyst",
        rehber=        "**Bu ekran ne işe yarar?** Sistemin şu anki nabzını gösterir: firma "
                "sayısı, sinyal hacmi ve veri kalitesi. \"Şu an ne oluyor?\" sorusu "
                "için bakılacak yerdir.\n\n"
                "**Nasıl kullanılır?** Otomatik yenilemeyi açarsanız seçtiğiniz "
                "aralıkta sayfa tazelenir; kapalıyken 🔄 Veriyi Yenile ile elle "
                "tazelersiniz.\n\n"
                "**Veriler nereden gelir?** Doğrudan veritabanından (`companies`, "
                "`company_signals`). Admin panelinde SSE kullanılmaz — mimari kural "
                "gereği canlı akış yalnız müşteri panelindedir.\n\n"
                "**Dikkat:** Değerler kısa süreli bir önbellekten okunur."

    ),
    # D-215: Proje'den kök seviyesine yükseltildi — "Güvenlik Kapısı" (erişim/uyum kapısı).
    TabTanimi(
        anahtar="denetim",
        baslik="Güvenlik Kapısı",
        ikon="🧾",
        grup=GRUP_SISTEM,
        aciklama="Denetim izi, kişisel veri ve giriş güvenliği ayarları",
        url_path="denetim",
        sira=5,  # NAV-AGAC-01: kök sıralaması (D-215)
        modul="web_dashboard.tabs.admin_audit",
        fonksiyon="render_audit_tab",
        min_rol="admin",
        rehber="**Bu ekran ne işe yarar?** Çalışma izlerinin kaydını toplar: son 30 karar kaydı (Karar Defteri), aktif dosya kilitleri, ajanlar arası handoff kayıtları, görev durum özeti ve son 20 tetik kaydı."
        "Bu ekran yalnız okuma amaçlıdır; hiçbir kaydı değiştirmez. Karar, kilit ve tetik kayıtları yalnız orkestratör tarafından yazılır, bu ekrandan değiştirilemez."
    ),
    # UI-ADMIN-KVKK-MODU-26 + UI-ADMIN-KVKK-RAPOR-28: KVKK Mode + Rapor birlesik (D-214).
    TabTanimi(
        anahtar="kvkk_mode",
        baslik="KVKK Mode",
        ikon="🔒",
        grup=GRUP_SISTEM,
        aciklama="Kişisel veri modu, geçmiş ve eğilim analizi",
        url_path="kvkk-mode",
        ust="denetim", sira=0,  # D-215: Güvenlik Kapısı'na taşındı
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_kvkk_mode_tab",
        min_rol="admin",
    ),
    # UI-KONTROL-PANOSU-32: Admin Kontrol Panosu
    # NAV-AGAC-01: Metrikler başlığı altında birleşti.
    TabTanimi(
        anahtar="kontrol_panosu",
        baslik="Kontrol Panosu",
        ikon="🎚️",
        grup=GRUP_SISTEM,
        aciklama="Maskeli alanlar, paket dağılımı ve eğilimler",
        url_path="kontrol-panosu",
        ust="veri_kalite", sira=3,
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_kontrol_panosu_tab",
        min_rol="admin",
    ),
    # UI-ADMIN-FEATURE-FLAG-25: Feature Flag Yönetim
    # NAV-AGAC-01: Sistem başlığı altında birleşti.
    TabTanimi(
        anahtar="feature_flags",
        baslik="Feature Flags",
        ikon="🚩",
        grup=GRUP_SISTEM,
        aciklama="Sistem özellik anahtarlarını yönetin (yalnız admin)",
        url_path="feature-flags",
        ust="sistem", sira=7,
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_feature_flags_tab",
        min_rol="admin",
    ),
    # UI-ADMIN-LTV-CAC-27: LTV/CAC Analiz Sekmesi
    TabTanimi(
        anahtar="ltv_cac",
        baslik="LTV/CAC",
        ikon="📉",
        grup=GRUP_GELIR,
        aciklama="Müşteri kazandırma maliyeti ve yaşam boyu değeri",
        url_path="ltv-cac",
        ust="musteri_onizleme", sira=1,
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_ltv_cac_tab",
        min_rol="admin",
    ),
    # D-215: Müşteriler'den Gelir Kapısı'na taşındı (para/katalog sorumluluğu).
    TabTanimi(
        anahtar="paket_kredi",
        baslik="Paket & Kredi",
        ikon="📦",
        grup=GRUP_GELIR,
        aciklama="Kredi yükleme, paket kategorileri ve paket yönetimi",
        url_path="paket-kredi",
        ust="musteri_onizleme", sira=2,
        modul="web_dashboard.tabs.musteri_yonetimi",
        fonksiyon="render_paket_kredi_tab",
        min_rol="admin",
    ),
    # UI-ADMIN-MFA-26: MFA Yönetim Sekmesi
    # NAV-AGAC-01: Sistem altında da görünür; hesap kartı popover'ı kısayol olarak kalır.
    TabTanimi(
        anahtar="mfa",
        baslik="MFA Yönetimi",
        ikon="🔐",
        grup=GRUP_SISTEM,
        aciklama="İki adımlı giriş doğrulama ayarları",
        url_path="mfa",
        ust="denetim", sira=1,  # D-215: Güvenlik Kapısı'na taşındı
        modul="web_dashboard.tabs.admin_mfa",
        fonksiyon="render_mfa_tab",
        min_rol="admin",
    ),
    # NAV-AGAC-01: Sistem altında da görünür; hesap kartı popover'ı kısayol olarak kalır.
    TabTanimi(
        anahtar="ayarlar",
        baslik=t("menu_m_ayarlar"),
        ikon="🎛️",
        grup=GRUP_SISTEM,
        aciklama="Görünüm, veri, bildirim ve bölge tercihleri",
        url_path="ayarlar",
        ust="sistem", sira=8,  # D-215: mfa cikinca kaydi
        modul="web_dashboard.tabs.admin_panel",
        fonksiyon="render_ayarlar_tab",
        min_rol="admin",
        rehber=        "**Bu ekran ne işe yarar?** Panel tercihlerinizi (tema, tablo satır sayısı, "
                "bildirimler vb.) kullanıcı bazında kalıcı olarak saklar. Bir kez kaydettiğinizde "
                "farklı tarayıcı veya cihazdan girseniz bile aynı ayarlar geçerli olur.\n\n"
                "**Nasıl kullanılır?** Her sekme bir ayar grubudur. İstediğiniz alanları değiştirip "
                "en alttaki **Kaydet** düğmesine basın. **Varsayılana dön** ile tüm ayarları "
                "başlangıç değerlerine sıfırlayabilirsiniz.\n\n"
                "**Veriler nereden gelir?** Ayar tanımları `company_master.settings` şemasından "
                "otomatik üretilir; yeni bir ayar eklendiğinde bu ekranda kendiliğinden görünür.\n\n"
                "**Dikkat:** Kaydetme işlemi hepsi-ya-hiç çalışır. Bir alan geçersizse "
                "hata gösterilir ve hiçbir değer kaydedilmez; düzeltip yeniden kaydedin."

    ),
    # NAV-AGAC-01: geliştirici demo sayfası — Sistem başlığının en altında.
    TabTanimi(
        anahtar="yukleme",
        baslik=t("menu_loading"),
        ikon="⏳",
        grup=GRUP_SISTEM,
        aciklama="Yükleniyor göstergesi ve iskelet ekran örnekleri",
        url_path="yukleme",
        ust="sistem", sira=9,  # D-215: mfa cikinca kaydi
        modul="web_dashboard.tabs.admin_loading",
        fonksiyon="render_loading_tab",
        min_rol="admin",
    ),
    TabTanimi(
        anahtar="musteri_yonetimi",
        baslik="Müşteriler",
        ikon="👥",
        grup=GRUP_IS,
        aciklama="Müşteri yönetim, paket, giriş ve destek ana sayfa",
        url_path="musteri-yonetimi",
        sira=1,  # NAV-AGAC-01: kök sıralaması
        modul="web_dashboard.tabs.musteri_yonetimi",
        fonksiyon="render_musteri_yonetimi_tab",
        hazir=True,
        min_rol="admin",
        rehber="**Bu ekran ne işe yarar?** Müteri tarafının idari işlerini yönetir: kullanıcı onayları, paket ve kredi işlemleri, giriş etkinliği, arama kayıtları, destek talepleri ve dışa aktarım."
        "En sondaki **Upsell Adayları** sekmesi, kullanım davranışına göre büyüme fırsatı olan firmaları listeler. Arama kayıtları KVKK gereği maskelenmiştir; ham e-posta görmek için maskeleme yetkisi gerekir."
    ),
    TabTanimi(
        anahtar="proje_yonetimi",
        baslik="Proje",
        ikon="📋",
        grup=GRUP_IS,
        aciklama="Karar defteri, açık işler, denetim izi ve hatalar",
        url_path="proje-yonetimi",
        sira=2,  # NAV-AGAC-01: kök sıralaması
        modul="web_dashboard.tabs.proje_yonetimi",
        fonksiyon="render_proje_yonetimi_tab",
        hazir=True,
        min_rol="admin",
        rehber="**Bu ekran ne işe yarar?** Proje çalışma defterini gösterir: karar defteri, 9Router (Abrakadabra) durumu, denetim izi, hata kayıtları ve işlenemeyen kayıt kuyruğu (DLQ)."
        "**Denetim İzi** sekmesi, ayrı **Denetim** sayfasındaki panelin satır içi çağrısıdır ve aynı kayıtları gösterir. Kararlar, dosya kilitleri ve görev durumu yalnız orkestratör tarafından güncellenir."
    ),
    TabTanimi(
        anahtar="veri_kalite",
        baslik="Metrikler",
        ikon="📈",
        grup=GRUP_IS,
        aciklama="Ana göstergeler, kalite, arama ve yönetici özeti",
        url_path="veri-kalite",
        sira=3,  # NAV-AGAC-01: kök sıralaması
        hazir=True,
        modul="web_dashboard.tabs.admin_kpi",
        fonksiyon="render_kpi_tab",
        min_rol="analyst",
        rehber="**Bu ekran ne işe yarar?** Müşteri ve sistem tarafının ölçülebilir özetini verir: toplam firma, MAU (30 gün), DAU (24 saat), toplam sinyal, API çağrısı, sistem durumu ve aktif/tamamlanan/blokaj görev sayıları."
        "Alt bölümler tenant sağlığı, kalite skoru trendi, alan bazlı kalite analizi, veri kaynaklarının durumu ve son 30 günün API kullanım trendini gösterir. Veri kaynağı henüz oluşmadıysa kart **veri kaynağı yok** yazar — bu, ölçülen değerin sıfır olduğu anlamına gelmez."
    ),
    TabTanimi(
        anahtar="musteri_onizleme",
        baslik="Gelir",
        ikon="💼",
        grup=GRUP_IS,
        aciklama="Paketler ve müşteri ekranı önizlemesi (Huginn)",
        url_path="musteri-onizleme",
        sira=4,  # NAV-AGAC-01: kök sıralaması
        hazir=True,
        modul="web_dashboard.tabs.paketler",
        fonksiyon="render_paketler_tab",
        min_rol="anon",
        # D-214: eski "paketler" ikiz-çocuğu YUZEY_HUGINN idi (MIG-UI-01); twin
        # silinirken bu kök yanlışlıkla MUNINN kalmıştı — düzeltildi, kayıp yok.
        yuzey=YUZEY_HUGINN,
        rehber=        "**Bu ekran ne işe yarar?** Sattığımız paketleri, fiyatlarını ve hangi firmaya "
                "hangi paketin atandığını tek ekranda gösterir. Bir firmaya teklif hazırlarken "
                "uygun paketi buradan seçebilirsiniz.\n\n"
                "**Nasıl kullanılır?** Üstteki özet kartlar toplam paket ve atama sayısını verir. "
                "Aşağıdaki tabloda paketleri karşılaştırabilir, firma bazında atama geçmişini "
                "görebilirsiniz.\n\n"
                "**Veriler nereden gelir?** `packages` ve `company_packages` tabloları. "
                "Tablolar henüz yoksa `data/demo/paketler_demo.jsonl` örnek verisi gösterilir "
                "ve ekranda **Demo** rozeti belirir.\n\n"
                "**Dikkat:** Demo modda paket ekleme, düzenleme ve atama kapalıdır; yalnızca "
                "görüntüleme yapılır. Fiyatlar KDV hariç ve aylık olarak listelenir."

    ),
)


ESKI_URL: dict[str, tuple[str, str]] = {
    "kullanicilar": ("musteri_yonetimi", "kullanicilar"),
    "yonetim": ("admin_yonetim", ""),
    "kimlik": ("admin_auth", ""),
    "kpi": ("veri_kalite", ""),
    "paketler": ("musteri_onizleme", ""),
    "kvkk-rapor": ("proje_yonetimi", "kvkk_mode"),
}


def eski_url_yonlendir(yol: str) -> tuple[str, str] | None:
    """Eski url_path -> (ust_sayfa_anahtari, alt_sekme_anahtari) veya None.

    NAV-IA-01: `tab_url_getir` ESki_URL bulamazsa buraya bakar.
    """
    temiz = (yol or "").strip().strip("/").lower()
    return ESKI_URL.get(temiz)


def ust_sayfalar(rol: str | None = None) -> dict[str, TabTanimi]:
    """Sidebar menü ağacının kökleri: `ust is None` olan TÜM bölümler.

    NAV-AGAC-01 (KAHİN, 2026-09-26): "oluşturulmuş bir sayfa navigatör menü
    ağacında gözükmeli, fakat aynı başlık altında bir sayfa birleşebiliyorsa
    birleşebilmeli." Eskiden burada 6 anahtarlık sabit bir frozenset vardı;
    listede olmayan kök bölüm sessizce menüden düşüyordu (yalnız "Hızlı geçiş"
    kutusundan erişilebiliyordu). Artık tek kural: bir sayfa alt sekme olacaksa
    `ust=` verilir, olmayacaksa menü kökünde görünür. Gizlemek için ayrı liste
    yok — `ust=` tek düğmedir (SSOT).
    `sira` alanı kök sayfalarda da sıralamayı belirler.
    """
    kokler = [
        t_ for t_ in SECTIONS
        if t_.ust is None and (rol is None or erisebilir(t_, rol))
    ]
    kokler.sort(key=lambda t_: t_.sira)
    return {t_.anahtar: t_ for t_ in kokler}


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
            except Exception as exc:  # noqa: BLE001
                _LOG.debug("session_state yok: %s", exc)
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
    except Exception as exc:  # noqa: BLE001 - tek bozuk sekme paneli düşürmemeli
        _LOG.warning(
            "Bölüm modülü yüklenemedi (%s → %s): %s", tanim.anahtar, tanim.modul, exc
        )
        return None
    fn = getattr(modul, tanim.fonksiyon, None)
    return fn if callable(fn) else None
