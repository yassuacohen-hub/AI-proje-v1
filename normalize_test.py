# -*- coding: utf-8 -*-
"""Sektör normalleştirme ve sözlük oluşturma - VERI-SEKTOR-01"""

import re
import json
from collections import Counter

# Turkish character fixes for mojibake
REPLACEMENTS = {
    'Ã§': 'ç', 'Ã¼': 'ü', 'Ä±': 'ı', 'ÄŸ': 'ğ', 'ÅŸ': 'ş', 'Ã¶': 'ö',
    'Ã‡': 'Ç', 'Ãœ': 'Ü', 'Ä°': 'İ', 'Ä': 'Ğ', 'ÅŸ': 'Ş', 'Ã–': 'Ö',
    'Ã¢': 'â', 'Ã¢': 'â',
    'Đ': 'Ğ', 'đ': 'ğ',
    'Ý': 'İ', 'ý': 'ı',
    'ÅŸ': 'ş', 'Å': 'İ', 'Ÿ': 'ş', 'ž': 'ş',
    'Â': '', 'Ã': '', 'Å': '', 'Ý': 'İ', 'ý': 'ı',
    # Common mojibake patterns
    'Â': '', 'Ã': '', 'Å': '', 'Ý': 'İ', 'ý': 'ı',
}

def fix_mojibake(text: str) -> str:
    """Fix common mojibake patterns in Turkish text."""
    if not text:
        return text
    result = text
    for wrong, correct in REPLACEMENTS.items():
        result = result.replace(wrong, correct)
    return result

def normalize_sector(text: str) -> str:
    """Normalize sector name: fix mojibake, remove counter suffixes, uppercase."""
    if not text:
        return ""
    
    # Fix mojibake
    s = fix_mojibake(text)
    
    # Remove trailing counter numbers (e.g., "Otomotiv1163" -> "Otomotiv")
    # Pattern: digits at the end of string
    s = re.sub(r'\d+$', '', s)
    
    # Remove any remaining trailing dots/spaces
    s = s.rstrip('. ')
    
    # Normalize Turkish characters to uppercase (for matching)
    # Keep Turkish characters as-is for display, but normalize for comparison
    s = s.strip()
    
    return s

def get_display_name(normalized: str) -> str:
    """Convert normalized name to proper display format (Title Case with Turkish)."""
    if not normalized:
        return ""
    # Title case with Turkish awareness
    words = normalized.split()
    result = []
    for word in words:
        if word.isupper() and len(word) > 2:
            # Already uppercase, keep as is
            result.append(word)
        else:
            # Title case with Turkish
            result.append(word.capitalize())
    return ' '.join(result)

# Test normalization on all values
raw_sectors = [
    "Otomotiv1163",
    "Metalurji ve Makina Sanayi",
    "Yap\u0131 ve \u0130n\u015faat794",
    "G\u0131da ve End\u00fcstriyel Mutfak",
    "Makine ve Makine Ekipmanlar\u0131757",
    "Metal ve Metal \u0130\u015flemesi752",
    "\u0130\u015f Makinalar\u0131780",
    "Otomotiv",
    "\u00c7e\u015fitli Ticari Faaliyetler410",
    "Diger",
    "Hizmetler380",
    "Elektrik ve Elektronik390",
    "Teknik Malzeme Tezgah ve Ekipman339",
    "Yap\u0131 ve \u0130n\u015faat",
    "Teknoloji ve Bili\u015fim",
    "Teknoloji ve Bili\u015fim192",
    "Metal ve Metal \u0130\u015flemesi",
    "Hizmetler",
    "Ambalaj - Ka\u011f\u0131t - Bask\u0131 ve K\u0131rtasiye127",
    "\u00c7e\u015fitli Ticari Faaliyetler",
    "K\u0130MYA-LABARATUVAR",
    "Kimyasallar - Boya - Temizlik ve G\u00fcvenlik110",
    "G\u0131da ve End\u00fcstriyel Mutfak98",
    "Plastik ve Kau\u00e7uk114",
    "Tekstil ve Deri71",
    "Savunma",
    "GIDA",
    "\u0130\u015f Makinalar\u0131",
    "Sa\u011fl\u0131k78",
    "Medikal - \u0130la\u00e7",
    "30. MESLEK GRUBU",
    "21. MESLEK GRUBU",
    "17. MESLEK GRUBU",
    "24. MESLEK GRUBU",
    "25. MESLEK GRUBU",
    "31. MESLEK GRUBU",
    "16. MESLEK GRUBU",
    "Makine ve Makine Ekipmanlar\u0131",
    "35. MESLEK GRUBU",
    "39. MESLEK GRUBU",
    "Kimyasallar - Boya - Temizlik ve G\u00fcvenlik",
    "34. MESLEK GRUBU",
    "41. MESLEK GRUBU",
    "26. MESLEK GRUBU",
    "End\u00fcstriyel Market",
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
    "Sa\u011fl\u0131k",
    "Kent Mobilyalar\u0131 ve Peyzaj16",
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
    "H\u0131rdavat",
    "H\u0130ZMET-DANI\u015eMANLIK",
    "Ambalaj - Ka\u011f\u0131t - Bask\u0131 ve K\u0131rtasiye",
    "33. MESLEK GRUBU",
    "Plastik ve Kau\u00e7uk",
    "22. MESLEK GRUBU",
    "05. MESLEK GRUBU",
    "12. MESLEK GRUBU",
    "32. MESLEK GRUBU",
    "19. MESLEK GRUBU",
    "10. MESLEK GRUBU",
    "Elektrik ve Elektronik",
    "Kargo",
    "36. MESLEK GRUBU",
    "H\u0130ZMET-\u00c7ALI\u015eMA",
    "Muhtelif Gaz Dolum",
    "Tekstil",
    "29. MESLEK GRUBU",
    "Kent Mobilyalar\u0131 ve Peyzaj",
    "Perakende",
    "Tekstil ve Deri",
    "H\u00c7ZMET-\u00c7SG",
]

print("Testing normalization:")
for s in raw_sectors:
    norm = normalize_sector(s)
    display = get_display_name(norm)
    print(f"  '{s}' -> '{norm}' -> '{display}'")

# Count unique normalized
normalized = [normalize_sector(s) for s in raw_sectors]
unique = set(normalized)
print(f"\nTotal unique normalized: {len(unique)}")
for u in sorted(unique):
    print(f"  {u}")