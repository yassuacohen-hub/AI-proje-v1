"""Normalize.py dosyasini gunceller - tam versiyon."""
import re
from py_compile import compile

path = r'C:\Projeler\Huginn Data Insights\src\company_master\etl\normalize.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Docstring guncelle
content = content.replace(
    'ANA KURAL:\n  - Firma adlari (legal_name) her zaman BUYUK HARFLE yazilir.\n  - Ticaret adi (trade_name) = firmanin ilk 2 KELIMESI (hece degil).\n    Ornek: "Dundar Elektrik Sanayi" -> "DUNDAR ELEKTRIK"',
    'ANA KURAL (V10/09_kurallar_ve_promptlar/11_unvan_kisaltma_ve_tabela_kurallari):\n  - Kural 1: Firma adlari (legal_name) her zaman BUYUK HARFLE yazilir.\n  - Kural 2: Uzun ifadeler standart kisaltilir (SANAYI VE TICARET -> SAN. VE TIC.)\n  - Kural 3: Tabela ismi (trade_name) = marka/ilgi alani (ilk 2-3 kelime,\n    sirket turu/faaliyet kisaltilari ve "VE" blogunu gecer)'
)
print('1. Docstring güncellendi')

# 2. Eski blocku yeni kodla degistir
new_code = '''# ── ANA KURAL: Firma ad normalizasyonu (ingest-time) ──
# Kural 1: Firma adlari her zaman BUYUK HARFLE yazilir
# Kural 2: Uzun ifadeler standart kisaltilir
# Kural 3: Tabela ismi = ilgi alani/marka (ilk 2-3 kelime, VE/Şirket Tur/ Faaliyet filtrelenerek)

_COMPANY_TYPE_ABBR = {
    'ANONIM SIRKETI': 'A.S.', 'ANONIM SIRKET': 'A.S.', 'ANONIM ORTAKLIK': 'A.S.',
    'ANONIM ORTAKLIGI': 'A.S.', 'LIMITED SIRKETI': 'LTD. STI.', 'LIMITED SIRKET': 'LTD. STI.',
    'LTD. SIRKETI': 'LTD. STI.', 'LTD. SIRKET': 'LTD. STI.', 'LIMITED': 'LTD. STI.',
    'LTD': 'LTD. STI.', 'KOLLEKTIF SIRKETI': 'KOL. STI.', 'KOLLEKTIF SIRKET': 'KOL. STI.',
    'KOMANDIT SIRKETI': 'KOM. STI.', 'KOMANDIT SIRKET': 'KOM. STI.',
    'ORTAKLIK': 'ORT.', 'ORTAKLIGI': 'ORT.', 'ADI ORTAKLIK': 'ORT.', 'ADI ORTAKLIGI': 'ORT.',
    'TURK ANONIM SIRKETI': 'TAS', 'TURK ANONIM ORTAKLIK': 'TAS', 'KOOPERATIF': 'KOOP.',
}

_ACTIVITY_ABBR = {
    'SANAYI': 'SAN.', 'SANAYII': 'SAN.', 'TICARET': 'TIC.', 'TICARETI': 'TIC.',
    'PAZARLAMA': 'PAZ.', 'ITHALAT': 'ITH.', 'IHRACAT': 'IHR.',
    'MUHENDISLIK': 'MUH.', 'MUHENDIS': 'MUH.', 'MIMARLIK': 'MIM.', 'MIMAR': 'MIM.',
    'INSANAT': 'INS.', 'INSAA': 'INS.', 'NAKLIYAT': 'NAK.', 'NAKLIYE': 'NAK.',
    'TASICILIK': 'NAK.', 'OTOMOTIV': 'OTO.', 'OTOMOBIL': 'OTO.', 'TURIZM': 'TUR.',
    'TEKSTIL': 'TEK.', 'GIDA': 'GIDA', 'HIZMET': 'HIZM.', 'HIZMETLERI': 'HIZM.',
    'TARIM': 'TAR.', 'TARIMSAL': 'TAR.', 'MADENCILIK': 'MAD.', 'MADEN': 'MAD.',
    'IMALAT': 'IMAL.', 'BILISIM': 'BIL.', 'BILGISAYAN': 'BIL.', 'YAZILIM': 'YAZ.',
    'MAKINE': 'MAK.', 'MAKINA': 'MAK.', 'MOBILYA': 'MOB.',
    'ELEKTRIK': 'ELEK.', 'ELEKTRONIK': 'ELEK.', 'KIMYA': 'KIM.', 'KIMYAVI': 'KIM.',
}

_COMBO_ABBR = {
    'SANAYI VE TICARET': 'SAN. VE TIC.', 'SANAYII VE TICARETI': 'SAN. VE TIC.',
    'TICARET VE SANAYI': 'TIC. VE SAN.', 'TICARETI VE SANAYII': 'TIC. VE SAN.',
    'ITHALAT VE IHRACAT': 'ITH. IHR.', 'IHRACAT VE ITHALAT': 'IHR. ITH.',
    'INSANAT SANAYI VE TICARET': 'INS. SAN. TIC.',
    'MUHENDISLIK MIMARLIK': 'MUH. MIM.', 'TURIZM VE TICARET': 'TUR. TIC.',
    'GIDA SANAYI VE TICARET': 'GIDA SAN. TIC.',
    'TEKSTIL SANAYI VE TICARET': 'TEK. SAN. TIC.',
    'NAKLIYAT VE TICARET': 'NAK. TIC.',
}

_TRADE_NAME_STOP_WORDS = frozenset({
    'VE', 'ILE', 'BI', 'AMMA', 'LAKIK',
    'SAN.', 'SANAYI', 'SANAYII', 'TIC.', 'TICARET', 'TICARETI',
    'LTD. STI.', 'LTD. STI', 'LTD.', 'LTD', 'A.S.', 'A.S', 'A.Ş.', 'A.Ş',
    'STI.', 'STI', 'ORT.', 'ORT', 'KOL. STI.', 'KOM. STI.', 'KOOP.',
    'PAZ.', 'ITH.', 'IHR.', 'MUH.', 'MIM.', 'INS.', 'NAK.', 'OTO.',
    'TUR.', 'TEK.', 'GIDA', 'HIZM.', 'TAR.', 'MAD.', 'IMAL.',
    'BIL.', 'YAZ.', 'MAK.', 'MOB.', 'ELEK.', 'KIM.',
    'KOOP', 'Tas', 'TAO', 'DTM', 'KOBI',
})


def normalize_company_name(name: str) -> str:
    """Firma adini BUYUK HARFE cevirir ve standart kisaltilari uygular."""
    if not name:
        return ""
    name = str(name).upper().strip()
    name = re.sub(r'\\s{2,}', ' ', name)
    for long_phrase, short_form in sorted(_COMBO_ABBR.items(), key=lambda x: -len(x[0])):
        name = name.replace(long_phrase, short_form)
    for long_phrase, short_form in sorted(_ACTIVITY_ABBR.items(), key=lambda x: -len(x[0])):
        name = re.sub(r'\\b' + re.escape(long_phrase) + r'\\b', short_form, name)
    for long_phrase, short_form in sorted(_COMPANY_TYPE_ABBR.items(), key=lambda x: -len(x[0])):
        name = re.sub(r'\\b' + re.escape(long_phrase) + r'\\b', short_form, name)
    return re.sub(r'\\s{2,}', ' ', name).strip()


def extract_trade_name(legal_name: str) -> str:
    """Uzun sirket adindan tabela ismini cikarir. Ilk 2-3 kelime, VE/Şirket Tur/ Faaliyet atlanir."""
    if not legal_name:
        return ""
    normalized = normalize_company_name(legal_name)
    words = re.split(r'[\\s.]+', normalized)
    filtered = [w for w in words if w and w not in _TRADE_NAME_STOP_WORDS and len(w) > 1]
    if not filtered:
        filtered = [w for w in words if w and w not in ('VE', 'ILE')]
    return ' '.join(filtered[:3])'''

# Regex ile eski blocku bul ve degistir
pattern = re.compile(
    r'# ── ANA KURAL:.*?return \' \'\.join\(words\[:2\]\)',
    re.DOTALL
)

match = pattern.search(content)
if match:
    content = content[:match.start()] + new_code + content[match.end():]
    print('2. Eski fonksiyonlar yeni ile değiştirildi')
else:
    print('✗ Eski block bulunamadı')
    idx = content.find('_SIRKET_TIPI')
    if idx >= 0:
        print(f'  _SIRKET_TIPI bulundu: {idx}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'3. {path} güncellendi ({len(content)} karakter)')

# Syntax kontrolu
try:
    compile(path, doraise=True)
    print('✓ Syntax OK')
except Exception as e:
    print(f'✗ Syntax error: {e}')