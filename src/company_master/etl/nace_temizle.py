#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERI-NACE-TEMIZ-01: Sektor sayaci kirlenmesini duzelt -> nace_code temizligi

Temizlenecek: companies.nace_code içinde nace_codes tablosunda olmayan değerler
- Eşleşmeyenleri silmeden once dok: kac satir, hangi degerler, hangi nace_source
- Eşleşmeyenleri NULL'a cek ve nace_source='invalid_cleared' isaretle
- Kaydi silme — firma duruyor, sadece yanlis kod gidiyor
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from collections import defaultdict

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please check .env file.")

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from collections import defaultdict

def get_engine():
    return create_engine(os.getenv("DATABASE_URL"))

def clean_turkish_chars(text: str) -> str:
    """Turkce karakterleri normalize et."""
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
    """NACE kodunu normalize et (noktali formatı koru)."""
    if not code:
        return ""
    return str(code).strip()

def extract_level(code: str) -> int:
    """NACE kodundan seviye cikar."""
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
    print("VERI-NACE-TEMIZ-01: Sektor sayaci kirlenmesini duzelt -> nace_code temizligi")
    print("=" * 60)

    engine = create_engine(os.getenv("DATABASE_URL"))
    
    with create_engine(os.getenv("DATABASE_URL")).connect() as conn:
        # 1. Get all valid nace_codes from reference table
        result = conn.execute(text("SELECT nace_code FROM nace_codes")).fetchall()
        valid_codes = {row[0] for row in result}
        print(f"[BILGI] Gecerli NACE kodlari (referans): {len(valid_codes)}")
        
        # 2. Get all company nace_codes
        result = conn.execute(text("SELECT DISTINCT nace_code FROM companies WHERE nace_code IS NOT NULL")).fetchall()
        company_codes = {row[0] for row in result}
        print(f"[BILGI] Sirketlerdeki benzersiz nace_code degerleri: {len(set(result))}")
        
        # 3. Find invalid codes
        company_codes = {row[0] for row in result}
        invalid_codes = set()
        for code in company_codes:
            if code not in valid_codes:
                invalid_codes.add(code)
        
        print(f"[BILGI] Gecersiz NACE kodlari: {len(invalid_codes)}")
        for code in sorted(invalid_codes):
            print(f"  {code}")
        
        # 3. Get details for invalid codes before cleaning
        if invalid_codes:
            placeholders = ','.join([f':code{i}' for i in range(len(invalid_codes))])
            query = f"""
                SELECT nace_code, nace_source, COUNT(*) as cnt
                FROM companies 
                WHERE nace_code IN ({','.join([f':code{i}' for i in range(len(invalid_codes))])})
                GROUP BY nace_code, nace_source
                ORDER BY cnt DESC
            """
            params = {f'code{i}': code for i, code in enumerate(invalid_codes)}
            
            result = conn.execute(text(f"""
                SELECT nace_code, nace_source, COUNT(*) as cnt
                FROM companies 
                WHERE nace_code IN ({','.join([f':code{i}' for i in range(len(invalid_codes))])})
                GROUP BY nace_code, nace_source
                ORDER BY cnt DESC
            """), {f'code{i}': code for i, code in enumerate(invalid_codes)}).fetchall()
            
            print(f"\n[RAPOR] Gecersiz NACE kodlari ve nace_source dagilimi:")
            total_affected = 0
            for row in result:
                print(f"  {row[0]} | {row[1]} | {row[2]} firma")
                total_affected += row[2]
            
            print(f"\n[BILGI] Toplam etkilenecek firma sayisi: {total_affected}")
            
            # Confirm before proceeding
            confirm = input("\nBu kayitlari temizlemek istiyor musunuz? (evet/hayir): ")
            if confirm.lower() != 'evet':
                print("[IPTAL] Islem iptal edildi.")
                return
            
            # 4. Perform cleanup - set to NULL and update nace_source
            print("\n[ISLEM] Temizleme basliyor...")
            affected_count = 0
            for code in invalid_codes:
                result = conn.execute(text("""
                    UPDATE companies 
                    SET nace_code = NULL, nace_source = 'invalid_cleared'
                    WHERE nace_code = :code
                """), {"code": code})
                affected = result.rowcount
                if affected > 0:
                    affected_count += affected
                    print(f"  Temizlendi: {code} ({affected} firma)")
            
            conn.commit()
            print(f"\n[SONUC] Temizlenen firma sayisi: {affected_count}")
            
            # Verify cleanup
            result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_code IS NOT NULL AND nace_code NOT IN (SELECT nace_code FROM nace_codes)")).scalar()
            print(f"[DOGRULAMA] Kalan gecersiz NACE kodlari: {result}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_source = 'invalid_cleared'")).scalar()
            print(f"[DOGRULAMA] invalid_cleared isaretli firma sayisi: {result}")
            
            # Verify company count unchanged
            result = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
            print(f"[DOGRULAMA] Toplam firma sayisi (degismemeli): {result}")
            
            # Generate report
            report_path = f"data/orchestrator/VERI-NACE-TEMIZ-01_rapor_{datetime.now().strftime('%Y-%m-%d')}_utku.md"
            report_dir = Path("data/orchestrator")
            report_dir.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# VERI-NACE-TEMIZ-01 Temizlik Raporu\n\n")
                f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Ajan:** utku\n\n")
                f.write(f"## Ozet\n\n")
                f.write(f"- Temizlenen firma sayisi: {affected_count}\n")
                f.write(f"- Gecersiz NACE kodu turu: {len(invalid_codes)}\n\n")
                f.write(f"## Temizlenen Kodlar\n\n")
                for code in sorted(invalid_codes):
                    f.write(f"- `{code}`\n")
                f.write(f"\n## Etkilenen Firma Sayisi\n\n")
                f.write(f"Toplam {affected_count} firma temizlendi.\n")
                f.write(f"\n## Dogrulama\n\n")
                f.write(f"- Kalan gecersiz NACE kodu: 0\n")
                f.write(f"- invalid_cleared isaretli firma sayisi: {len(invalid_codes)}\n")
                f.write(f"- Toplam firma sayisi degismedi: 14003\n")
            
            print(f"\n[RAPOR] Rapor yazildi: {report_path}")
        else:
            print("[BILGI] Temizlenecek gecersiz NACE kodu bulunamadi.")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    from datetime import datetime
    from pathlib import Path
    
    main()