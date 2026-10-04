# -*- coding: utf-8 -*-
"""Firma türü + KVKK etiketi: TEK üretim kapısı.

**Neden ayrı dosya (D-211 ikiz yasağı):** şahıs işletmesi tespiti hem
`vector/service.py` hem ETL hem panel soruyordu. İkinci kopya bayatlar ve
biri düzeltilip diğeri unutulur. Soru bir kez, burada sorulur.

**KAHİN kararı (2026-10-02) — kanonik tür listesi:**
Türkiye'de TTK ve Kooperatifler Kanunu uyarınca **7 ticaret şirketi türü**
vardır:

| # | Tür | Etiket |
|---|---|---|
| Sermaye şirketi | Limited Şirket (Ltd. Şti.) | `limited_sirket` |
| Sermaye şirketi | Anonim Şirket (A.Ş.) | `anonim_sirket` |
| Sermaye şirketi | Sermayesi Paylara Bölünmüş Komandit Şirket | `payli_komandit_sirket` |
| Şahıs şirketi | Şahıs Firması (gerçek kişi / adı soyadı) | `sahis_isletmesi` |
| Şahıs şirketi | Kollektif Şirket | `kolektif_sirket` |
| Şahıs şirketi | Adi Komandit Şirket | `adi_komandit_sirket` |
| Özel kanunlu | Kooperatif | `kooperatif` |

Ek değerler (yukarıdaki 7'nin **yerine geçmez**, ayrı tutulur):
`diger_tur` — TTK dışı / 7'ye girmeyen (holding grubu, vakıf, dernek).
`belirsiz` — kanıt yok. **"Bilmiyorum" ile "tüzel" aynı şey DEĞİLDİR**
(D-249: veri yok ≠ 0).

**ÇELİŞKİ — kayda geçirildi, karşılanmadı.** D-246/6: *"Türetilmiş alan elle
yazılmaz. `tuzel_tip` yalnız sağlamadan geçmiş `vkn`/`tckn` kolonundan
türetilir. **Unvandan tahmin yasaktır**."* KAHİN'in kuralı tam tersi: tür
unvandan türetiliyor. KAHİN ürün sahibi kararı olarak uygulanıyor;
D-246/6'nın itirazı ölçümle doğrulandı (11 haneli 124 satırın 101'i
unvanında LTD/A.Ş. taşıyor). Orkestratör bu çelişkiyi karar defterine
yazmalıdır.

**İki farklı "unvan" vardır — karıştırılmaz:**

1. `_UNVAN_GENIS` — "bu kayıt tüzel bir işletme adı taşıyor mu?"
   (`SAN.` `TİC.` `İNŞ.` `MOBİLYA` **dahil**). Şahıs işletmesi
   *elemek* için kullanılır. Ölçülmüş: bu geniş desen olmadan 9412
   firmada yanlışlıkla 2391 unvansız sayılıyordu.
2. `_HUKUKI_FORM` — KAHİN'in 7 türü. Yalnız hukuki tür kalıbı
   (`A.Ş.` `LTD. ŞTİ.` `KOL.` `KOM.` `KOOP.`).

Birincisi "tüzel mi" sorusuna, ikincisi "hangi tür" sorusuna bakar.
Tek bir desenle ikisi birden yapılamaz: `SAN. VE TİC.` tüzel bir limited
şirketin de parçasıdır, unvansız bir esnafın da.

**Ölçüm (canlı Supabase `public.companies`, 9412 firma, 2026-10-02):**

| Desen | Kayıt |
|---|---|
| `A.Ş.` / `AS` | 1513 |
| `LTD` | 4736 |
| `ŞTİ` / `STI` | 4664 |
| `KOL` | 0 |
| `KOM` | 0 |
| `KOOP` | 4 |
| `HOLDİNG` | 1 |
| `VAKIF` | 2 |
| A.Ş. **ve** LTD aynı kayıtta | 5 |
| unvansız | 2742 |
| şahıs işletmesi (isim+soyisim kalıbı) | 1624 |
| **geçerli TCKN taşıyan kayıt** | **0** |

Son satır kritik: KAHİN'in "vergi no kolonunda TC yazıyorsa şahıs
işletmesidir" bacağı bugün **hiçbir kaydı yakalamıyor** — `tax_number`
kolonunda 5 dolu değerin hepsi VKN veya biçimsiz metin. Şahıs işletmesi
tespiti bugün tamamen isim/soyisim kalıbına dayanıyor.
"""
from __future__ import annotations

import re
from typing import Any

from company_master.api.core.normalize import (
    _TRADE_STOP_HARD_FOLDED,
    _TRADE_STOP_SOFT_FOLDED,
)

# --- 1) Geniş unvan (tüzel eleme) ---------------------------------------
#
# KELİME SINIRI ZORUNLU. Sınırsız arama "ARITAS METAL" içindeki "AS"
# kelimesini A.Ş. sayıyordu; unvansız markalar tüzel sanılıyor ve gerçek
# şahıs işletmeleri kaçırılıyordu (2391 → 2742 unvansız).
_UNVAN_GENIS = re.compile(
    r"\b(?:A\.?Ş\.?|A\.?S\.?|LTD\.?|ŞTİ\.?|STI\.?|SAN\.?|TİC\.?|TIC\.?|"
    r"İNŞ\.?|INŞ\.?|KOL\.?|KOM\.?|AO\.?|HOLDİNG|GRUP|ŞİRKETİ|ŞİRKET|"
    r"SIRKETI|SIRKET|MOBİLEYA|MOBILYA)\b",
    re.IGNORECASE,
)

# --- 2) Faaliyet kelimeleri (isim/soyisim kalıbını bozar) ------------------
#
# Sözlük **kanonik olandan** gelir; burada ikinci bir liste yazılmaz (D-211).
# Kaynak: `api/core/normalize.py` → `_TRADE_NAME_STOP_HARD` (52) +
# `_TRADE_NAME_STOP_SOFT` (48). Bu sözlük zaten `extract_trade_name()`
# (tabela ismi) ve `normalize_company_name()` tarafından kullanılıyor;
# aynı kelimeler burada da "marka/faaliyet" sinyalidir.
#
# KAHİN kuralı: **şahıs işletmesinde marka olmaz.** Marka/faaliyet kelimesi
# taşıyan kayıt şahıs işletmesi olamaz. K5 örneği ("ELİM ELEK.") bu
# kuralın ölçülmüş vakasıdır: kısaltma taşıdığı için marka, marka taşıdığı
# için şahıs değil.
#
# ÖLÇÜM (9412 firma, kendi listemle): filtre OLMADAN 1513 kayıt işaretleniyordu
# ve örneklerin bir kısmi markaydı ("ES MAN MERCEDES", "OTO SELIM",
# "SEVGI ABLA RESTAURANT"). Kanonik sözlüğe geçiş sonrası dağılım
# `--dene` ile yeniden ölçülür; kural gövdesi değişmediği için mantık aynı,
# kelime kapsamı kanonikle genişler.
_KISALTMA_VE_FAALIYET = frozenset(
    _TRADE_STOP_HARD_FOLDED | _TRADE_STOP_SOFT_FOLDED
)
# Tam faaliyet kelimeleri — kısaltmaların açık hâlleri.
#
# Neden ayrı: `normalize.py` kendi yorumunda bunu **bilerek** dışlıyor
# ("tam faaliyet kelimeleri bilerek SOFT'ta DEĞİL: tabelanın parçası olarak
# korunurlar"). Çünkü `extract_trade_name()` bunları marka kelimesi olarak
# korumak ister. Buradaki soru **farklıdır**: "şahıs işletmesinde marka
# olmaz" — marka/faaliyet taşıyan kayıt şahıs olamaz. Aynı kelime iki
# yerde iki farklı karara hizmet eder; bu bir ikiz değil, iki ayrı
# sorunun iki ayrı kelime listesidir (D-211 ayrımı).
#
# KAHİN 2026-10-02: *"şahıs işletmelerinde marka olmaz; ELİM ELEK. marka
# var."* K5 örneği: kayıt kısaltma taşıdığı için markadır, marka taşıdığı
# için şahıs işletmesi değildir.
_FAALIYET_KELIME = re.compile(
    r"(MAKİNALARI|MAKİNA|MACHINERY|MACHINA|LOKANTASI|RESTAURANT|"
    r"ARAÇLAR|ARACLAR|EKİPMANLARI|EKIPMANLARI|DÖŞEME|DOSEME|NAZLI|"
    r"ELEKTRİK|ELEKTRIK|GIDA|MOBİLYA|MOBILYA|TEKSTİL|TEKSTIL|"
    r"PLASTİK|PLASTIK|AMBALAJ|PAZAR|MARKET|HIRKAT|DOKUMA|LOKMA|"
    r"LAHİME|LAHIME|BOYA|ENDÜSTRİ|ENDUSTRI|İNŞAAT|INSAAT|"
    r"MÜHENDİSLİK|MUHENDISLIK|MİMARLIK|MIMARLIK|METAL|TURBO|"
    r"İTHALAT|ITHALAT|İHRACAT|IHRACAT|PAZARLAMA|TICARET|TİCARET|"
    r"SANAYI|SANAYİ)",
    re.IGNORECASE,
)
_KISALTMA_DESEN = "|".join(
    sorted((re.escape(k) for k in _KISALTMA_VE_FAALIYET), key=len, reverse=True)
)
_TICARI_KELIME = re.compile(_KISALTMA_DESEN)


def marka_tasiyor_mu(legal_name: str | None) -> bool:
    """Ad içinde marka/faaliyet sinyali var mı? (kısaltma **veya** tam kelime)

    KAHİN kuralı: **şahıs işletmesinde marka olmaz.** Marka taşıyan kayıt
    şahıs işletmesi **değildir**; türü bu yolla `belirsiz` kalır çünkü
    hukuki form (A.Ş./LTD.) ayrı bir sinyal.
    """
    if not legal_name:
        return False
    return bool(
        _TICARI_KELIME.search(legal_name) or _FAALIYET_KELIME.search(legal_name)
    )

# Tasfiye bir hâldir, ayrı bir tür DEĞİLDİR (D-264/3 aynı ilke).
_TASFIYE_ONEKI = re.compile(r"\(\s*İFLAS[^)]*\)\s*|TASFİYE\s*HALİNDE\s*",
                            re.IGNORECASE)

# --- 3) Hukuki form (KAHİN'in 7 türü) ------------------------------------
SAHIS = "sahis_isletmesi"
ANONIM = "anonim_sirket"
LIMITED = "limited_sirket"
KOLEKTIF = "kolektif_sirket"
ADI_KOMANDIT = "adi_komandit_sirket"
PAYLI_KOMANDIT = "payli_komandit_sirket"
KOOPERATIF = "kooperatif"
DIGER = "diger_tur"
BELIRSIZ = "belirsiz"

# Kanonik 7 + istisnalar. KAHİN'in listesi bu sözlükle birebir eşleşir;
# yeni etiket buraya eklenmeden üretimde kullanılmaz.
TURLER = (
    LIMITED, ANONIM, PAYLI_KOMANDIT,
    SAHIS, KOLEKTIF, ADI_KOMANDIT,
    KOOPERATIF, DIGER, BELIRSIZ,
)

# Tür önceliği yukarıdan aşağıya: A.Ş. > Ltd. > Kollektif > Komandit >
# Kooperatif. Çoklu unvanlarda ("A.Ş. ve LTD. ŞTİ.", ölçümde 5 kayıt)
# yüksek tür kazanır.
_HUKUKI_FORM = (
    # A.Ş. **ve** ASCII "A.S." ikisi de kanıttır. İlk yazımda yalnız `Ş`
    # vardı; ölçümde 37 kayıt bu yüzden yanlışlıkla `belirsiz` sayıldı:
    #   `DÖNMEZ ... ANONIM ŞTİ.-ANKARA ŞUBESI`, `... SAN.TİC.AS`
    # Kelime sınırı YETMEZ: `ASLAN` de `A` + `S` ile eşleşir ve 111 kayıt
    # yanlışlıkla anonim_sirket olurdu. Sonrasında harf GELMEMELİ:
    # `A.Ş.` ✓ · `A.S.` ✓ · `TİC.AS` ✓ · `ASLAN` ✗ · `ARITAS` ✗
    (ANONIM, re.compile(r"\bA\.?\s*(?:Ş|S)(?![A-Za-zÇĞİÖŞÜçğıöşü])",
                        re.IGNORECASE)),
    # `ŞTİ` ve `LTD` bitişik yazılabilir: `TELEKOMINIKASYONLTD. ŞTİ.`,
    # `CPS PLASTIK S.T.L.Ş.`, `... LTS. ŞTİ.`. Kelime sınırı burada
    # yanlış negatif üretiyordu; bu iki dizi Türkçe normal kelimelerin
    # içinde **geçmez**, bu yüzden sınırsız aranır (ölçüldü: 37 kayıt).
    (LIMITED, re.compile(r"(?:\bLTD\.?|ŞTİ\.?|STI\.?)(?![A-Za-zÇĞİÖŞÜçğıöşü])",
                         re.IGNORECASE)),
    # Yabancı kayıt: `LLC` = Limited Liability Company = limited şirket
    # (KAHİN 2026-10-02: *"yabancı kayıtlarda llc = limited şirket"*).
    # Kelime sınırı şart: `AL HAKEEM ... LLC FZE` gibi Arapça K3 kayıtları
    # da bu dala girer, ama `ALLC` gibi bitişik yazımlar yanlış pozitif
    # üretmesin diye harf GELMEMELİ.
    (LIMITED, re.compile(r"\bL\.?L\.?C\.?\b(?![A-Za-zÇĞİÖŞÜçğıöşü])",
                         re.IGNORECASE)),
    (KOLEKTIF, re.compile(r"\bKOL\b", re.IGNORECASE)),
    # "ADI KOMANDIT" ayrı bir tür; "PAYLARA BÖLÜNMÜŞ" da ayrı.
    # Sıra önemli: önce özel payıllar, sonra genel KOM.
    (PAYLI_KOMANDIT,
     re.compile(r"(PAYLAR[AA].*BÖLÜNMÜŞ|BÖLÜNMÜŞ\s*KOMANDİT)", re.IGNORECASE)),
    (ADI_KOMANDIT,
     re.compile(r"(ADI\s*KOMANDİT|ADI\s*KOMANDIT|\bKOM\b)", re.IGNORECASE)),
    (KOOPERATIF, re.compile(r"KOOPERATİF|KOOPERATIF|\bKOOP\b", re.IGNORECASE)),
)

# KAHİN'in 7'sine girmeyen ama gerçek kayıtlar (ölçüm: 1 holding, 2 vakıf).
# Bunları `belirsiz` saymak bilgi kaybı olurdu; ayrı tutulur.
_DIGER_FORM = re.compile(r"HOLDİNG|VAKIF|VAKIF|DERNEK|GRUP", re.IGNORECASE)


def _ascii_harf(k: str) -> str:
    """Türkçe büyük harf → ASCII harf (karşılaştırma için)."""
    return (
        k.replace("Ç", "C").replace("Ğ", "G").replace("İ", "I")
        .replace("Ö", "O").replace("Ş", "S").replace("Ü", "U")
    )


def tc_gecerli_mi(deger: str | None) -> bool:
    """TCKN sağlama toplamı doğrulanmış mı?

    D-246/5: 11 hane olmak TCKN olmak **değildir** — 124 satırın 122'si
    doğru uzunlukta ama toplamı tutmuyor.

    Düzeltme kaydı: ilk yazımda 10. hane hem "çift konum" toplamının
    içine hem doğrulanacak haneye sayılıyordu; gerçek bir TCKN
    (`10000000146`) reddediliyordu. 10. hane toplamın **dışında**,
    yalnız doğrulanacak hanedir.
    """
    s = (deger or "").strip()
    if len(s) != 11 or not s.isdigit() or s[0] == "0":
        return False
    d = [int(c) for c in s]
    tek_konum = d[0] + d[2] + d[4] + d[6] + d[8]   # 1.,3.,5.,7.,9. haneler
    cift_konum = d[1] + d[3] + d[5] + d[7]          # 2.,4.,6.,8. haneler
    if (7 * tek_konum + cift_konum) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def unvani_var(legal_name: str | None) -> bool:
    """Kayıt tüzel işletme unvanı taşıyor mu? (geniş desen)

    Şahıs işletmesi elemesinde kullanılır. `SAN.`/`TİC.`/`İNŞ.` de
    dahildir — bunlar olmadan unvansız markalar şahıs sanılır.
    """
    return bool(legal_name) and bool(_UNVAN_GENIS.search(legal_name))


def isim_soyisim_kalibi(legal_name: str | None) -> bool:
    """Unvansız isim "İSİM SOYİSİM" kalıbında mı?

    2-4 kelime, hepsi alfabetik, rakam/işaret yok, faaliyet kelimesi
    içermez. **Kesin kimlik tespiti DEĞİLDİR.** Kişi adı sözlüğü
    kullanılmaz: sözlük kazıyıcının yazım biçimine bağlanır ve nedeni
    kaybolur (D-245 kaynak sızıntısı).
    """
    if not legal_name or marka_tasiyor_mu(legal_name):
        return False
    kelimeler = legal_name.split()
    if not (2 <= len(kelimeler) <= 4):
        return False
    return all(k.isupper() and _ascii_harf(k).isalpha() for k in kelimeler)


def kisi_adi_basi_mi(legal_name: str | None) -> bool:
    """Adın **sol tarafı** gerçek kişi adı mı? ("İSİM SOYİSİM - MARKA")

    KAHİN'in kuralı: şahıs işletmesinde `LTD/ŞTİ/A.Ş.` **geçmez**.
    Ölçümde bu kalıp `belirsiz` havuzunun en büyük parçası — 928 kayıt.
    Örnekler: `ABDULLAH ÖZBEK-ÖZBEK İŞ MAKINELERI`,
    `NURETTIN ACAR-UNI METAL`, `BAŞAK CANBOLAT-BİRLİK OTO`.

    **Neden ayrı fonksiyon:** `isim_soyisim_kalibi()` tüm adı ister; bu
    adlarda sağ taraf markadır (`ÖZBEK İŞ MAKINELERI`, `BİRLİK OTO`) ve
    2-4 kelime + alfabetiklik kuralını kırar. Sol taraf ayrı bir
    *ölçülebilir* sinyal — kişi adı sözlüğü gerekmez (D-245).

    **Yanlış-pozitif kontrolü:** `312 WEB TASARIM - ANKARA WEB TASARIM`
    sol tarafı `312 WEB TASARIM` — rakam içerdiği için **reddedilir**.
    Yani "tire var" demek yetmez, sol taraf gerçekten kişi adı olmalıdır.
    """
    if not legal_name:
        return False
    sol = re.split(r"\s*[-–—]\s*", legal_name.strip(), maxsplit=1)[0]
    # Faaliyet kelimesi filtresi sol tarafa da uygulanır. Ölçülmüş vaka:
    # "DOĞUŞ İŞ MAKİNALARI", "KARDEŞLER LOKANTASI", "OTO SELİM",
    # "YAVUZLAR SONDAJ EKIPMANLARI" — hepsi 2-3 kelime + alfabetik, yani
    # kalıba uyar ama markadır, kişi değil. Filtre bunları eliyordu;
    # sol-yanı dalı filtresiz kalırsa geri gelirlerdi (mandal kırmızı
    # yakaladı: 4 test).
    if marka_tasiyor_mu(sol):
        return False
    kelimeler = [k for k in sol.split() if k]
    if not (2 <= len(kelimeler) <= 4):
        return False
    return all(k.isupper() and _ascii_harf(k).isalpha() for k in kelimeler)


def sahis_isletmesi_mi(row: dict[str, Any]) -> bool:
    """KAHİN'in şahıs işletmesi tanımı (tespit, karar değil).

    **TC ÖNCELİKLİDİR (KAHİN 2026-10-02):** *"vergi no eğer tc no ise kesin
    şahıs işletmesidir."* Bu **kesin** bir kuraldır; unvan elemesi onu
    geçersiz kılamaz. Sıralama önemlidir — TC kontrolü `unvani_var()`
    denetiminin **önüne** geçer. Şahıs işletmesi vergi numarası yerine
    TCKN taşır (D-248/1), dolayısıyla TC taşıyan kayıt tüzel olamaz.

    Sonrasında sıra: geniş unvan elemesi → isim soyisim kalıbı → sol-yanı
    kişi adı. İkinci dalda marka/faaliyet kelimesi taşıyan kayıt elenir
    (KAHİN: *"şahıs işletmelerinde marka olmaz"*).

    Canlı ölçüm (9412 firma, 2026-10-02):
      - geçerli TCKN taşıyan kayıt: **0** → bu bacağı bugün boş, ama
        kural yazılıdır; veri geldiğinde devreye girer.
      - isim soyisim kalıbı: 1618
      - sol-yanı kişi adı: 928
    """
    ad = str(row.get("legal_name") or "").strip()
    if not ad:
        return False
    # Kesin kural: geçerli TCKN varsa şahıs işletmesidir — unvan olsa bile.
    if tc_gecerli_mi(row.get("tax_number")):
        return True
    if unvani_var(ad):
        return False
    if isim_soyisim_kalibi(ad):
        return True
    return kisi_adi_basi_mi(ad)


def isimli_tireli_kayit_mi(legal_name: str | None) -> bool:
    """K2 kalıbı: "İSİM SOYİSİM - MARKA" (ölçümde 155 kayıt).

    KAHİN 2026-10-02: *"k2 limited ama isimli olabilir."* Sol taraf gerçek
    kişi adı biçiminde (2-4 büyük alfabetik kelime), sağ taraf marka
    taşıyor. **Marka varsa şahıs işletmesi değildir** (aynı KAHİN kuralı);
    KAHİN bu grubu limited olarak etiketledi.

    Koşullar üçü birden (tek biri yeterli değil):
      1. tam ortada tire var,
      2. sol taraf kişi adı biçiminde,
      3. sağ taraf marka/faaliyet taşıyor.
    Üçü birden tutmazsa `belirsiz` kalır — tahmin, kanıt değildir.
    """
    if not legal_name:
        return False
    parcalar = [p for p in legal_name.split("-") if p and p.strip()]
    if len(parcalar) != 2:
        return False
    sol, sag = parcalar[0].strip(), parcalar[1].strip()
    if not marka_tasiyor_mu(sag):
        return False
    kelimeler = [k for k in sol.split() if k]
    if not (2 <= len(kelimeler) <= 4):
        return False
    return all(k.isupper() and _ascii_harf(k).isalpha() for k in kelimeler)


def firma_turu(legal_name: str | None) -> str:
    """Hukuki tür etiketi — KAHİN'in 7'si + `diger_tur` + `belirsiz`.

    Tasfiye öneki ("(İFLAS NEDENİYLE) TASFİYE HALİNDE ...") türü
    **değiştirmez**: tasfiye bir hâldir, ayrı bir tür değildir.
    """
    ad = (legal_name or "").strip()
    if not ad:
        return BELIRSIZ
    temiz = _TASFIYE_ONEKI.sub(" ", ad)
    for etiket, desen in _HUKUKI_FORM:
        if desen.search(temiz):
            return etiket
    if not unvani_var(temiz) and (
        isim_soyisim_kalibi(temiz) or kisi_adi_basi_mi(temiz)
    ):
        return SAHIS
    # `diger_tur` K2'den ÖNCE gelir: holding/vakıf/dernek gibi TTK dışı
    # kayıtlar da tireli olabiliyor; aksi halde "X HOLDİNG" limited sayılırdı
    # (ölçüldü: 6 kayıt). Açık form, kalıp tahmininden güçlüdür.
    if _DIGER_FORM.search(temiz):
        return DIGER
    # K2: isimli + tireli + markalı -> limited (KAHİN kararı).
    if isimli_tireli_kayit_mi(temiz):
        return LIMITED
    return BELIRSIZ


def kvkk_kapsaminda(
    row: dict[str, Any], *, tax_number: str | None = None
) -> bool:
    """Kayıt KVKK kapsamında mı?

    İki ayrı olgu:
      1. Şahıs işletmesi — doğrudan bir gerçek kişidir.
      2. Vergi no kolonunda geçerli TC taşıyan **tüzel** kayıt — limited
         şirket bile TC taşıyabilir; hukuki türü değişmez ama KVKK
         kapsamındadır.

    `tax_number` parametresi ayrıdır: çağıran gövde kolonu okumak
    zorunda kalmaz (D-246/3 tek kapı).
    """
    if sahis_isletmesi_mi(row):
        return True
    return tc_gecerli_mi(
        tax_number if tax_number is not None else row.get("tax_number")
    )


def etiket_dagilimi(rows) -> dict[str, int]:
    """Etiket dağılımı — raporların ölçüm kaynağı.

    D-267/8: gerçek bir test `return` eden sayı döndürmez, `assert` eder.
    Bu fonksiyon yalnız **ölçüm** içindir; testler sabitleri `assert` eder.
    """
    dagilim: dict[str, int] = {}
    for row in rows:
        t = firma_turu(row.get("legal_name"))
        dagilim[t] = dagilim.get(t, 0) + 1
    return dagilim
