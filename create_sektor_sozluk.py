# -*- coding: utf-8 -*-
"""VERI-SEKTOR-01: Sektör sözlüğü oluşturma ve kolon ekleme"""

import json
import re
from pathlib import Path

# Turkish character fixes for mojibake
REPLACEMENTS = {
    # Common UTF-8 double-encoding / mojibake patterns
    'Ã§': 'ç', 'Ã¼': 'ü', 'Ä±': 'ı', 'ÄŸ': 'ğ', 'ÅŸ': 'ş', 'Ã¶': 'ö',
    'Ã‡': 'Ç', 'Ãœ': 'Ü', 'Ä°': 'İ', 'Ä': 'Ğ', 'ÅŸ': 'Ş', 'Ã–': 'Ö',
    'Ã¢': 'â', 'Ã¢': 'â',
    'Đ': 'Ğ', 'đ': 'ğ',
    'Ý': 'İ', 'ý': 'ı',
    'ÅŸ': 'ş', 'Å': 'İ', 'Ÿ': 'ş', 'ž': 'ş',
    'Ã§': 'ç', 'Ã¼': 'ü', 'Ä±': 'ı', 'ÄŸ': 'ğ', 'ÅŸ': 'ş', 'Ã¶': 'ö',
    'Ã‡': 'Ç', 'Ãœ': 'Ü', 'Ä°': 'İ', 'Ä': 'Ğ', 'ÅŸ': 'Ş', 'Ã–': 'Ö',
    'Ã¢': 'â', 'Ã¢': 'â',
    'Đ': 'Ğ', 'đ': 'ğ',
    'Ý': 'İ', 'ý': 'ı',
    'ÅŸ': 'ş', 'Å': 'İ', 'Ÿ': 'ş', 'ž': 'ş',
    'Ã§': 'ç', 'Ã¼': 'ü', 'Ä±': 'ı', 'ÄŸ': 'ğ', 'ÅŸ': 'ş', 'Ã¶': 'ö',
    'Ã‡': 'Ç', 'Ãœ': 'Ü', 'Ä°': 'İ', 'Ä': 'Ğ', 'ÅŸ': 'Ş', 'Ã–': 'Ö',
    'Ã¢': 'â', 'Ã¢': 'â',
    # Additional patterns from output
    '¬': 'ü', '¯': 'ı', '': 'ğ', '¶': 'ö', '§': 'ş', '·': 'ç',
    '©': 'ç', 'ª': 'ü', '«': 'ğ', '®': 'ö', '¬': 'ü', '­': 'ı', '°': 'ğ', '±': 'ö', '²': 'ş', '³': 'ç',
    '¸': 'ü', '¹': 'ı', 'º': 'ğ', '»': 'ö', '¼': 'ü', '½': 'ı', '¾': 'ğ', '¿': 'ö',
    'À': 'İ', 'Á': 'ı', 'Â': 'ğ', 'Ã': 'ö', 'Ä': 'ş', 'Å': 'ç', 'Æ': 'İ', 'Ç': 'ı', 'È': 'ğ', 'É': 'ö', 'Ê': 'ş', 'Ë': 'ç', 'Ì': 'İ', 'Í': 'ı', 'Î': 'ğ', 'Ï': 'ö', 'Ð': 'ş', 'Ñ': 'ç', 'Ò': 'İ', 'Ó': 'ı', 'Ô': 'ğ', 'Õ': 'ö', 'Ö': 'ş', '×': 'ç', 'Ø': 'İ', 'Ù': 'ı', 'Ú': 'ğ', 'Û': 'ö', 'Ü': 'ş', 'Þ': 'ç', 'ß': 'İ', 'à': 'ı', 'á': 'ğ', 'â': 'ö', 'ã': 'ş', 'ä': 'ç', 'å': 'İ', 'æ': 'ı', 'ç': 'ğ', 'è': 'ö', 'é': 'ş', 'ê': 'ç', 'ë': 'İ', 'ì': 'ı', 'í': 'ğ', 'î': 'ö', 'ï': 'ş', 'ð': 'ç', 'ñ': 'İ', 'ò': 'ı', 'ó': 'ğ', 'ô': 'ö', 'õ': 'ş', 'ö': 'ç', '÷': 'İ', 'ø': 'ı', 'ù': 'ğ', 'ú': 'ö', 'û': 'ş', 'ü': 'ç', 'ý': 'İ', 'þ': 'ı', 'ÿ': 'ğ',
}

def fix_mojibake(text: str) -> str:
    """Fix common mojibake patterns in Turkish text."""
    if not text:
        return text
    result = text
    for wrong, correct in REPLACEMENTS.items():
        result = result.replace(wrong, correct)
    # Clean up any remaining non-printable characters
    result = ''.join(c for c in result if c.isprintable() or c in ' \t\n\r')
    return result

def normalize_sector(text: str) -> str:
    """Normalize sector name: fix mojibake, remove counter suffixes, uppercase."""
    if not text:
        return ""
    
    # Fix mojibake
    s = fix_mojibake(text)
    
    # Remove trailing counter numbers (e.g., "Otomotiv1163" -> "Otomotiv")
    s = re.sub(r'\d+$', '', s)
    
    # Remove any remaining trailing dots/spaces
    s = s.rstrip('. ')
    
    s = s.strip()
    return s

def get_display_name(normalized: str) -> str:
    """Convert normalized name to proper display format (Title Case with Turkish)."""
    if not normalized:
        return ""
    words = normalized.split()
    result = []
    for word in words:
        if word.isupper() and len(word) > 2:
            result.append(word)
        else:
            result.append(word.capitalize())
    return ' '.join(result)

# Raw sector values from database (with mojibake)
RAW_SECTORS = [
    "Otomotiv1163",
    "Metalurji ve Makina Sanayi",
    "Yapı ve İnşaat794",
    "Gıda ve Endüstriyel Mutfak",
    "Makine ve Makine Ekipmanları757",
    "Metal ve Metal İşlemesi752",
    "İş Makinaları780",
    "Otomotiv",
    "Çeşitli Ticari Faaliyetler410",
    "Diğer",
    "Hizmetler380",
    "Elektrik ve Elektronik390",
    "Teknik Malzeme Tezgah ve Ekipman339",
    "Yapı ve İnşaat",
    "Teknoloji ve Bilişim",
    "Teknoloji ve Bilişim192",
    "Metal ve Metal İşlemesi",
    "Hizmetler",
    "Ambalaj - Kağıt - Basım ve Kırtasiye127",
    "Çeşitli Ticari Faaliyetler",
    "KIMYA-LABARATUVAR",
    "Kimyasallar - Boya - Temizlik ve Güvenlik110",
    "Gıda ve Endüstriyel Mutfak98",
    "Plastik ve Kauçuk114",
    "Tekstil ve Deri71",
    "Savunma",
    "GIDA",
    "İş Makinaları",
    "Sağlık78",
    "Medikal - İlaç",
    "30. MESLEK GRUBU",
    "21. MESLEK GRUBU",
    "17. MESLEK GRUBU",
    "24. MESLEK GRUBU",
    "25. MESLEK GRUBU",
    "31. MESLEK GRUBU",
    "16. MESLEK GRUBU",
    "Makine ve Makine Ekipmanları",
    "35. MESLEK GRUBU",
    "39. MESLEK GRUBU",
    "Kimyasallar - Boya - Temizlik ve Güvenlik",
    "34. MESLEK GRUBU",
    "41. MESLEK GRUBU",
    "26. MESLEK GRUBU",
    "Endüstriyel Market",
    "13. MESLEK GRUBU",
    "Elektrikli Cihaz Sanayi",
    "22. MESLEK GRUBU",
    "11. MESLEK GRUBU",
    "03. MESLEK GRUBU",
    "23. MESLEK GRUBU",
    "28. MESLEK GRUBU",
    "Teknik Malzeme Tezgah ve Ekipman",
    "20. MESLEK GRUBU",
    "Maden",
    "31. MESLEK GRUBU",
    "09. MESLEK GRUBU",
    "08. MESLEK GRUBU",
    "Sağlık",
    "Kent Mobilyaları ve Peyzaj16",
    "Mobilya",
    "38. MESLEK GRUBU",
    "Ziraat",
    "15. MESLEK GRUBU",
    "14. MESLEK GRUBU",
    "01. MESLEK GRUBU",
    "27. MESLEK GRUBU",
    "02. MESLEK GRUBU",
    "40. MESLEK GRUBU",
    "Matbaa",
    "07. MESLEK GRUBU",
    "06. MESLEK GRUBU",
    "18. MESLEK GRUBU",
    "37. MESLEK GRUBU",
    "Hırdavat",
    "HİZMET-DANIŞMANLIK",
    "Ambalaj - Kağıt - Basım ve Kırtasiye",
    "33. MESLEK GRUBU",
    "Plastik ve Kauçuk",
    "22. MESLEK GRUBU",
    "05. MESLEK GRUBU",
    "12. MESLEK GRUBU",
    "32. MESLEK GRUBU",
    "19. MESLEK GRUBU",
    "10. MESLEK GRUBU",
    "Elektrik ve Elektronik",
    "Kargo",
    "36. MESLEK GRUBU",
    "HİZMET-ÇALIŞMA",
    "Muhtelif Gaz Dolum",
    "Tekstil",
    "29. MESLEK GRUBU",
    "Kent Mobilyaları ve Peyzaj",
    "Perakende",
    "Tekstil ve Deri",
    "HİZMET-ÇSG",
    "GIDA",
    "Gıda ve Endüstriyel Mutfak",
    "İş Makinaları",
    "Sağlık",
    "Medikal - İlaç",
    "Kent Mobilyaları ve Peyzaj",
    "Muhtelif Gaz Dolum",
    "Tekstil",
    "Perakende",
    "Tekstil ve Deri",
    "HİZMET-ÇSG",
    "Otomotiv",
    "Metalurji ve Makina Sanayi",
    "Yapı ve İnşaat",
    "Gıda ve Endüstriyel Mutfak",
    "Makine ve Makine Ekipmanları",
    "Metal ve Metal İşlemesi",
    "İş Makinaları",
    "Otomotiv",
    "Çeşitli Ticari Faaliyetler",
    "Diğer",
    "Hizmetler",
    "Elektrik ve Elektronik",
    "Teknik Malzeme Tezgah ve Ekipman",
    "Yapı ve İnşaat",
    "Teknoloji ve Bilişim",
    "Metal ve Metal İşlemesi",
    "Hizmetler",
    "Ambalaj - Kağıt - Basım ve Kırtasiye",
    "Çeşitli Ticari Faaliyetler",
    "KIMYA-LABARATUVAR",
    "Kimyasallar - Boya - Temizlik ve Güvenlik",
    "Gıda ve Endüstriyel Mutfak",
    "Plastik ve Kauçuk",
    "Tekstil ve Deri",
    "Savunma",
    "GIDA",
    "İş Makinaları",
    "Sağlık",
    "Medikal - İlaç",
    "Kent Mobilyaları ve Peyzaj",
    "Muhtelif Gaz Dolum",
    "Tekstil",
    "Perakende",
    "Tekstil ve Deri",
    "HİZMET-ÇSG",
]

def normalize_sector(text: str) -> str:
    """Normalize sector name: remove counter suffixes, strip."""
    if not text:
        return ""
    s = str(text).strip()
    # Remove trailing counter numbers
    s = re.sub(r'\d+$', '', s)
    s = s.rstrip('. ')
    s = s.strip()
    return s

def get_display_name(normalized: str) -> str:
    """Convert normalized name to proper display format."""
    if not normalized:
        return ""
    words = normalized.split()
    result = []
    for word in words:
        if word.isupper() and len(word) > 2:
            result.append(word)
        else:
            result.append(word.capitalize())
    return ' '.join(result)

# Filter out ASO meslek grubu patterns (N. MESLEK GRUBU)
def is_aso_meslek_grubu(text: str) -> bool:
    """Check if text is an ASO meslek grubu code (N. MESLEK GRUBU format)."""
    if not text:
        return False
    # Pattern: N. MESLEK GRUBU or NN. MESLEK GRUBU
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

def main():
    print("Creating sector dictionary...")
    
    # Normalize all raw sectors
    normalized_sectors = []
    for s in RAW_SECTORS:
        norm = normalize_sector(s)
        if not is_aso_meslek_grubu(norm):
            normalized_sectors.append(norm)
    
    # Get unique normalized sectors
    unique_normalized = list(set(normalized_sectors))
    unique_normalized.sort()
    
    print(f"Total unique normalized sectors (excluding ASO): {len(unique_normalized)}")
    
    # Build dictionary entries
    sektör_sozluk = []
    for norm in unique_normalized:
        display = get_display_name(norm)
        
        # Determine nace_ipucu based on sector name
        nace_ipucu = []
        sector_lower = norm.lower()
        
        # Simple keyword-based NACE hints
        nace_hints = {
            'otomotiv': ['29'],
            'metalurji': ['24', '25'],
            'metal ve metal': ['24', '25'],
            'yapı ve inşaat': ['41', '42', '43'],
            'gıda': ['10', '11'],
            'makine': ['28'],
            'metal ve metal işlemesi': ['25'],
            'iş makinaları': ['28'],
            'otomotiv': ['29'],
            'çeşitli ticari faaliyetler': ['46', '47'],
            'diğer': [],
            'hizmetler': ['46', '47', '49', '50', '51', '52', '53', '55', '56', '58', '59', '60', '61', '62', '63', '64', '65', '66', '68', '69', '70', '71', '72', '73', '74', '75', '77', '78', '78', '79', '80', '81', '82', '84', '85', '86', '87', '88', '90', '91', '92', '93', '94', '95', '96'],
            'elektrik ve elektronik': ['26', '27'],
            'tekstil ve deri': ['13', '14', '15'],
            'savunma': ['25'],
            'gıda': ['10', '11'],
            'iş makinaları': ['28'],
            'sağlık': ['21', '26', '32', '86', '87', '88'],
            'medikal': ['21', '26', '32'],
            'kent mobilyaları': ['31'],
            'muhtelif gaz dolum': ['20'],
            'tekstil': ['13', '14', '15'],
            'perakende': ['47'],
            'tekstil ve deri': ['13', '14', '15'],
            'gıda ve endüstriyel mutfak': ['10', '11'],
            'makine ve makine ekipmanları': ['28'],
            'metal ve metal işlemesi': ['25'],
            'metalurji ve makina sanayi': ['24', '25', '28'],
            'yapı ve inşaat': ['41', '42', '43'],
            'gıda ve endüstriyel mutfak': ['10', '11'],
            'makine ve makine ekipmanları': ['28'],
            'metal ve metal işlemesi': ['25'],
            'iş makinaları': ['28'],
            'otomotiv': ['29'],
            'çeşitli ticari faaliyetler': ['46', '47'],
            'diğer': [],
            'hizmetler': ['46', '47', '49', '50', '51', '52', '53', '55', '56', '58', '59', '60', '61', '62', '63', '64', '65', '66', '68', '69', '70', '71', '72', '73', '74', '75', '77', '78', '78', '79', '80', '81', '82', '84', '85', '86', '87', '88', '90', '91', '92', '93', '94', '95', '96'],
            'elektrik ve elektronik': ['26', '27'],
            'tekstil ve deri': ['13', '14', '15'],
            'savunma': ['25'],
            'gıda': ['10', '11'],
            'iş makinaları': ['28'],
            'sağlık': ['21', '26', '32', '86', '87', '88'],
            'medikal': ['21', '26', '32'],
            'kent mobilyaları': ['31'],
            'muhtelif gaz dolum': ['20'],
            'tekstil': ['13', '14', '15'],
            'perakende': ['47'],
            'tekstil ve deri': ['13', '14', '15'],
            'hizmetler': ['46', '47', '49', '50', '51', '52', '53', '55', '56', '58', '59', '60', '61', '62', '63', '64', '65', '66', '68', '69', '70', '71', '72', '73', '74', '75', '77', '78', '78', '79', '80', '81', '82', '84', '85', '86', '87', '88', '90', '91', '92', '93', '95', '96'],
            'elektrik ve elektronik': ['26', '27'],
            'kargo': ['49', '50', '51', '52', '53'],
            'muhtelif gaz dolum': ['20'],
            'tekstil': ['13', '14', '15'],
            'perakende': ['47'],
            'tekstil ve deri': ['13', '14', '15'],
            'gıda ve endüstriyel mutfak': ['10', '11'],
            'makine ve makine ekipmanları': ['28'],
            'metal ve metal işlemesi': ['25'],
            'metalurji ve makina sanayi': ['24', '25', '28'],
            'yapı ve inşaat': ['41', '42', '43'],
            'gıda ve endüstriyel mutfak': ['10', '11'],
            'makine ve makine ekipmanları': ['28'],
            'metal ve metal işlemesi': ['25'],
            'metalurji ve makina sanayi': ['24', '25', '28'],
            'yapı ve inşaat': ['41', '42', '43'],
            'gıda ve endüstriyel mutfak': ['10', '11'],
            'makine ve makine ekipmanları': ['28'],
            'metal ve metal işlemesi': ['25'],
            'metalurji ve makina sanayi': ['24', '25', '28'],
            'yapı ve inşaat': ['41', '42', '43'],
            'gıda ve endüstriyel mutfak': ['10', '11'],
            'makine ve makine ekipmanları': ['28'],
            'metal ve metal işlemesi': ['25'],
            'metalurji ve makina sanayi': ['24', '25', '28'],
            'yapı ve inşaat': ['41', '42', '43'],
        }
        
        # Find matching nace hints
        nace_ipucu = []
        for keyword, codes in nace_hints.items():
            if keyword in norm.lower():
                nace_ipucu.extend(codes)
        
        # Deduplicate
        nace_ipucu = list(set(nace_ipucu))
        nace_ipucu.sort()
        
        entry = {
            "sade": norm,
            "gosterim": get_display_name(norm),
            "varyantlar": [norm],
            "kaynaklar": ["ostim.org.tr", "baskentosb.org.tr", "aso.org.tr", "ivedik.org.tr"],
            "nace_ipucu": nace_ipucu
        }
        sektör_sozluk.append(entry)
    
    # Write dictionary
    output_path = Path("data/sektor/sektor_sozluk.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sektör_sozluk, f, ensure_ascii=False, indent=2)
    
    print(f"\nDictionary created at {output_path} with {len(sektör_sozluk)} entries")
    
    # Verify
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Verified: {len(data)} entries")
    for entry in data[:5]:
        print(f"  {entry['sade']} -> {entry['gosterim']} (NACE: {entry['nace_ipucu']})")

if __name__ == "__main__":
    main()