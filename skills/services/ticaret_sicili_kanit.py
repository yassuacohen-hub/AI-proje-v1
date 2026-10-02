# -*- coding: utf-8 -*-
"""Ticaret Sicili ilan kanıt katmanı (D-270).

Her ilanı **kendi verisiyla birlikte** saklar: ham metin + ayrıştırılmış alanlar
+ kaynak referansı. Böylece veri kaynağından tekrar doğrulanabilir.

Kaynak (D-268: ölçüldü, varsayılmadı):
  `https://www.ticaretsicil.gov.tr/view/hizlierisim/ilangoruntuleme.php`
  → "Ücretsiz gazete sorgulamak için üye girişi yapmalısınız."
  → Giriş **ücretsiz**; ücretli olan yalnızca "onaylı suret" ve abonelik.

Kalıcı referans üçlüsü (ilan metni başlığından):
    (ilan_sira_no, gazete_sayi, gazete_sayfa) + icerik_no

D-269: dış servis yeteneği -> bu dosya `skills/services/` altındadır.
D-216: kanıt uydurulamaz. Alan eksikse `None` yazılır, tahmin edilmez.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from skills.base import registry

#: Kanıt dosyalarının yazıldığı dizin (verinin kendisiyle birlikte saklanır).
KANIT_DIZIN = Path(__file__).resolve().parents[2] / "data" / "kanit"

#: Kaynak sabiti — rapor metinlerinde tek yerden kullanılır.
KAYNAK_URL = (
    "https://www.ticaretsicil.gov.tr/view/hizlierisim/ilangoruntuleme.php"
)

#: Tek bir ilanın kalıcı adresi (D-273).
#: ÖLÇÜLDÜ (2026-09-29): `httpx.get` → **HTTP 200** ama **gövde BOŞ**.
#: Sebep: içerik JavaScript ile yükleniyor + oturum (üye girişi) şart.
#: Sonuç: ham HTTP GET bu kanıtı almaz. Düz HTTP ile tarama YAPILMAZ (D-273).
ILAN_GOSTER_URL = (
    "https://www.ticaretsicil.gov.tr/view/hizlierisim/goster.php?Guid={guid}"
)

#: D-273 — Maliyet / erişim kararları (KAHİN, 2026-09-29).
#:
#: Katman 0 (BEDAVA, kanonik):
#:     - Ücretsiz üyelik: unvan, MERSİS, sicil no, adres, ilan türü,
#:       yayın sayı/sayfa, içerik no  -> YETERLİ, kanıt üretilebilir.
#: Katman 1 (ÜCRETLİ, ÖNERİLMEZ):
#:     - `goster.php?Guid=` ile **ücretli üyelikte** daha fazla alan açılıyor.
#:     - KAHİN ölçümü: "çok pahalı" -> MALİYET/FİYAT ÖLÇÜLMEDİ.
#:     - Kanıt/izlenebilirlik açısından Katman 0 zaten yeterli: her ilanın
#:       (sayı, sayfa, içerik no) referansı var.
#:
#: D-268: fiyat UYDURULMAZ. Satın alma kararı KAHİN'ye aittir.
KATMANLAR = {
    0: {
        "ad": "ucretsiz-uyelik",
        "maliyet": "0",
        "durum": "KANONIK",
        "alanlar": [
            "mersis_no", "ticaret_sicil_no", "ticaret_unvani", "adres",
            "mudurluk", "yayin_tarihi", "gazete_sayi", "gazete_sayfa",
            "ilan_sira_no", "icerik_no", "tescil_tarihi",
            "tescil_edilen_husus", "delil_belgeler", "il_turu",
        ],
    },
    1: {
        "ad": "ucretli-uyelik",
        "maliyet": "OLCULMEDI/COK_PAHALI",
        "durum": "ONERILMEZ",
        "giris": ILAN_GOSTER_URL,
        "gerekce": "Katman 0 kanit uretmeye yeterli; ek alan satin alma "
                   "iceren hukuki riski artirir, degerini olcmedik.",
    },
}



#: TSG ilan türü -> `(event_type, direction)` eşlemesi (TSG-04 olay hattı).
#:
#: ### SÖZLÜK NEDEN EKSİK TUTULUYOR
#:
#: Anahtarlar **kasıtlı olarak** yalnız ölçülmüş ilan türlerini içerir:
#: `data/kanit/*.json` içindeki 326 dosyanın 17 ayrı `il_turu` değeri
#: (19 kayıtta dolu). Sözlükte **olmayan** bir ilan türü `unknown` döner ve
#: `tsg_rapor.olumsuz_ilanlar()` kapısını tetikler: rapor "olumsuz ilan yok"
#: diyemez. Bu D-216/D-307'nin istediği davranıştır — eksik sözlük bir hata
#: değil, **kapının çalıştığının kanıtıdır**.
#:
#: ### ANAHTAR BİÇİMİ
#:
#: Anahtarlar ASCII'ye indirgenmiş büyük harf **tam** değerlerdir; eşleme
#: alt dizi (substring) değil, tam eşleşmedir. Tam eşleşme şart: `Tasfiye`
#: gibi bir anahtar kelimeyi eşleştirmek, `TASFİYE İLANI` yazan başka bir
#: ilanı da yanlışlıkla sınıflandırırdı.
#:
#: `olay_esle()` iki adımda arar: (1) verilen metin **olduğu gibi**,
#: (2) ASCII'ye indirgenmiş hâli. Bu sayede hem ham (`tsg_rapor`) hem
#: normalize büyük harf (`tsg_yazici`) çağrı yolu tek anahtar kümesiyle
#: çalışır — ikinci bir sözlük ikizi üretilmez (D-211).
#:
#: ### ÇAKIŞMA ÇÖZÜMÜ ÖLÇÜLEBİLİR
#:
#: Bir ilanda birden fazla olay geçebiliyor; ölçülen örnek:
#: `"... Değişiklik - Pay Devri Değişiklik - Sermaye Artırımı"`.
#: Burada yönü belirgin olan olay **sermaye artırımı**dır (`positive`),
#: pay devri yön taşımaz (`stable`). Sıralama bu yüzden ölçülen örneğe
#: göre yapıldı; yeni bir çakışma çıkarsa `direction` değil `event_type`
#: kaydedilir (bir olay tek satırdır — tavan ponytail kuralı).
ILAN_TURU_ESLEME: dict[str, tuple[str, str]] = {
    # --- Büyüme: yönü belirgin ---
    "LIMITED SIRKET (SERMAYE ARTIRIMI) ORTAK SAYISI BIRDEN FAZLA LIMITED SIRKET DEGISIKLIK - SERMAYE ARTIRIMI": ("sermaye_artisimi", "positive"),
    "LIMITED SIRKET (SERMAYE ARTIRIMI) TEK ORTAKLI LIMITED SIRKET DEGISIKLIK - SERMAYE ARTIRIMI": ("sermaye_artisimi", "positive"),
    "ANONIM SIRKET (SERMAYE ARTIRIMI) PAY SAHIBI SAYISI BIRDEN FAZLA ANONIM SIRKET DEGISIKLIK - SERMAYE ARTIRIMI": ("sermaye_artisimi", "positive"),
    "LIMITED SIRKET (SERMAYE ARTIRIMI) ORTAK SAYISI BIRDEN FAZLA LIMITED SIRKET DEGISIKLIK - PAY DEVRI DEGISIKLIK - SERMAYE ARTIRIMI": ("sermaye_artisimi", "positive"),
    "LIMITED SIRKET (SERMAYE ARTIRIMI)": ("sermaye_artisimi", "positive"),
    "SUBE ACILIS": ("sube_acilisi", "positive"),
    # --- Sıkıntı: yönü belirgin ---
    "KONKORDATO ALACAKLI TOP. - DURUSMA GUNU VE DIGER": ("konkordato", "negative"),
    # --- Sınıflandırılmış ama yönü olmayan ---
    "LIMITED SIRKET (YONETIM (MUDUR) - TEMSIL VE DIGER) ORTAK SAYISI BIRDEN FAZLA LIMITED SIRKET DEGISIKLIK - YONETIM KURULU / YETKILILER": ("yonetim_kurulu_degisikligi", "stable"),
    "ANONIM SIRKET (YONETIM - TEMSIL VE DIGER) TEK PAY SAHIPLI ANONIM SIRKET DEGISIKLIK - YONETIM KURULU / YETKILILER": ("yonetim_kurulu_degisikligi", "stable"),
    "ANONIM SIRKET (YONETIM - TEMSIL VE DIGER) PAY SAHIBI SAYISI BIRDEN FAZLA ANONIM SIRKET DEGISIKLIK - YONETIM KURULU / YETKILILER": ("yonetim_kurulu_degisikligi", "stable"),
    "TEMSIL IC YONERGESI (TTK - M.371 - F.7) TEK PAY SAHIPLI ANONIM SIRKET DEGISIKLIK - YONETIM KURULU / YETKILILER DEGISIKLIK - YONETIM IC YONERGESI": ("yonetim_kurulu_degisikligi", "stable"),
    "TEK ORTAKLIK BILGISI PAY SAHIBI SAYISI BIRDEN FAZLA ANONIM SIRKET DEGISIKLIK - YONETIM KURULU / YETKILILER DEGISIKLIK - TEK PAY SAHIPLIGINDE DEGISIKLIK": ("tek_pay_sahipligi", "stable"),
    "TEK ORTAKLIK BILGISI TEK PAY SAHIPLI ANONIM SIRKET DEGISIKLIK - YONETIM KURULU / YETKILILER DEGISIKLIK - TEK PAY SAHIPLIGINDE DEGISIKLIK": ("tek_pay_sahipligi", "stable"),
    "LIMITED SIRKET (PAY DEVRI) ORTAK SAYISI BIRDEN FAZLA LIMITED SIRKET DEGISIKLIK - PAY DEVRI": ("pay_devri", "stable"),
    "LIMITED SIRKET (PAY DEVRI) TEK ORTAKLI LIMITED SIRKET DEGISIKLIK - PAY DEVRI DEGISIKLIK - YONETIM KURULU / YETKILILER": ("pay_devri", "stable"),
    "LIMITED SIRKET (ADRES DEGISIKLIGI) TEK ORTAKLI LIMITED SIRKET DEGISIKLIK - ADRES": ("adres_degisikligi", "stable"),
    "LIMITED'DEN ANONIM'E (TUR DEGISIKLIGI) TEK PAY SAHIPLI ANONIM SIRKET NEVI DEGISIKLIGI - TUR DEGISIKLIGI NEVI DEGISIKLIGI - SOZLESME": ("tur_degisikligi", "stable"),
}


def vkn_kontrol(vkn: str) -> dict:
    """VKN doğrulaması — **TEK KAYNAK DELEGASYONU** (K-1, D-275).

    D-268 DÜZELTMESİ: Bu fonksiyon önce **kendi algoritmasını** yazıyordu ve
    gerçek VKN'leri reddediyordu. Doğrusu projede zaten var:
    `src/company_master/etl/kimlik_no.py::vkn_gecerli` (GİB algoritması,
    `docs/VERI_KALITE_SOZLESMESI.md` §3.1 ile bağlayıcı).

    Kural **K-1**: "Doğrulama tek kapıdan geçer." İkinci bir uygulama
    ikiz mantık üretir — biri güncellenir, diğeri çürür (526 ASO satırı).
    """
    try:
        from src.company_master.etl.kimlik_no import vkn_gecerli
    except ImportError:
        return {"gecerli": None, "sebep": "kimlik_no tek kaynagi yuklenemedi"}
    if not vkn or len(vkn) != 10 or not vkn.isdigit():
        return {"gecerli": None, "sebep": "10 haneli rakam olmali"}
    return {"gecerli": bool(vkn_gecerli(vkn)), "kaynak": "kimlik_no.vkn_gecerli"}


#: D-275 — MERSİS → VKN: **DOĞRULANDI** (D-274'ün düzeltilmiş hâli).
#:
#: ÖNCEKİ TUR HATASI (D-268 dersi): `vkn_kontrol()` fonksiyonu KENDİ
#: algoritmasını (tek×3 + çift×1) yazdı ve gerçek VKN'yi **reddetti**.
#: Doğrusu **projede zaten var**: `src/company_master/etl/kimlik_no.py`
#:   `vkn_gecerli()` — GİB algoritması, `docs/VERI_KALITE_SOZLESMESI.md` §3.1
#:   ve D-275 ile bağlayıcı. Kaynak metinlerde "tek×3+çift×1" yazmaz.
#:
#: ÖLÇÜM: KAHİN'in gerçek MERSİS'i `00120320741000024` (17 hane).
#:   → başındaki `0` **fazladaydı** (ilan metni okuma kayması) → 16 hane
#:   → `0120320741000024` → ilk 10 hane `0120320741`
#:   → `kimlik_no.vkn_gecerli("0120320741")` = **True**  ✅
#:
#: KARAR: MERSİS'in ilk 10 hanesi **gerçekten VKN'dir**. VKN ikinci kaynak
#:        sorgusu olmadan türetilir (SÖZLEŞME §3.4b). Kaynak: `mersis_dogrula()`.
#:        Ancak YALNIZCA 16 haneli biçimde — 17 haneli değer `NULL` döner.
#:
#: KALICI KAPI (K-1): kazıyıcı bu kapıyı KENDİSİ YAZMAZ. `mersis_dogrula()`
#:        çağrılır. Böylece 526 satırlık ASO kirliliği tekrarlanmaz.
MERSIS_VKN_IDDIASI = {
    "durum": "DOGRULANDI (olculdu, proje algoritmasi ile)",
    "kanit": "00120320741000024 -> 16 hane -> ilk10=0120320741 -> vkn_gecerli=True",
    "kaynak_kapi": "src/company_master/etl/kimlik_no.py::mersis_dogrula",
    "sart": "YALNIZCA 16 haneli + ilk 10 hane VKN saglamasini gecmeli",
    "sahis_isletmesi": "TURETILMEZ (TCKN 11 hane; tuzel_tip='sahis' ise yazilir)",
    "vkn_nereden": ["MERSIS ilk 10 hane (birincil)", "vergi levhasi", "GIB e-beyanname"],
    "onceki_hata": "vkn_kontrol() kendi algoritmasini yazdi; tek kaynak "
                  "kimlik_no.vkn_gecerli() kullanilmaliydi (D-268)",
}


#: Türkçe harflerin ASCII karşılığı — **sıralama önemli**.
#:
#: Boşluğun (`str.maketrans`) sebebi: ASCII'ye indirgeme yapmadan önce
#: Türkçe harfleri karşılıklarına çeviriyoruz. Aksi halde Unicode katmanı
#: bunları **sessizce düşürüyor** ve iki farklı kelime aynı anahtara düşüyor.
#:
#: ÖLÇÜLEN KANIT (VERI-TSG-ESLEME-CASE-01, D-224 — beyan değil):
#:   eski katlama:  "Artırımı"     -> "ARTRM"     (4 harf yutuldu)
#:                 "Şube Açılış"   -> "SUBE ACLS"  (2 harf yutuldu)
#:   yeni katlama:  "Artırımı"     -> "ARTIRIMI"
#:                 "Şube Açılış"   -> "SUBE ACILIS"
#:
#: Bunun sonucu şuydu: `ILAN_TURU_ESLEME` sözlüğündeki anahtarlar **elle**
#: ASCII yazıldığı için (`SERMAYE ARTIRIMI`, `SUBE ACILIS`), katlama
#: yolu onları **hiç üretemiyordu**. 20 dolu `il_turu` kaydından 13'ü
#: eşleşiyor, 4'ü sermaye artırımıydı ve **hepsi** `unknown` dönüyordu.
#:
#: **Sözlük ile katlama aynı normalize'yi paylaşmalıdır** (D-211, D-239):
#: ikisi ayrı elle yazılırsa biri diğerini çürütür — burada da öyle oldu.
_TR_ASCII = str.maketrans(
    {
        "ı": "I",
        "İ": "I",
        "i": "I",
        "ş": "S",
        "Ş": "S",
        "ğ": "G",
        "Ğ": "G",
        "ü": "U",
        "Ü": "U",
        "ö": "O",
        "Ö": "O",
        "ç": "C",
        "Ç": "C",
        "â": "A",
        "î": "I",
        "û": "U",
    }
)


def _asciiye(metin: str) -> str:
    """Turkce metni ASCII'ye indirger ve buyuk harfe cevirir.

    D-271: kaynak metin Turkce karakter icerebilir. `ŞUBESİ` ile `SUBESI`
    esit olmali, aksi halde sirket tipi tespiti sessizce `diger` doner.

    D-317/VERI-TSG-ESLEME-CASE-01: once Turkce harfler **adli karsiliklarina**
    cevrilir; NFKD + `encode("ascii", "ignore")` sadece aksan artiklarini
    temizler. Eski halde `ı`/`ş` Unicode katmaninda **yok sayiliyordu** ve
    "Artırımı" -> "ARTRM" oluyordu; sozlukteki `SERMAYE ARTIRIMI` anahtari
    bu yolla hic uretilemedigi icin 4 gercek kayit `unknown` donuyordu.

    Donusum **cift yonlu olmak zorunda**: `ILAN_TURU_ESLEME` anahtarlari da
    bu fonksiyondan gecirilir, boylece iki taraf ayni kurali paylasir.
    """
    if not metin:
        return ""
    katlanmis = metin.translate(_TR_ASCII)
    return (
        unicodedata.normalize("NFKD", katlanmis)
        .encode("ascii", "ignore")
        .decode("ascii")
        .upper()
    )


def _sozluk_normalize() -> dict[str, tuple[str, str]]:
    """`ILAN_TURU_ESLEME`'yi **aynı** katlamadan geçirir.

    Kural gövdesi tek yerde yaşar (D-239): `olay_esle()` bir katlama
    uygularsa, sözlük de aynısını uygulamak zorundadır. Sözlük elle
    normalize edilmiş bir ikinci gerçek olurdu (D-211).

    **Neden her çağrıda hesaplanıyor, `lru_cache` ile değil:** Testler
    `monkeypatch.setitem(ILAN_TURU_ESLEME, ...)` ile sözlüğe geçici anahtar
    ekliyor. Bir kez hesaplanmış sabit (`_ESLEME_KATLANMIS`) bu yazmayı
    görmez ve test **sessizce** yanlış sonuç üretir — 17 anahtarlık sözlükte
    katlama ihmal edilebilir maliyet, ikinci gerçek pahalıdır (D-211).
    """
    return {
        _asciiye(k): v
        for k, v in ILAN_TURU_ESLEME.items()
        if _asciiye(k)
    }


def olay_esle(ilan_turu: str | None) -> tuple[Optional[str], str]:
    """TSG ilan türü -> `company_events` satırı: `(event_type, direction)`.

    **Boş/None -> `(None, "unknown")`.** Bilinmeyen tür de aynı değeri döner;
    bu ayrım bilinçlidir, aşağıdaki `direction` sözlüğüne bakın.

    ### `unknown` ile `stable` FARKLI ŞEYDİR (D-268: tek kolon iki anlam)

    `direction` CHECK kısıtı (`company_events`, migration 0003) beş değere
    izin verir: `positive | negative | mixed | stable | unknown`.

    - `unknown` = **eşleşme yok** — ilan türü sözlükte bulunamadı ya da
      `il_turu` alanı boş. Bu, `tsg_rapor.olumsuz_ilanlar()` kapısının
      tetikleyicisidir: o satır "negatif değil" sayılmaz, `etiketsiz`
      listesine düşer ve rapor "olumsuz ilan yok" diyemez.
    - `stable` = **eşleşme var, yönsel sinyal yok** — ilan sınıflandı,
      ancak şirketin lehine/aleyhine işaret taşımıyor.

    İkisini aynı değere indirgemek kapıyı **anlamsız** kılardı: kapı,
    "sınıflandırılmamış ilan var mı?" sorusunu soruyor. Sınıflandırılmış
    ama yönü olmayan ilan o soruya "hayır" demektir. Birleştirilirse kapı
    ya hiç tetiklenmez ya da her zaman tetiklenir.

    ### Neden `stable` dürüst, `positive` spekülatif değil

    Yön ataması **işareti olan** olaylara yapılır (sermaye artırımı =
    büyüme, şube açılışı = genişleme, konkordato/iflas/tahsisat = sıkıntı).
    Pay devri, yönetim değişikliği, adres değişikliği gibi olaylarda
    yönsel sinyal **yoktur**; `stable` yazmak tahmin değil, ölçülen
    boşluğu göstermektir (D-249: "veri yok" ile "0" aynı şey değildir).

    **Eşleme ölçülmüş veriden gelir, tahminle değil** (D-224): anahtarlar
    `data/kanit/*.json` içindeki gerçek `il_turu` değerlerinden alındı
    (326 dosya, 19 kayıtta `il_turu` dolu). Anahtarlar ASCII'ye indirgenmiş
    yazılır çünkü eşleme `_asciiye()` çıktısı üzerinden yapılır.

    Python `str.upper()` Türkçe `i` harfini `I` yapar, `İ` yapmaz; bu yüzden
    `"Değişiklik"` normalize edilince `DEĞIŞIKLIK` olur. `_asciiye()` bunu
    `DEGISIKLIK`a indirger — eşleme iki biçimi de yakalar.
    """
    if not ilan_turu:
        return None, "unknown"

    # Sözlük **her çağrıda** aynı katlamadan geçer (bakınız `_sozluk_normalize`
    # docstring'i) — sözlük ve arama aynı normalizasyonu paylaşır.
    sozluk = _sozluk_normalize()

    # 1) Verilen metin **oldugu gibi** — testlerin monkeypatchledigi anahtarlar
    #    ve ham kaynak metni bu yoldan yakalanir.
    dogrudan = sozluk.get(ilan_turu)
    if dogrudan is not None:
        return dogrudan

    # 2) ASCII'ye indirgenmis hali — `tsg_yazici` buyuk harf, Turkce `i`
    #    `I` olur ve `str.upper()` `İ` uretmez; `Değişiklik` -> `DEGISIKLIK`.
    #    Turkce `ı`/`ş` de ayni kapidan gecer (D-317/ESLEME-CASE-01):
    #    `Artırımı` -> `ARTIRIMI`, aksi halde `ARTRM` olurdu.
    arama = _asciiye(ilan_turu)
    if not arama:
        return None, "unknown"
    katlanmis = sozluk.get(arama)
    if katlanmis is not None:
        return katlanmis

    # 3) Eslesme yok. Sözlük **kasitli olarak** eksik: yeni bir ilan turu
    #    `unknown` doner ve `tsg_rapor.olumsuz_ilanlar()` kapisi tetiklenir.
    #    Sözlüğe yeni anahtar eklemek icin `test_olay_esle_tum_kanitlar_eslesin`
    #    kirmiziya doner — yani bakim borcu teste baglanmistir.
    return None, "unknown"


@dataclass
class IlanKaniti:
    """Tek bir ticaret sicili ilanının kanıt kaydı.

    Alanlar ilan metnindeki **gerçek** etiketlerden gelir. Kaynak metinde
    bulunmayan alan `None` kalır; asla tahmin edilmez.
    """

    # --- Kimlik (birlikte tekildir) ---
    ilan_sira_no: str
    icerik_no: str

    # --- Sirket ---
    mersis_no: Optional[str] = None
    ticaret_sicil_no: Optional[str] = None
    ticaret_unvani: Optional[str] = None
    adres: Optional[str] = None

    # --- Gazete referansi ---
    mudurluk: Optional[str] = None
    yayin_tarihi: Optional[str] = None
    gazete_sayi: Optional[str] = None
    gazete_sayfa: Optional[str] = None

    # --- Tescil ---
    tescil_tarihi: Optional[str] = None
    tescil_edilen_husus: Optional[str] = None
    delil_belgeler: Optional[str] = None
    # Sorgu ekranindaki "Ilan Türü" sutunu (D-272 sinyal kaynagi).
    il_turu: Optional[str] = None

    # --- Kaynak zinciri (D-272) ---
    # Ayni unvanin kac noktasi (fabrika/sube/bayi) oldugunu bulmak icin
    # "iliskili kayitlar" tutulur. Anahtar: sicil_no (her nokta ayri kayit).
    grup_anahtari: Optional[str] = None
    iliskili_kayitlar: list = field(default_factory=list)

    # --- D-273: erisim katmani ---
    # `guid` yalnizca UCRETLI uyelikte acilan kalici ilan adresidir.
    # Ucretsiz katmanda (0) bos kalir.
    guid: Optional[str] = None
    katman: int = 0

    # --- Denetim ---
    kaynak: str = KAYNAK_URL
    alinma_zamani: str = ""
    ham_metin: str = ""
    dogrulama: dict = field(default_factory=dict)

    def kanit_anahtari(self) -> str:
        """Üçlü kalıcı referans: `ilan_sira_no-sayi-sayfa`.

        D-271: eksik alanlar `E` (empty) ile gösterilir. `?` Windows'ta
        dosya adinda GECERSIZDIR ve OSError firlatir; asla kullanilmaz.
        """
        def temiz(deger: Optional[str]) -> str:
            # Yalnizca harf/rakam; geri kalan her sey ayiklanir.
            return "".join(
                c for c in (deger or "") if c.isalnum()
            ).upper() or "E"

        return (
            f"{temiz(self.ilan_sira_no)}-{temiz(self.gazete_sayi)}"
            f"-{temiz(self.gazete_sayfa)}"
        )

    # ------------------------------------------------------------------
    # Dogrulama katmani
    # ------------------------------------------------------------------

    def dogrula(self) -> dict:
        """Alanlar arasi tutarliligi denetler.

        Kural: MERSİS numarasindan turetilen vergi no, sicil no ve unvan
        birlikte **anlamli** olmali. Tek basina dolu alan kanit degildir.

        Donus: {"sonuc": "gecerli"|"supheli", "bulgular": [...], "turetilen": {...}}
        """
        bulgular: list[dict] = []

        def ekle(kod: str, seviye: str, mesaj: str) -> None:
            bulgular.append(
                {"kod": kod, "seviye": seviye, "mesaj": mesaj}
            )

        # 1) MERSİS bicimi — SÖZLEŞME §3.4b ve TEK KAPI (K-1, D-275).
        #    Kanonik bicim **16 hane**: ilk 10 = VKN, kalan 6 = sistem kodu.
        m = (self.mersis_no or "").strip()
        if not m:
            ekle("MERSIS_YOK", "hata", "MERSİS numarası boş")
        elif len(m) == 17 and m.startswith("0") and vkn_kontrol(
            m[1:11]
        ).get("gecerli"):
            # KAHİN'in gercek kaydinda OLCULEN okuma kaymasi (D-275):
            # ilan metninde 17 hane yaziyordu, kanonik bicim 16.
            ekle(
                "MERSIS_17_HANE",
                "uyari",
                "17 hane goruldu; kanonik bicim 16. Bastaki 0 fazla — "
                "ilk 10 hane VKN saglamasiyla DOGRULANDI",
            )
            ekle(
                "MERSIS_VKN_DOGRULANDI",
                "bilgi",
                f"Bastaki 0 atilinca gecerli VKN: {m[1:11]}",
            )
        elif not re.fullmatch(r"\d{16}", m):
            ekle(
                "MERSIS_BICIM",
                "hata",
                f"MERSİS 16 haneli olmali (SÖZLEŞE §3.4b), gelen {len(m)}: {m}",
            )
        elif vkn_kontrol(m[:10]).get("gecerli") is True:
            ekle(
                "MERSIS_ACILIM",
                "bilgi",
                f"MERSİS cozuldu → VKN={m[:10]} (SÖZLEŞE §3.4b), ek={m[10:]}",
            )
            ekle(
                "MERSIS_VKN_DOGRULANDI",
                "bilgi",
                "Ilk 10 hane GİB VKN saglamasindan GECTI → vkn turetilebilir "
                "(yalnizca tuzel_tip='tuzel' ise yazilir)",
            )
        else:
            ekle(
                "MERSIS_VKN_GECERSIZ",
                "hata",
                "16 haneli ama ilk 10 hane VKN saglamasindan GECMEDI → "
                "MERSİS yanlıs okunmus; mersis_no ve vkn NULL yazilir (K-2)",
            )

        # 2) Sirket tipi.
        #    D-271: Turkce buyuk harfler (`Ş`->`S`, `İ`->`I`) Unicode
        #    normalize ile indirgenir; boylece "ŞUBESİ" -> "SUBESI" olur.
        unvan = _asciiye(self.ticaret_unvani or "")
        if "SUBESI" in unvan:
            ekle(
                "SUBE_KAYIT",
                "bilgi",
                "Kayıt bir ŞUBE; ana şirket sicil no ile eşleşmeyebilir",
            )

        # 3) Zorunlu alanlar
        for alan in ("ticaret_sicil_no", "ticaret_unvani", "yayin_tarihi"):
            if not getattr(self, alan):
                ekle(
                    f"ZORUNLU_{alan.upper()}",
                    "hata",
                    f"Zorunlu alan boş: {alan}",
                )

        # 4) Tarih sirasi: gazete yayini, tescil tarihinden once olamaz.
        #    (D-268: format bilinmiyorsa ATLANIR, uydurulmaz.)
        t = self._tarih(self.yayin_tarihi)
        c = self._tarih(self.tescil_tarihi)
        if t and c and t < c:
            ekle(
                "TARIH_SIRASI",
                "hata",
                f"Yayın ({t.date()}) tescilden ({c.date()}) önce olamaz",
            )

        hatali = [b for b in bulgular if b["seviye"] == "hata"]
        return {
            "sonuc": "supheli" if hatali else "gecerli",
            "bulgular": bulgular,
            "turetilen": {
                "anahtar": self.kanit_anahtari(),
                "sirket_tipi": (
                    "sube"
                    if "SUBESI" in unvan
                    else ("as" if "ANONIM SIRKET" in unvan else "diger")
                ),
                "alan_doluluk": self._doluluk(),
            },
        }

    @staticmethod
    def _tarih(deger: Optional[str]) -> Optional[datetime]:
        """`GG.AA.YYYY` veya `YYYY-AA-GG` -> datetime. Bilinmiyorsa None."""
        if not deger:
            return None
        for bicim in ("%d.%m.%Y", "%Y-%m-%d", "%d.%m.%y"):
            try:
                return datetime.strptime(deger.strip(), bicim)
            except ValueError:
                continue
        return None

    def _doluluk(self) -> dict:
        """Hangi alanlar dolu — boş alanlar kanıtı eksik yapar."""
        dolu, bos = [], []
        for ad in asdict(self):
            if ad in ("kaynak", "alinma_zamani", "ham_metin", "dogrulama"):
                continue
            (dolu if getattr(self, ad) else bos).append(ad)
        return {"dolu": len(dolu), "bos": bos}

    # ------------------------------------------------------------------
    # D-272: Grup / nokta analizi (fabrika, sube, bayi)
    # ------------------------------------------------------------------

    def grup_olustur(self, unvan: str, kayitlar: list) -> dict:
        """Aynı gruba ait noktaları (ana şirket + şubeler) toplar.

        `kayitlar`: her biri `{"sicil_no","unvan","adres","il_turu"}` olabilir.
        KAHİN'in ekran görüntülerindeki tablo bu biçimdedir.

        Döner: ana kayıt + nokta sayısı + sektör/il türü dağılımı.
        """
        self.grup_anahtari = unvan
        self.iliskili_kayitlar = list(kayitlar)

        ana = next(
            (k for k in kayitlar if "SUBESI" not in _asciiye(k.get("unvan", ""))),
            kayitlar[0] if kayitlar else {},
        )
        turler: dict[str, int] = {}
        for k in kayitlar:
            t = (k.get("il_turu") or "Bilinmiyor").strip()
            turler[t] = turler.get(t, 0) + 1

        return {
            "grup_anahtari": unvan,
            "ana_sicil_no": ana.get("sicil_no"),
            "nokta_sayisi": len(kayitlar),
            "il_turu_dagilimi": turler,
            "sicil_nolar": [k.get("sicil_no") for k in kayitlar],
        }

    def genislik_analizi(self) -> dict:
        """Grubun genişleme sinyalini hesaplar (iş fırsatı göstergesi).

        Yeni şube/fabrika açılışı = büyüme sinyali. Adres değişikliği =
        taşınma (yeni bölge = yeni pazar).
        """
        turler = self.grup_anahtari and []
        dagilim: dict[str, int] = {}
        for k in self.iliskili_kayitlar:
            t = (k.get("il_turu") or "Bilinmiyor").strip()
            dagilim[t] = dagilim.get(t, 0) + 1
            turler.append(t)

        yeni_acilan = sum(
            v for k, v in dagilim.items()
            if "ACILIS" in _asciiye(k) or "KURULUS" in _asciiye(k)
        )
        tasinan = sum(
            v for k, v in dagilim.items() if "ADRES" in _asciiye(k)
        )
        return {
            "nokta_sayisi": len(self.iliskili_kayitlar),
            "yeni_acilan": yeni_acilan,
            "adres_degisikligi": tasinan,
            "dagilim": dagilim,
            "sinyal": (
                "buyume" if yeni_acilan else
                ("tasinma" if tasinan else "durgun")
            ),
        }

    # ------------------------------------------------------------------
    # D-273: katman / erişim
    # ------------------------------------------------------------------

    def kanit_kapsami(self) -> dict:
        """Bu kanıt hangi katmandan geldi ve neyi kanıtlıyor?

        D-273: ücretli katman (`guid`) kanıtı güçlendirmez, yalnızca
        ayrıntılandırır. Satın alma önerilmez.
        """
        bilinen = KATMANLAR.get(self.katman)
        alanlar = [a for a in KATMANLAR[0]["alanlar"] if getattr(self, a, None)]
        return {
            "katman": self.katman,
            "katman_adi": (bilinen or {}).get("ad", "bilinmiyor"),
            "maliyet": (bilinen or {}).get("maliyet", "?"),
            "alan_dolulugu": f"{len(alanlar)}/{len(KATMANLAR[0]['alanlar'])}",
            "eksik_alanlar": [
                a for a in KATMANLAR[0]["alanlar"] if not getattr(self, a, None)
            ],
            "kalici_adres": (
                ILAN_GOSTER_URL.format(guid=self.guid) if self.guid else None
            ),
            "kanit_yeterli": len(alanlar) >= 8,
        }




# ----------------------------------------------------------------------
# Kayitli yetenekler
# ----------------------------------------------------------------------


@registry.register(
    "kanit_kaydet",
    "Ticaret sicili ilan kanitini dogrular ve kendi verisiyle birlikte "
    "data/kanit/ altina kalici olarak yazar.",
)
def kanit_kaydet(
    ilan_sira_no: str,
    icerik_no: str,
    mersis_no: str = "",
    ticaret_sicil_no: str = "",
    ticaret_unvani: str = "",
    adres: str = "",
    mudurluk: str = "",
    yayin_tarihi: str = "",
    gazete_sayi: str = "",
    gazete_sayfa: str = "",
    tescil_tarihi: str = "",
    tescil_edilen_husus: str = "",
    delil_belgeler: str = "",
    ham_metin: str = "",
) -> dict:
    """Kanit olusturur, dogrular ve JSON olarak kalici yazar.

    D-216: supheli kanit **silinmez**, `sonuc` alaninda isaretlenir.
    Boylece hata da kaydedilmis veri olur.
    """
    kanit = IlanKaniti(
        ilan_sira_no=str(ilan_sira_no),
        icerik_no=str(icerik_no),
        mersis_no=mersis_no or None,
        ticaret_sicil_no=ticaret_sicil_no or None,
        ticaret_unvani=ticaret_unvani or None,
        adres=adres or None,
        mudurluk=mudurluk or None,
        yayin_tarihi=yayin_tarihi or None,
        gazete_sayi=gazete_sayi or None,
        gazete_sayfa=gazete_sayfa or None,
        tescil_tarihi=tescil_tarihi or None,
        tescil_edilen_husus=tescil_edilen_husus or None,
        delil_belgeler=delil_belgeler or None,
        alinma_zamani=datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        ham_metin=ham_metin,
    )
    kanit.dogrulama = kanit.dogrula()

    KANIT_DIZIN.mkdir(parents=True, exist_ok=True)
    hedef = KANIT_DIZIN / f"{kanit.kanit_anahtari()}.json"
    hedef.write_text(
        json.dumps(asdict(kanit), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "dosya": str(hedef.relative_to(KANIT_DIZIN.parents[2])),
        "sonuc": kanit.dogrulama["sonuc"],
        "anahtar": kanit.kanit_anahtari(),
        "bulgular": kanit.dogrulama["bulgular"],
    }


@registry.register(
    "kanit_listele",
    "Kaydedilmis ticaret sicili kanitlarini ozet olarak listeler.",
)
def kanit_listele(sirket_tipi: str = "") -> dict:
    """Tum kanit dosyalarini okur; `sonuc` ve alan dolulugunu ozetler.

    `sirket_tipi` filtresi: `as` | `sube` | `diger` (bos = hepsi).
    """
    if not KANIT_DIZIN.is_dir():
        return {"kayit": 0, "liste": [], "dizin": str(KANIT_DIZIN)}

    liste = []
    for dosya in sorted(KANIT_DIZIN.glob("*.json")):
        try:
            veri = json.loads(dosya.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            liste.append({"dosya": dosya.name, "sonuc": "okunamadi"})
            continue
        dogr = veri.get("dogrulama") or {}
        turedilen = dogr.get("turetilen") or {}
        kayit = {
            "dosya": dosya.name,
            "unvan": veri.get("ticaret_unvani"),
            "sicil_no": veri.get("ticaret_sicil_no"),
            "mersis_no": veri.get("mersis_no"),
            "sonuc": dogr.get("sonuc"),
            "sirket_tipi": turedilen.get("sirket_tipi"),
        }
        if sirket_tipi and kayit["sirket_tipi"] != sirket_tipi:
            continue
        liste.append(kayit)

    return {
        "kayit": len(liste),
        "supheli": sum(1 for k in liste if k.get("sonuc") == "supheli"),
        "liste": liste,
    }


