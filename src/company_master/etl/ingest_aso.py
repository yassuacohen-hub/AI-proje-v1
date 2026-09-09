# -*- coding: utf-8 -*-
"""ASO mevcut veriyi (488KB) ingest et."""

import json
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from company_master.db.connection import get_engine

ASO_DATA_DIR = Path("data/aso")


def ingest_aso_data():
    """ASO'nun 488KB'lik mevcut verisini companies tablosuna ekle."""
    engine = get_engine()
    
    # ASO veri dosyalarını bul
    aso_files = list(ASO_DATA_DIR.glob("*.csv")) + list(ASO_DATA_DIR.glob("*.json"))
    
    if not aso_files:
        print("ASO veri dosyası bulunamadı!")
        return
    
    for aso_file in aso_files:
        print(f"İşleniyor: {aso_file}")
        
        if aso_file.suffix == ".csv":
            df = pd.read_csv(aso_file)
        elif aso_file.suffix == ".json":
            df = pd.read_json(aso_file, lines=True)
        else:
            continue
        
        # Sütunları companies tablosuna uyarlama
        column_mapping = {
            'Firma Adı': 'legal_name',
            'Ticaret Adı': 'trade_name',
            'Vergi No': 'tax_number',
            'Adres': 'address',
            'Telefon': 'phone',
            'Web': 'website_domain',
            'NACE': 'nace_code',
            'OSB Parsel': 'osb_parsel',
            'İletişim': 'contact_info',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Zorunlu alanları doldur
        df['is_ankara'] = True
        df['is_osb_member'] = True
        df['source_name'] = 'ASO'
        df['source_type'] = 'OSB'
        df['ingested_at'] = pd.Timestamp.now().isoformat()
        
        # Sadece gerekli sütunları tut
        valid_columns = [
            'legal_name', 'trade_name', 'tax_number', 'address',
            'phone', 'website_domain', 'nace_code', 'osb_parsel',
            'is_ankara', 'is_osb_member', 'source_name', 'source_type'
        ]
        df = df[[c for c in valid_columns if c in df.columns]]
        
        # PostgreSQL'e ekle
        df.to_sql('companies', engine, if_exists='append', index=False, method='multi')
        print(f"  ✓ {len(df)} firma eklendi")
    
    print("ASO veri ingest tamamlandı.")


if __name__ == "__main__":
    ingest_aso_data()