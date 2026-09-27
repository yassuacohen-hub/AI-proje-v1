#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERI-NACE-COKLU-01: Çoklu NACE kodunu yaz → company_industries.is_primary

Bu script source_records.raw_nace verilerini kullanarak company_industries tablosunu doldurur.
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

# Proje kök dizini
PROJECT_ROOT = Path(__file__).resolve().parents[3]
XLSX_PATH = PROJECT_ROOT / "data" / "nace" / "sektor_meslek_nace_2026-05_resmi.xlsx"
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please check .env file.")

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
import openpyxl

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


def main():
    print("=" * 60)
    print("VERI-NACE-COKLU-01: Çoklu NACE kodunu company_industries'a yaz")
    print("=" * 60)

    if not XLSX_PATH.exists():
        print(f"[HATA] Dosya bulunamadı: {XLSX_PATH}")
        sys.exit(1)

    print(f"[BİLGİ] Dosya okunuyor: {XLSX_PATH}")

    engine = create_engine(os.getenv("DATABASE_URL"))
    
    # Mevcut nace_codes'ları cache'le
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        existing_codes = set()
        result = conn.execute(text("SELECT nace_code FROM nace_codes")).fetchall()
        existing_codes = {row[0] for row in result}
        print(f"[BİLGİ] Mevcut NACE kodları: {len(existing_codes)}")
        
        # Mevcut company_industries kayıtlarını kontrol et
        result = conn.execute(text("SELECT COUNT(*) FROM company_industries")).scalar()
        print(f"[BİLGİ] Mevcut company_industries kayıtları: {result}")

    # 1. Adım: Source_records'tan şirket-NACE eşleşmelerini çıkar
    print("[BİLGİ] Source_records'tan şirket-NACE eşleşmeleri çıkarılıyor...")
    
    with engine.connect() as conn:
        # source_records'tan şirket vergi numarası ile şirketleri eşleştir
        rows = conn.execute(
            text("""
                SELECT c.company_id, sr.raw_nace, sr.raw_tax_number, sr.raw_name
                FROM companies c
                JOIN source_records sr ON sr.raw_tax_number = c.tax_number
                WHERE sr.raw_nace IS NOT NULL
            """)
        ).fetchall()
    
    print(f"[BİLGİ] {len(rows)} kaynak kayıt bulundu")
    
    # Şirket başına NACE kodlarını topla
    company_nace_codes = defaultdict(set)
    company_names = {}
    
    for row in rows:
        company_id = row[0]
        nace_code = normalize_nace_code(row[1])
        if nace_code:
            company_nace_codes[company_id].add(nace_code)
            if row[3] and company_id not in company_names:
                company_names[company_id] = clean_turkish_chars(str(row[3]))
    
    print(f"[BİLGİ] {len(company_nace_codes)} şirket için NACE kodu bulundu")
    
    # Mevcut company_industries kayıtlarını kontrol et
    with engine.connect() as conn:
        existing = conn.execute(text("SELECT company_id, nace_code FROM company_industries")).fetchall()
        existing_pairs = set((row[0], row[1]) for row in existing)
        print(f"[BİLGİ] Mevcut company_industries kayıtları: {len(existing_pairs)}")
    
    # Yeni kayıtları hazırla
    new_records = []
    skipped = 0
    
    for company_id, nace_codes in company_nace_codes.items():
        # Mevcut companies.nace_code'u al (ana kod olarak)
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT nace_code FROM companies WHERE company_id = :cid"),
                {"cid": company_id}
            ).scalar()
            primary_nace = normalize_nace_code(result) if result else None
        
        # Tüm kodları sırala: ana kod önce, sonra diğerleri
        all_codes = list(nace_codes)
        if primary_nace and primary_nace in all_codes:
            # Ana kodu başa al
            all_codes.remove(primary_nace)
            all_codes.insert(0, primary_nace)
        elif primary_nace:
            # Ana kod listede yoksa da başa al
            all_codes.insert(0, primary_nace)
        
        for idx, nace_code in enumerate(all_codes):
            if (company_id, nace_code) in existing_pairs:
                skipped += 1
                continue
            
            # nace_codes tablosunda var mı kontrol et
            if nace_code not in existing_codes:
                print(f"[UYARI] NACE kodu nace_codes'ta yok: {nace_code} - atlanıyor")
                continue
            
            is_primary = (idx == 0)
            new_records.append({
                'company_id': company_id,
                'nace_code': nace_code,
                'nace_version': '2026.01.01',
                'nace_level': extract_level(nace_code),
                'is_primary': is_primary,
                'source_id': None,  # TODO: source_id belirlenebilir
                'confidence': 0.9 if is_primary else 0.7,
            })
    
    print(f"[BİLGİ] Eklenecek yeni kayıtlar: {len(new_records)}, Atlanan: {skipped}")
    
    if not new_records:
        print("[BİLGİ] Eklenecek yeni kayıt yok.")
        return
    
    # Batch insert
    print("[BİLGİ] Veritabanına yazılıyor...")
    batch_size = 100
    inserted = 0
    errors = 0
    
    for i in range(0, len(new_records), batch_size):
        batch = new_records[i:i+batch_size]
        try:
            with create_engine(os.getenv("DATABASE_URL")).begin() as conn:
                for data in batch:
                    conn.execute(
                        text("""
                            INSERT INTO company_industries 
                            (company_id, nace_code, nace_version, nace_level, is_primary, source_id, confidence, verified_at)
                            VALUES (:company_id, :nace_code, :nace_version, :nace_level, :is_primary, :source_id, :confidence, NOW())
                            ON CONFLICT (company_id, nace_code) DO UPDATE SET
                                is_primary = EXCLUDED.is_primary,
                                confidence = EXCLUDED.confidence,
                                verified_at = NOW()
                        """),
                        {
                            "company_id": data['company_id'],
                            "nace_code": data['nace_code'],
                            "nace_version": data['nace_version'],
                            "nace_level": data['nace_level'],
                            "is_primary": data['is_primary'],
                            "source_id": data['source_id'],
                            "confidence": data['confidence'],
                        }
                    )
            inserted += len(batch)
            if (i // batch_size + 1) % 10 == 0:
                print(f"  İşlenen: {min(i+batch_size, len(new_records))}/{len(new_records)}")
        except Exception as e:
            errors += len(batch)
            print(f"  [HATA] Batch {i//batch_size + 1}: {e}")
    
    print(f"\n[SONUÇ] Eklenen: {inserted}, Hatalı: {errors}, Atlanan: {skipped}")
    print("[TAMAM] Çoklu NACE yazma işlemi tamamlandı.")


if __name__ == "__main__":
    import sys
    import os
    main()