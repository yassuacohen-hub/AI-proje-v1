#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""FastAPI backend - Company Master Web Dashboard API (SQLite-uyumlu)."""
from __future__ import annotations

import os
import uuid
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from company_master.orchestrator import task_board as tb

# Query profiler
import time as _perf_time
_DB_TIME_MS = 0.0
_CACHE_HITS = 0
_CACHE_MISSES = 0
_QUERY_COUNT = 0
_QUERY_TIMES = []

def _profile_query(name, fn):
    global _DB_TIME_MS, _QUERY_COUNT
    start = _perf_time.perf_counter()
    result = fn()
    elapsed_ms = (_perf_time.perf_counter() - start) * 1000
    _DB_TIME_MS += elapsed_ms
    _QUERY_COUNT += 1
    _QUERY_TIMES.append({'name': name, 'ms': round(elapsed_ms, 2)})
    return result

# ── ANA KURAL: Firma ad normalizasyonu (V10/09_kurallar_ve_promptlar/11_unvan_kisaltma_ve_tabela_kurallari) ──
# Kural 1: Firma adlari her zaman BUYUK HARFLE yazilir
# Kural 2: Uzun ifadeler standart kisaltilir (SANAYİ VE TİCARET → SAN. VE TİC.)
# Kural 3: Tabela ismi = ilgi alanı/marka (ilk 2-3 kelime, VE/Şirket Turu/Faaliyet filtrelenerek)

import re as _re

# Turkce duyarsiz eslesme: kural 2 kisaltmalari ASCII tanimli; girdideki
# Turkce harfler (I noktali/ciftesleri) de eslesmeli.
_TR_INSENSITIVE_CLS = {'I': '[İI]', 'C': '[ÇC]', 'G': '[ĞG]', 'O': '[ÖO]', 'U': '[ÜU]', 'S': '[ŞS]'}


def _tr_insensitive(escaped: str) -> str:
    """_re.escape() sonrasi pattern'i Turkce harf duyarsiz yapar."""
    out = []
    i = 0
    while i < len(escaped):
        ch = escaped[i]
        if ch == '\\' and i + 1 < len(escaped):
            out.append(escaped[i:i + 2])
            i += 2
            continue
        out.append(_TR_INSENSITIVE_CLS.get(ch, ch))
        i += 1
    return ''.join(out)


def _tr_rx_key(phrase: str) -> str:
    """Sozluk anahtari icin regex.

    Kendi noktasiyla biten anahtarlar (TIC., ITH. ...) icin sondaki
    (?![\\w.]) bakisi KOYULMAZ: 'TIC.LTD.' gibi bitisik zincirlerde
    anahtarin noktasindan sonraki harf eslesmeyi engelliyordu.
    """
    pat = r'(?<!\w)' + _tr_insensitive(_re.escape(phrase))
    return pat if phrase.endswith('.') else pat + r'(?![\w.])'


def _tr_rx(phrase: str) -> str:
    """Kelime sinirlu + Turkce duyarsiz regex uretir (nokta dahil engel)."""
    return r'(?<!\w)' + _tr_insensitive(_re.escape(phrase)) + r'(?![\w.])'


def _tr_rx_soft_end(phrase: str) -> str:
    """Turkce duyarsiz + basi kelime sinirli; sonda sadece harf engellenir.
    Nokta ile biten combo anahtarlari (r'SAN VE TIC') icin gerekli."""
    return r'(?<!\w)' + _tr_insensitive(_re.escape(phrase)) + r'(?!\w)'


# Standart Kısaltmalar Sozlugu — kaynak: AI proje v1/V10/09_kurallar_ve_promptlar/
# 11_unvan_kisaltma_ve_tabela_kurallari.md (Bolum 2). Degerler Turkce karakterlidir.
# ANAHTARLAR ASCII (upper() sonrasi); _tr_insensitive sayesinde İ/ı varyantlari da eslesir.
_COMPANY_TYPE_ABBR = {
    'ANONIM SIRKETI': 'A.Ş.', 'ANONIM SIRKET': 'A.Ş.', 'ANONIM ORTAKLIK': 'A.Ş.',
    'ANONIM ORTAKLIGI': 'A.Ş.', 'LIMITED SIRKETI': 'LTD. ŞTİ.', 'LIMITED SIRKET': 'LTD. ŞTİ.',
    'LTD. SIRKETI': 'LTD. ŞTİ.', 'LTD. SIRKET': 'LTD. ŞTİ.', 'LIMITED': 'LTD. ŞTİ.',
    'LTD': 'LTD.', 'LTD.': 'LTD.', 'STI.': 'ŞTİ.', 'STI': 'ŞTİ.',
    'ŞTI.': 'ŞTİ.', 'ŞTI': 'ŞTİ.', 'SIRKETI': 'ŞTİ.', 'SIRKET': 'ŞTİ.',
    'KOLLEKTIF SIRKETI': 'KOL. ŞTİ.', 'KOLLEKTIF SIRKET': 'KOL. ŞTİ.',
    'KOMANDIT SIRKETI': 'KOM. ŞTİ.', 'KOMANDIT SIRKET': 'KOM. ŞTİ.',
    'ORTAKLIK': 'ORT.', 'ORTAKLIGI': 'ORT.', 'ADI ORTAKLIK': 'ORT.', 'ADI ORTAKLIGI': 'ORT.',
    'TURK ANONIM SIRKETI': 'TAŞ', 'TURK ANONIM ORTAKLIK': 'TAŞ', 'TURK ANONIM ORTAKLIGI': 'TAO', 'KOOPERATIF': 'KOOP.',
    # Eski DB formu ASCII A.S. -> Turkce A.Ş. (canli veri regresyonu)
    'A.S.': 'A.Ş.', 'A.S': 'A.Ş.',
}

_ACTIVITY_ABBR = {
    'SANAYI': 'SAN.', 'SANAYII': 'SAN.', 'TICARET': 'TİC.', 'TICARETI': 'TİC.',
    'PAZARLAMA': 'PAZ.', 'ITHALAT': 'İTH.', 'IHRACAT': 'İHR.',
    'MUHENDISLIK': 'MÜH.', 'MUHENDIS': 'MÜH.', 'MIMARLIK': 'MİM.', 'MIMAR': 'MİM.',
    'INSAAT': 'İNŞ.', 'INSAATI': 'İNŞ.', 'INSAA': 'İNŞ.', 'INS.': 'İNŞ.', 'INS': 'İNŞ.', 'İNŞ.': 'İNŞ.', 'İNŞ': 'İNŞ.',
    'NAKLIYAT': 'NAK.', 'NAKLIYE': 'NAK.', 'TASICILIK': 'NAK.', 'OTOMOTIV': 'OTO.', 'OTOMOBIL': 'OTO.',
    'TURIZM': 'TUR.', 'TEKSTIL': 'TEK.', 'GIDA': 'GIDA', 'HIZMET': 'HİZM.', 'HIZMETLERI': 'HİZM.',
    'TARIM': 'TAR.', 'TARIMSAL': 'TAR.', 'MADENCILIK': 'MAD.', 'MADEN': 'MAD.',
    'IMALAT': 'İMAL.', 'BILISIM': 'BİL.', 'BILGISAYAR': 'BİL.', 'YAZILIM': 'YAZ.',
    'MAKINE': 'MAK.', 'MAKINA': 'MAK.', 'MOBILYA': 'MOB.',
    'ELEKTRIK': 'ELEK.', 'ELEKTRONIK': 'ELEK.', 'KIMYA': 'KİM.', 'KIMYAVI': 'KİM.',
    'IMALATCI': 'İMAL.', 'IMALATCISI': 'İMAL.',
    # Eski DB formlari (noktali ASCII) -> Turkce standart (2026-09-09 canli veri regresyonu)
    'TIC.': 'TİC.', 'TIC': 'TİC.', 'ITH.': 'İTH.', 'ITH': 'İTH.', 'IHR.': 'İHR.', 'IHR': 'İHR.',
    'MUH.': 'MÜH.', 'MUH': 'MÜH.', 'MIM.': 'MİM.', 'MIM': 'MİM.',
    'HIZM.': 'HİZM.', 'HIZM': 'HİZM.', 'IMAL.': 'İMAL.', 'IMAL': 'İMAL.',
    'BIL.': 'BİL.', 'BIL': 'BİL.', 'KIM.': 'KİM.', 'KIM': 'KİM.',
}

# Ozel kombinasyonlar (kaynak dokuman Bolum 2.3)
_COMBO_ABBR = {
    'SANAYI VE TICARET': 'SAN. VE TİC.', 'SANAYII VE TICARETI': 'SAN. VE TİC.',
    'TICARET VE SANAYI': 'TİC. VE SAN.', 'TICARETI VE SANAYII': 'TİC. VE SAN.',
    'ITHALAT VE IHRACAT': 'İTH. İHR.', 'IHRACAT VE ITHALAT': 'İHR. İTH.',
    'INSAAT SANAYI VE TICARET': 'İNŞ. SAN. TİC.',
    'MUHENDISLIK MIMARLIK': 'MÜH. MİM.', 'TURIZM VE TICARET': 'TUR. TİC.',
    'GIDA SANAYI VE TICARET': 'GIDA SAN. TİC.',
    'TEKSTIL SANAYI VE TICARET': 'TEK. SAN. TİC.',
    'NAKLIYAT VE TICARET': 'NAK. TİC.',
    'SAN VE TIC': 'SAN. TİC.', 'SAN VE TICARET': 'SAN. TİC.',
    'TIC VE SAN': 'TİC. SAN.', 'TICARET VE SAN': 'TİC. SAN.',
    'MAK VE IMAL': 'MAK. İMAL.', 'MAKINA VE IMALAT': 'MAK. İMAL.',
    'INS VE TIC': 'İNŞ. TİC.', 'INSAAT VE TICARET': 'İNŞ. TİC.',
}

# Şirket türü/faaliyet kelimeleri (tabela ismi için filtrelenecek)
_TRADE_NAME_STOP_WORDS = frozenset({
    'VE', 'ILE', 'BI', 'AMMA', 'LAKIK',
    'SAN.', 'SAN', 'SANAYI', 'SANAYII', 'TIC.', 'TIC', 'TICARET', 'TICARETI',
    'LTD. ŞTI.', 'LTD. STI.', 'LTD.', 'LTD', 'A.S.', 'A.S', 'A.Ş.', 'A.Ş',
    'STI.', 'STI', 'ŞTI.', 'ŞTI', 'ORT.', 'ORT', 'KOL. ŞTI.', 'KOM. ŞTI.', 'KOOP.',
    'PAZ.', 'PAZ', 'ITH.', 'ITH', 'IHR.', 'IHR', 'MUH.', 'MUH', 'MIM.', 'MIM',
    'İNŞ.', 'INS.', 'INS', 'INŞ', 'NAK.', 'NAK', 'OTO.', 'OTO',
    'TUR.', 'TUR', 'TEK.', 'TEK', 'HIZM.', 'HIZM', 'TAR.', 'TAR', 'MAD.', 'MAD',
    'IMAL.', 'IMAL', 'BIL.', 'BIL', 'YAZ.', 'YAZ', 'MAK.', 'MAK', 'MOB.', 'MOB',
    'ELEK.', 'ELEK', 'KIM.', 'KIM', 'GIDA', 'GID', 'GIDA.',
    'KOOP', 'TAS', 'TAO', 'DTM', 'KOBI',
})

def _clean_double_dots(name: str) -> str:
    """Cift noktalari temizle (LTD. STI..STI. -> LTD. STI.)"""
    while '..' in name:
        name = name.replace('..', '.')
    return name


# ── KVKK PII maskeleme yardimcileri (Y7) ──
def _mask_email(email) -> str:
    """ahmet@gmail.com -> ah***@gmail.com (KVKK veri minimizasyonu)."""
    if not email or '@' not in str(email):
        return email
    local, _, domain = str(email).partition('@')
    if not local:
        return f"***@{domain}"
    return f"{local[:2]}***@{domain}"


def _mask_phone(phone) -> str:
    """0 532 123 45 67 -> 053***67 (ilk 3 + son 2 hane)."""
    if not phone:
        return phone
    phone = str(phone)
    digits = _re.sub(r'\D', '', phone)
    if len(digits) >= 8:
        return f"{digits[:3]}***{digits[-2:]}"
    return f"{digits[:2]}***" if digits else '***'


def apply_kvkk_mask(row: dict) -> dict:
    """PII alanlari maskeler. Politika: telefon + e-posta maskeli;
    firma unvani/web/VKN kamuya acik sayilir (PO karari 2026-09-01)."""
    if not isinstance(row, dict):
        return row
    if row.get('primary_phone'):
        row['primary_phone'] = _mask_phone(row['primary_phone'])
    if row.get('primary_email'):
        row['primary_email'] = _mask_email(row['primary_email'])
    return row


def _mask_active(mask_param: int = 0) -> bool:
    """Maskeleme aktif mi: env (DASH_MASK_PII=1) Veya istek ?mask=1."""
    return DASH_MASK_PII or mask_param == 1


def normalize_company_name(name) -> str:
    """Firma adini BUYUK HARFE cevirir ve standart kisaltilari uygular."""
    if not name:
        return ""
    name = str(name).upper().strip()
    name = _re.sub(r'\s{2,}', ' ', name)

    # Oncelikle en uzun eslesmeleri bulmak icin key length'e gore sirala
    for long_phrase, short_form in sorted(_COMBO_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx_soft_end(long_phrase), short_form, name)

    # Ayri sozcukleri kisaltil (zaten kisaltilmis olanlari tekrar degistirme)
    # Noktali anahtarlar _tr_rx_key ile bitisik zincirlerde de eslesir (TIC.LTD.)
    for long_phrase, short_form in sorted(_ACTIVITY_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx_key(long_phrase), short_form, name)

    for long_phrase, short_form in sorted(_COMPANY_TYPE_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx_key(long_phrase), short_form, name)
    
    name = _re.sub(r'\s{2,}', ' ', name).strip()
    name = _clean_double_dots(name)
    # STI.STI. gibi tekrarlanan kisaltilari temizle
    name = _re.sub(r'(\b\w+\.)\s*\1', r'\1', name)
    return name


# Tabela ismi icin iki katmanli stop-word:
#   HARD  -> her zaman cikar (sirket turu, baglaclar, SAN/TIC)
#   SOFT  -> faaliyet kelimeleri; yalnizca baska marka kelimesi varken cikar
_TRADE_NAME_STOP_HARD = frozenset({
    'VE', 'ILE', 'BI', 'AMMA', 'LAKIK',
    'SAN.', 'SAN', 'SANAYI', 'SANAYII', 'TIC.', 'TIC', 'TICARET', 'TICARETI',
    'IC', 'DIS',
    'LTD. ŞTI.', 'LTD. STI.', 'LTD.', 'LTD', 'LIMITED', 'LIM.', 'LIM',
    'A.S.', 'A.S', 'A.Ş.', 'A.Ş',
    'STI.', 'STI', 'ŞTI.', 'ŞTI', 'SIRKETI', 'SIRKET', 'ANONIM', 'ANONIM ŞIRKETI',
    'ORT.', 'ORT', 'ORTAKLIK', 'KOL. ŞTI.', 'KOM. ŞTI.', 'KOOP.', 'KOOP',
    'KOLLEKTIF', 'KOMANDIT', 'TAS', 'TAO', 'DTM', 'KOBI',
})
# SOFT: yalnizca KISALTMALAR (ELEK., INŞ., MAK. vb.) — tam faaliyet kelimeleri
# (ELEKTRIK, INSAAT, MOBILYA...) bilerek SOFT'ta DEGIL: tabelanin parcasi
# olarak korunurlar. Ornek: "DÜNDAR ELEKTRİK SANAYİ" -> "DÜNDAR ELEKTRİK"
_TRADE_NAME_STOP_SOFT = frozenset({
    'PAZ.', 'PAZ', 'ITH.', 'ITH', 'IHR.', 'IHR', 'MUH.', 'MUH', 'MIM.', 'MIM',
    'İNŞ.', 'INS.', 'INS', 'INŞ', 'NAK.', 'NAK', 'OTO.', 'OTO',
    'TUR.', 'TUR', 'TEK.', 'TEK', 'HIZM.', 'HIZM', 'TAR.', 'TAR', 'MAD.', 'MAD',
    'IMAL.', 'IMAL', 'BIL.', 'BIL', 'YAZ.', 'YAZ', 'MAK.', 'MAK', 'MOB.', 'MOB',
    'ELEK.', 'ELEK', 'KIM.', 'KIM', 'GIDA.', 'GID.',
})
# Turkce duyarsiz karsilastirma icin fold map
_TRADE_FOLD_MAP = str.maketrans({'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C', 'ı': 'I'})
_TRADE_STOP_HARD_FOLDED = frozenset(w.translate(_TRADE_FOLD_MAP) for w in _TRADE_NAME_STOP_HARD)
_TRADE_STOP_SOFT_FOLDED = frozenset(w.translate(_TRADE_FOLD_MAP) for w in _TRADE_NAME_STOP_SOFT)


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
    raw = _re.sub(r'\s{2,}', ' ', str(legal_name).upper().strip())
    words = [w for w in _re.split(r'[\s.]+', raw) if w]

    full = [w for w in words
            if len(w) > 1
            and not _trade_is_stop(w, _TRADE_STOP_HARD_FOLDED)
            and not _trade_is_stop(w, _TRADE_STOP_SOFT_FOLDED)]
    if full:
        return ' '.join(full[:2])

    # Tum kelimeler HARD/SOFT'a carpti -> HARD disi (faaliyet) ilk kelimeyi marka yap
    hard_kept = [w for w in words
                 if len(w) > 1 and not _trade_is_stop(w, _TRADE_STOP_HARD_FOLDED)]
    if hard_kept:
        return hard_kept[0]

    # Son care: sadece baglaclari at, ilk iki kelimeyi ver
    minimal = [w for w in words if w.translate(_TRADE_FOLD_MAP) not in ('VE', 'ILE') and len(w) > 1]
    return ' '.join(minimal[:2]) if minimal else raw

def normalize_company(row: dict) -> dict:
    """Bir firma satirina ad normalizasyon kurallarini uygular."""
    if not row:
        return row
    # legal_name -> kisaltilmis BUYUK HARF
    if row.get('legal_name'):
        row['legal_name'] = normalize_company_name(row['legal_name'])
    # trade_name -> Kural 3: tabela ismi HER ZAMAN unvandan (legal_name)
    # uretilir; eski/kısmi trade_name degerleri guncellenir. legal_name
    # bos ise mevcut trade_name kaynak olarak kullanilir.
    source = row.get('legal_name') or row.get('trade_name') or ''
    row['trade_name'] = extract_trade_name(source)
    return row

# ── Turkce case-insensitive arama destegi ──
# PostgreSQL LOWER() Turkce karakterleri dogru kucultmez (I->i, ama İ->i degil).
# Bu yuzden arama terimini ve karsilastirma alanlarini ASCII'ye yaklastiriyoruz.
_TR_LOWER_MAP = str.maketrans({
    'İ': 'i', 'I': 'i', 'Ş': 's', 'Ğ': 'g', 'Ü': 'u', 'Ö': 'o', 'Ç': 'c',
    'ş': 's', 'ğ': 'g', 'ü': 'u', 'ö': 'o', 'ç': 'c', 'ı': 'i', 'İ': 'i',
})

def tr_normalize(s: str) -> str:
    """Turkce karakterleri ASCII'ye cevirir + kucuk harf yapar.
    Ornek: 'ARITES' -> 'arites', 'Arıtes' -> 'arites', 'DÜNDAR' -> 'dundar'
    """
    if not s:
        return ""
    return s.translate(_TR_LOWER_MAP).lower()

# Dashboard performance counters

app = FastAPI(title="Company Master Dashboard API", version="1.0")

# ── API Key Auth & Rate Limiting (Y6) ──
# DASH_API_KEY env'de tanimliysa zorunlu, degilse dev modu (herkese acik).
# Frontend dashboard'a ?api_key=KEY ile erisince key otomatik tasinir.
DASH_API_KEY = os.getenv("DASH_API_KEY", "").strip()
_auth_banner = "API key zorunlu degil (dev modu)" if not DASH_API_KEY else "API key korumasi AKTIF"

# ── KVKK PII Maskeleme (Y7) ──
# DASH_MASK_PII=1 ise TUM PII maskelemeli doner (musteri preview modu).
# Endpoint bazinda ?mask=1 ile istek bazli da acilabilir (env'den bagimsiz).
DASH_MASK_PII = os.getenv("DASH_MASK_PII", "0").strip() == "1"

# Basit in-memory rate limit: ip -> [tick, sayac]
_RATE_LIMIT: dict[str, list] = {}
_RATE_LIMIT_MAX = int(os.getenv("DASH_RATE_LIMIT_MAX", "120"))  # istek / dakika
_RATE_LIMIT_WINDOW = 60


def require_api_key(request: Request) -> str:
    """Endpoint'lere dependency olarak eklenir:
        def endpoint(api_key: str = Depends(require_api_key)):
    """
    # 1) API key kontrolu (env'de tanimliysa)
    key = request.headers.get("X-API-Key", "") or request.query_params.get("api_key", "")
    if DASH_API_KEY:
        if not key or key != DASH_API_KEY:
            raise HTTPException(status_code=401, detail="Gecersiz API key. ?api_key= veya X-API-Key header gerekli.")

    # 2) Rate limiting (her IP icin 1 dakikalik pencere)
    ip = request.client.host if request.client else "local"
    now = time.time()
    entry = _RATE_LIMIT.get(ip)
    if not entry or now - entry[0] > _RATE_LIMIT_WINDOW:
        _RATE_LIMIT[ip] = [now, 1]
    else:
        entry[1] += 1
        if entry[1] > _RATE_LIMIT_MAX:
            raise HTTPException(status_code=429, detail="Cok fazla istek. Lutfen biraz bekleyin.")

    return key or "public"


def require_api_key_optional(request: Request) -> str:
    """Zorunlu olmayan auth (rate limit yine uygulanir) - dashboard HTML icin."""
    return require_api_key(request) if DASH_API_KEY else "public"

_CACHE: dict[str, tuple[float, Any]] = {}
_CACHE_TTL = 300


def cache_get(key: str) -> Any | None:
    global _CACHE_HITS, _CACHE_MISSES
    entry = _CACHE.get(key)
    if entry and time.time() - entry[0] < _CACHE_TTL:
        _CACHE_HITS += 1
        return entry[1]
    _CACHE_MISSES += 1
    _CACHE.pop(key, None)
    return None


def cache_set(key: str, value: Any) -> None:
    _CACHE[key] = (time.time(), value)


ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

WEB_DIR = ROOT / "web_dashboard"
WEB_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="web-static")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.get("/metrics")
def metrics() -> dict:
    """Prometheus formatinda metrik verisi - tek sorgu optimize."""
    global _CACHE_HITS, _CACHE_MISSES
    import json, hashlib
    cache_key = hashlib.md5(b'metrics:v1').hexdigest()
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT COUNT(*) as total,
                   AVG(data_quality_score) as avg_score,
                   SUM(CASE WHEN tax_number IS NOT NULL AND tax_number != '' THEN 1 ELSE 0 END) as with_tax,
                   SUM(CASE WHEN website_domain IS NOT NULL AND website_domain != '' THEN 1 ELSE 0 END) as with_web,
                   SUM(CASE WHEN nace_code IS NOT NULL AND nace_code != '' THEN 1 ELSE 0 END) as with_nace,
                   SUM(CASE WHEN primary_phone IS NOT NULL AND primary_phone != '' THEN 1 ELSE 0 END) as with_phone,
                   SUM(CASE WHEN primary_email IS NOT NULL AND primary_email != '' THEN 1 ELSE 0 END) as with_email,
                   SUM(CASE WHEN osb_parsel IS NOT NULL AND osb_parsel != '' THEN 1 ELSE 0 END) as with_parsel,
                   SUM(CASE WHEN adres IS NOT NULL AND adres != '' THEN 1 ELSE 0 END) as with_adres
            FROM companies
            WHERE is_ankara=TRUE
        """)).mappings().first()
        if not r:
            return {}
        _db_elapsed = (_perf_time.perf_counter() - _q_start) * 1000
        global _DB_TIME_MS
        _DB_TIME_MS += _db_elapsed
        return {
            "huginn_companies_total": r["total"],
            "huginn_companies_avg_quality_score": round(float(r["avg_score"]) if r.get("avg_score") is not None else 0, 2),
            "huginn_companies_with_tax_number": r["with_tax"],
            "huginn_companies_with_website": r["with_web"],
            "huginn_companies_with_nace_code": r["with_nace"],
            "huginn_companies_with_phone": r["with_phone"],
            "huginn_companies_with_email": r["with_email"],
            "huginn_companies_with_osb_parsel": r["with_parsel"],
            "huginn_companies_with_adres": r["with_adres"],
            "huginn_query_count": _QUERY_COUNT,
            "huginn_db_time_ms": round(_DB_TIME_MS, 2),
            "huginn_cache_hits": _CACHE_HITS,
            "huginn_cache_misses": _CACHE_MISSES,
            "huginn_cache_hit_rate": round(_CACHE_HITS / max(1, _CACHE_HITS + _CACHE_MISSES), 4),
            "huginn_db_time_ms": round(_DB_TIME_MS, 2),
            "huginn_query_count": _QUERY_COUNT,
            "huginn_timestamp": datetime.now().isoformat(),
        }


@app.get("/api/kpi")
def api_kpi(_auth: str = Depends(require_api_key)) -> dict:
    """KPI ozeti - SQLite/PostgreSQL uyumlu (FILTER yerine CASE WHEN)."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT COUNT(*) as total,
                SUM(CASE WHEN c.tax_number IS NOT NULL AND c.tax_number != '' THEN 1 ELSE 0 END) as tax,
                SUM(CASE WHEN c.vergi_no IS NOT NULL AND c.vergi_no != '' THEN 1 ELSE 0 END) as vergi,
                SUM(CASE WHEN COALESCE(c.tax_number, c.vergi_no) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no) != '' THEN 1 ELSE 0 END) as vkn_either,
                SUM(CASE WHEN c.website_domain IS NOT NULL AND c.website_domain != '' THEN 1 ELSE 0 END) as web,
                SUM(CASE WHEN c.osb_parsel IS NOT NULL AND c.osb_parsel != '' THEN 1 ELSE 0 END) as parsel,
                SUM(CASE WHEN c.adres IS NOT NULL AND c.adres != '' THEN 1 ELSE 0 END) as adres,
                SUM(CASE WHEN c.primary_phone IS NOT NULL AND c.primary_phone != '' THEN 1 ELSE 0 END) as tel,
                SUM(CASE WHEN c.primary_email IS NOT NULL AND c.primary_email != '' THEN 1 ELSE 0 END) as email,
                SUM(CASE WHEN c.nace_code IS NOT NULL AND c.nace_code != '' THEN 1 ELSE 0 END) as nace,
                AVG(c.data_quality_score) as avg_score
            FROM companies c
            WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        """)).mappings().first()
        if r:
            row = dict(r)
            row["avg_score"] = float(row["avg_score"]) if row.get("avg_score") is not None else None
            return row
        return {}


@app.get("/api/tasks")
def api_tasks(_auth: str = Depends(require_api_key)) -> list[dict]:
    board = tb.gorev_listesi()
    return board or []


@app.get("/api/handoffs")
def api_handoffs(_auth: str = Depends(require_api_key)) -> dict:
    return tb.handoff_tum() or {}


MAX_COMPANIES_LIMIT = 500
MAX_SEARCH_LENGTH = 100


@app.get("/api/companies")
def api_companies(limit: int = 50, offset: int = 0, search: str = "", min_score: int = 0, max_score: int = 100, source: str = "", sources: str = "", nace: str = "", mask: int = 0, _auth: str = Depends(require_api_key)) -> dict:
    """Firma listesi - coklu kaynak destegi (sources= virgulle ayrilmis).
    KVKK: mask=1 (veya env DASH_MASK_PII=1) ile telefon/e-posta maskeli doner."""
    limit = min(max(limit, 1), MAX_COMPANIES_LIMIT)
    offset = max(offset, 0)
    search = search.strip()[:MAX_SEARCH_LENGTH]
    min_score = max(0, min(min_score, 100))
    max_score = max(0, min(max_score, 100))

    # Coklu kaynak: sources="ostim.org.tr,aso.org.tr" -> liste
    # Geriye donuk uyum: tek source= parametresi de desteklenir
    source_list = []
    if sources:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
    elif source:
        source_list = [source.strip()] if source.strip() else []

    # P4-4: cache hit — DB roundtrip'i tamamen atlar (TTL 300s)
    # Not: source_list yukarida hesaplandi; mask durumu anahtarda (maskeli/maskesiz ayri).
    import hashlib
    _ck = hashlib.md5(f'companies:{limit}:{offset}:{search}:{min_score}:{max_score}:{source_list}:{nace}:mask={_mask_active(mask)}'.encode()).hexdigest()
    _cached = cache_get(_ck)
    if _cached is not None:
        return _cached

    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        where_clauses = ["c.is_ankara=TRUE AND c.is_osb_member=TRUE"]
        params: dict[str, Any] = {"limit": limit, "offset": offset, "min_score": min_score, "max_score": max_score}

        if search:
            # PostgreSQL ILIKE + expression index kullanimi
            # tr_normalize artik sadece fallback; ILIKE trigram/expression index kullanir
            where_clauses.append("""
                (c.legal_name ILIKE :search
                OR c.trade_name ILIKE :search
                OR c.primary_phone ILIKE :search
                OR c.primary_email ILIKE :search
                OR c.tax_number ILIKE :search
                OR c.vergi_no ILIKE :search)
            """)
            params["search"] = f"%{search}%"

        if nace:
            where_clauses.append("c.nace_code LIKE :nace")
            params["nace"] = f"{nace}%"

        # Coklu kaynak filtresi: companies.source_record_id -> source_records.source_id -> sources.source_name
        if source_list:
            if len(source_list) == 1:
                where_clauses.append("""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name = :source_name
                )""")
                params["source_name"] = source_list[0]
            else:
                # Coklu kaynak: IN (...) ile
                placeholders = []
                for i, src in enumerate(source_list):
                    key = f"src_{i}"
                    placeholders.append(f":{key}")
                    params[key] = src
                where_clauses.append(f"""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name IN ({", ".join(placeholders)})
                )""")

        where_clauses.append("c.data_quality_score >= :min_score")
        where_clauses.append("c.data_quality_score <= :max_score")

        where_sql = " AND ".join(where_clauses)

        _q_start = _perf_time.perf_counter()
        total = conn.execute(text(f"SELECT COUNT(*) FROM companies c WHERE {where_sql}"), params).scalar()
        rows = conn.execute(text(f"""
            SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
                   c.tax_number, c.vergi_no, c.osb_parsel, c.nace_code, c.data_quality_score
            FROM companies c
            WHERE {where_sql}
            ORDER BY c.data_quality_score DESC
            LIMIT :limit OFFSET :offset
        """), params).mappings().all()
        _db_elapsed = (_perf_time.perf_counter() - _q_start) * 1000
        global _DB_TIME_MS, _QUERY_COUNT
        _DB_TIME_MS += _db_elapsed
        _QUERY_COUNT += 2
        items = []
        for r in rows:
            row = dict(r)
            if row.get("data_quality_score") is not None:
                row["data_quality_score"] = float(row["data_quality_score"])
            row = normalize_company(row)
            if _mask_active(mask):
                row = apply_kvkk_mask(row)
            items.append(row)
        result = {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
        }
        cache_set(_ck, result)
        return result


@app.get("/api/companies/export")
def api_companies_export(format: str = "csv", search: str = "", min_score: int = 0, max_score: int = 100, source: str = "", sources: str = "", nace: str = "", mask: int = 0, _auth: str = Depends(require_api_key)) -> Response:
    """CSV export - coklu kaynak + nace + turkce arama destekli.
    KVKK: mask=1 ile telefon/e-posta maskeli export."""
    import csv
    import io

    search = search.strip()[:MAX_SEARCH_LENGTH]
    min_score = max(0, min(min_score, 100))
    max_score = max(0, min(max_score, 100))
    nace = nace.strip()[:8]

    # Coklu kaynak: sources= oncelikli, source= geriye donuk uyum
    source_list = []
    if sources:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
    elif source:
        # source= parametresinde virgul de olabilir
        source_list = [s.strip() for s in source.split(",") if s.strip()]

    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        where_clauses = ["c.is_ankara=TRUE AND c.is_osb_member=TRUE"]
        params: dict[str, Any] = {"min_score": min_score, "max_score": max_score}

        if search:
            # PostgreSQL ILIKE + expression index kullanimi
            where_clauses.append("""
                (c.legal_name ILIKE :search
                OR c.trade_name ILIKE :search
                OR c.primary_phone ILIKE :search
                OR c.primary_email ILIKE :search
                OR c.tax_number ILIKE :search
                OR c.vergi_no ILIKE :search)
            """)
            params["search"] = f"%{search}%"

        if source_list:
            if len(source_list) == 1:
                where_clauses.append("""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name = :source_name
                )""")
                params["source_name"] = source_list[0]
            else:
                placeholders = []
                for i, src in enumerate(source_list):
                    key = f"src_{i}"
                    placeholders.append(f":{key}")
                    params[key] = src
                where_clauses.append(f"""c.source_record_id IN (
                    SELECT sr.source_record_id
                    FROM source_records sr
                    JOIN sources s ON sr.source_id = s.source_id
                    WHERE s.source_name IN (", ".join(placeholders))
                )""")

        if nace:
            where_clauses.append("c.nace_code LIKE :nace")
            params["nace"] = f"{nace}%"

        where_clauses.append("c.data_quality_score >= :min_score")
        where_clauses.append("c.data_quality_score <= :max_score")

        where_sql = " AND ".join(where_clauses)

        _q_start = _perf_time.perf_counter()
        rows = conn.execute(text(f"""
            SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
                   c.tax_number, c.vergi_no, c.osb_parsel, c.nace_code, c.data_quality_score
            FROM companies c
            WHERE {where_sql}
            ORDER BY c.created_at DESC
            LIMIT :limit
        """), {**params, 'limit': MAX_COMPANIES_LIMIT}).mappings().all()
        _db_elapsed = (_perf_time.perf_counter() - _q_start) * 1000
        global _DB_TIME_MS, _QUERY_COUNT
        _DB_TIME_MS += _db_elapsed
        _QUERY_COUNT += 1

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Firma Adi", "Ticaret Adi", "Web", "Telefon", "E-posta", "VKN", "NACE", "Skor"])
        for r in rows:
            row = normalize_company(dict(r))
            if _mask_active(mask):
                row = apply_kvkk_mask(row)
            writer.writerow([
                row.get("legal_name", ""),
                row.get("trade_name", ""),
                row.get("website_domain", ""),
                row.get("primary_phone", ""),
                row.get("primary_email", ""),
                row.get("tax_number") or row.get("vergi_no", ""),
                row.get("nace_code", ""),
                row.get("data_quality_score", ""),
            ])

        csv_data = output.getvalue()
        return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=companies.csv"})


# ── Y19: V9 Smart Matching MVP ──────────────────────────────────────────────

# NACE ana-grup komşuluk ağırlıkları (tamamlayıcı sektörler; 1.0 = aynı grup).
# Kaynak: OSTIM/Ankara üretim zinciri kurgusu (montaj<-yan sanayi<-hammadde).
_NACE_KOMSU = {
    "29": {"28": 0.75, "25": 0.65, "24": 0.45, "46": 0.55},
    "28": {"29": 0.75, "25": 0.70, "24": 0.50, "46": 0.55},
    "25": {"28": 0.70, "29": 0.65, "24": 0.45, "23": 0.40},
    "10": {"46": 0.60, "01": 0.50, "11": 0.40},
    "62": {"63": 0.75, "58": 0.55},
    "41": {"43": 0.80, "23": 0.50, "25": 0.40},
    "24": {"25": 0.60, "28": 0.50, "29": 0.45},
    "46": {"10": 0.55, "29": 0.50, "28": 0.50},
    "43": {"41": 0.80, "23": 0.50},
}


def _nace_grup(nace: str) -> str:
    return (nace or "").split(".")[0].strip()


def _match_puan(row, buyer_grup: str, buyer_osb: str, mode: str):
    """Firma için 0-100 eşleştirme puanı + bileşen kırılımı. (None = elensin)"""
    hedef_grup = _nace_grup(row.get("nace_code") or "")
    if not hedef_grup:
        return None

    # 1) sektör uyumu (0-45)
    if hedef_grup == buyer_grup:
        sektor = 45.0
        iliski = "ayni-sektor"
    elif mode == "komple" and buyer_grup in _NACE_KOMSU:
        kom = _NACE_KOMSU[buyer_grup].get(hedef_grup, 0.0)
        sektor = 45.0 * kom
        iliski = "komple-sektor" if kom >= 0.4 else "uzak-sektor"
    else:
        sektor = 0.0
        iliski = "farkli"

    # 2) konum (0-20)
    hedef_osb = row.get("osb_id") or ""
    if buyer_osb and hedef_osb and hedef_osb == buyer_osb:
        konum = 20.0
    elif row.get("is_ankara"):
        konum = 12.0
    else:
        konum = 0.0

    # 3) firma kalitesi (0-25)
    try:
        kalite = min(max(float(row.get("data_quality_score") or 0), 0), 100) * 0.25
    except (TypeError, ValueError):
        kalite = 0.0

    # 4) kanıt gücü (0-10): web 5 + email 3 + telefon 2
    kanit = (5.0 if row.get("web_sitesi") else 0.0) \
        + (3.0 if row.get("primary_email") else 0.0) \
        + (2.0 if row.get("primary_phone") else 0.0)

    return {
        "puan": round(sektor + konum + kalite + kanit, 1),
        "kirilim": {
            "sektor": round(sektor, 1),
            "konum": round(konum, 1),
            "kalite": round(kalite, 1),
            "kanit": round(kanit, 1),
        },
        "iliski": iliski,
    }


@app.get("/api/match")
def api_match(
    buyer_id: str = "",
    nace: str = "",
    osb_id: str = "",
    mode: str = "komple",
    min_puan: int = 30,
    limit: int = 20,
    offset: int = 0,
    mask: int = 0,
    _auth: str = Depends(require_api_key),
) -> dict:
    """V9 smart matching MVP: buyer profiline uygun firmaları puanla.

    - buyer_id verirse: DB'den buyer alınır (nace + osb)
    - yoksa nace (+ opsiyonel osb_id) ile serbest profil
    - mode: komple (komşu sektörler dahil) | ayni (sadece aynı ana grup)
    """
    mode = mode if mode in ("komple", "ayni") else "komple"
    limit = max(1, min(limit, 100))

    buyer_nace, buyer_osb, buyer_adi = nace, osb_id, None
    engine = get_engine()
    if buyer_id:
        try:
            uuid.UUID(buyer_id)
        except (ValueError, AttributeError, TypeError):
            raise HTTPException(status_code=404, detail=f"buyer bulunamadi: {buyer_id}")
        with engine.connect() as conn:
            r = conn.execute(text(
                "SELECT company_id, legal_name, nace_code, osb_id FROM companies "
                "WHERE company_id = :id"), {"id": buyer_id}).mappings().first()
        if not r:
            raise HTTPException(status_code=404, detail=f"buyer bulunamadi: {buyer_id}")
        buyer_nace = r["nace_code"] or buyer_nace
        buyer_osb = r["osb_id"] or buyer_osb
        buyer_adi = r["legal_name"]

    buyer_grup = _nace_grup(buyer_nace)
    if not buyer_grup:
        raise HTTPException(
            status_code=400,
            detail="buyer nace belirtilmeli (buyer_id veya nace parametresi)",
        )

    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT company_id, legal_name, trade_name, nace_code, nace_name, osb_id, "
            "is_ankara, is_osb_member, data_quality_score, web_sitesi, primary_phone, "
            "primary_email, website_domain "
            "FROM companies WHERE nace_code IS NOT NULL AND is_ankara = TRUE "
            "ORDER BY data_quality_score DESC NULLS LAST LIMIT 5000"
        )).mappings().all()

    skorlu = []
    for r in rows:
        d = dict(r)
        if buyer_id and d.get("company_id") == buyer_id:
            continue  # kendisi
        m = _match_puan(d, buyer_grup, buyer_osb or "", mode)
        if not m or m["puan"] < min_puan:
            continue
        d["match"] = m
        d = normalize_company(d)
        if _mask_active(mask):
            d = apply_kvkk_mask(d)
        skorlu.append(d)

    skorlu.sort(key=lambda x: x["match"]["puan"], reverse=True)
    return {
        "buyer": {
            "buyer_id": buyer_id or None,
            "adi": buyer_adi,
            "nace": buyer_nace,
            "nace_grup": buyer_grup,
            "osb_id": buyer_osb or None,
        },
        "mode": mode,
        "toplam": len(skorlu),
        "limit": limit,
        "offset": offset,
        "items": skorlu[offset:offset + limit],
    }

@app.get("/api/dashboard", response_class=HTMLResponse)
def serve_dashboard(_auth: str = Depends(require_api_key)) -> HTMLResponse:
    index = WEB_DIR / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)
    return HTMLResponse(index.read_text(encoding="utf-8"))


@app.get("/api/performance")
def performance_report(_auth: str = Depends(require_api_key)) -> dict:
    global _DB_TIME_MS, _QUERY_COUNT, _CACHE_HITS, _CACHE_MISSES
    return {
        "db_time_ms": round(_DB_TIME_MS, 2),
        "query_count": _QUERY_COUNT,
        "cache_hits": _CACHE_HITS,
        "cache_misses": _CACHE_MISSES,
        "cache_hit_rate": round(_CACHE_HITS / max(1, _CACHE_HITS + _CACHE_MISSES), 4),
        "slow_queries": [q for q in _QUERY_TIMES if q["ms"] > 100],
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/quality-trend")
def api_quality_trend(_auth: str = Depends(require_api_key)) -> list[dict]:
    """Kalite skoru dagilimi (bucket bazli) - SQLite/PostgreSQL uyumlu."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT CASE
                WHEN data_quality_score >= 80 THEN '80-100'
                WHEN data_quality_score >= 60 THEN '60-79'
                WHEN data_quality_score >= 40 THEN '40-59'
                WHEN data_quality_score >= 20 THEN '20-39'
                ELSE '0-19'
            END as bucket, COUNT(*) as cnt
            FROM companies
            WHERE is_ankara=TRUE AND is_osb_member=TRUE
            GROUP BY 1
            ORDER BY 1 DESC
        """)).mappings().all()
        return [dict(r) for r in rows] if rows else []


@app.get("/api/nace-distribution")
def api_nace_distribution(limit: int = 20, _auth: str = Depends(require_api_key)) -> list[dict]:
    """NACE kodu x firma sayisi (top N) - nace_codes tablosu olmadan."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT c.nace_code, COUNT(*) as cnt
            FROM companies c
            WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE AND c.nace_code IS NOT NULL AND c.nace_code != ''
            GROUP BY c.nace_code
            ORDER BY cnt DESC
            LIMIT :lim
        """), {"lim": limit}).mappings().all()
        return [dict(r) for r in rows] if rows else []


@app.get("/api/sources")
def api_sources(_auth: str = Depends(require_api_key)) -> list[dict]:
    """Veri kaynaklari durumu - PostgreSQL (sources + source_records tablolari)."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT s.source_name, s.source_type, s.url,
                   COUNT(sr.source_record_id) as record_count,
                   MAX(sr.collected_at) as last_scrape
            FROM sources s
            LEFT JOIN source_records sr ON sr.source_id = s.source_id
            GROUP BY s.source_id, s.source_name, s.source_type, s.url
            ORDER BY record_count DESC
        """)).mappings().all()
        return [dict(r) for r in rows] if rows else []


@app.get("/api/company/{company_id}")
def api_company_detail(company_id: str, mask: int = 0, _auth: str = Depends(require_api_key)) -> dict:
    """Tek firma detayi. KVKK: mask=1 ile telefon/e-posta maskeli."""
    engine = get_engine()
    _q_start = _perf_time.perf_counter()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT c.* FROM companies c WHERE c.company_id = :cid
        """), {"cid": company_id}).mappings().first()
        if r:
            row = dict(r)
            for k, v in row.items():
                if isinstance(v, (float,)) and v is not None:
                    row[k] = float(v)
            row = normalize_company(row)
            if _mask_active(mask):
                row = apply_kvkk_mask(row)
            return row
        return {}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
