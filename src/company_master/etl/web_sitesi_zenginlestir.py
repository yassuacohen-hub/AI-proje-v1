# -*- coding: utf-8 -*-
"""website_domain zenginlestirme: unvan -> arama -> aday -> canli HTTP 200 ->
icerik dogrulama -> kabul() -> kaydet.

GOREVIN NEDENI (olculdu, 2026-10-04 canli Supabase / scripts/web_kaynak_olcum.py)
    Firma 10123 · `companies.website_domain` dolu 2780 · bos 7343.
    Bos alanli 2623 firmanin `source_records.raw_website` ham adayi var
    (kolon `companies`'ta **yok**, D-254 kolon birligi); **sablonsuz ham aday
    = 0**. Yani ham veriden bedava site GELMEZ; `scripts/backfill_websites.py`
    yalnizca `isim.org.tr` (2140 firma) ve `ostimistihdam.com` (474 firma)
    yazacakti — ikisi de sablon. O yol olcumle REDDEDILDI (asagida "Olumlu").

    Eski dolu 2780 DEGILDIR: `scripts/website_sablon_yedek.py` goc 0052 oncesi
    2666 sahte satiri yedekledi ve `NULL`'a cekti. Bu modul o 2780'e dokunmaz.

ZINCIR (sozlesme 3.7 + K-1/K-2/K-7)
    1. Arama   : unvan -> arama motoru -> aday alan adlari  (9Router /v1/search)
    2. Ele     : sablon (yazma_kapisi.SABLON_WEB), sosyal medya, kaynak domain
    3. Dogrula : izin kapisi (KazimaYazici.izin_var) -> HTTP 200 ->
                 icerikte firmanin ayirt edici unvan kelimesi
    4. Kapi    : yazma_kapisi.kabul()  (D-246 tek kapi)
    5. Yaz     : **yalniz bos alana**; iz `source_records` icinde `web_sitesi`
                 adiyla. Ayrica siteden `primary_phone`/`primary_email`/`address`
                 adayi cikarilir, yine yalniz bos alana.
    NACE ipucu SADECE `raw_payload`'a yazilir — puanlanmaz (D-252/3 TAHMIN katmani).

YENI HTTP ISTEMCISI YAZILMAZ (brief adim 4)
    Getirme: `scripts/kazima_jina_fallback.py::cek()` (once dogrudan, sonra
    9Router `/v1/web/fetch`). Arama: `ninerouter_client.web_search()`.
    Testlerde ag YOK: `arayuz`/`ceki` parametreleri enjekte edilir (D-243:
    testin kirlilettigi yer, yesil testin goremedigi yerdir).

KURALLAR
    * `kuru=True` (VARSAYILAN) HICBIR sey yazmaz — diske de, DB'ye de.
      Prova diske yazmaz (D-243).
    * Yikici is yok: sadece `UPDATE ... WHERE website_domain IS NULL` ve
      `source_records` INSERT. Yedek gerekmez (veri silinmez).
    * Dolu alan ASLA ezilmez.
    * Kaynak satiri idempotent: `(source_id, external_id)` UNIQUE.

CLI
    Betik `scripts/` altinda DEGILDIR; modul `src/company_master/etl/` icindedir.
    `src/` dizininden (paket yolu bulunur):
        python -X utf8 -m company_master.etl.web_sitesi_zenginlestir --kuru --asama 10
        python -X utf8 -m company_master.etl.web_sitesi_zenginlestir --yaz --asama 10
    Depo kokunden: `python -X utf8 scripts/web_kaynak_olcum.py` gibi once
    `set PYTHONPATH=src` verilir. `--kap-denetimi` ag kullanmaz.

Ilgili Nodlar: [[Huginn Data Insights/docs/VERI_KALITE_SOZLESMESI]] (3.7, K-7) ·
[[Huginn Data Insights/src/company_master/db/yazma_kapisi]] ·
[[Huginn Data Insights/scripts/web_kaynak_olcum]] ·
[[Huginn Data Insights/plans/brief_utku_VERI-WEB-SITESI-ZENGINLESTIR-01]]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.db.yazma_kapisi import SABLON_WEB, kabul, sablon_mu, temizle

__all__ = [
    "KAYNAK_ADI",
    "SOSYAL_MEDYA",
    "ICERIK_DAGITICI",
    "PARKLANMIS_IZLERI",
    "unvan_anahtar_kelimeler",
    "aday_domainler",
    "icerik_dogrula",
    "zenginlestir",
]

KAYNAK_ADI = "web_sitesi"
GIRIS_SATIRI = "companies"

#: Sosyal medya / pazar yeri / dizin siteleri. Bunlar alan adi degil, icerik
#: dagitimidir; 3.7 "kabul edilmez" (c) maddesi. Ozel liste degil — kanonik
#: liste `SABLON_WEB`; bu yalnizca "sosyal medya" sinifidir.
SOSYAL_MEDYA = (
    "facebook.com", "fb.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "youtube.com", "tiktok.com", "pinterest.com", "reddit.com",
    "sahibinden.com", "letgo.com", "hepsiburada.com", "trendyol.com", "n11.com",
    "sinyal.com.tr", "gpturk.com", "rsgd.com.tr", "ilan.net",
)

#: Alan adi pazarlama sayfalari. HTTP 200 doner ama icerik sirf "domain is for
#: sale" turundendir; 3.7 "kabul edilmez" (d) maddesi.
PARKLANMIS_IZLERI = (
    "domain is for sale", "domain for sale", "this domain", "parked",
    "alan adi satilik", "bu alan adi", "parklanmis", "alan adi kayit",
)

#: Dizin/ansiklopedi/platform siteleri. Sirketin kendi sitesi DEGILDIR;
#: 3.7 "kabul edilmez" (c) maddesi. Wikipedia testi bunu yakaladi:
#: 200 donen bir ansiklopedi sayfasi firma sitesi sanilabilirdi.
#: `all.biz` **olculerek** girdi (pilot 2); `kompass`, `yellowpages`,
#: `firma.com`, `alibaba` gibi girisler **ihtiyati**dir — ayni sinif
#: (ucretli B2B dizini). Olculemeyen bir madde yalnizca **red** tarafina
#: etki eder (veri kaybi), kabul tarafina degil; bu yuzden ihtiyati
#: maddeler tutulur. D-245: her birinin gercekten olculdugunu varsayma.
ICERIK_DAGITICI = (
    "wikipedia.org", "wikimedia.org", "wiktionary.org", "foursquare.com",
    "yelp.com", "yellowpages.com.tr", "yellowpages.com", "dmoz.org",
    "ekşi.com", "flickr.com", "vimeo.com", "github.com", "gitlab.com",
    "medium.com", "blogspot.com", "wordpress.com", "xing.com",
    "researchgate.net", "glassdoor.com",
    "all.biz", "alibaba.com", "kompass.com", "europages.com", "1x.com",
    "firmalar.com", "firma.com", "isletme.com", "yellowpages.co.uk",
    "cylex.com.tr", "listfirm.com", "b2b", "tradeindia.com", "exportersindia",
)

#: Kaynak (OSB/oda) domain'leri: firma listesi sayfalari. Kanit: 2623 bos
#: alanli firmanin ham adayi %100 bunlar. Sembolik liste, kanonik degil.
KAYNAK_DOMAIN = (
    "ostim.org.tr", "aso.org.tr", "baskentosb.org.tr", "ivedik.org.tr",
    "ostimistihdam.com", "ostimonline.com", "isim.org.tr", "osp.com.tr",
    "ankaraosb.org.tr", "osb.org.tr", "tobb.org.tr", "mevzuat.gov.tr",
)


def _dagitici_mi(url: str) -> bool:
    """Sosyal medya / pazar yeri / dizin degilse False.

    **Host siniri ile eslenir**, alt dize ile degil: pilot regresyonu —
    liste `firma.com` iceriyor, `a-firma.com.tr` alt dize kuraliyla
    eleniyordu (kendi adini tasiyan bir firmanin sitesi). Dogrusu
    `host == d veya host.endswith("." + d)`.
    """
    host = _host(url)
    for d in SOSYAL_MEDYA + ICERIK_DAGITICI:
        if host == d or host.endswith("." + d):
            return True
    return False

_ALAN_ADI_DESENI = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?"
                             r"(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$")
_TURKCE_KARSILIK = str.maketrans({
    "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
    "Ç": "c", "Ğ": "g", "İ": "i", "I": "i", "Ö": "o", "Ş": "s", "Ü": "u",
})

#: Unvanda sirfce gecen, ayirt edici olmayan kelimeler. `normalize.py`
#: `_TRADE_NAME_STOP_WORDS` ile ayni isi yapar; burada kapi kendi kopyasini
#: TUTMAZ, kanonik modulu import eder (D-211 ikiz yasagi).
_BOS_KELIMELER = frozenset({
    "ve", "ile", "ve", "san", "tic", "sanayi", "ticaret", "ltd", "sti",
    "as", "anonim", "sirketi", "limited", "sirket", "kol", "kom", "ort",
    "koop", "paz", "ith", "ihr", "muh", "mim", "ins", "nak", "oto", "tur",
    "tek", "gida", "hizm", "tar", "mad", "imal", "bil", "yaz", "mak", "mob",
    "elek", "kim", "dis", "ic", "tic", "ve", "sirket", "holding", "group",
    "grup", "is", "seviyesi", "sistemleri", "sistem", "cihaz", "makinalari",
})

#: **SEKTOR + SIRFCE + KONUM kelimeleri** — olcumle cikartildi, elle yazilmadi.
#:
#: Neden ayri liste: `icerik_dogrula` "unvandan >=2 kelime icerikte gecsin"
#: kuralini kullanir. `makina`, `metal`, `sanayi`, `celik`, `ostim`, `mehmet`
#: gibi kelimeler her sayfada gecer; sayilirlarsa kural **anlamini yitirir**
#: ve kuralin kendisi FP uretir. 2026-10-04 pilotu iki FP'yi bu yuzden
#: yazdi:
#:   * `AKIN MAKINA OTOMOTIV...` -> `ostimbul.com`  (Ostim *bulteni*)
#:   * `OZLEM CIECEKILIK` -> `cicekrehberi.net`   (cicek *dizini*)
#: Ikisinde de eslesme yalnizca sektor kelimelerinden geliyordu.
#:
#: OLÇÜM: 10123 canli `legal_name` tokeninin frekansi; unvanlarin %0.4'unden
#: fazla gecen token bu listeye girer. Uretici/denetleyici:
#: `scripts/genel_kelime_olcum.py` (`--kod` literal uretir, `--drift` kodu
#: denetler). Elle kelime EKLEME; eklenirse olcum tutmuyor demektir.
#: D-224 (olcmeden karar yok) + D-245 (doluluk gecerlilik degil).
GENEL_KELIMELER = frozenset({
    "ahmet", "aluminyum", "ambalaj", "ankara", "anonim", "araclar",
    "arge", "asansor", "bakim", "baskent", "boru", "boya",
    "celik", "danismanlik", "dekorasyon", "demir", "dogan", "dokum",
    "donusum", "egitim", "ekipmanlari", "elek", "emlak", "endustri",
    "endustriyel", "enerji", "geri", "gida", "grup", "halinde",
    "havacilik", "hayvancilik", "hidrolik", "hird", "hirdavat", "hizm",
    "huseyin", "iflas", "ihracat", "imal", "imalat", "insaat",
    "ismail", "ithalat", "kalip", "kapi", "kaplama", "kaucuk",
    "kesim", "lastik", "lazer", "limited", "lojistik", "makina",
    "makinalari", "malz", "malzemeleri", "market", "medikal", "mehmet",
    "mekanik", "metal", "motorlu", "muhendislik", "murat", "mustafa",
    "nedeniyle", "orman", "ostim", "otom", "otomasyon", "otomotiv",
    "parca", "petrol", "plastik", "profil", "proje", "reklam",
    "rulman", "saglik", "sahin", "sanayi", "savunma", "servis",
    "servisi", "sirketi", "sist", "sistemleri", "sondaj", "subesi",
    "taah", "taahhut", "tamir", "tasarim", "tasfiye", "tasimacilik",
    "teknik", "teknoloji", "teknolojileri", "temizlik", "ticaret", "turizm",
    "turz", "unlu", "uretim", "urunleri", "yalitim", "yapi",
    "yedek", "yeni", "yildiz", "yilmaz",
})

#: Sirfce + sektor + konum birlestirilmis bos kume (tek kapi).
_BOS_KELIMELER = _BOS_KELIMELER | GENEL_KELIMELER


def _duz(metin: str) -> str:
    """Turkce normalize: aksan katlama + kucuk harf. Ayni esleme icin tek yol.

    ONEMLI: once katla, sonra kucult. `"İ".lower()` U+0069 + U+0307
    (birlesik nokta) uretir; kucultme once yapilirsa "TİCARET" -> "ti̇caret"
    olur ve bolme `caret` gibi sahte kelimeler uretir (2026-10-04 kapida
    yakalandi: `unvan_anahtar_kelimeler(...) == ('metal', 'caret')`).
    """
    return str(metin or "").translate(_TURKCE_KARSILIK).lower()


def unvan_anahtar_kelimeler(unvan: str) -> tuple[str, ...]:
    """Unvandan ayirt edici kelimeler; sirfce olmayanlar dusurulur.

    Yalniz **kendi yazimi degil, normalize edilmis hali** doner; icerik
    dogrulamasi ayni katlamayi kullanir. `normalize_company_name()` bilerek
    KICAYARAK kisaltir ("ARITES METAL SAN. VE TIC."); burada tam kelimeler
    gerek, yoksa "SAN." ile "SANAYI" ayirt edilemez.
    """
    duz = _duz(unvan)
    kelimeler = re.split(r"[^a-z0-9]+", duz)
    secilen = [k for k in kelimeler if len(k) >= 4 and k not in _BOS_KELIMELER]
    # Uzun unvanda ilk 6 kelime yeter: hepsi gecmek zorunda degil, en az biri.
    return tuple(dict.fromkeys(secilen[:6]))


def _host(url: str) -> str:
    """URL'den alan adi: https://www.ornek.com.tr/yol?x=1 -> ornek.com.tr"""
    s = str(url or "").strip().lower()
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", s)
    s = s.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    s = s.split("@")[-1].split(":")[0]
    s = re.sub(r"^www\d?\.", "", s)
    return s.strip(".")


#: Unvanda Turk sirket turu **tanimi** varsa kayit Turk sirketidir; alan adi
#: `.tr` degilse yurt disi marka cakismasi riski vardir.
_TURK_SIRKET_TURU = ("ltd", "sti", "as", "anonim", "sirketi", "limited", "san", "tic")
#: Türkiye'de isletme kaydi acilan alan adlari.
_TURKIYE_UZANTI = ("tr", "com.tr", "net.tr", "org.tr", "gen.tr", "web.tr", "bel.tr")


def _uzanti(host: str) -> str:
    """Alan adinin **uzanti** kismi: `gezencadir.com.tr` -> `com.tr`,
    `gezencadir.com` -> `com`, `gomap.be` -> `be`, `ornek.tr` -> `tr`.

    Son iki etiketi birlestirmek hatayi uretiyordu: `gezencadir.com` ->
    `gezencadir.com` (uzanti degil, alan adinin kendisi) ve `ornek.tr` ->
    `ornek.tr` (yani **gercek bir `.tr` alan adi yurt disi sayiliyordu**).
    Ikincil ek yalniz `tr` sonunda turer; o durumda son uc etiket alinir,
    aksi halde son etiket uzantinin kendisidir.
    """
    parcalar = [p for p in host.split(".") if p]
    if len(parcalar) < 2:
        return host
    if parcalar[-1] == "tr" and len(parcalar) >= 3:
        return ".".join(parcalar[-2:])   # com.tr / net.tr / org.tr
    return parcalar[-1]


def yurt_kakismasi_olasilik(unvan: str, alan_adi: str) -> str | None:
    """Turk sirketi + yurt disi alan adi -> FP suphesi; gerekce doner.

    Pilot 4 (2026-10-04) canli FP: `GOMAP MÜH. MÜŞAVİRLİK DAN. VE ARAŞT.
    TİC. LTD. ŞTİ.` -> `gomap.be`. Marka kelimesi domain'de **vardi**, icerik
    dogrulamasi gecti; ama sayfa **GOMAP SCS** (BCE0806.750.087) — Belcika
    sirketi. Ayni marka, farkli ulke. Sahiplik kaniti bu turu yakalamaz:
    domain gercekten o markaya ait.

    Ayirici tek sinyal: unvanda Turk sirket turu (`LTD. ŞTİ.`) var, alan
    adi `.tr` degil. Turk siciline kayitli bir firmanin yurt disi sitesi
    *olabilir* — bu yuzden **reddedilmez**, `el_tasidi`'ye dusurulur.
    """
    duz = _duz(unvan)
    kelimeler = set(re.split(r"[^a-z0-9]+", duz))
    if not kelimeler & set(_TURK_SIRKET_TURU):
        return None
    uzanti = _uzanti(_host(alan_adi))
    if uzanti in _TURKIYE_UZANTI:
        return None
    return (f"yurt_kakismasi_suspesi: unvan Turk sirketi, alan adi .{uzanti} "
            f"— ayni marka yurt disinde kullanilabilir")


def aday_domainler(aranan_unvan: str, arama_sonucu: Any,
                   en_fazla: int = 5) -> list[tuple[str, str]]:
    """Arama sonucundan yazilabilir aday alan adlari: `[(host, kaynak_url)]`.

    Eleme sirasi: gecersiz bicim -> sosyal medya -> kanonik sablon ->
    kaynak domain -> ayni adayin tekrari. **Arama motoru sirasi korunur**
    (ilk sonuc en guclu aday); sirfca en cok aday degil.
    """
    if not unvan_anahtar_kelimeler(aranan_unvan):
        return []
    sonuclar = _arama_sonuclari(arama_sonucu)
    adaylar: list[tuple[str, str]] = []
    gorulen: set[str] = set()
    for url in sonuclar:
        host = _host(url)
        if not host or host in gorulen:
            continue
        if not _ALAN_ADI_DESENI.match(host):
            continue
        if host.endswith((".tr.gov", ".gov.tr", ".bel.tr", ".edu.tr")):
            continue
        tam = f"https://{host}"
        if _dagitici_mi(tam):
            continue
        if sablon_mu(tam, SABLON_WEB):
            continue
        if any(d in tam for d in KAYNAK_DOMAIN):
            continue
        gorulen.add(host)
        adaylar.append((host, url))
        if len(adaylar) >= en_fazla:
            break
    return adaylar


def _arama_sonuclari(arama_sonucu: Any) -> list[str]:
    """9Router/arama saglayicisinin dondurdugu URL'leri cikar.

    Saglayiciya gore sarmalayici degisir; **liste ureti tek yoldadir**.
    Bilinmeyen bicim bos sayilir (sessizce "sonuc yok" doner — 0 sayim yazilir,
    D-245: "0" ile "yapi bilinmiyor" ayni degildir, bu yuzden `sebep` alani
    ayri tutulur).
    """
    if arama_sonucu is None:
        return []
    if isinstance(arama_sonucu, list):
        return [str(x) for x in arama_sonucu if isinstance(x, str)]
    if not isinstance(arama_sonucu, dict):
        return []
    for anahtar in ("results", "data", "items", "web_results"):
        blok = arama_sonucu.get(anahtar)
        if isinstance(blok, list):
            return [str(x.get("url")) for x in blok
                    if isinstance(x, dict) and x.get("url")]
        if isinstance(blok, dict):
            ic = blok.get("results")
            if isinstance(ic, list):
                return [str(x.get("url")) for x in ic
                        if isinstance(x, dict) and x.get("url")]
    return []


def icerik_dogrula(icerik: str, unvan: str, alan_adi: str = "") -> tuple[bool, str]:
    """(gecer, sebep). Sayfa, firmanin AYIRT EDICI kVtigi tasiyabilir.

    Kurallar:
      * HTTP 200 **yetmez** — icerik dogrulamasi ayrica sart (3.7 "saglama").
      * Tek basina zayif kelime **yetmez**. Kanit (canli pilot, 8 firma,
        2026-10-04 — iki tur, üç gerçek yanlis pozitif):
          1) `BERAT MAK.` -> `info-albania.com` (Arnavutluk/Berat turizm
             rehberi). Eslesen "berat": 5 karakter, domain'de **yok**.
          2) `MERCAN MAK.` -> `8438-tr.all.biz` (ucretli B2B dizini).
             Eslesen "mercan": 6 karakter, domain'de yok. -> `all.biz`
             ayrica dizin listesine girdi, ama asil kapı zayif-kelime kuralı.
          3) `ÖZLEM ÇIÇEKCILIK` -> `alocicek.com` (baska cicekci).
             Eslesen "cicekcilik": 10 karakter, domain'de yok. **6+ karakter
             kacisi bu yuzden kaldirildi.**
        Kapalı kural (2026-10-04, 3 pilot): ayirt edici kelimenin alan adının
        **kendisinde** geçmesi **zorunludur**; "ya da içerikte iki kelime"
        seçeneği ölçümle kaldırıldı (aşağıdaki `sahiplik_kaniti_yok`).
      * Alan adı + içerik eşleşmesi **farklı** kelimelerden olmalıdır
        (`marka_kalintisi_kaniti_yok`): `GMT Pano` -> `EGEMEN PANO` FP'si.
      * Icinde gecen **baska** firmanin unvani varsa reddet: aday yanlis.
      * Parklanmis alan adi izleri reddet.
    """
    metin = _duz(icerik)
    if not metin.strip():
        return False, "icerik_bos"
    if len(metin) < 200:
        return False, f"icerik_kisa ({len(metin)} karakter)"
    for iz in PARKLANMIS_IZLERI:
        if iz in metin:
            return False, f"parklanmis_alan_adi: {iz}"
    kelimeler = unvan_anahtar_kelimeler(unvan)
    if not kelimeler:
        return False, "unvan_ayirt_edici_kelime_yok"
    eslesen = [k for k in kelimeler if k in metin]
    if not eslesen:
        return False, f"unvan_kelimesi_gecmiyor ({len(kelimeler)} denendi)"

    host = _duz(_host(alan_adi))
    domain_diyor = [k for k in kelimeler if k in host]
    if not domain_diyor:
        # SAHIPLIK KANITI YOK. 2026-10-04 uc pilotun olcumu:
        #   pilot 2: MERCAN MAK. -> 8438-tr.all.biz       marka domain'de DEGIL
        #   pilot 3: AKIN MAKINA   -> ostimbul.com           marka domain'de DEGIL
        #   pilot 3: FABRIKA ANKARA -> atonet.org.tr        marka domain'de DEGIL
        #   pilot 4: OZLEM CIECEKILIK -> cicekrehberi.net  marka domain'de DEGIL
        # Ve olcumlu olarak **her gercek eslesmede marka domain'deydi**
        # (duzeygd, gezencadir, gomap.be, mkbhidrolik, aksisgrup,
        # ahsapteknik, beratmakinam, aritesnord). "icerikte 2 kelime" dalinin
        # urettigi 4 FP'nin 4'u de o daldan geldi; kaniti olmayan acik
        # birakmaktan baska ise yaramadi. D-245: dogrulanmayan eslesme
        # kanit degildir. Dizin sayfalari (bir firmanin kaydi) eslesme
        # uretir ama site sahibi degildir — sahiplik yalniz domain'de
        # kanitlanir.
        return False, (f"sahiplik_kaniti_yok: {eslesen[0]} icerikte geciyor ama "
                       "marka kelimesi alan adinin kendisinde degil")
    if len(kelimeler) == 1:
        # Unvan tek bir ayirt edici kelimeye iniyor (`BERAT MAK.` -> "berat").
        # Tek kelime + marka domain'de = **zayif kanit**: pilot 3'te
        # `beratmakinam.com` sayfasi SEO kelime yiginiydi ("ahsap isleme,
        # ahsap isleme makinalari, ..." tekrar tekrar) ve DB'deki kisaltilmis
        # unvan ayni adi tasiyan baska firmalarla paylasiliyor olabilir.
        # Yazmak yerine **adaya** dusurulur; elle dogrulanir (D-66).
        return False, (f"tek_anahtar_kelime_elle_gerekli ({domain_diyor[0]}): "
                       "unvan tek kelimeye indigi icin kanit yetersiz")

    # MARKA KALINTISI KANITI (2026-10-04, pilot 5 — D-66 olculmus FP).
    # Alan adindaki kelime **sector/faaliyet** kelimesi olabilir. Bu durumda
    # icerik eslesmesi de ayni kelimeden gelir ve **sayfa kimin oldugu
    # belirlemez**:
    #   `EGEMEN PANO` -> `gmtpano.com` icerik "GMT Pano", "egemen" SAYFADA
    #   YOK. Eslesen tek kelime "pano" idi; hem icerikte hem domain'de.
    #   -> icerik dogrulamasi GECTI, gercekte **yanlis pozitif**.
    # Ayni sekilde `FATİH ÇIKMA ...` -> `volkswagencikmaparca.com.tr`
    # ("Fatih Volkswagen"): "cikma" yedek parca jargonu, marka kaniti degil.
    # Kapalı kural: alan adinda **gecmeyen** unvan kelimesinden en az biri
    # icerikte de geçmeli. O kelime markanın *kalanidir*; o olmadan sayfa
    # yalnizca ayni sektoru yapan baska bir firmaya ait olabilir.
    kalan = [k for k in kelimeler if k not in domain_diyor]
    kalan_eslesen = [k for k in kalan if k in metin]
    if kalan and not kalan_eslesen:
        # NOT: `kalan` bos ise (unvanin **tamami** alan adinda — orn.
        # `ARİTES NORD` -> `aritesnord.com.tr`) reddetme: bu en guclu
        # kanittir, alan adi markanin tam kendisidir.
        return False, (f"marka_kalintisi_kaniti_yok ({domain_diyor[0]}): alan "
                       f"adinda + icerikte gecen kelime sektor kelimesi; "
                       f"unvanin diger kelimesi ({', '.join(kalan)}) icerikte "
                       "yok — sayfa ayni sektoru yapan baska firma olabilir")

    if not kalan:
        return True, (f"eslesti: {'+'.join(domain_diyor)} [marka domain'de: "
                      "unvanin tamami alan adinda]")
    return True, (f"eslesti: {domain_diyor[0]} [marka domain'de] + "
                  f"{kalan_eslesen[0]} [marka kalintisi icerikte]")


#: TR telefonu: `0`/`+90` onekli, 3+3+2+2. Cep (5xx) ve sabit (3xx, 4xx)
#: ayni bicimde oldugu icin tek desen yeter. Oneksiz rakam ADRES/yil
#: sayisidir; oneksiz numara aday sayilmaz (D-243 sahte pozitif yasagi).
_TELEFON_DESENI = re.compile(
    r"(?<![\d])0\s?\d{3}[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}(?!\d)")


def _telefon_adayi(metin: str) -> str | None:
    """TR telefonunu tek aday olarak cikar; yoksa `None` (uydurma yok)."""
    temiz = str(metin or "").replace("+90", " ")
    m = _TELEFON_DESENI.search(temiz)
    if not m:
        return None
    rakam = re.sub(r"\D", "", m.group(0))
    if len(rakam) != 11 or not rakam.startswith("0"):
        return None
    return "+90" + rakam[1:]


def _telefon_kisisel_mi(telefon: str | None) -> bool | None:
    """KVKK ipucu: TR GSM onbeki `5` ile basliyorsa olasi kisisel cep.

    Silmez/reddetmez (utku notu: cep numaralari kabul edilir) -- sadece
    D-252/3 ile ayni "sadece ipucu, raw_payload'a, hic skorlanmaz" kalibinda
    etiket uretir. Sabit hat (2/3/4 ile baslayan alan kodu) -> False.
    `None`: telefon yok, karar verilecek bir sey yok.
    """
    if not telefon:
        return None
    rakam = re.sub(r"\D", "", telefon)  # +905xxxxxxxxx -> 905xxxxxxxxx
    if rakam.startswith("90"):
        rakam = rakam[2:]
    return rakam.startswith("5")


_EPOSTA_DESENI = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def _eposta_adayi(metin: str) -> str | None:
    """Gorunur e-posta: gorsel metinde yazan adres (info@osb... reddedilir)."""
    for m in _EPOSTA_DESENI.finditer(metin):
        adres = m.group(0).lower()
        yerel = adres.split("@")[0]
        if _dagitici_mi(adres) or any(d in adres for d in KAYNAK_DOMAIN):
            continue
        if yerel in ("info", "iletisim", "contact", "info@example"):
            continue
        return adres
    return None


_ADRES_DESENI = re.compile(r"(?:adres|address)\s*[:\-]\s*([^\n]{10,200})", re.I)
_ETIKET_DESENI = re.compile(r"<[^>]+>")


def _adres_adayi(metin: str) -> str | None:
    """`Adres:` kalibindan sonraki satir. Kalip yoksa aday yok (uydurma yok).

    HTML etiketi **soyulur** (pilot 2026-10-04: `GEZEN GRUP` sayfasinda
    `Adres:` satirinda `</div><div class="textwidget"><p>...` geliyordu;
    etiket kirletilmeden yazilsaydi kolona HTML giderdi). Soyma sonrasi
    25 karakterden kisa kalirsa aday **yok**: parca calis, adres degil.
    """
    m = _ADRES_DESENI.search(metin)
    if not m:
        return None
    aday = " ".join(_ETIKET_DESENI.sub(" ", m.group(1)).split()).strip(" -:;")
    if len(aday) < 25:
        return None
    return aday


def zenginlestir(engine, *, arama: Callable[[str], Any] | None = None,
                 ceki: Callable[[str], tuple[str, str]] | None = None,
                 kuru: bool = True, asama: int = 20,
                 hedefler: list[dict] | None = None) -> dict:
    """Bos `website_domain` alanlarini arama + canli dogrulama ile doldurur.

    `kuru=True` HICBIR sey yazmaz. `kuru=False` icin:
      * yalniz `website_domain IS NULL` satirlar hedeflenir (dolu ezilmez),
      * her yazimdan once `kabul()` (D-246),
      * iz `source_records` icinde `web_sitesi` adiyla birakilir.
    """
    from sqlalchemy import text

    if arama is None or ceki is None:
        arama, ceki = _varsayilan_arama, _varsayilan_ceki

    if hedefler is None:
        with engine.connect() as conn:
            hedefler = [dict(r) for r in conn.execute(text(f"""
                SELECT company_id, legal_name
                FROM {GIRIS_SATIRI}
                WHERE website_domain IS NULL OR btrim(website_domain) = ''
                ORDER BY company_id
                LIMIT :asama
            """), {"asama": asama}).mappings()]
    ozet = {"hedef": len(hedefler), "yazilan": 0, "dogrulanan": 0,
            "el_tasidi": 0, "kuru": bool(kuru), "satirlar": []}
    kaynak_id = None if kuru else _kaynak_id(engine)

    for firma in hedefler:
        unvan = firma.get("legal_name") or ""
        kayit = _satir_isle(firma, unvan, arama, ceki)
        ozet["satirlar"].append(kayit)
        if kayit.get("kabul"):
            ozet["dogrulanan"] += 1
        # Manuel aday **sayisi**: D-66 elle inceleme kuyrugu bu olcumle
        # takip edilir. Satir ici `el_tasidi` listesinden turetilir; ikinci
        # bir sayac tutulmaz (D-263: bir olcunun iki yerde yazilmasi).
        ozet["el_tasidi"] += len(kayit.get("el_tasidi") or ())
        if kuru or not kayit.get("kabul"):
            continue
        yazilan = _yaz(engine, kaynak_id, firma["company_id"], unvan, kayit)
        ozet["yazilan"] += yazilan
    return ozet


def _satir_isle(firma: dict, unvan: str, arama, ceki) -> dict:
    """Tek firma: arama -> aday -> izin -> 200 -> icerik -> kabul()."""
    satir = {"company_id": firma.get("company_id"), "legal_name": unvan,
             "domain": None, "sebep": "", "kabul": False,
             "telefon": None, "eposta": None, "adres": None}
    kelimeler = unvan_anahtar_kelimeler(unvan)
    if not kelimeler:
        satir["sebep"] = "unvan_ayirt_edici_kelime_yok"
        return satir
    try:
        adaylar = aday_domainler(unvan, arama(unvan))
    except Exception as exc:  # arama saglayicisi yoksa sessizce gecme
        satir["sebep"] = f"arama_hatasi: {type(exc).__name__}"
        return satir
    if not adaylar:
        satir["sebep"] = "arama_adayi_yok"
        return satir

    from company_master.etl.scrape_kayit import KazimaYazici
    #: Her adayin gerekcesi. Tek `sebep` **son** adayi gosteriyordu; 8 adayli
    #: bir firmanin gercek nedeni (sahiplik/izin/sekil) raporda gorunuyordu,
    #: gormuyordu. D-66 incelemesi aday aday yapildigi icin tam liste birakilir.
    denemeler = []
    #: HTTP 200 + icerikte kelime gecen ama **kanit yetersiz** adaylar.
    #: Yazilmaz; raporda gorunur, elle dogrulanir (D-66 ≥20 ornek).
    el_tasidi = []
    #: Kaniti yetersiz ama **dogrulanabilir** aday: gercekten o firmanin
    #: sitesi olabilir, ancak olculmus kapilar tek basina yetmiyor. Duzeltme
    #: yazmaz, kuyruga atar.
    ELLE_GEREKEN_SEBEPLER = ("tek_anahtar_kelime_elle_gerekli",
                            "marka_kalintisi_kaniti_yok")
    for host, kaynak_url in adaylar:
        url = f"https://{host}"
        # Yurt kapisi **icerik cekmeden once** calisir: `.be`/`.de` alan adli
        # bir Turk `LTD. STI.` adayi Turk sirketinin resmi sitesi olamaz
        # (D-66 `gomap.be`). Onceki sira hem anlamsiz bir istek atiyordu hem
        # sonucu sayfa icerigine bagliydi; karar artik deterministik.
        kacak = yurt_kakismasi_olasilik(unvan, url)
        if kacak:
            denemeler.append({"domain": url, "sebep": kacak})
            el_tasidi.append({"domain": url, "sebep": kacak})
            continue
        izin, izin_sebep = KazimaYazici.izin_var(url)
        if not izin:
            denemeler.append({"domain": url, "sebep": f"izin_yok: {izin_sebep}"})
            continue
        metin, hata = ceki(url)
        if not metin:
            denemeler.append({"domain": url, "sebep": f"cek_hatasi: {hata or 'metin_bos'}"})
            continue
        gecer, sebep = icerik_dogrula(metin, unvan, alan_adi=url)
        if not gecer:
            denemeler.append({"domain": url, "sebep": sebep})
            if sebep.startswith(ELLE_GEREKEN_SEBEPLER):
                el_tasidi.append({"domain": url, "sebep": sebep})
            continue

        kayit = {"website_domain": url, "source_record_id": f"web:{firma['company_id']}",
                 "primary_phone": _telefon_adayi(metin),
                 "primary_email": _eposta_adayi(metin),
                 "address": _adres_adayi(metin)}
        temiz, ret = kabul(kayit)
        satir["domain"] = url
        satir["telefon"] = temiz.get("primary_phone")
        satir["eposta"] = temiz.get("primary_email")
        satir["adres"] = temiz.get("address")
        satir["sebep"] = sebep
        satir["kabul"] = bool(temiz.get("website_domain"))
        if ret:
            satir["ret_sebepleri"] = ret
        satir["kaynak_url"] = kaynak_url
        satir["denenen_aday"] = len(adaylar)
        break
    if denemeler:
        satir["aday_denemeleri"] = denemeler
    if el_tasidi:
        satir["el_tasidi"] = el_tasidi
    if not satir["kabul"]:
        satir["sebep"] = (f"{len(denemeler)}/{len(adaylar)} aday elendi; "
                          f"son: {denemeler[-1]['sebep']}") if denemeler \
            else "aday_dogrulanmadi"
    return satir


def _yaz(engine, kaynak_id, company_id, unvan: str, kayit: dict) -> int:
    """Yalniz bos alana yazar; izi `source_records`'a birakir (brief adim 5)."""
    from sqlalchemy import text

    yazilan = 0
    with engine.begin() as conn:
        for alan, deger in (("website_domain", kayit["domain"]),
                            ("primary_phone", kayit.get("telefon")),
                            ("primary_email", kayit.get("eposta")),
                            ("address", kayit.get("adres"))):
            if not deger:
                continue
            sonuc = conn.execute(text(f"""
                UPDATE {GIRIS_SATIRI}
                SET {alan} = :deger, updated_at = NOW()
                WHERE company_id = :cid
                  AND ({alan} IS NULL OR btrim({alan}) = '')
            """), {"deger": deger, "cid": company_id})
            yazilan += sonuc.rowcount or 0
        conn.execute(text("""
            INSERT INTO source_records
                (source_id, external_id, raw_name, raw_website, raw_payload)
            VALUES (:sid, :eid, :ad, :web, CAST(:payload AS jsonb))
            ON CONFLICT (source_id, external_id) DO UPDATE
               SET raw_website = COALESCE(EXCLUDED.raw_website, raw_website),
                   raw_payload  = COALESCE(source_records.raw_payload, '{}'::jsonb)
                                 || COALESCE(EXCLUDED.raw_payload, '{}'::jsonb)
        """), {
            "sid": kaynak_id, "eid": f"web:{company_id}", "ad": unvan,
            "web": kayit["domain"],
            "payload": json.dumps({
                "kaynak": KAYNAK_ADI,
                "kaynak_url": kayit.get("kaynak_url"),
                "dogrulama": kayit.get("sebep"),
                # NACE ipucu SADECE ham arsive gider; puanlanmaz (D-252/3).
                "nace_tahmin": None,
                # KVKK ipucu: ayni D-252/3 kalibi -- sadece ham arsive,
                # hic skorlanmaz/maskelenmez; elle inceleme icin isaret.
                "telefon_kisisel_olabilir": _telefon_kisisel_mi(kayit.get("telefon")),
            }, ensure_ascii=False),
        })
    return yazilan


def _kaynak_id(engine):
    """`sources` icinde `web_sitesi` kaydini bul; yoksa olustur (idempotent)."""
    from sqlalchemy import text

    with engine.begin() as conn:
        kayit = conn.execute(text(
            "SELECT source_id FROM sources WHERE source_name = :ad LIMIT 1"),
            {"ad": KAYNAK_ADI}).first()
        if kayit:
            return kayit[0]
        yeni = conn.execute(text("""
            INSERT INTO sources (source_name, source_type, url, collection_method,
                                 authority_score)
            VALUES (:ad, 'company_website', NULL, 'arama + canli dogrulama', 0.5)
            ON CONFLICT DO NOTHING
            RETURNING source_id
        """), {"ad": KAYNAK_ADI}).first()
        if yeni:
            return yeni[0]
        return conn.execute(text(
            "SELECT source_id FROM sources WHERE source_name = :ad LIMIT 1"),
            {"ad": KAYNAK_ADI}).scalar()


def _varsayilan_arama(unvan: str) -> Any:
    """9Router `/v1/search`. Saglayici yoksa hata firlatilir (sessiz 0 degil)."""
    from company_master.gateway.ninerouter_client import get_client
    return get_client().web_search(f'"{unvan}" Ankara firma web sitesi',
                                   max_results=8)


_SCRIPTS_YOLU_EKLENDI = False


def _varsayilan_ceki(url: str) -> tuple[str, str]:
    """`kazima_jina_fallback.cek` — yeni HTTP istemcisi yazmaz (brief adim 4).

    HTTP 200 SORNESI: dogrudan yolda `raise_for_status()` 200 disini hata
    yapar, yani 404/500 metin donmez. Jina yolunda ise 200 **9Router
    geçidinin** kodudur; koken sayfasi 404 olsa da gecit 200 doner ve hata
    metni icerik olarak gelir. Bu yuzden 200 kaniti orada **zayiftir**; asil
    kapı `icerik_dogrula`'dır (hata sayfasinda unvan kelimesi gecmez).
    Jina yolunu kanıt diye saymıyoruz; yalnız metin deneriz.
    """
    global _SCRIPTS_YOLU_EKLENDI
    if not _SCRIPTS_YOLU_EKLENDI:
        sys.path.insert(0, str(ROOT / "scripts"))
        _SCRIPTS_YOLU_EKLENDI = True
    from kazima_jina_fallback import cek  # noqa: E402
    sonuc = cek(url)
    return sonuc.get("metin", ""), sonuc.get("hata", "")


def sema_dogrula(engine) -> list[str]:
    """Yazma yolunun gercekten var oldugu kolonlari olcer (SALT OKUNUR).

    D-245/D-260: `CREATE TABLE` dosyasinda gordugum kolonla canli semadaki
    kolon ayni sey DEGIL (0031/0033/0035 kolonlari ekledi, ikizleri dustu).
    Yazma oncesi **olcer**; uyusmazsa `_yaz` patlar ve hicbir sey yazilmaz.

    Doner: eksik/yanlis bulunan maddelerin listesi (bos = uyumlu).
    """
    from sqlalchemy import text

    istenen = {
        "companies": ["company_id", "legal_name", "website_domain", "primary_phone",
                      "primary_email", "address", "updated_at"],
        "source_records": ["source_id", "external_id", "raw_name", "raw_website",
                           "raw_payload"],
        "sources": ["source_id", "source_name", "source_type"],
    }
    eksik: list[str] = []
    with engine.connect() as conn:
        for tablo, kolonlar in istenen.items():
            var = {r[0] for r in conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name = :t"), {"t": tablo})}
            for k in kolonlar:
                if k not in var:
                    eksik.append(f"{tablo}.{k} kolonu yok")
        # ON CONFLICT (source_id, external_id) yazma yolu icin ZORUNLU.
        kisit = {r[0] for r in conn.execute(text("""
            SELECT c.conname FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE t.relname = 'source_records' AND c.contype = 'u'
        """))}
        if not any("source_records" in s for s in kisit):
            eksik.append("source_records UNIQUE kisiti yok — ON CONFLICT patlar "
                         "(goc 0031 uygulanmamis olabilir)")
        # source_type CHECK: 'company_website' kabul ediliyor mu?
        if conn.execute(text(
                "SELECT 1 FROM sources WHERE source_type = 'company_website'"
                " LIMIT 1")).first() is None:
            # Kayit yoksa CHECK tanimini oku.
            ck = conn.execute(text("""
                SELECT pg_get_constraintdef(oid) FROM pg_constraint
                WHERE conrelid = 'sources'::regclass AND contype = 'c'
            """)).scalars().all()
            if ck and not any("company_website" in d for d in ck):
                eksik.append("sources.source_type CHECK'i 'company_website'"
                             " degerini kabul etmiyor")
    return eksik


if __name__ == "__main__":
    import argparse

    # D-86: Windows cp1254 — once stdout utf-8'ye cevrilir.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    def _kap_denetimi() -> None:
        """Kirarak dogrulama: saf katman, ag ve DB yok."""
        k = unvan_anahtar_kelimeler("ARİTES NORD SANAYİ VE TİCARET LTD. ŞTİ.")
        assert k == ("arites", "nord"), k
        assert unvan_anahtar_kelimeler("ARİTES METAL SAN. LTD.") == ("arites",), \
            "sektor kelimesi marka sayilmamali (GENEL_KELIMELER)"
        assert "sanayi" not in k and "ltd" not in k, k
        a = aday_domainler("ARİTES NORD", {"results": [
            {"url": "https://www.aritesnord.com.tr/iletisim"},
            {"url": "https://www.facebook.com/aritesnord"},
            {"url": "https://www.isim.org.tr/firma"},
            {"url": "https://ostim.org.tr/uye"},
        ]})
        assert a == [("aritesnord.com.tr",
                      "https://www.aritesnord.com.tr/iletisim")], a
        g, s = icerik_dogrula("ARITES NORD " * 40, "ARİTES NORD SAN. LTD.",
                              alan_adi="https://aritesnord.com.tr")
        assert g, s
        assert not icerik_dogrula("KOMŞU FIRMA " * 60, "ARİTES NORD SAN. LTD.",
                                  alan_adi="https://aritesnord.com.tr")[0]
        assert not icerik_dogrula("", "ARİTES NORD",
                                  alan_adi="https://aritesnord.com.tr")[0]
        # 2026-10-04 pilot 4: marka domain'de yoksa icerik eslesmesi YETMEZ
        assert not icerik_dogrula("ARITES NORD " * 40, "ARİTES NORD SAN. LTD.",
                                  alan_adi="https://firma-dizini.com")[0]
        # 2026-10-04 pilot 5 canli FP: `EGEMEN PANO` -> `gmtpano.com`
        # (icerik "GMT Pano"; "egemen" sayfada YOK). Eslesen tek kelime
        # "pano" idi — hem icerikte hem domain'de. Sektor kelimesi marka
        # kaniti degildir.
        assert not icerik_dogrula("GMT PANO " * 40, "EGEMEN PANO",
                                  alan_adi="https://gmtpano.com")[0], \
            "sektor kelimesi tek basina (pano) kabul edilmemeli"
        # Ayni sayfada unvanin kalinti kelimesi varsa kabul edilir.
        assert icerik_dogrula("EGEMEN PANO " * 40, "EGEMEN PANO",
                              alan_adi="https://gmtpano.com")[0], \
            "marka kalinti kelimesi icerikteyse kabul edilmeli"
        # Uzanti hesabi: `.tr` son ek degil, gercek Turk uzantisi.
        assert _uzanti("ornek.tr") == "tr", _uzanti("ornek.tr")
        assert _uzanti("gezencadir.com") == "com", _uzanti("gezencadir.com")
        assert _uzanti("gezencadir.com.tr") == "com.tr"
        assert _uzanti("gomap.be") == "be", _uzanti("gomap.be")
        assert yurt_kakismasi_olasilik("FATİH ÇIKMA OTO YED. PAR. SAN. TİC. LTD. ŞTİ.",
                                       "https://ornek.tr") is None, \
            "gercek .tr alan adi yurt disi sayilmamali"
        assert _telefon_adayi("Tel: 0312 123 45 67") == "+903121234567"
        assert _telefon_adayi("Adres: Ostim OSB") is None

    def _main() -> int:
        ap = argparse.ArgumentParser(
            description="website_domain zenginlestirici (varsayilan: --kuru)")
        ap.add_argument("--kuru", action="store_true",
                        help="HICBIR sey yazmaz (VARSAYILAN)")
        ap.add_argument("--yaz", action="store_true",
                        help="Dogrulanmis degerleri bos alana yaz (kapidan gecerse)")
        ap.add_argument("--asama", type=int, default=20,
                        help="Kac firma islenecek (varsayilan 20)")
        ap.add_argument("--kap-denetimi", action="store_true",
                        help="Saf katman dogrulama; DB ve ag acmaz")
        ap.add_argument("--sema-denetimi", action="store_true",
                        help="Yazma yolunun kolonlarini canli semada olcer "
                             "(SALT OKUNUR)")
        sec = ap.parse_args()

        if sec.kap_denetimi:
            _kap_denetimi()
            print("[OK] web_sitesi_zenginlestir kapi mandallari gecti")
            return 0

        from company_master.db.connection import get_engine
        engine = get_engine()

        if sec.sema_denetimi:
            eksik = sema_dogrula(engine)
            if eksik:
                print("[HATA] yazma yolu semaya uymuyor:")
                for e in eksik:
                    print(f"  - {e}")
                return 1
            print("[OK] canli semada yazma yolunun tum kolonlari ve "
                  "UNIQUE kisiti mevcut (salt okunur)")
            return 0
        if sec.yaz and sec.kuru:
            ap.error("--kuru ile --yaz birlikte verilemez")
        # Yazma oncesi sema kapisi: uyusmazsa hicbir sey yazilmaz (D-245).
        if sec.yaz:
            eksik = sema_dogrula(engine)
            if eksik:
                print("[HATA] --yaz iptal: sema uyusmadi")
                for e in eksik:
                    print(f"  - {e}")
                return 1

        ozet = zenginlestir(engine, kuru=not sec.yaz, asama=sec.asama)
        # stdout **saf JSON** (D-260: tuketici ayristirmak zorunda kalmamali).
        # Ozet `stderr`'e gider; `2>` ile yakalanir.
        print(json.dumps(ozet, ensure_ascii=False, indent=2, default=str))
        if ozet["kuru"]:
            print(f"[OK] kuru kosu: {ozet['dogrulanan']}/{ozet['hedef']} dogrulandi, "
                  f"{ozet['el_tasidi']} aday elle inceleme kuyrugunda, "
                  "0 yazildi", file=sys.stderr)
        else:
            print(f"[OK] yazma kosu: {ozet['yazilan']} alan yazildi",
                  file=sys.stderr)
        return 0

    raise SystemExit(_main())
