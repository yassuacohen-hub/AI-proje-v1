#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERI-NACE-SOZLUK-01: Resmi NACE listesini nace_codes tablosuna yükle
Kaynak: data/nace/sektor_meslek_nace_2026-05_resmi.xlsx
"""

import sys
from pathlib import Path
import openpyxl
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

# Proje kök dizini
PROJECT_ROOT = Path(__file__).resolve().parents[3]
XLSX_PATH = PROJECT_ROOT / "data" / "nace" / "sektor_meslek_nace_2026-05_resmi.xlsx"
DB_URL = "postgresql://postgres:postgres@localhost:5432/huginn"


def get_engine():
    return create_engine(DB_URL)


def clean_turkish_chars(text: str) -> str:
    """Türkçe karakterleri normalize et."""
    if not text:
        return ""
    # openpyxl Türkçe karakterleri bazen bozuyor, düzelt
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
    """NACE kodundan seviye çıkar (nokta sayısı + 1)."""
    if not code:
        return 0
    # 47.79.04 -> 3 nokta -> seviye 6 (6 haneli)
    # 47.79    -> 1 nokta -> seviye 4 (4 haneli)
    # 47       -> 0 nokta -> seviye 2 (2 haneli)
    # D        -> 0 nokta -> seviye 1 (sektör harfi)
    code = str(code).strip()
    if not code:
        return 0
    dots = code.count('.')
    if dots == 0:
        # Tek harf (sektör) veya 2 haneli
        if len(code) == 1:
            return 1  # Sektör harfi (D, F, G...)
        elif len(code) <= 2:
            return 2  # 2 haneli (10, 11, ...)
        else:
            return 4  # 4 haneli (47.79 -> 47.79 = 4 hane)
    elif dots == 1:
        return 4  # 47.79 formatı
    elif dots == 2:
        return 6  # 47.79.04 formatı
    return 0


def extract_parent_code(code: str) -> str:
    """6 haneli koddan 4 haneli parent kod çıkar (47.79.04 -> 47.79)."""
    if not code:
        return None
    code = str(code).strip()
    if code.count('.') >= 2:
        # 47.79.04 -> 47.79
        parts = code.split('.')
        return '.'.join(parts[:2])
    elif code.count('.') == 1:
        # 47.79 formatında, parent yok (zaten 4 haneli)
        return None
    return None


def upsert_nace_code(engine, nace_code, version, level, parent_code, title, sector_group, is_manufacturing):
    """NACE kodunu upsert et."""
    with engine.connect() as conn:
        try:
            conn.execute(
                text("""
                    INSERT INTO nace_codes (nace_code, version, level, parent_code, title, sector_group, is_manufacturing)
                    VALUES (:nace_code, :version, :level, :parent_code, :title, :sector_group, :is_manufacturing)
                    ON CONFLICT (nace_code) DO UPDATE SET
                        version = EXCLUDED.version,
                        level = EXCLUDED.level,
                        parent_code = EXCLUDED.parent_code,
                        title = EXCLUDED.title,
                        sector_group = EXCLUDED.sector_group,
                        is_manufacturing = EXCLUDED.is_manufacturing
                """),
                {
                    "nace_code": nace_code,
                    "version": version,
                    "level": level,
                    "parent_code": parent_code,
                    "title": title,
                    "sector_group": sector_group,
                    "is_manufacturing": is_manufacturing,
                },
            )
            conn.commit()
        except Exception as e:
            print(f"[HATA] {nace_code} upsert hatası: {e}")
            conn.rollback()


def insert_source_record(engine, source_url, version, description):
    """Kaynak kaydı ekle."""
    with engine.connect() as conn:
        try:
            conn.execute(
                text("""
                    INSERT INTO sources (source_url, version, description, source_type)
                    VALUES (:source_url, :version, :description, 'official')
                    ON CONFLICT (source_url) DO UPDATE SET
                        version = EXCLUDED.version,
                        description = EXCLUDED.description,
                        updated_at = NOW()
                """),
                {
                    "source_url": source_url,
                    "version": version,
                    "description": description,
                },
            )
            conn.commit()
        except Exception as e:
            print(f"[HATA] Source kaydı hatası: {e}")
            conn.rollback()


def main():
    print("=" * 60)
    print("VERI-NACE-SOZLUK-01: NACE Sözlüğü Yükleme")
    print("=" * 60)

    if not XLSX_PATH.exists():
        print(f"[HATA] Dosya bulunamadı: {XLSX_PATH}")
        sys.exit(1)

    print(f"[BİLGİ] Dosya okunuyor: {XLSX_PATH}")

    # Excel dosyasını oku
    wb = openpyxl.load_workbook(XLSX_PATH)
    ws = wb.active

    print(f"[BİLGİ] Satır sayısı: {ws.max_row}, Sütun sayısı: {ws.max_column}")

    # Sütun indeksleri (0-based)
    # 0: SEKTOR KODU
    # 1: SEKTOR TANIM
    # 2: MESLEK KODU
    # 3: MESLEK TANIM
    # 4: NACE REV. 2.1 KODU
    # 5: NACE REV.2.1 TANIM

    engine = get_engine()

    # Tablo var mı kontrol et
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'nace_codes'
        """)).scalar()
        if not result:
            print("[HATA] nace_codes tablosu bulunamadı!")
            sys.exit(1)

    # Kaynak kaydı ekle
    source_url = "https://ticaret.gov.tr/esnaf-sanatkarlar/esnaf-ve-sanatkar-meslek-kollari/sektor-meslek-nace-listeleri/guncel-liste"
    source_version = "2026.01.01 / Mayıs 2026"
    insert_source_record(engine, "ticaret.gov.tr", source_version, 
                         "Resmi NACE Rev 2.1 listesi - Sektör Meslek NACE Listeleri")

    # Veriyi işle
    processed = 0
    inserted = 0
    updated = 0
    errors = 0

    # Önce 4 haneli parent kodları toplu eklemek için set tut
    parent_codes = set()

    # İlk geçiş: veriyi oku ve parent kodları topla
    print("[BİLGİ] Veri okunuyor ve parent kodlar toplanıyor...")
    rows_data = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        sektor_kodu = clean_turkish_chars(str(row[0])) if row[0] else ""
        sektor_tanim = clean_turkish_chars(str(row[1])) if row[1] else ""
        meslek_kodu = clean_turkish_chars(str(row[2])) if row[2] else ""
        meslek_tanim = clean_turkish_chars(str(row[3])) if row[3] else ""
        nace_kodu = normalize_nace_code(row[4]) if row[4] else ""
        nace_tanim = clean_turkish_chars(str(row[5])) if row[5] else ""

        if not nace_kodu:
            continue

        # NACE kodunu normalize et
        nace_code = normalize_nace_code(nace_kodu)
        
        # Seviye belirle
        level = extract_level(nace_kodu)
        
        # Parent kod çıkar
        parent_code = extract_parent_code(nace_kodu)

        # 4 haneli parent kodları topla (level 4 için)
        if level == 6 and parent_code:
            parent_codes.add(parent_code)

        rows_data.append({
            'nace_code': nace_code,
            'version': '2026.01.01',
            'level': level,
            'parent_code': parent_code,
            'title': nace_tanim,
            'sector_group': sektor_tanim,
            'is_manufacturing': False,  # TODO: sektör koduna göre belirlenebilir
        })

    # 4 haneli parent kodları (level 4) de ekle
    print(f"[BİLGİ] {len(parent_codes)} adet 4 haneli parent kod bulundu")
    for parent in parent_codes:
        if parent and parent not in [d['nace_code'] for d in rows_data]:
            rows_data.append({
                'nace_code': parent,
                'version': '2026.01.01',
                'level': 4,
                'parent_code': extract_parent_code(parent),  # 2 haneli parent
                'title': '',  # title sonra doldurulabilir
                'sector_group': '',  # sector_group sonra doldurulabilir
                'is_manufacturing': False,
            })

    # Veritabanına yaz
    print("[BİLGİ] Veritabanına yazılıyor...")
    for data in rows_data:
        try:
            upsert_nace_code(
                engine=get_engine(),
                nace_code=data['nace_code'],
                version=data['version'],
                level=data['level'],
                parent_code=data['parent_code'],
                title=data['title'],
                sector_group=data['sector_group'],
                is_manufacturing=data['is_manufacturing'],
            )
            processed += 1
            if processed % 100 == 0:
                print(f"  İşlenen: {processed}/{len(rows_data)}")
        except Exception as e:
            errors += 1
            print(f"  [HATA] {data['nace_code']}: {e}")

    print(f"\n[SONUÇ] İşlenen: {processed}, Hatalı: {errors}")
    print("[TAMAM] NACE sözlüğü yükleme tamamlandı.")


if __name__ == "__main__":
    main()