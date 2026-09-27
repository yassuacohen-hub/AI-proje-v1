#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOZLUK-01 DÜZELTME: 566 boş başlığı doldur

Bu script nace_codes tablosundaki 566 boş başlığı (title) doldurur.
Kaynak veriler: Excel (sektor_meslek_nace_2026-05_resmi.xlsx) + JSON dosyaları
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
import openpyxl
import json

# Proje kök dizini
PROJECT_ROOT = Path(__file__).resolve().parents[3]
XLSX_PATH = PROJECT_ROOT / "data" / "nace" / "sektor_meslek_nace_2026-05_resmi.xlsx"
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please check .env file.")

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
import openpyxl
import json

def get_engine():
    return create_engine(os.getenv("DATABASE_URL"))

def clean_turkish_chars(text: str) -> str:
    """Türkçe karakterleri normalize et."""
    if not text:
        return ""
    replacements = {
        'â': 'a', 'Â': 'A',
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()

def normalize_nace_code(code: str) -> str:
    """NACE kodunu normalize et (noktalı formatı koru)."""
    if not code:
        return ""
    return str(code).strip()

def extract_level(code: str) -> int:
    """NACE kodundan seviye çıkar."""
    if not code:
        return 0
    code = str(code).strip()
    if not code:
        return 0
    dots = code.count('.')
    if dots == 0:
        if len(code) == 1:
            return 1
        elif len(code) <= 2:
            return 2
        else:
            return 4
    elif dots == 1:
        return 4
    elif dots == 2:
        return 6
    return 0


def load_xlsx_titles():
    """Excel dosyasından NACE kod -> başlık eşlemesini yükle."""
    wb = openpyxl.load_workbook(XLSX_PATH)
    ws = wb.active
    
    titles = {}
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        # Columns: 0=SEKTOR KODU, 1=SEKTOR TANIM, 2=MESLEK KODU, 3=MESLEK TANIM, 4=NACE REV. 2.1 KODU, 5=NACE REV.2.1 TANIM
        nace_kodu = str(row[4]).strip() if row[4] else ""
        nace_tanim = clean_turkish_chars(str(row[5])) if row[5] else ""
        
        if nace_kodu:
            nace_kodu = normalize_nace_code(nace_kodu)
            if nace_kodu and nace_tanim:
                # Keep the longest/most specific title
                if nace_kodu not in titles or len(nace_tanim) > len(titles.get(nace_kodu, "")):
                    titles[nace_kodu] = nace_tanim
    return titles


def load_turkiye_nace():
    """turkiye_nace.json'dan kod -> başlık eşlemesi."""
    json_path = PROJECT_ROOT / "data" / "nace" / "turkiye_nace.json"
    with open(json_path1, 'r', encoding='utf-8') as f:
        data = json.load(f)
    titles = {}
    for item in data:
        if 'code' in item and 'name_tr' in item:
            code = normalize_nace_code(item['code'])
            if code:
                titles[code] = item['name_tr']
    return titles


def load_rev_json_titles():
    """rev JSON dosyalarından kod -> başlık eşlemesi."""
    titles = {}
    
    # nace-rev-2-1.json
    json_path2 = PROJECT_ROOT / "data" / "nace" / "nace-rev-2-1.json"
    with open(json_path2, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            if 'Class' in item and 'Activity' in item and item['Class']:
                code = normalize_nace_code(item['Class'])
                if code and item['Activity']:
                    titles[code] = item['Activity']
    
    # nace-rev-2.json
    json_path3 = PROJECT_ROOT / "data" / "nace" / "nace-rev-2.json"
    with open(json_path3, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            if 'Class' in item and 'Activity' in item and item['Class']:
                code = normalize_nace_code(item['Class'])
                if code and item['Activity']:
                    # Only add if not already present (prefer first source)
                    if code not in titles:
                        titles[code] = item['Activity']
    return titles


def clean_turkish_chars(text: str) -> str:
    """Türkçe karakterleri normalize et."""
    if not text:
        return ""
    replacements = {
        'â': 'a', 'Â': 'A',
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()

def normalize_nace_code(code: str) -> str:
    """NACE kodunu normalize et (noktalı formatı koru)."""
    if not code:
        return ""
    return str(code).strip()

def extract_level(code: str) -> int:
    """NACE kodundan seviye çıkar."""
    if not code:
        return 0
    code = str(code).strip()
    if not code:
        return 0
    dots = code.count('.')
    if dots == 0:
        if len(code) == 1:
            return 1
        elif len(code) <= 2:
            return 2
        else:
            return 4
    elif dots == 1:
        return 4
    elif dots == 2:
        return 6
    return 0


def main():
    print("=" * 60)
    print("SOZLUK-01 DÜZELTME: 566 boş başlığı doldur")
    print("=" * 60)

    # Load all title mappings
    print("[BİLGİ] Kaynak veriler yükleniyor...")
    
    xlsx_titles = load_xlsx_titles()
    print(f"[BİLGİ] XLSX başlıkları: {len(xlsx_titles)}")
    
    turkiye_titles = load_turkiye_nace()
    print(f"[BİLGİ] Türkiye NACE başlıkları: {len(turkiye_titles)}")
    
    rev_titles = load_rev_json_titles()
    print(f"[BİLGİ] Rev JSON başlıkları: {len(rev_titles)}")
    
    # Build combined title map (priority: XLSX > Türkiye NACE > Rev JSON)
    title_map = {}
    title_map.update(rev_titles)
    title_map.update(turkiye_titles)
    title_map.update(xlsx_titles)
    print(f"[BİLGİ] Toplam benzersiz başlık haritası: {len(title_map)}")
    
    # Get empty titles from database
    engine = create_engine(os.getenv('DATABASE_URL'))
    with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text('SELECT nace_code, level FROM nace_codes WHERE title IS NULL OR title = \'\' ORDER BY level, nace_code')).fetchall()
        empty_titles = [(row[0], row[1]) for row in result]
        print(f"[BİLGİ] Boş başlıklı kodlar: {len(result)}")
    
    # Get existing codes from DB to verify
    engine = create_engine(os.getenv('DATABASE_URL'))
    with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
        result = conn.execute(text("SELECT nace_code FROM nace_codes")).fetchall()
        existing_codes = {row[0] for row in result}
        print(f"[BİLGİ] Veritabanındaki toplam NACE kodu: {len(existing_codes)}")
    
    # Update empty titles
    updated = 0
    not_found = 0
    updated_codes = []
    
    # Build combined title map with priority: XLSX > Türkiye NACE > (we don't have rev JSON titles with code mapping)
    title_map = {}
    # We'll use the XLSX as primary source since it has the most complete data
    
    # Load XLSX titles
    xlsx_titles = load_xlsx_titles()
    print(f"[BİLGİ] XLSX başlıkları: {len(xlsx_titles)}")
    
    with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
        from sqlalchemy import text
        
        # Get empty titles from database
        result = conn.execute(text('SELECT nace_code, level FROM nace_codes WHERE title IS NULL OR title = \'\' ORDER BY level, nace_code')).fetchall()
        empty_titles = [(row[0], row[1]) for row in result]
        print(f"[BİLGİ] Boş başlıklı kodlar: {len(result)}")
        
        # Load XLSX titles
        xlsx_titles = load_xlsx_titles()
        
        # Try to fill from XLSX first
        updated = 0
        not_found = 0
        
        for nace_code, level in empty_titles:
            # Try XLSX first
            title = xlsx_titles.get(nace_code)
            
            if not title and level == 6:
                # For 6-digit codes, try parent (4-digit)
                parent = '.'.join(nace_code.split('.')[:2])
                if parent in title_map:
                    title = title_map[parent] + " - " + nace_code.split('.')[-1]
            elif level == 4:
                # For 4-digit codes, try 2-digit parent
                parent = nace_code.split('.')[0] if '.' in nace_code else None
                if parent and parent in title_map:
                    title = title_map[parent] + " - " + nace_code.split('.')[-1]
            
            if title:
                conn.execute(
                    text("UPDATE nace_codes SET title = :title WHERE nace_code = :code"),
                    {"title": title, "code": nace_code}
                )
                updated += 1
            else:
                not_found += 1
                print(f"[UYARI] Başlık bulunamadı: {nace_code} (level {level})")
        
        conn.commit()
        print(f"\n[SONUÇ] Güncellenen: {updated}, Bulunamayan: {not_found}")
        print("[TAMAM] SOZLUK-01 başlık düzeltmesi tamamlandı.")


def load_xlsx_titles():
    """Excel dosyasından NACE kod -> başlık eşlemesini yükle."""
    wb = openpyxl.load_workbook(XLSX_PATH)
    ws = wb.active
    
    titles = {}
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        # Columns: 0=SEKTOR KODU, 1=SEKTOR TANIM, 2=MESLEK KODU, 3=MESLEK TANIM, 4=NACE REV. 2.1 KODU, 5=NACE REV.2.1 TANIM
        nace_kodu = str(row[4]).strip() if row[4] else ""
        nace_tanim = clean_turkish_chars(str(row[5])) if row[5] else ""
        
        if nace_kodu:
            nace_kodu = normalize_nace_code(nace_kodu)
            if nace_kodu and nace_tanim:
                # Keep the longest/most specific title
                if nace_kodu not in titles or len(nace_tanim) > len(titles.get(nace_kodu, "")):
                    titles[nace_kodu] = nace_tanim
    return titles


def clean_turkish_chars(text: str) -> str:
    """Türkçe karakterleri normalize et."""
    if not text:
        return ""
    replacements = {
        'â': 'a', 'Â': 'A',
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()

def normalize_nace_code(code: str) -> str:
    """NACE kodunu normalize et (noktalı formatı koru)."""
    if not code:
        return ""
    return str(code).strip()

def extract_level(code: str) -> int:
    """NACE kodundan seviye çıkar."""
    if not code:
        return 0
    code = str(code).strip()
    if not code:
        return 0
    dots = code.count('.')
    if dots == 0:
        if len(code) == 1:
            return 1
        elif len(code) <= 2:
            return 2
        else:
            return 4
    elif dots == 1:
        return 4
    elif dots == 2:
        return 6
    return 0


def main():
    print("=" * 60)
    print("SOZLUK-01 DÜZELTME: 566 boş başlığı doldur")
    print("=" * 60)

    import os
    import sys
    from pathlib import Path
    import openpyxl
    import json
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import IntegrityError
    from collections import defaultdict

    # Load env
    import os
    from dotenv import load_dotenv
    load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    XLSX_PATH = PROJECT_ROOT / "data" / "nace" / "sektor_meslek_nace_2026-05_resmi.xlsx"
    DB_URL = os.getenv("DATABASE_URL")
    if not DB_URL:
        raise ValueError("DATABASE_URL environment variable not set. Please check .env file.")

    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import IntegrityError
    from collections import defaultdict
    import openpyxl
    import json

    def get_engine():
        return create_engine(os.getenv("DATABASE_URL"))

    # Load XLSX titles
    print("[BİLGİ] XLSX başlıkları yükleniyor...")
    xlsx_titles = load_xlsx_titles()
    print(f"[BİLGİ] XLSX başlıkları: {len(xlsx_titles)}")

    # Get empty titles from database
    engine = create_engine(os.getenv('DATABASE_URL'))
    with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text('SELECT nace_code, level FROM nace_codes WHERE title IS NULL OR title = \'\' ORDER BY level, nace_code')).fetchall()
        empty_titles = [(row[0], row[1]) for row in result]
        print(f"[BİLGİ] Boş başlıklı kodlar: {len(result)}")

    # Build title map from XLSX
    title_map = {}
    title_map.update(load_xlsx_titles())
    print(f"[BİLGİ] Toplam benzersiz başlık haritası: {len(title_map)}")

    # Update empty titles
    updated = 0
    not_found = 0
    updated_codes = []

    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        for nace_code, level in empty_titles:
            # Try to find title in our mappings
            title = title_map.get(nace_code)
            
            if not title and level == 6:
                # For 6-digit codes, try parent (4-digit)
                parent = '.'.join(nace_code.split('.')[:2])
                if parent in title_map:
                    title = title_map[parent] + " - " + nace_code.split('.')[-1]
            elif level == 4:
                # For 4-digit codes, try 2-digit parent
                parent = nace_code.split('.')[0] if '.' in nace_code else None
                if parent and parent in title_map:
                    title = title_map[parent] + " - " + nace_code.split('.')[-1]
            
            if title:
                conn.execute(
                    text("UPDATE nace_codes SET title = :title WHERE nace_code = :code"),
                    {"title": title, "code": nace_code}
                )
                updated += 1
                updated_codes.append(nace_code)
            else:
                not_found += 1
                print(f"[UYARI] Başlık bulunamadı: {nace_code} (level {level})")
        
        conn.commit()
        print(f"\n[SONUÇ] Güncellenen: {updated}, Bulunamayan: {not_found}")
        print("[TAMAM] SOZLUK-01 başlık düzeltmesi tamamlandı.")


if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path
    import openpyxl
    import json
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import IntegrityError
    from collections import defaultdict
    
    # Load env
    from dotenv import load_dotenv
    load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
    
    import os
    import sys
    from pathlib import Path
    import openpyxl
    import json
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import IntegrityError
    from collections import defaultdict
    
    main()