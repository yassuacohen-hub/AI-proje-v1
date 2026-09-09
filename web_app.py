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
from company_master.intelligence.job_intelligence.api.router import router as job_intelligence_router
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

# Y26: API key kullanim metrikleri (tier bazli istek sayaci, in-memory)
_API_USAGE: dict[str, dict[str, int]] = {}  # tier -> endpoint -> sayac
_TIER_RATE_LIMITS = {"terminal": 60, "strategic": 120, "enterprise": 600}  # istek/dk


def _record_api_usage(tier: str, path: str) -> None:
    """Tier bazli istek sayaci (/metrics raporu icin)."""
    entry = _API_USAGE.setdefault(tier, {})
    entry[path] = entry.get(path, 0) + 1


def api_usage_snapshot() -> dict:
    """Kopya dondurur (metrik endpoint'i icin)."""
    return {t: dict(v) for t, v in _API_USAGE.items()}


def _user_from_api_key(api_key: str):
    """Y26: API key ile kullaniyi bulur (enterprise tier kontrolu icin)."""
    if not api_key or not api_key.startswith("ent_"):
        return None
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT user_id, email, role, status, tier, api_key FROM users "
                "WHERE api_key = :k"), {"k": api_key}).mappings().first()
        return dict(row) if row else None
    except Exception:
        return None


def require_api_key(request: Request) -> str:
    """Endpoint'lere dependency olarak eklenir:
        def endpoint(api_key: str = Depends(require_api_key)):
    Y26: gecen key enterprise uye key'i ise tier bazli sayac + yuksek rate limit uygulanir.
    """
    # 1) API key kontrolu (env'de tanimliysa)
    key = request.headers.get("X-API-Key", "") or request.query_params.get("api_key", "")
    tier = "public"

    if DASH_API_KEY:
        if key and key != DASH_API_KEY:
            # enterprise uye key'i mi? (users tablosundan dogrula)
            u = _user_from_api_key(key)
            if u and u.get("api_key") == key and u.get("tier") == "enterprise":
                tier = "enterprise"
            else:
                raise HTTPException(status_code=401, detail="Gecersiz API key. ?api_key= veya X-API-Key header gerekli.")
        elif not key:
            raise HTTPException(status_code=401, detail="Gecersiz API key. ?api_key= veya X-API-Key header gerekli.")
    elif key:
        u = _user_from_api_key(key)
        if u and u.get("tier") == "enterprise":
            tier = "enterprise"

    # 2) Rate limiting (tier bazli; her IP icin 1 dakikalik pencere)
    limit = _TIER_RATE_LIMITS.get(tier, _RATE_LIMIT_MAX)
    ip = request.client.host if request.client else "local"
    now = time.time()
    entry = _RATE_LIMIT.get(ip)
    if not entry or now - entry[0] > _RATE_LIMIT_WINDOW:
        _RATE_LIMIT[ip] = [now, 1]
    else:
        entry[1] += 1
        if entry[1] > max(limit, _RATE_LIMIT_MAX):
            raise HTTPException(status_code=429, detail="Cok fazla istek. Lutfen biraz bekleyin.")

    if tier == "enterprise":
        _record_api_usage(tier, request.url.path)
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

app.include_router(job_intelligence_router)
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


def _match_puan(row, buyer_grup: str, buyer_osb: str, mode: str, yon: str = "tedarikci",
                buyer_profil: dict | None = None):
    """Firma için 0-100 eşleştirme puanı + bileşen kırılımı. (None = elensin)

    yon (Y22 - eslestirme yonu):
    - tedarikci: buyer tedarikçi arıyor (montaj -> yan sanayi/hammadde; varsayilan)
    - musteri:   buyer musteri/satis kanali arıyor (yon TERS: hedef firmanin
                 komsuluk haritasindan buyer grubuna agirlik - orn. yedek parcaciga
                 45.20 servis / 46.75 toptan firmalari)
    - rakip:     sadece ayni NACE ana grubu (rakip analizi)
    """
    hedef_grup = _nace_grup(row.get("nace_code") or "")
    if not hedef_grup:
        return None

    # 1) sektör uyumu (0-45)
    if hedef_grup == buyer_grup:
        sektor = 45.0
        iliski = "ayni-sektor"
    elif yon == "rakip":
        sektor = 0.0
        iliski = "farkli"
    elif yon == "musteri" and mode == "komple":
        # ters yon: hedef firmanin ayni-sektor inanlari kimlere satar?
        kom = _NACE_KOMSU.get(hedef_grup, {}).get(buyer_grup, 0.0)
        sektor = 45.0 * kom
        iliski = "musteri-kanal" if kom >= 0.4 else "musteri-uzak"
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

    # 5) X03: buyer profili bonusu (0-5): olcek uyumu + sertifika + amac
    bonus, bonus_nedenler = _profil_bonus(buyer_profil, row)

    return {
        "puan": round(min(sektor + konum + kalite + kanit + bonus, 100.0), 1),
        "kirilim": {
            "sektor": round(sektor, 1),
            "konum": round(konum, 1),
            "kalite": round(kalite, 1),
            "kanit": round(kanit, 1),
            "profil": round(bonus, 1),
        },
        "iliski": iliski,
        "profil_bonus": bonus_nedenler,
    }


# Y26/X03: calisan sayisi araliklarinin buyukluk sirasi (olcek uyumu icin)
_EMPLOYEE_SCALE = {"1-5": 1, "6-20": 2, "21-50": 3, "51-250": 4, "250+": 5}


def _profil_bonus(buyer_profil: dict | None, hedef_row: dict) -> tuple[float, list]:
    """X03 MATCH v3: buyer profilinden bonus puan (0-5, toplam 100'e yuvarlanir).

    - olcek uyumu (0-2): hedef firmanin kalite skoru + kanit gucu, buyer'in
      calisan sayisina gore "kapasite sinyali" verir; buyuk buyer daha olgun
      (kayitli/verili) tedarikci ister.
    - sertifika bonusu (0-2): buyer sertifikali ve hedef firma kalitesi yuksekse
      kucuk bonus (hedef firmanin sertifikasyon verisi su an yok; vekil sinyal).
    - amac uyumu (0-1): buyer'in goal'i ile arama yonu ayni yonde ise +1.
    """
    if not buyer_profil:
        return 0.0, []
    bonus = 0.0
    nedenler = []
    # 1) olcek uyumu (0-2)
    buyer_scale = _EMPLOYEE_SCALE.get(buyer_profil.get("employee_range") or "")
    if buyer_scale_uygun(buyer_profil, hedef_row):
        bonus += 2.0
        nedenler.append("olcek-uyum")
    # 2) sertifika sinyali (0-2): buyer sertifikalarini yazmis ise
    #    kanit gucu yuksek (web+email) firmalari tercih et
    if (buyer_profil.get("certificates") or "").strip():
        cert_sinyal = (2.0 if hedef_row.get("web_sitesi") else 0.0) \
            + (1.0 if hedef_row.get("primary_email") else 0.0)
        bonus += min(cert_sinyal, 2.0)
        if cert_sinyal > 0:
            nedenler.append("sertifika-kapasite")
    # 3) amac uyumu (0-1)
    goal = (buyer_profil.get("goal") or "").strip()
    if goal and goal != "tumu":
        bonus += 1.0
        nedenler.append("amac-uyum")
    return bonus, nedenler


def buyer_scale_uygun(buyer_profil: dict, hedef_row: dict) -> bool:
    """Buyer'in calisan sayisina gore hedef firmanin kapasite sinyali yeterli mi?
    companies tablosunda calisan sayisi yok; vekil: kalite skoru + kanit gucu.
    Buyer buyudukce daha yuksek kalite/kanit esigi bekler."""
    buyer_scale = _EMPLOYEE_SCALE.get(buyer_profil.get("employee_range") or "", 0)
    if buyer_scale <= 0:
        return False
    try:
        kalite = float(hedef_row.get("data_quality_score") or 0)
    except (TypeError, ValueError):
        kalite = 0.0
    kanit = (1 if hedef_row.get("web_sitesi") else 0) \
        + (1 if hedef_row.get("primary_email") else 0) \
        + (1 if hedef_row.get("primary_phone") else 0)
    # olcek arttikca beklenti artar: kucuk buyer kalite>40 yeter, buyuk 70+
    esik = 30.0 + buyer_scale * 8.0
    return kalite >= esik or (kalite >= 40 and kanit >= 2)


@app.get("/api/match")
def api_match(
    buyer_id: str = "",
    nace: str = "",
    osb_id: str = "",
    mode: str = "komple",
    yon: str = "tedarikci",
    min_puan: int = 30,
    limit: int = 20,
    offset: int = 0,
    mask: int = 0,
    user_token: str = "",
    _auth: str = Depends(require_api_key),
) -> dict:
    """V9 smart matching MVP: buyer profiline uygun firmaları puanla.

    - buyer_id verirse: DB'den buyer alınır (nace + osb)
    - yoksa nace (+ opsiyonel osb_id) ile serbest profil
    - mode: komple (komşu sektörler dahil) | ayni (sadece aynı ana grup)
    - yon (Y22): tedarikci (varsayilan) | musteri (ters yon satis kanali) | rakip
      (sadece ayni grup; rakip analizi)
    - user_token: onaylı kullanıcı tokenı → 1 kredi düşülür; kredi bittiyse
      sonuçlar otomatik maskelenir + credit_pack önerisi döner
    """
    mode = mode if mode in ("komple", "ayni") else "komple"
    yon = yon if yon in ("tedarikci", "musteri", "rakip") else "tedarikci"
    limit = max(1, min(limit, 100))

    user = _user_from_token(user_token) if user_token else None
    credit_info = None
    if user is not None and user["status"] == "onayli":
        kalan = _charge_credit(str(user["user_id"]), user["email"], "match")
        if kalan >= 0 and kalan == 0:
            mask = 1  # kredi bitti: sonuc maskele (V8 Credit Exhaustion UX)
            credit_info = {"credit_balance": 0,
                           "notice": "Krediniz tükendi — sonuçlar maskeli görüntüleniyor.",
                           "credit_pack": "750 TRY / 50 kredi (credit pack ile devam edebilirsiniz)"}
        else:
            credit_info = {"credit_balance": kalan if kalan >= 0 else "sinirsiz"}

    buyer_nace, buyer_osb, buyer_adi = nace, osb_id, None
    engine = get_engine()
    buyer_profil = None
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

    # X03 MATCH v3: girisli kullanicinin profili skorlamaya katilir
    if user is not None:
        with engine.connect() as conn:
            up = conn.execute(text(
                "SELECT employee_range, certificates, goal, target_nace FROM users "
                "WHERE user_id = :u"), {"u": str(user["user_id"])}).mappings().first()
        if up:
            buyer_profil = dict(up)

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
        m = _match_puan(d, buyer_grup, buyer_osb or "", mode, yon, buyer_profil)
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
        "yon": yon,
        "profil_uygulandi": bool(buyer_profil),
        "toplam": len(skorlu),
        "limit": limit,
        "offset": offset,
        "items": skorlu[offset:offset + limit],
        "credit": credit_info,
    }

# ── Monetizasyon MVP (V7 Hybrid Credit) ─────────────────────────────────────

import hashlib
import hmac
import time as _time

_FREE_DOMAINS = {"gmail.com", "hotmail.com", "outlook.com", "yandex.com", "yahoo.com",
                 "hotmail.com.tr", "yandex.com.tr", "icloud.com", "protonmail.com"}
_TIER_CREDITS = {"terminal": 100, "strategic": 500, "enterprise": 0}  # 0 = sinirsiz
_DASH_SECRET = os.getenv("DASH_SECRET", (os.getenv("DASH_API_KEY") or "huginn-secret") + "-secret")


def _user_token(email: str) -> str:
    """MVP auth: e-posta + zaman damgali HMAC token (24 saat gecerli)."""
    exp = int(_time.time()) + 86400
    sig = hmac.new(_DASH_SECRET.encode(), f"{email}:{exp}".encode(), hashlib.sha256).hexdigest()[:32]
    return f"{email}|{exp}|{sig}"


_PBKDF2_ITER = 120_000


def _hash_password(password: str) -> str:
    """PBKDF2-SHA256, rastgele 16 bayt salt; format: pbkdf2$iter$salt$hash."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITER)
    return f"pbkdf2${_PBKDF2_ITER}${salt.hex()}${dk.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_hex, hash_hex = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iters))
        return hmac.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False


def _user_from_token(token: str):
    """Token'dan kullaniciyi dogrular; gecersizse None."""
    try:
        email, exp, sig = token.split("|")
        if int(exp) < int(_time.time()):
            return None
        ok = hmac.new(_DASH_SECRET.encode(), f"{email}:{exp}".encode(), hashlib.sha256).hexdigest()[:32]
        if not hmac.compare_digest(ok, sig):
            return None
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(text(
                "SELECT user_id, email, company_name, role, status, tier, credit_balance, api_key "
                "FROM users WHERE email = :e"), {"e": email}).mappings().first()
        return row
    except Exception:
        return None


def _charge_credit(user_id: str, email: str, reason: str, amount: int = 1) -> int:
    """Kredi dusurur (enterprise sinirsiz); yeni bakiyeyi dondurur."""
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text("SELECT tier, credit_balance FROM users WHERE user_id = :u"),
                           {"u": user_id}).mappings().first()
        if not row:
            return 0
        if row["tier"] == "enterprise":
            return -1  # sinirsiz
        yeni = max(int(row["credit_balance"] or 0) - amount, 0)
        conn.execute(text("UPDATE users SET credit_balance = :b, updated_at = CURRENT_TIMESTAMP "
                          "WHERE user_id = :u"), {"b": yeni, "u": user_id})
        conn.execute(text("INSERT INTO credit_ledger (user_id, delta, reason, balance_after) "
                          "VALUES (:u, :d, :r, :b)"), {"u": user_id, "d": -amount, "r": reason, "b": yeni})
    return yeni


@app.post("/api/buyer/register")
def api_buyer_register(req: dict):
    """Kurumsal e-posta + sifre ile kayit. Kurumsal domain dogrulamasi + KVKK zorunlu.
    Sifre PBKDF2-SHA256 ile hash'lenir (ham sifre DB'ye yazilmaz).
    Sonuc: status=onay_bekliyor (admin onayindan sonra onayli + kredi yuklenir)."""
    email = (req.get("email") or "").strip().lower()
    company_name = (req.get("company_name") or "").strip()
    kvkk = bool(req.get("kvkk_consent"))
    password = req.get("password") or ""
    if not email or "@" not in email or not company_name:
        raise HTTPException(status_code=400, detail="email ve company_name zorunlu")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="sifre en az 8 karakter olmali")
    domain = email.split("@")[-1]
    if domain.lower() in _FREE_DOMAINS:
        raise HTTPException(status_code=400, detail=(
            f"'{domain}' kurumsal degil. Lutfen sirket e-postanizla kayit olun "
            "(gmail/outlook vb. kabul edilmez)."))
    if not kvkk:
        raise HTTPException(status_code=400, detail="KVKK aydinlatma metni onayı zorunlu")

    # mevcut 14k kayitla eslesme (web domain eslestirmesi)
    linked = None
    engine = get_engine()
    with engine.begin() as conn:
        dup = conn.execute(text("SELECT user_id, status FROM users WHERE email = :e"), {"e": email}).first()
        if dup:
            raise HTTPException(status_code=409, detail="Bu e-posta zaten kayitli")
        # firma eslestirme: web domain veya benzer unvan
        cweb = (req.get("website") or "").replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        if cweb:
            l = conn.execute(text("SELECT company_id FROM companies WHERE website_domain = :w LIMIT 1"),
                             {"w": cweb}).scalar()
            linked = l
        conn.execute(text("""
            INSERT INTO users (email, email_domain, company_name, linked_company_id, nace_code,
                               products_desc, target_nace, goal, contact_name, website,
                               kvkk_consent, password_hash, status)
            VALUES (:email, :domain, :company_name, :linked, :nace, :products, :target,
                    :goal, :contact, :website, :kvkk, :phash, 'onay_bekliyor')
        """), {"email": email, "domain": domain, "company_name": company_name,
               "linked": linked, "nace": req.get("nace_code"), "products": req.get("products_desc"),
               "target": req.get("target_nace"), "goal": req.get("goal", "tumu"),
               "contact": req.get("contact_name"), "website": req.get("website"),
               "kvkk": kvkk, "phash": _hash_password(password)})
    return {
        "ok": True,
        "status": "onay_bekliyor",
        "message": ("Kaydınız alındı. Kurumsal e-posta doğrulaması ve üyelik onayından sonra "
                    "krediniz yüklenecek. Onay genellikle 1 iş günü içinde tamamlanır."),
        "linked_company_id": str(linked) if linked else None,
    }


@app.get("/api/buyer/categories")
def api_buyer_categories(_auth: str = Depends(require_api_key)) -> dict:
    """Urun katalogu (kayit formunda hedef sektor/urun secimi icin)."""
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT code, label_tr, nace_group, description FROM product_categories "
            "WHERE active = TRUE ORDER BY nace_group, label_tr")).mappings().all()
    return {"items": [dict(r) for r in rows]}


@app.get("/api/buyer/profile")
def api_buyer_profile(token: str = ""):
    """Isletmem sayfasi: profil + kredi + son hareketler."""
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    engine = get_engine()
    with engine.connect() as conn:
        prof = conn.execute(text(
            "SELECT u.user_id, u.email, u.company_name, u.nace_code, u.products_desc, "
            "u.target_nace, u.goal, u.contact_name, u.website, u.department, u.kvkk_consent, "
            "u.employee_range, u.certificates, u.tax_number, u.phone, "
            "u.trade_name, u.address, "
            "u.status, u.tier, u.credit_balance, u.api_key, u.linked_company_id, u.created_at "
            "FROM users u WHERE u.user_id = :u"), {"u": u["user_id"]}).mappings().first()
        ledger = conn.execute(text(
            "SELECT delta, reason, balance_after, created_at FROM credit_ledger "
            "WHERE user_id = :u ORDER BY created_at DESC LIMIT 12"),
            {"u": u["user_id"]}).mappings().all()
        kategori = conn.execute(text(
            "SELECT code, label_tr, nace_group FROM product_categories "
            "WHERE active = TRUE ORDER BY nace_group, label_tr")).mappings().all()
    p = dict(prof) if prof else {}
    # profil tamamlanma skoru (ne kadar cok bilgi = o kadar iyi eslesme)
    alanlar = ["company_name", "nace_code", "products_desc", "target_nace", "goal",
               "department", "website", "contact_name", "employee_range", "certificates"]
    dolu = sum(1 for a in alanlar if p.get(a))
    p["profil_tamlama"] = round(dolu / len(alanlar) * 100)
    return {
        "profil": p,
        "ledger": [dict(r) for r in ledger],
        "kategoriler": [dict(r) for r in kategori],
    }


@app.put("/api/buyer/profile")
def api_buyer_profile_update(req: dict, token: str = ""):
    """Isletmem sayfasindan profil guncelleme (gonullu + onayli kullanici)."""
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    alanlar = {
        "company_name": req.get("company_name"),
        "nace_code": req.get("nace_code"),
        "products_desc": req.get("products_desc"),
        "target_nace": req.get("target_nace"),
        "goal": req.get("goal"),
        "contact_name": req.get("contact_name"),
        "website": req.get("website"),
        "department": req.get("department"),
        "employee_range": req.get("employee_range"),
        "certificates": req.get("certificates"),
        "tax_number": req.get("tax_number"),
        "phone": req.get("phone"),
        "trade_name": req.get("trade_name"),
        "address": req.get("address"),
    }
    sets, params = [], {"u": str(u["user_id"])}
    for k, v in alanlar.items():
        if v is not None:
            sets.append(f"{k} = :{k}")
            params[k] = str(v).strip()
    if not sets:
        raise HTTPException(status_code=400, detail="guncellenecek alan yok")
    sets.append("updated_at = CURRENT_TIMESTAMP")
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"UPDATE users SET {', '.join(sets)} WHERE user_id = :u"), params)
        row = conn.execute(text(
            "SELECT company_name, nace_code, products_desc, target_nace, goal, department, "
            "website, contact_name, employee_range, certificates, tax_number, phone, "
            "trade_name, address, credit_balance, tier "
            "FROM users WHERE user_id = :u"),
            {"u": str(u["user_id"])}).mappings().first()
    alanlar_dolu = sum(1 for a in ["company_name", "nace_code", "products_desc", "target_nace",
                                   "goal", "department", "website", "contact_name",
                                   "employee_range", "certificates"]
                       if row.get(a))
    return {"ok": True, "profil_tamlama": round(alanlar_dolu / 10 * 100), "profil": dict(row)}


@app.get("/api/buyer/ledger")
def api_buyer_ledger(token: str = "", limit: int = 20):
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT delta, reason, balance_after, created_at FROM credit_ledger "
            "WHERE user_id = :u ORDER BY created_at DESC LIMIT :l"),
            {"u": u["user_id"], "l": max(1, min(limit, 50))}).mappings().all()
    return {"items": [dict(r) for r in rows]}

@app.post("/api/buyer/login")
def api_buyer_login(req: dict):
    """E-posta + sifre ile giris. Sifresi olmayan eski MVP kayitlarina ozel:
    password bos gonderilirse ve DB'de hash yoksa giris izin verilir (gecis donemi).
    Onayli kullaniciya 24 saatlik token doner; kredi bakiyesi dahil."""
    email = (req.get("email") or "").strip().lower()
    password = req.get("password") or ""
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="gecerli e-posta girin")
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT user_id, email, status, tier, credit_balance, role, company_name, password_hash "
            "FROM users WHERE email = :e"), {"e": email}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Bu e-posta ile kayit bulunamadi")
    stored = row["password_hash"]
    if stored and not _verify_password(password, stored):
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı")
    if not stored and len(password) < 8:
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı")
    if row["status"] != "onayli":
        durum = "onayınız değerlendiriliyor" if row["status"] == "onay_bekliyor" else "kabul edilmedi"
        raise HTTPException(status_code=403, detail=f"Üyelik onayı: {durum}. Sorularınız için iletişime geçin.")
    return {
        "token": _user_token(row["email"]),
        "user": {
            "email": row["email"], "company_name": row["company_name"],
            "tier": row["tier"], "credit_balance": row["credit_balance"],
            "role": row["role"],
        },
    }


@app.post("/api/buyer/logout")
def api_buyer_logout(req: dict):
    """Cikis: istemci tarafinda token silinir; sunucu tarafi stateless oldugundan
    tokenin kalan suresi kadar gecerliligi teknik olarak surer (MVP notu: tam
    iptal icin token blocklist Scale asamasinda). Donus: ok (istemci temizler)."""
    return {"ok": True, "message": "Cikis yapildi"}


@app.post("/api/buyer/change-password")
def api_buyer_change_password(req: dict, token: str = ""):
    """Oturumdaki kullanici sifresini degistirir (PBKDF2)."""
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    new = req.get("new_password") or ""
    old = req.get("old_password") or ""
    if len(new) < 8:
        raise HTTPException(status_code=400, detail="yeni sifre en az 8 karakter olmali")
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT password_hash FROM users WHERE user_id = :u"),
                           {"u": str(u["user_id"])}).mappings().first()
    if row and row["password_hash"] and not _verify_password(old, row["password_hash"]):
        raise HTTPException(status_code=401, detail="mevcut sifre hatali")
    with engine.begin() as conn:
        conn.execute(text("UPDATE users SET password_hash = :p, updated_at = CURRENT_TIMESTAMP "
                          "WHERE user_id = :u"), {"p": _hash_password(new), "u": str(u["user_id"])})
    return {"ok": True, "message": "sifre guncellendi"}


@app.get("/api/me")
def api_me(token: str = ""):
    u = _user_from_token(token)
    if not u:
        raise HTTPException(status_code=401, detail="oturum gecersiz veya suresi doldu")
    return {"user": dict(u)}


# ── Admin: onay kuyrugu + kredi yonetimi (DASH_API_KEY ile) ─────────────────

def require_admin(authorization: str = Header(None, alias="Authorization"),
                  x_api_key: str = Header(None, alias="X-API-Key"),
                  api_key: str = ""):
    """Yonetici erisimi: DASH_API_KEY VEYA role=admin kullanici tokeni (Bearer)."""
    if (x_api_key or api_key) == (os.getenv("DASH_API_KEY") or ""):
        return "admin-key"
    if authorization:
        tok = authorization.replace("Bearer ", "").strip()
        u = _user_from_token(tok)
        if u and u.get("role") == "admin" and u.get("status") == "onayli":
            return "admin-user"
    raise HTTPException(status_code=403, detail="Yonetici erisimi gerekli")


@app.get("/api/admin/pending")
def api_admin_pending(_auth: str = Depends(require_admin)):
    engine = get_engine()
    with engine.connect() as conn:
        bekleyen = conn.execute(text(
            "SELECT user_id, email, company_name, nace_code, products_desc, target_nace, "
            "goal, website, linked_company_id, created_at FROM users "
            "WHERE status = 'onay_bekliyor' ORDER BY created_at")).mappings().all()
        son = conn.execute(text(
            "SELECT user_id, email, company_name, tier, credit_balance, status, updated_at "
            "FROM users WHERE status = 'onayli' ORDER BY updated_at DESC LIMIT 10")).mappings().all()
    return {"bekleyen": [dict(r) for r in bekleyen], "onayli_son": [dict(r) for r in son]}


@app.post("/api/admin/approve")
def api_admin_approve(req: dict, _auth: str = Depends(require_admin)):
    """Onayla: tier sec (terminal/strategic/enterprise) -> kredi yukle + enterprise'a api_key uret."""
    user_id = req.get("user_id") or ""
    tier = req.get("tier") or "terminal"
    reject = bool(req.get("reject"))
    note = req.get("note") or ""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id zorunlu")
    try:
        uuid.UUID(user_id)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(status_code=400, detail="user_id UUID olmali")
    kredi = _TIER_CREDITS.get(tier, 100)
    api_key = None
    engine = get_engine()
    with engine.begin() as conn:
        u = conn.execute(text("SELECT email, tier, status FROM users WHERE user_id = :u"),
                         {"u": user_id}).mappings().first()
        if not u:
            raise HTTPException(status_code=404, detail="kullanici bulunamadi")
        if reject:
            conn.execute(text("UPDATE users SET status='reddedildi', rejection_note=:n, "
                              "updated_at=CURRENT_TIMESTAMP WHERE user_id=:u"),
                         {"n": note, "u": user_id})
            return {"ok": True, "status": "reddedildi"}
        if tier == "enterprise":
            api_key = "ent_" + hmac.new(_DASH_SECRET.encode(), user_id.encode(),
                                        hashlib.sha256).hexdigest()[:32]
            conn.execute(text("UPDATE users SET status='onayli', tier=:t, credit_balance=0, "
                              "api_key=:k, updated_at=CURRENT_TIMESTAMP WHERE user_id=:u"),
                         {"t": tier, "k": api_key, "u": user_id})
            yeni = -1
        else:
            conn.execute(text("UPDATE users SET status='onayli', tier=:t, credit_balance=:b, "
                              "updated_at=CURRENT_TIMESTAMP WHERE user_id=:u"),
                         {"t": tier, "b": kredi, "u": user_id})
            yeni = kredi
        conn.execute(text("INSERT INTO credit_ledger (user_id, delta, reason, balance_after) "
                          "VALUES (:u, :d, 'approve', :b)"), {"u": user_id, "d": kredi, "b": yeni})
    return {"ok": True, "status": "onayli", "tier": tier, "credit_balance": yeni,
            "api_key": api_key}


@app.post("/api/admin/credit")
def api_admin_credit(req: dict, _auth: str = Depends(require_admin)):
    """Credit Pack / manuel kredi yukleme (750 TRY/50 kredi vb.)."""
    user_id = req.get("user_id") or ""
    amount = int(req.get("amount") or 0)
    if not user_id or amount <= 0:
        raise HTTPException(status_code=400, detail="user_id ve pozitif amount zorunlu")
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text("SELECT credit_balance, tier FROM users WHERE user_id = :u"),
                           {"u": user_id}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="kullanici bulunamadi")
        yeni = int(row["credit_balance"] or 0) + amount
        conn.execute(text("UPDATE users SET credit_balance=:b, updated_at=CURRENT_TIMESTAMP "
                          "WHERE user_id=:u"), {"b": yeni, "u": user_id})
        conn.execute(text("INSERT INTO credit_ledger (user_id, delta, reason, balance_after) "
                          "VALUES (:u, :d, 'credit_pack', :b)"),
                     {"u": user_id, "d": amount, "b": yeni})
    return {"ok": True, "credit_balance": yeni}


@app.get("/api/admin/api-usage")
def api_admin_api_usage(_auth: str = Depends(require_admin)):
    """Y26: Tier bazli API kullanim raporu (enterprise key istek sayacları)."""
    return {"items": api_usage_snapshot(), "rate_limits": dict(_TIER_RATE_LIMITS)}


@app.post("/api/admin/rotate-key")
def api_admin_rotate_key(req: dict, _auth: str = Depends(require_admin)):
    """Y26: Enterprise kullanicinin API key'ini yeniler (eski key gecersiz olur).
    Girdi: user_id. Cikti: yeni api_key (bir kez gorunur)."""
    user_id = req.get("user_id") or ""
    try:
        uuid.UUID(user_id)
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(status_code=400, detail="user_id UUID olmali")
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text(
            "SELECT email, tier, status FROM users WHERE user_id = :u"),
            {"u": user_id}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="kullanici bulunamadi")
        if row["tier"] != "enterprise":
            raise HTTPException(status_code=400, detail="key rotasyonu yalnizca enterprise tier icin")
        yeni = "ent_" + hmac.new(_DASH_SECRET.encode(),
                                 f"{user_id}:{_time.time()}".encode(),
                                 hashlib.sha256).hexdigest()[:32]
        conn.execute(text(
            "UPDATE users SET api_key = :k, updated_at = CURRENT_TIMESTAMP WHERE user_id = :u"),
            {"k": yeni, "u": user_id})
    return {"ok": True, "api_key": yeni}


@app.get("/api/admin/categories")
def api_admin_categories(_auth: str = Depends(require_admin)):
    """Y25: Urun katalogu yonetimi - tum kategoriler (aktif + pasif)."""
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT category_id, code, label_tr, nace_group, description, active, created_at "
            "FROM product_categories ORDER BY nace_group, code")).mappings().all()
    return {"items": [dict(r) for r in rows]}


@app.post("/api/admin/categories")
def api_admin_categories_save(req: dict, _auth: str = Depends(require_admin)):
    """Kategori ekle/guncelle. category_id varsa guncelle, yoksa yeni olustur.
    active=false ile pasiflesirme (kayit silinmez, kayit formunda kaybolur)."""
    code = (req.get("code") or "").strip().upper()
    label_tr = (req.get("label_tr") or "").strip()
    nace_group = (req.get("nace_group") or "").strip() or None
    description = (req.get("description") or "").strip() or None
    active = bool(req.get("active", True))
    category_id = req.get("category_id") or None
    if not code or not label_tr:
        raise HTTPException(status_code=400, detail="code ve label_tr zorunlu")
    if len(code) > 20:
        raise HTTPException(status_code=400, detail="code en fazla 20 karakter")
    if nace_group and not nace_group.isdigit():
        raise HTTPException(status_code=400, detail="nace_group 2 haneli sayi olmali (orn. 29)")
    engine = get_engine()
    with engine.begin() as conn:
        if category_id:
            try:
                uuid.UUID(str(category_id))
            except (ValueError, AttributeError, TypeError):
                raise HTTPException(status_code=400, detail="category_id UUID olmali")
            row = conn.execute(text(
                "SELECT code FROM product_categories WHERE category_id = :c"),
                {"c": category_id}).mappings().first()
            if not row:
                raise HTTPException(status_code=404, detail="kategori bulunamadi")
            if row["code"] != code:
                dup = conn.execute(text(
                    "SELECT 1 FROM product_categories WHERE code = :k"), {"k": code}).first()
                if dup:
                    raise HTTPException(status_code=409, detail="Bu code zaten kayitli")
            conn.execute(text(
                "UPDATE product_categories SET code=:k, label_tr=:l, nace_group=:n, "
                "description=:d, active=:a WHERE category_id=:c"),
                {"k": code, "l": label_tr, "n": nace_group, "d": description, "a": active,
                 "c": category_id})
            return {"ok": True, "updated": True}
        dup = conn.execute(text(
            "SELECT 1 FROM product_categories WHERE code = :k"), {"k": code}).first()
        if dup:
            raise HTTPException(status_code=409, detail="Bu code zaten kayitli")
        conn.execute(text(
            "INSERT INTO product_categories (code, label_tr, nace_group, description, active) "
            "VALUES (:k, :l, :n, :d, :a)"),
            {"k": code, "l": label_tr, "n": nace_group, "d": description, "a": active})
    return {"ok": True, "created": True}

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
