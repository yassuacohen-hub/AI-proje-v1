# -*- coding: utf-8 -*-
"""web_app.py ikinci duzeltme paketi:
1) Combo kisaltmalar nokta ile bitse bile eslesir ((?!\\w) sonu).
2) extract_trade_name: kisaltmasiz orijinal formdan, iki katmanli
   stop-word ile tabela ismi uretir (Kural 3 ornekleriyle uyumlu).
"""
from pathlib import Path

p = Path(r"C:\Projeler\Huginn Data Insights\web_app.py")
src = p.read_text(encoding="utf-8")

# 1) _tr_rx: combo icin yumusak son (nokta engellemeyen) varyant ekle
old = """def _tr_rx(phrase: str) -> str:
    \"\"\"Kelime sinirlu + Turkce duyarsiz regex uretir.\"\"\"
    return r'(?<!\\w)' + _tr_insensitive(_re.escape(phrase)) + r'(?![\\w.])'"""
new = """def _tr_rx(phrase: str) -> str:
    \"\"\"Kelime sinirlu + Turkce duyarsiz regex uretir (nokta dahil engel).\"\"\"
    return r'(?<!\\w)' + _tr_insensitive(_re.escape(phrase)) + r'(?![\\w.])'


def _tr_rx_soft_end(phrase: str) -> str:
    \"\"\"Turkce duyarsiz + basi kelime sinirli; sonda sadece harf engellenir.
    Nokta ile biten combo anahtarlari (r'SAN VE TIC') icin gerekli.\"\"\"
    return r'(?<!\\w)' + _tr_insensitive(_re.escape(phrase)) + r'(?!\\w)'"""
assert old in src, "_tr_rx blok yok"
src = src.replace(old, new)

# 2) COMBO dongusu soft-end kullansin
old = """    for long_phrase, short_form in sorted(_COMBO_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx(long_phrase), short_form, name)"""
new = """    for long_phrase, short_form in sorted(_COMBO_ABBR.items(), key=lambda x: -len(x[0])):
        name = _re.sub(_tr_rx_soft_end(long_phrase), short_form, name)"""
assert old in src, "combo dongu yok"
src = src.replace(old, new)

# 3) extract_trade_name'i iki katmanli stop-word ile yeniden yaz
start = src.find("def extract_trade_name(legal_name: str) -> str:")
end = src.find("def normalize_company(row: dict) -> dict:")
assert start != -1 and end != -1, "extract_trade_name sinirlari bulunamadi"

new_trade = '''# Tabela ismi icin iki katmanli stop-word:
#   HARD  -> her zaman cikar (sirket turu, baglaclar, SAN/TIC)
#   SOFT  -> faaliyet kelimeleri; yalnizca baska marka kelimesi varken cikar
_TRADE_NAME_STOP_HARD = frozenset({
    'VE', 'ILE', 'BI', 'AMMA', 'LAKIK',
    'SAN.', 'SAN', 'SANAYI', 'SANAYII', 'TIC.', 'TIC', 'TICARET', 'TICARETI',
    'LTD. ŞTI.', 'LTD. STI.', 'LTD.', 'LTD', 'A.S.', 'A.S', 'A.Ş.', 'A.Ş',
    'STI.', 'STI', 'ŞTI.', 'ŞTI', 'SIRKETI', 'SIRKET', 'ANONIM', 'ANONIM ŞIRKETI',
    'ORT.', 'ORT', 'ORTAKLIK', 'KOL. ŞTI.', 'KOM. ŞTI.', 'KOOP.', 'KOOP',
    'KOLLEKTIF', 'KOMANDIT', 'TAS', 'TAO', 'DTM', 'KOBI',
})
_TRADE_NAME_STOP_SOFT = frozenset({
    'PAZ.', 'PAZ', 'ITH.', 'ITH', 'IHR.', 'IHR', 'MUH.', 'MUH', 'MIM.', 'MIM',
    'İNŞ.', 'INS.', 'INS', 'INŞ', 'INSAAT', 'NAK.', 'NAK', 'OTO.', 'OTO',
    'TUR.', 'TUR', 'TEK.', 'TEK', 'HIZM.', 'HIZM', 'TAR.', 'TAR', 'MAD.', 'MAD',
    'IMAL.', 'IMAL', 'BIL.', 'BIL', 'YAZ.', 'YAZ', 'MAK.', 'MAK', 'MAKINA', 'MAKINE',
    'MOB.', 'MOB', 'ELEK.', 'ELEK', 'KIM.', 'KIM', 'GIDA', 'TEKSTIL', 'TEKstil'.upper(),
    'MOBILYA', 'MUHENDISLIK', 'MIMARLIK', 'OTOMOTIV', 'NAKLIYAT', 'NAKLIYE',
    'PAZARLAMA', 'ITHALAT', 'IHRACAT', 'ELEKTRIK', 'ELEKTRONIK', 'BILISIM',
    'YAZILIM', 'IMAlAT'.upper(), 'TURIZM', 'HIZMET', 'HIZMETLERI',
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
    ve SAN/TIC (HARD) her zaman; faaliyet kelimeleri (SOFT) marka kelimesi
    varken atlanir. Ilk 2-3 kelime alinir.
    Ornekler:
        "DÜNDAR ELEKTRİK SANAYİ"            -> "DÜNDAR ELEKTRİK"
        "ARITES METAL SANAYI VE TICARET..." -> "ARITES METAL"
        "GIDA SANAYI VE TICARET A.Ş."       -> "GIDA"
        "BUYUK AGAC MOB.INS.SAN. VE TIC..." -> "BUYUK AGAC"
    """
    if not legal_name:
        return ""
    raw = _re.sub(r'\\s{2,}', ' ', str(legal_name).upper().strip())
    words = [w for w in _re.split(r'[\\s.]+', raw) if w]

    full = [w for w in words
            if len(w) > 1
            and not _trade_is_stop(w, _TRADE_STOP_HARD_FOLDED)
            and not _trade_is_stop(w, _TRADE_STOP_SOFT_FOLDED)]
    if full:
        return ' '.join(full[:3])

    # Tum kelimeler HARD/SOFT'a carpti -> HARD disi (faaliyet) ilk kelimeyi marka yap
    hard_kept = [w for w in words
                 if len(w) > 1 and not _trade_is_stop(w, _TRADE_STOP_HARD_FOLDED)]
    if hard_kept:
        return hard_kept[0]

    # Son care: sadece baglaclari at, ilk iki kelimeyi ver
    minimal = [w for w in words if w.translate(_TRADE_FOLD_MAP) not in ('VE', 'ILE') and len(w) > 1]
    return ' '.join(minimal[:2]) if minimal else raw

'''
src = src[:start] + new_trade + src[end:]

p.write_text(src, encoding="utf-8", newline="")
print("web_app.py 2. duzeltme paketi uygulandi")
