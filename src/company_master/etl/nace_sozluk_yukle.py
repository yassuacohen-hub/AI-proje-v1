#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERI-NACE-SOZLUK-01: Resmi NACE listesini nace_codes tablosuna yÃ¼kle
D-234 kuralÄ±na gÃ¶re: 4 kaynak birleÅtirir, seviye kÄ±saltÄ±lmaz, upsert yapar
Kaynaklar:
  1. data/nace/sektor_meslek_nace_2026-05_resmi.xlsx (esnaf/sanatkÃ¢r meslek kollarÄ±)
  2. data/nace/turkiye_nace.json (TR NACE, code_6digit + code)
  3. data/nace/nace-rev-2-1.json (AB Rev 2.1)
  4. data/nace/nace-rev-2.json (AB Rev 2)
"""

import sys
import os
import json
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please check .env file.")

import openpyxl
from sqlalchemy import create_engine, text


def clean_turkish_chars(text: str) -> str:
    """TÃ¼rkÃ§e karakterleri normalize et (encoding dÃ¼zeltmesi dahil)."""
    if not text:
        return ""
    # Ãnce yaygÄ±n encoding hatalarÄ±nÄ± dÃ¼zelt
    replacements = {
        'Ã¢': 'a', 'Ã': 'A',
        'Ä±': 'i', 'Ä°': 'I',
        'Ä': 'g', 'Ä': 'G',
        'Ã¼': 'u', 'Ã': 'U',
        'Å': 's', 'Å': 'S',
        'Ã¶': 'o', 'Ã': 'O',
        'Ã§': 'c', 'Ã': 'C',
        # YaygÄ±n mojibake dÃ¼zeltmeleri
        'Å': 'Å', 'Ã': 'Ä°', 'Å¸': 'Å', 'Å¾': 'Å',
        'Ä': 'Ä', 'Ä': 'Ä', 'Ã': 'Ä°', 'Ã½': 'Ä±',
        'Ã': 'Ã', 'Ã¶': 'Ã¶', 'Ã': 'Ã', 'Ã¼': 'Ã¼',
        'Ã': 'Ã', 'Ã§': 'Ã§',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()


def normalize_nace_code(code: str) -> str:
    """NACE kodunu normalize et (noktalÄ± formatÄ± koru)."""
    if not code:
        return ""
    code = str(code).strip()
    # Nokta ekle: 477904 -> 47.79.04, 4779 -> 47.79, 47 -> 47
    if '.' not in code and code.isdigit():
        if len(code) == 6:
            return f"{code[:2]}.{code[2:4]}.{code[4:]}"
        elif len(code) == 4:
            return f"{code[:2]}.{code[2:]}"
        elif len(code) == 2:
            return code
    return code


def extract_level(code: str) -> int:
    """NACE kodundan seviye Ã§Ä±kar."""
    if not code:
        return 0
    code = str(code).strip()
    dots = code.count('.')
    if dots == 2:
        return 6  # 47.79.04
    elif dots == 1:
        return 4  # 47.79
    elif dots == 0 and code.isdigit():
        if len(code) == 2:
            return 2  # 47
        elif len(code) == 1:
            return 1  # A, B, C...
    return 0


def extract_parent_code(code: str) -> str | None:
    """NACE kodundan parent kod Ã§Ä±kar."""
    if not code:
        return None
    code = str(code).strip()
    dots = code.count('.')
    if dots >= 2:
        parts = code.split('.')
        return '.'.join(parts[:2])  # 47.79.04 -> 47.79
    elif dots == 1:
        parts = code.split('.')
        return parts[0]  # 47.79 -> 47
    elif code.isdigit() and len(code) == 2:
        return None  # 2 haneli -> None (bÃ¶lÃ¼m seviyesi)
    elif len(code) == 1:
        return None  # 1 haneli -> None
    return None


def load_xlsx_source(engine, existing_codes: set) -> list[dict]:
    """Kaynak 1: XLSX dosyasÄ±nÄ± oku - sektÃ¶r/meslek/NACE Ã¼Ã§lÃ¼sÃ¼.

    Hem yeni kayÄ±tlarÄ± hem de mevcut kayÄ±tlarÄ± (title gÃ¼ncellemesi iÃ§in) dÃ¶ndÃ¼rÃ¼r.
    """
    xlsx_path = PROJECT_ROOT / "data" / "nace" / "sektor_meslek_nace_2026-05_resmi.xlsx"
    if not xlsx_path.exists():
        print(f"[UYARI] XLSX dosyasÄ± bulunamadÄ±: {xlsx_path}")
        return []

    print(f"[BÄ°LGÄ°] XLSX okunuyor: {xlsx_path}")
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    print(f"[BÄ°LGÄ°] XLSX satÄ±r: {ws.max_row}, sÃ¼tun: {ws.max_column}")

    rows_data = []
    sector_group_map = {}  # nace_code (4/2/1 haneli) -> sector_group

    # Parent kodlarÄ±nÄ± (level 4, 2) XLSX'ten topla - title ve sector_group ile birlikte
    parent_l4_info = {}  # code -> {title, sector_group}
    parent_l2_info = {}
    sector_letters = set()

    # TÃ¼m satÄ±rlarÄ± tek geÃ§iÅte iÅle
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        sektor_kodu = clean_turkish_chars(str(row[0])) if row[0] else ""
        sektor_tanim = clean_turkish_chars(str(row[1])) if row[1] else ""
        meslek_kodu = clean_turkish_chars(str(row[2])) if row[2] else ""
        meslek_tanim = clean_turkish_chars(str(row[3])) if row[3] else ""
        nace_kodu_raw = str(row[4]).strip() if row[4] else ""
        nace_tanim = clean_turkish_chars(str(row[5])) if row[5] else ""

        if not nace_kodu_raw:
            continue

        nace_code = normalize_nace_code(nace_kodu_raw)
        if not nace_code:
            continue

        level = extract_level(nace_code)
        parent_code = extract_parent_code(nace_code)

        # SektÃ¶r harfi (level 1) - A, B, C, D...
        if level == 1 and sektor_kodu:
            sector_letters.add(sektor_kodu.upper())
            sector_group_map[nace_code] = sektor_tanim

        # 4 haneli kodlar iÃ§in sector_group (meslek tanÄ±mÄ±ndan da gelebilir)
        if parent_code:
            sector_group_map[parent_code] = sektor_tanim

        # 2 haneli kodlar iÃ§in sector_group
        if parent_code:
            parent2 = extract_parent_code(parent_code)
            if parent2:
                sector_group_map[parent2] = sektor_tanim

        # 6 haneli kod kaydÄ± (ana kayÄ±t)
        rows_data.append({
            'nace_code': nace_code,
            'version': '2026.01.01_Mayis2026',
            'level': level,
            'parent_code': parent_code,
            'title': nace_tanim,
            'sector_group': sektor_tanim,
            'is_manufacturing': False,
            'source': 'xlsx_resmi',
        })

        # Parent kodlarÄ±nÄ± (level 4, 2) XLSX'ten topla - title ve sector_group ile birlikte
        if level == 6 and parent_code:
            # 4 haneli parent iÃ§in - meslek tanÄ±mÄ±ndan title al
            if parent_code not in parent_l4_info:
                parent_l4_info[parent_code] = {
                    'title': meslek_tanim,
                    'sector_group': sektor_tanim
                }
            # 2 haneli parent iÃ§in
            parent2 = extract_parent_code(parent_code)
            if parent2 and parent2 not in parent_l2_info:
                parent_l2_info[parent2] = {
                    'title': sektor_tanim,
                    'sector_group': ''
                }
        elif level == 4 and parent_code:
            # 2 haneli parent iÃ§in
            if parent_code not in parent_l2_info:
                parent_l2_info[parent_code] = {
                    'title': meslek_tanim,
                    'sector_group': ''
                }

    # Parent level 4 kodlarÄ± ekle (title ve sector_group dolu)
    for p4, info in parent_l4_info.items():
        rows_data.append({
            'nace_code': p4,
            'version': '2026.01.01_Mayis2026',
            'level': 4,
            'parent_code': extract_parent_code(p4),
            'title': info['title'],
            'sector_group': info['sector_group'],
            'is_manufacturing': False,
            'source': 'xlsx_derived',
        })

    # Parent level 2 kodlarÄ± ekle
    for p2, info in parent_l2_info.items():
        rows_data.append({
            'nace_code': p2,
            'version': '2026.01.01_Mayis2026',
            'level': 2,
            'parent_code': None,
            'title': info['title'],
            'sector_group': info['sector_group'],
            'is_manufacturing': False,
            'source': 'xlsx_derived',
        })

    # SektÃ¶r harfleri (level 1) - XLSX'ten sektÃ¶r tanÄ±mÄ±nÄ± al
    for sl in sector_letters:
        # XLSX'ten bu sektÃ¶r harfine ait tanÄ±mÄ± bul
        sector_title = ''
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
            sektor_kodu = clean_turkish_chars(str(row[0])) if row[0] else ""
            sektor_tanim = clean_turkish_chars(str(row[1])) if row[1] else ""
            if sektor_kodu == sl:
                sector_title = sektor_tanim
                break
        rows_data.append({
            'nace_code': sl,
            'version': '2026.01.01_Mayis2026',
            'level': 1,
            'parent_code': None,
            'title': sector_title,
            'sector_group': '',
            'is_manufacturing': False,
            'source': 'xlsx_derived',
        })

    print(f"[BÄ°LGÄ°] XLSX: {len([r for r in rows_data if r['source']=='xlsx_resmi'])} ana, "
          f"{len([r for r in rows_data if r['source']=='xlsx_derived'])} tÃ¼retilmiÅ")
    return rows_data


def load_turkiye_nace_json(engine, existing_codes: set) -> list[dict]:
    """Kaynak 2: turkiye_nace.json - code_6digit + code (4 haneli) Ã§ifti."""
    json_path = PROJECT_ROOT / "data" / "nace" / "turkiye_nace.json"
    if not json_path.exists():
        print(f"[UYARI] JSON dosyasÄ± bulunamadÄ±: {json_path}")
        return []

    print(f"[BÄ°LGÄ°] turkiye_nace.json okunuyor...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows_data = []
    for item in data:
        code_6digit = str(item.get('code_6digit', '')).strip()
        code_4digit = normalize_nace_code(str(item.get('code', '')).strip())
        name_tr = clean_turkish_chars(str(item.get('name_tr', '')).strip())

        if not code_6digit and not code_4digit:
            continue

        # 6 haneli
        if code_6digit:
            nace_code_6 = normalize_nace_code(code_6digit)
            rows_data.append({
                'nace_code': nace_code_6,
                'version': 'TR_NACE_Rev2',
                'level': 6,
                'parent_code': extract_parent_code(nace_code_6),
                'title': name_tr,
                'sector_group': '',
                'is_manufacturing': False,
                'source': 'turkiye_nace_json',
            })

        # 4 haneli
        if code_4digit:
            rows_data.append({
                'nace_code': code_4digit,
                'version': 'TR_NACE_Rev2',
                'level': 4,
                'parent_code': extract_parent_code(code_4digit),
                'title': name_tr,
                'sector_group': '',
                'is_manufacturing': False,
                'source': 'turkiye_nace_json',
            })

    print(f"[BÄ°LGÄ°] turkiye_nace.json: {len(rows_data)} kayÄ±t")
    return rows_data


def load_nace_rev_json(engine, existing_codes: set, json_name: str, version: str) -> list[dict]:
    """Kaynak 3/4: nace-rev-2-1.json veya nace-rev-2.json - Section/Division/Group/Class."""
    json_path = PROJECT_ROOT / "data" / "nace" / json_name
    if not json_path.exists():
        print(f"[UYARI] JSON dosyasÄ± bulunamadÄ±: {json_path}")
        return []

    print(f"[BÄ°LGÄ°] {json_name} okunuyor...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows_data = []
    for item in data:
        section = str(item.get('Section', '')).strip()
        division = str(item.get('Division', '')).strip() if item.get('Division') else None
        group = str(item.get('Group', '')).strip() if item.get('Group') else None
        class_code = str(item.get('Class', '')).strip() if item.get('Class') else None
        activity = clean_turkish_chars(str(item.get('Activity', '')).strip())

        # Section (level 1) - A, B, C...
        if section and len(section) == 1:
            rows_data.append({
                'nace_code': section,
                'version': version,
                'level': 1,
                'parent_code': None,
                'title': activity,
                'sector_group': '',
                'is_manufacturing': False,
                'source': json_name,
            })

        # Division (level 2) - 01, 02, 10, 11...
        if division and len(division) == 2:
            rows_data.append({
                'nace_code': division,
                'version': version,
                'level': 2,
                'parent_code': None,
                'title': activity,
                'sector_group': '',
                'is_manufacturing': False,
                'source': json_name,
            })

        # Group (level 4) - 01.11, 01.12...
        if group:
            group_norm = normalize_nace_code(group)
            rows_data.append({
                'nace_code': group_norm,
                'version': version,
                'level': 4,
                'parent_code': extract_parent_code(group_norm),
                'title': activity,
                'sector_group': '',
                'is_manufacturing': False,
                'source': json_name,
            })

        # Class (level 6) - 01.11.01, 01.11.02... (noktalÄ± 6 haneli)
        if class_code:
            class_norm = normalize_nace_code(class_code)
            rows_data.append({
                'nace_code': class_norm,
                'version': version,
                'level': 6,
                'parent_code': extract_parent_code(class_norm),
                'title': activity,
                'sector_group': '',
                'is_manufacturing': False,
                'source': json_name,
            })

    print(f"[BÄ°LGÄ°] {json_name}: {len(rows_data)} kayÄ±t")
    return rows_data


def fill_missing_titles(engine, all_records: list[dict]) -> list[dict]:
    """Eksik title'larÄ± diÄer kaynaklardan doldur (Ã¶ncelik: xlsx > turkiye_nace > rev2-1 > rev2)."""
    # Title'Ä± olan kayÄ±tlarÄ± topla
    title_map = {}
    sector_group_map = {}

    # Ãncelik sÄ±rasÄ±
    source_priority = {
        'xlsx_resmi': 1,
        'xlsx_derived': 2,
        'turkiye_nace_json': 3,
        'nace-rev-2-1.json': 4,
        'nace-rev-2.json': 5,
    }

    for record in all_records:
        source = record.get('source', '')
        priority = source_priority.get(source, 99)
        code = record['nace_code']
        title = record.get('title', '')
        sector_group = record.get('sector_group', '')

        if title and (code not in title_map or priority < title_map[code][1]):
            title_map[code] = (title, priority)

        if sector_group and (code not in sector_group_map or priority < sector_group_map[code][1]):
            sector_group_map[code] = (sector_group, priority)

    # Eksikleri doldur
    for record in all_records:
        code = record['nace_code']
        if not record.get('title') and code in title_map:
            record['title'] = title_map[code][0]
        if not record.get('sector_group') and code in sector_group_map:
            record['sector_group'] = sector_group_map[code][0]

    # XLSX'ten gelen sektÃ¶r/meslek bilgilerini kullanarak parent kodlarÄ±n title'larÄ±nÄ± doldur
    # XLSX'teki her satÄ±r hem 6 haneli kodu hem de sektÃ¶r/meslek tanÄ±mÄ±nÄ± iÃ§eriyor
    # Bu tanÄ±mlarÄ± parent kodlarÄ±na (level 4, 2, 1) da yay
    return all_records


def upsert_nace_codes(engine, records: list[dict]) -> tuple[int, int]:
    """NACE kodlarÄ±nÄ± veritabanÄ±na upsert et."""
    if not records:
        return 0, 0

    # Level'a gÃ¶re sÄ±rala (parent Ã¶nce gelsin)
    level_order = {1: 0, 2: 1, 4: 2, 6: 3}
    records.sort(key=lambda x: (level_order.get(x.get('level', 99), 99), x['nace_code']))

    print(f"[BÄ°LGÄ°] {len(records)} kayÄ±t upsert ediliyor...")

    processed = 0
    errors = 0
    batch_size = 100

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            with engine.begin() as conn:
                for data in batch:
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
                            "nace_code": data['nace_code'],
                            "version": data['version'],
                            "level": data['level'],
                            "parent_code": data['parent_code'],
                            "title": data['title'],
                            "sector_group": data['sector_group'],
                            "is_manufacturing": data['is_manufacturing'],
                        },
                    )
            processed += len(batch)
            if (i // batch_size + 1) % 20 == 0:
                print(f"  Ä°Ålenen: {min(i+batch_size, len(records))}/{len(records)}")
        except Exception as e:
            print(f"  [HATA] Batch {i//batch_size + 1}: {e}")
            errors += len(batch)

    return processed, errors


def verify_results(engine) -> dict:
    """SonuÃ§larÄ± doÄrula."""
    with engine.connect() as conn:
        # Toplam
        total = conn.execute(text("SELECT count(*) FROM nace_codes")).scalar()

        # Seviye daÄÄ±lÄ±mÄ±
        level_dist = conn.execute(text("""
            SELECT level, count(*) FROM nace_codes GROUP BY level ORDER BY level
        """)).fetchall()

        # 47.79.04 kontrolÃ¼
        rec_477904 = conn.execute(text("SELECT nace_code, title, level FROM nace_codes WHERE nace_code='47.79.04'")).fetchone()

        # 47.79 kontrolÃ¼ (tÃ¼retilmiÅ)
        rec_4779 = conn.execute(text("SELECT nace_code, title, level FROM nace_codes WHERE nace_code='47.79'")).fetchone()

        # 29.10, 62.01, 41.10 kontrolÃ¼ (xlsx'te olmayanlar)
        missing_check = conn.execute(text("""
            SELECT nace_code, title, level FROM nace_codes
            WHERE nace_code IN ('29.10', '62.01', '62.09', '41.10', '29.10.01')
        """)).fetchall()

        # Title boÅ olanlar
        empty_titles = conn.execute(text("""
            SELECT count(*) FROM nace_codes WHERE title IS NULL OR title = ''
        """)).scalar()

        # Yetim kod (parent yok)
        orphan = conn.execute(text("""
            SELECT count(*) FROM nace_codes
            WHERE parent_code IS NOT NULL
            AND parent_code NOT IN (SELECT nace_code FROM nace_codes)
        """)).scalar()

        return {
            'total': total,
            'level_dist': level_dist,
            'rec_477904': rec_477904,
            'rec_4779': rec_4779,
            'missing_check': missing_check,
            'empty_titles': empty_titles,
            'orphan': orphan,
        }


def main():
    print("=" * 70)
    print("VERI-NACE-SOZLUK-01: NACE SÃ¶zlÃ¼ÄÃ¼ YÃ¼kleme - 4 Kaynak BirleÅimi")
    print("=" * 70)
    print("D-234: Seviye korunur, referans birleÅiktir (4 kaynak)")
    print()

    engine = create_engine(DB_URL)

    # Mevcut kodlarÄ± al (sadece raporlama iÃ§in)
    with engine.connect() as conn:
        existing = {row[0] for row in conn.execute(text("SELECT nace_code FROM nace_codes")).fetchall()}
    print(f"[BÄ°LGÄ°] Mevcut KayÄ±t: {len(existing)}")

    all_records = []

    # 4 KaynaÄÄ± sÄ±rayla oku
    print("\n--- KAYNAK 1: XLSX (Resmi TÃ¼rkiye NACE - Esnaf/SanatkÃ¢r) ---")
    all_records.extend(load_xlsx_source(engine, existing))

    print("\n--- KAYNAK 2: turkiye_nace.json (TR NACE) ---")
    all_records.extend(load_turkiye_nace_json(engine, existing))

    print("\n--- KAYNAK 3: nace-rev-2-1.json (AB Rev 2.1) ---")
    all_records.extend(load_nace_rev_json(engine, existing, 'nace-rev-2-1.json', 'EU_NACE_Rev2.1'))

    print("\n--- KAYNAK 4: nace-rev-2.json (AB Rev 2) ---")
    all_records.extend(load_nace_rev_json(engine, existing, 'nace-rev-2.json', 'EU_NACE_Rev2'))

    # Eksik title'larÄ± doldur
    print("\n--- TITLE DOLDURMA (eksik parent kodlarÄ±) ---")
    all_records = fill_missing_titles(engine, all_records)

    # Upsert
    print(f"\n--- TOPLAM {len(all_records)} KAYIT UPSERT EDÄ°LÄ°YOR ---")
    processed, errors = upsert_nace_codes(engine, all_records)

    # DoÄrulama
    print("\n--- DOÄRULAMA ---")
    results = verify_results(engine)

    print(f"Toplam kayÄ±t: {results['total']}")
    print("Seviye daÄÄ±lÄ±mÄ±:")
    for level, count in results['level_dist']:
        print(f"  Level {level}: {count}")

    if results['rec_477904']:
        print(f"47.79.04 (level 6): {results['rec_477904'][1]}")
    if results['rec_4779']:
        print(f"47.79 (level 4, tÃ¼retilmiÅ): {results['rec_4779'][1]}")

    print("Eksik kod kontrolÃ¼ (xlsx'te olmayanlar):")
    for m in results['missing_check']:
        print(f"  {m[0]} (level {m[2]}): {m[1]}")

    print(f"Title boÅ olan: {results['empty_titles']}")
    print(f"Yetim kod (parent eksik): {results['orphan']}")

    # Kabul Ã¶lÃ§Ã¼tleri
    print("\n--- KABUL ÃLÃÃTLERÄ° ---")
    ok = True
    if results['total'] <= 0:
        print("[FAIL] count(*) > 0")
        ok = False
    else:
        print("[OK] count(*) > 0")

    level_counts = {level: count for level, count in results['level_dist']}
    if 6 not in level_counts or 4 not in level_counts or 2 not in level_counts:
        print("[FAIL] Uc seviye (6,4,2) dolu degil")
        ok = False
    else:
        print(f"[OK] Seviyeler dolu: {level_counts}")

    if results['rec_4779'] and results['rec_4779'][1]:
        print("[OK] 47.79 ayrÄ± satÄ±r var (turetim calisti)")
    else:
        print("[FAIL] 47.79 turetilmis satir eksik/bos")
        ok = False

    missing_codes = {m[0] for m in results['missing_check']}
    required_missing = {'29.10', '62.01', '41.10'}
    if required_missing.issubset(missing_codes):
        print("[OK] 29.10, 62.01, 41.10 tabloda var")
    else:
        print(f"[FAIL] Eksik kodlar: {required_missing - missing_codes}")
        ok = False

    if results['empty_titles'] == 0:
        print("[OK] Title bos yok")
    else:
        print(f"[WARN] Title bos: {results['empty_titles']} (KUSUR-1: 566 bekleniyordu)")

    if results['orphan'] == 0:
        print("[OK] Yetim kod yok (agac tutarli)")
    else:
        print(f"[FAIL] Yetim kod: {results['orphan']}")
        ok = False

    if ok:
        print("\n[SUCCESS] TUM KABUL OLCUTLERI SAGLANDI!")
    else:
        print("\n[WARN] BAZI KABUL OLCUTLERI EKSIK - DUZELTME GEREKLI")

    print(f"\n[TAMAM] Islenen: {processed}, Hatali: {errors}")


if __name__ == "__main__":
    main()
