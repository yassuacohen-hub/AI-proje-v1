#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Invalid VKN temizligi ve kalite skoru yenileme."""
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.begin() as conn:
    # 1. Gecersiz VKN'leri temizle (10 haneli olmayanlari NULL yap)
    # Not: 11 haneli TCKN de olabilir, onu da temizleyelim
    result = conn.execute(text("""
        UPDATE companies 
        SET vergi_no = NULL 
        WHERE vergi_no IS NOT NULL 
        AND vergi_no != ''
        AND LENGTH(vergi_no) NOT IN (10, 11)
    """))
    invalid_cleaned = result.rowcount
    print(f"Temizlenen gecersiz VKN: {invalid_cleaned}")
    
    # 2. 11 haneli olanlari da kontrol et (sadece sayi mi?)
    result2 = conn.execute(text("""
        UPDATE companies 
        SET vergi_no = NULL 
        WHERE vergi_no IS NOT NULL 
        AND vergi_no != ''
        AND LENGTH(vergi_no) = 11
        AND vergi_no !~ '^[0-9]+$'
    """))
    invalid_11 = result2.rowcount
    print(f"Temizlenen gecersiz 11 haneli VKN: {invalid_11}")
    
    # 3. 10 haneli olanlari da kontrol et
    result3 = conn.execute(text("""
        UPDATE companies 
        SET vergi_no = NULL 
        WHERE vergi_no IS NOT NULL 
        AND vergi_no != ''
        AND LENGTH(vergi_no) = 10
        AND vergi_no !~ '^[0-9]+$'
    """))
    invalid_10 = result3.rowcount
    print(f"Temizlenen gecersiz 10 haneli VKN: {invalid_10}")

print("\nKalite skorlari yeniden hesaplaniyor...")
import subprocess
result = subprocess.run(["python", "scripts/recalculate_quality_scores.py"], 
                       capture_output=True, text=True, cwd="C:/Projeler/Huginn Data Insights")
print(result.stdout)
if result.stderr:
    print("Hata:", result.stderr[:500])
