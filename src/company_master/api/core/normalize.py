# -*- coding: utf-8 -*-
"""API Normalization & KVKK Masking Module.

From web_app.py extract (API-SPLIT-01):
- _tr_insensitive, _tr_rx_key, _tr_rx, _tr_rx_soft_end
- _clean_double_dots, _mask_email, _mask_phone, apply_kvkk_mask, _mask_active
- normalize_company_name, _trade_is_stop, extract_trade_name, normalize_company, tr_normalize
"""
from __future__ import annotations

import os
import re as _re
import unicodedata
from typing import Any, Final

DASH_MASK_PII = os.getenv("DASH_MASK_PII", "0").strip() == "1"

_TR_INSENSITIVE_CLS = {
    "I": "[İI]",
    "C": "[ÇC]",
    "G": "[ĞG]",
    "O": "[ÖO]",
    "U": "[ÜU]",
    "S": "[ŞS]",
}




def _tr_insensitive(escaped: str) -> str:
    """_re.escape() sonrasi pattern'i Turkce harf duyarsiz yapar."""
    out = []
    i = 0
    while i < len(escaped):
        ch = escaped[i]
        if ch == "\\" and i + 1 < len(escaped):
            out.append(escaped[i : i + 2])
            i += 2
            continue
        out.append(_TR_INSENSITIVE_CLS.get(ch, ch))
        i += 1
    return "".join(out)


def _tr_rx_key(phrase: str) -> str:
    """Sozluk anahtari icin regex.

    Kendi noktasiyla biten anahtarlar (TIC., ITH. ...) icin sondaki
    (?![\\w.]) bakisi KOYULMAZ: 'TIC.LTD.' gibi bitisik zincirlerde
    anahtarin noktasindan sonraki harf eslesmeyi engelliyordu.
    """
    pat = r"(?<!\w)" + _tr_insensitive(_re.escape(phrase))
    return pat if phrase.endswith(".") else pat + r"(?![\w.])"


def _tr_rx(phrase: str) -> str:
    """Kelime sinirlu + Turkce duyarsiz regex uretir (nokta dahil engel)."""
    return r"(?<!\w)" + _tr_insensitive(_re.escape(phrase)) + r"(?![\w.])"


def _tr_rx_soft_end(phrase: str) -> str:
    """Turkce duyarsiz + basi kelime sinirli; sonda sadece harf engellenir.
    Nokta ile biten combo anahtarlari (r'SAN VE TIC') icin gerekli."""
    return r"(?<!\w)" + _tr_insensitive(_re.escape(phrase)) + r"(?!\w)"


# Standart Kısaltmalar Sozlugu — kaynak: AI proje v1/V10/09_kurallar_ve_promptlar/
# 11_unvan_kisaltma_ve_tabela_kurallari.md (Bolum 2). Degerler Turkce karakterlidir.
# ANAHTARLAR ASCII (upper() sonrasi); _tr_insensitive sayesinde İ/ı varyantlari da eslesir.
_COMPANY_TYPE_ABBR = {
    "ANONIM SIRKETI": "A.Ş.",
    "ANONIM SIRKET": "A.Ş.",
    "ANONIM ORTAKLIK": "A.Ş.",
    "ANONIM ORTAKLIGI": "A.Ş.",
    "LIMITED SIRKETI": "LTD. ŞTİ.",
    "LIMITED SIRKET": "LTD. ŞTİ.",
    "LTD. SIRKETI": "LTD. ŞTİ.",
    "LTD. SIRKET": "LTD. ŞTİ.",
    "LIMITED": "LTD. ŞTİ.",
    "LTD": "LTD.",
    "LTD.": "LTD.",
    "STI.": "ŞTİ.",
    "STI": "ŞTİ.",
    "ŞTI.": "ŞTİ.",
    "ŞTI": "ŞTİ.",
    "SIRKETI": "ŞTİ.",
    "SIRKET": "ŞTİ.",
    "KOLLEKTIF SIRKETI": "KOL. ŞTİ.",
    "KOLLEKTIF SIRKET": "KOL. ŞTİ.",
    "KOMANDIT SIRKETI": "KOM. ŞTİ.",
    "KOMANDIT SIRKET": "KOM. ŞTİ.",
    "ORTAKLIK": "ORT.",
    "ORTAKLIGI": "ORT.",
    "ADI ORTAKLIK": "ORT.",
    "ADI ORTAKLIGI": "ORT.",
    "TURK ANONIM SIRKETI": "TAŞ",
    "TURK ANONIM ORTAKLIK": "TAŞ",
    "TURK ANONIM ORTAKLIGI": "TAO",
    "KOOPERATIF": "KOOP.",
    # Eski DB formu ASCII A.S. -> Turkce A.Ş. (canli veri regresyonu)
    "A.S.": "A.Ş.",
    "A.S": "A.Ş.",
}

_ACTIVITY_ABBR = {
    "SANAYI": "SAN.",
    "SANAYII": "SAN.",
    "TICARET": "TİC.",
    "TICARETI": "TİC.",
    "PAZARLAMA": "PAZ.",
    "ITHALAT": "İTH.",
    "IHRACAT": "İHR.",
    "MUHENDISLIK": "MÜH.",
    "MUHENDIS": "MÜH.",
    "MIMARLIK": "MİM.",
    "MIMAR": "MİM.",
    "INSAAT": "İNŞ.",
    "INSAATI": "İNŞ.",
    "INSAA": "İNŞ.",
    "INS.": "İNŞ.",
    "INS": "İNŞ.",
    "İNŞ.": "İNŞ.",
    "İNŞ": "İNŞ.",
    "NAKLIYAT": "NAK.",
    "NAKLIYE": "NAK.",
    "TASICILIK": "NAK.",
    "OTOMOTIV": "OTO.",
    "OTOMOBIL": "OTO.",
    "TURIZM": "TUR.",
    "TEKSTIL": "TEK.",
    "GIDA": "GIDA",
    "HIZMET": "HİZM.",
    "HIZMETLERI": "HİZM.",
    "TARIM": "TAR.",
    "TARIMSAL": "TAR.",
    "MADENCILIK": "MAD.",
    "MADEN": "MAD.",
    "IMALAT": "İMAL.",
    "BILISIM": "BİL.",
    "BILGISAYAR": "BİL.",
    "YAZILIM": "YAZ.",
    "MAKINE": "MAK.",
    "MAKINA": "MAK.",
    "MOBILYA": "MOB.",
    "ELEKTRIK": "ELEK.",
    "ELEKTRONIK": "ELEK.",
    "KIMYA": "KİM.",
    "KIMYAVI": "KİM.",
    "IMALATCI": "İMAL.",
    "IMALATCISI": "İMAL.",
    # Eski DB formlari (noktali ASCII) -> Turkce standart (2026-09-09 canli veri regresyonu)
    "TIC.": "TİC.",
    "TIC": "TİC.",
    "ITH.": "İTH.",
    "ITH": "İTH.",
    "IHR.": "İHR.",
    "IHR": "İHR.",
    "MUH.": "MÜH.",
    "MUH": "MÜH.",
    "MIM.": "MİM.",
    "MIM": "MİM.",
    "HIZM.": "HİZM.",
    "HIZM": "HİZM.",
    "IMAL.": "İMAL.",
    "IMAL": "İMAL.",
    "BIL.": "BİL.",
    "BIL": "BİL.",
    "KIM.": "KİM.",
    "KIM": "KİM.",
}

# Ozel kombinasyonlar (kaynak dokuman Bolum 2.3)
_COMBO_ABBR = {
    "SANAYI VE TICARET": "SAN. VE TİC.",
    "SANAYII VE TICARETI": "SAN. VE TİC.",
    "TICARET VE SANAYI": "TİC. VE SAN.",
    "TICARETI VE SANAYII": "TİC. VE SAN.",
    "ITHALAT VE IHRACAT": "İTH. İHR.",
    "IHRACAT VE ITHALAT": "İHR. İTH.",
    "INSAAT SANAYI VE TICARET": "İNŞ. SAN. TİC.",
    "MUHENDISLIK MIMARLIK": "MÜH. MİM.",
    "TURIZM VE TICARET": "TUR. TİC.",
    "GIDA SANAYI VE TICARET": "GIDA SAN. TİC.",
    "TEKSTIL SANAYI VE TICARET": "TEK. SAN. TİC.",
    "NAKLIYAT VE TICARET": "NAK. TİC.",
    "SAN VE TIC": "SAN. TİC.",
    "SAN VE TICARET": "SAN. TİC.",
    "TIC VE SAN": "TİC. SAN.",
    "TICARET VE SAN": "TİC. SAN.",
    "MAK VE IMAL": "MAK. İMAL.",
    "MAKINA VE IMALAT": "MAK. İMAL.",
    "INS VE TIC": "İNŞ. TİC.",
    "INSAAT VE TICARET": "İNŞ. TİC.",
}

# Şirket türü/faaliyet kelimeleri (tabela ismi için filtrelenecek)
_TRADE_NAME_STOP_WORDS = frozenset(
    {
        "VE",
        "ILE",
        "BI",
        "AMMA",
        "LAKIK",
        "SAN.",
        "SAN",
        "SANAYI",
        "SANAYII",
        "TIC.",
        "TIC",
        "TICARET",
        "TICARETI",
        "LTD. ŞTI.",
        "LTD. STI.",
        "LTD.",
        "LTD",
        "A.S.",
        "A.S",
        "A.Ş.",
        "A.Ş",
        "STI.",
        "STI",
        "ŞTI.",
        "ŞTI",
        "ORT.",
        "ORT",
        "KOL. ŞTI.",
        "KOM. ŞTI.",
        "KOOP.",
        "PAZ.",
        "PAZ",
        "ITH.",
        "ITH",
        "IHR.",
        "IHR",
        "MUH.",
        "MUH",
        "MIM.",
        "MIM",
        "İNŞ.",
        "INS.",
        "INS",
        "INŞ",
        "NAK.",
        "NAK",
        "OTO.",
        "OTO",
        "TUR.",
        "TUR",
        "TEK.",
        "TEK",
        "HIZM.",
        "HIZM",
        "TAR.",
        "TAR",
        "MAD.",
        "MAD",
        "IMAL.",
        "IMAL",
        "BIL.",
        "BIL",
        "YAZ.",
        "YAZ",
        "MAK.",
        "MAK",
        "MOB.",
        "MOB",
        "ELEK.",
        "ELEK",
        "KIM.",
        "KIM",
        "GIDA",
        "GID",
        "GIDA.",
        "KOOP",
        "TAS",
        "TAO",
        "DTM",
        "KOBI",
    }
)


def _clean_double_dots(name: str) -> str:
    """Cift noktalari temizle (LTD. STI..STI. -> LTD. STI.)"""
    while ".." in name:
        name = name.replace("..", ".")
    return name


# â”€â”€ KVKK PII maskeleme yardimcileri (Y7) â”€â”€
def _mask_email(email) -> str:
    """ahmet@gmail.com -> ah***@gmail.com (KVKK veri minimizasyonu)."""
    if not email or "@" not in str(email):
        return email
    local, _, domain = str(email).partition("@")
    if not local:
        return f"***@{domain}"
    return f"{local[:2]}***@{domain}"


def _mask_phone(phone) -> str:
    """0 532 123 45 67 -> 053***67 (ilk 3 + son 2 hane)."""
    if not phone:
        return phone
    phone = str(phone)
    digits = _re.sub(r"\D", "", phone)
    if len(digits) >= 8:
        return f"{digits[:3]}***{digits[-2:]}"
    return f"{digits[:2]}***" if digits else "***"


def apply_kvkk_mask(row: dict) -> dict:
    """PII alanlari maskeler. Politika: telefon + e-posta maskeli;
    firma unvani/web/VKN kamuya acik sayilir (PO karari 2026-09-01)."""
    if not isinstance(row, dict):
        return row
    if row.get("primary_phone"):
        row["primary_phone"] = _mask_phone(row["primary_phone"])
    if row.get("primary_email"):
        row["primary_email"] = _mask_email(row["primary_email"])
    return row


def _mask_active(mask_param: int = 0) -> bool:
    """Maskeleme aktif mi: env (DASH_MASK_PII=1) Veya istek ?mask=1."""
    return DASH_MASK_PII or mask_param == 1


def normalize_company_name(name) -> str:
    """Firma adini BUYUK HARFE cevirir ve standart kisaltilari uygular."""
    if not name:
        return ""
    name = str(name).upper().strip()
    name = _re.sub(r"\s{2,}", " ", name)

    # Oncelikle en uzun eslesmeleri bulmak icin key length'e gore sirala
    for long_phrase, short_form in sorted(
        _COMBO_ABBR.items(), key=lambda x: -len(x[0])
    ):
        name = _re.sub(_tr_rx_soft_end(long_phrase), short_form, name)

    # Ayri sozcukleri kisaltil (zaten kisaltilmis olanlari tekrar degistirme)
    # Noktali anahtarlar _tr_rx_key ile bitisik zincirlerde de eslesir (TIC.LTD.)
    for long_phrase, short_form in sorted(
        _ACTIVITY_ABBR.items(), key=lambda x: -len(x[0])
    ):
        name = _re.sub(_tr_rx_key(long_phrase), short_form, name)

    for long_phrase, short_form in sorted(
        _COMPANY_TYPE_ABBR.items(), key=lambda x: -len(x[0])
    ):
        name = _re.sub(_tr_rx_key(long_phrase), short_form, name)

    name = _re.sub(r"\s{2,}", " ", name).strip()
    name = _clean_double_dots(name)
    # STI.STI. gibi tekrarlanan kisaltilari temizle
    name = _re.sub(r"(\b\w+\.)\s*\1", r"\1", name)
    return name


# Tabela ismi icin iki katmanli stop-word:
#   HARD  -> her zaman cikar (sirket turu, baglaclar, SAN/TIC)
#   SOFT  -> faaliyet kelimeleri; yalnizca baska marka kelimesi varken cikar
_TRADE_NAME_STOP_HARD = frozenset(
    {
        "VE",
        "ILE",
        "BI",
        "AMMA",
        "LAKIK",
        "SAN.",
        "SAN",
        "SANAYI",
        "SANAYII",
        "TIC.",
        "TIC",
        "TICARET",
        "TICARETI",
        "IC",
        "DIS",
        "LTD. ŞTI.",
        "LTD. STI.",
        "LTD.",
        "LTD",
        "LIMITED",
        "LIM.",
        "LIM",
        "A.S.",
        "A.S",
        "A.Ş.",
        "A.Ş",
        "STI.",
        "STI",
        "ŞTI.",
        "ŞTI",
        "SIRKETI",
        "SIRKET",
        "ANONIM",
        "ANONIM ŞIRKETI",
        "ORT.",
        "ORT",
        "ORTAKLIK",
        "KOL. ŞTI.",
        "KOM. ŞTI.",
        "KOOP.",
        "KOOP",
        "KOLLEKTIF",
        "KOMANDIT",
        "TAS",
        "TAO",
        "DTM",
        "KOBI",
    }
)
# SOFT: yalnizca KISALTMALAR (ELEK., INŞ., MAK. vb.) — tam faaliyet kelimeleri
# (ELEKTRIK, INSAAT, MOBILYA...) bilerek SOFT'ta DEGIL: tabelanin parcasi
# olarak korunurlar. Ornek: "DÜNDAR ELEKTRİK SANAYİ" -> "DÜNDAR ELEKTRİK"
_TRADE_NAME_STOP_SOFT = frozenset(
    {
        "PAZ.",
        "PAZ",
        "ITH.",
        "ITH",
        "IHR.",
        "IHR",
        "MUH.",
        "MUH",
        "MIM.",
        "MIM",
        "İNŞ.",
        "INS.",
        "INS",
        "INŞ",
        "NAK.",
        "NAK",
        "OTO.",
        "OTO",
        "TUR.",
        "TUR",
        "TEK.",
        "TEK",
        "HIZM.",
        "HIZM",
        "TAR.",
        "TAR",
        "MAD.",
        "MAD",
        "IMAL.",
        "IMAL",
        "BIL.",
        "BIL",
        "YAZ.",
        "YAZ",
        "MAK.",
        "MAK",
        "MOB.",
        "MOB",
        "ELEK.",
        "ELEK",
        "KIM.",
        "KIM",
        "GIDA.",
        "GID.",
    }
)
# Turkce duyarsiz karsilastirma icin fold map
_TRADE_FOLD_MAP = str.maketrans(
    {"İ": "I", "I": "I", "Ş": "S", "Ğ": "G", "Ü": "U", "Ö": "O", "Ç": "C", "ı": "I"}
)
_TRADE_STOP_HARD_FOLDED = frozenset(
    w.translate(_TRADE_FOLD_MAP) for w in _TRADE_NAME_STOP_HARD
)
_TRADE_STOP_SOFT_FOLDED = frozenset(
    w.translate(_TRADE_FOLD_MAP) for w in _TRADE_NAME_STOP_SOFT
)


def _trade_is_stop(word: str, stop_folded: frozenset) -> bool:
    return word.translate(_TRADE_FOLD_MAP) in stop_folded


def extract_trade_name(legal_name: str) -> str:
    """Uzun sirket adindan tabela ismini (marka/ilgi alanini) cikarir.

    Kural 3: Kisaltma UYGULANMAMIS buyuk harf formdan; sirket turu, baglac
    ve SAN/TIC (HARD) her zaman; kisaltma faaliyet kelimeleri (SOFT) marka
    kelimesi varken atlanir. Kalan ilk 2 kelime alinir.
    Ornekler:
        "DÜNDAR ELEKTRİK SANAYİ"            -> "DÜNDAR ELEKTRİK"
        "ARITES METAL SANAYI VE TICARET..." -> "ARITES METAL"
        "GIDA SANAYI VE TICARET A.Ş."       -> "GIDA"
        "BUYUK AGAC MOB.INS.SAN. VE TIC..." -> "BUYUK AGAC"
        "ZMT PTO HIDROLIK"                  -> "ZMT PTO"
    """
    if not legal_name:
        return ""
    raw = _re.sub(r"\s{2,}", " ", str(legal_name).upper().strip())
    words = [w for w in _re.split(r"[\s.]+", raw) if w]

    full = [
        w
        for w in words
        if len(w) > 1
        and not _trade_is_stop(w, _TRADE_STOP_HARD_FOLDED)
        and not _trade_is_stop(w, _TRADE_STOP_SOFT_FOLDED)
    ]
    if full:
        return " ".join(full[:2])

    # Tum kelimeler HARD/SOFT'a carpti -> HARD disi (faaliyet) ilk kelimeyi marka yap
    hard_kept = [
        w
        for w in words
        if len(w) > 1 and not _trade_is_stop(w, _TRADE_STOP_HARD_FOLDED)
    ]
    if hard_kept:
        return hard_kept[0]

    # Son care: sadece baglaclari at, ilk iki kelimeyi ver
    minimal = [
        w
        for w in words
        if w.translate(_TRADE_FOLD_MAP) not in ("VE", "ILE") and len(w) > 1
    ]
    return " ".join(minimal[:2]) if minimal else raw


def normalize_company(row: dict) -> dict:
    """Bir firma satirina ad normalizasyon kurallarini uygular."""
    if not row:
        return row
    # legal_name -> kisaltilmis BUYUK HARF
    if row.get("legal_name"):
        row["legal_name"] = normalize_company_name(row["legal_name"])
    # trade_name -> Kural 3: tabela ismi HER ZAMAN unvandan (legal_name)
    # uretilir; eski/kısmi trade_name degerleri guncellenir. legal_name
    # bos ise mevcut trade_name kaynak olarak kullanilir.
    source = row.get("legal_name") or row.get("trade_name") or ""
    row["trade_name"] = extract_trade_name(source)
    return row


# â”€â”€ Turkce case-insensitive arama destegi â”€â”€
# PostgreSQL LOWER() Turkce karakterleri dogru kucultmez (I->i, ama İ->i degil).
# Bu yuzden arama terimini ve karsilastirma alanlarini ASCII'ye yaklastiriyoruz.
_TR_LOWER_MAP = str.maketrans(
    {
        "İ": "i",
        "I": "i",
        "Ş": "s",
        "Ğ": "g",
        "Ü": "u",
        "Ö": "o",
        "Ç": "c",
        "ş": "s",
        "ğ": "g",
        "ü": "u",
        "ö": "o",
        "ç": "c",
        "ı": "i",
        "İ": "i",
    }
)


def tr_normalize(s: str) -> str:
    """Turkce karakterleri ASCII'ye cevirir + kucuk harf yapar.
    Ornek: 'ARITES' -> 'arites', 'Arıtes' -> 'arites', 'DÜNDAR' -> 'dundar'
    """
    if not s:
        return ""
    return s.translate(_TR_LOWER_MAP).lower()


