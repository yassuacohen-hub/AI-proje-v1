# -*- coding: utf-8 -*-
"""VERI-SEKTOR-01: Sektör sözlüğü oluşturma - veritabanından doğrudan"""

import json
import re
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

def is_aso_meslek_grubu(text: str) -> bool:
    """Check if text is an ASO meslek grubu code."""
    if not text:
        return False
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

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

def is_aso_meslek_grubu(text: str) -> bool:
    if not text:
        return False
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

def normalize_sector(text: str) -> str:
    if not text:
        return ""
    s = str(text).strip()
    s = re.sub(r'\d+$', '', s)
    s = s.rstrip('. ')
    s = s.strip()
    return s

def get_display_name(normalized: str) -> str:
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

def is_aso_meslek_grubu(text: str) -> bool:
    if not text:
        return False
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

def get_nace_hints(norm: str) -> list:
    if not norm:
        return []
    norm_lower = norm.lower()
    nace_hints = {
        'otomotiv': ['29'],
        'metalurji': ['24', '25'],
        'metal ve metal': ['24', '25'],
        'yapı ve inşaat': ['41', '42', '43'],
        'gıda': ['10', '11'],
        'makine': ['28'],
        'metal ve metal işlemesi': ['25'],
        'iş makinaları': ['28'],
        'çeşitli ticari faaliyetler': ['46', '47'],
        'diğer': [],
        'hizmetler': ['46', '47', '49', '50', '51', '52', '53', '55', '56', '58', '59', '60', '61', '62', '63', '64', '65', '66', '68', '69', '70', '71', '72', '73', '74', '75', '77', '78', '79', '80', '81', '82', '84', '85', '86', '87', '88', '90', '91', '92', '93', '94', '95', '96'],
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
        'gıda ve endüstriyel mutfak': ['10', '11'],
        'makine ve makine ekipmanları': ['28'],
        'metal ve metal işlemesi': ['25'],
        'metalurji ve makina sanayi': ['24', '25', '28'],
        'yapı ve inşaat': ['41', '42', '43'],
        'gıda ve endüstriyel mutfak': ['10', '11'],
    }
    
    nace_ipucu = []
    norm_lower = norm.lower()
    for keyword, codes in nace_hints.items():
        if keyword in norm_lower:
            nace_ipucu.extend(codes)
    
    # Deduplicate
    nace_ipucu = list(set(nace_ipucu))
    nace_ipucu.sort()
    return nace_ipucu

def is_aso_meslek_grubu(text: str) -> bool:
    if not text:
        return False
    return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))

def normalize_sector(text: str) -> str:
    if not text:
        return ""
    s = str(text).strip()
    s = re.sub(r'\d+$', '', s)
    s = s.rstrip('. ')
    s = s.strip()
    return s

def get_display_name(normalized: str) -> str:
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

def main():
    print("Fetching sector data from database...")
    
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    load_dotenv()
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT sr.raw_payload->>'sektor' as sektor, COUNT(*) as cnt
            FROM source_records sr
            WHERE sr.raw_payload->>'sektor' IS NOT NULL
            GROUP BY sr.raw_payload->>'sektor'
            ORDER BY cnt DESC
        """)).fetchall()
    
    print(f"Found {len(rows)} unique sector values in database")
    
    # Process sectors
    sector_counts = {}
    aso_count = 0
    for row in rows:
        sektor = row[0]
        count = row[1]
        
        if is_aso_meslek_grubu(sektor):
            aso_count += count
            continue
        
        norm = normalize_sector(sektor)
        if norm in sector_counts:
            sector_counts[norm] += count
        else:
            sector_counts[norm] = count
    
    print(f"Total unique normalized sectors (excluding ASO): {len(sector_counts)}")
    print(f"ASO meslek grubu records: {aso_count}")
    
    # Sort by count descending
    sorted_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop sectors by count:")
    for norm, count in sorted_sectors[:20]:
        print(f"  {norm}: {count}")
    
    # NACE hints mapping
    nace_hints = {
        'otomotiv': ['29'],
        'metalurji': ['24', '25'],
        'metal ve metal': ['24', '25'],
        'yapı ve inşaat': ['41', '42', '43'],
        'gıda': ['10', '11'],
        'makine': ['28'],
        'metal ve metal işlemesi': ['25'],
        'iş makinaları': ['28'],
        'çeşitli ticari faaliyetler': ['46', '47'],
        'diğer': [],
        'hizmetler': ['46', '47', '49', '50', '51', '52', '53', '55', '56', '58', '59', '60', '61', '62', '63', '64', '65', '66', '68', '69', '70', '71', '72', '73', '74', '75', '77', '78', '79', '80', '81', '82', '84', '85', '86', '87', '88', '90', '91', '92', '93', '94', '95', '96'],
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
        'gıda ve endüstriyel mutfak': ['10', '11'],
        'makine ve makine ekipmanları': ['28'],
        'metal ve metal işlemesi': ['25'],
        'metalurji ve makina sanayi': ['24', '25', '28'],
        'yapı ve inşaat': ['41', '42', '43'],
        'gıda ve endüstriyel mutfak': ['10', '11'],
    }
    
    def get_nace_hints(norm: str) -> list:
        if not norm:
            return []
        norm_lower = norm.lower()
        nace_ipucu = []
        for keyword, codes in nace_hints.items():
            if keyword in norm.lower():
                nace_ipucu.extend(codes)
        return sorted(list(set(nace_ipucu)))
    
    def get_display_name(normalized: str) -> str:
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
    
    def normalize_sector(text: str) -> str:
        if not text:
            return ""
        s = str(text).strip()
        s = re.sub(r'\d+$', '', s)
        s = s.rstrip('. ')
        s = s.strip()
        return s
    
    def get_display_name(normalized: str) -> str:
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
    
    def is_aso_meslek_grubu(text: str) -> bool:
        if not text:
            return False
        return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))
    
    def normalize_sector(text: str) -> str:
        if not text:
            return ""
        s = str(text).strip()
        s = re.sub(r'\d+$', '', s)
        s = s.rstrip('. ')
        s = s.strip()
        return s
    
    def get_display_name(normalized: str) -> str:
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
    
    def is_aso_meslek_grubu(text: str) -> bool:
        if not text:
            return False
        return bool(re.match(r'^\d{1,2}\.\s*MESLEK\s+GRUBU$', text.strip(), re.IGNORECASE))
    
    def normalize_sector(text: str) -> str:
        if not text:
            return ""
        s = str(text).strip()
        s = re.sub(r'\d+$', '', s)
        s = s.rstrip('. ')
        s = s.strip()
        return s
    
    def get_display_name(normalized: str) -> str:
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
    
    # Build dictionary
    sektör_sozluk = []
    
    for norm, count in sorted_sectors:
        display = get_display_name(norm)
        
        # Get NACE hints
        nace_ipucu = []
        for keyword, codes in nace_hints.items():
            if keyword in norm.lower():
                nace_ipucu.extend(codes)
        nace_ipucu = sorted(list(set(nace_ipucu)))
        
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
    for entry in data[:10]:
        print(f"  {entry['sade']} -> {entry['gosterim']} (NACE: {entry['nace_ipucu']})")

if __name__ == "__main__":
    import os
    from pathlib import Path
    import re
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    main()