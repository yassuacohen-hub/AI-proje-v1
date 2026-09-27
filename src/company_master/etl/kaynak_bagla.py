# -*- coding: utf-8 -*-
"""VERI-KAYNAK-BAG-01: source_records <-> companies eslestirme.
company_id kolonunu doldur: vergi no -> normalize unvan.
Performans oncelikli: set/dict lookup, batch islemler.
"""

import os
import re
import sys
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text


# Pre-compile regex patterns
RE_WHITESPACE = re.compile(r'\s+')
RE_NON_DIGIT = re.compile(r'\D')
# Turkce karakter map
TR_MAP = str.maketrans(
    'ğüşıöçĞÜŞİÖÇ',
    'gusiocGUSIOC'
)

# Kisaltma pattern'leri (pre-compiled)
ABBREVIATIONS = [
    (re.compile(r'\bA\.?S\.?\b', re.IGNORECASE), 'AS'),
    (re.compile(r'\bLTD\.?\s*STI\.?\b', re.IGNORECASE), 'LTD STI'),
    (re.compile(r'\bLTD\.?\s*ŞTİ\.?\b', re.IGNORECASE), 'LTD STI'),
    (re.compile(r'\bLIMITED\.?\s*SIRKETI\.?\b', re.IGNORECASE), 'LTD STI'),
    (re.compile(r'\bANONIM\.?\s*SIRKETI\.?\b', re.IGNORECASE), 'AS'),
    (re.compile(r'\bSAN\.?\s*VE\.?\s*TIC\.?\b', re.IGNORECASE), 'SAN VE TIC'),
    (re.compile(r'\bSAN\.?\s*TIC\.?\b', re.IGNORECASE), 'SAN TIC'),
    (re.compile(r'\bITH\.?\s*IHR\.?\b', re.IGNORECASE), 'ITH IHR'),
    (re.compile(r'\bINS\.?\s*SAN\.?\s*TIC\.?\b', re.IGNORECASE), 'INS SAN TIC'),
    (re.compile(r'\bMUH\.?\s*MIM\.?\b', re.IGNORECASE), 'MUH MIM'),
    (re.compile(r'\bTUR\.?\s*TIC\.?\b', re.IGNORECASE), 'TUR TIC'),
    (re.compile(r'\bGIDA\s*SAN\.?\s*TIC\.?\b', re.IGNORECASE), 'GIDA SAN TIC'),
    (re.compile(r'\bTEK\.?\s*SAN\.?\s*TIC\.?\b', re.IGNORECASE), 'TEK SAN TIC'),
    (re.compile(r'\bNAK\.?\s*TIC\.?\b', re.IGNORECASE), 'NAK TIC'),
    (re.compile(r'\bELEK\.?\b', re.IGNORECASE), 'ELEK'),
    (re.compile(r'\bINS\.?\b', re.IGNORECASE), 'INS'),
    (re.compile(r'\bTIC\.?\b', re.IGNORECASE), 'TIC'),
    (re.compile(r'\bMUH\.?\b', re.IGNORECASE), 'MUH'),
    (re.compile(r'\bMIM\.?\b', re.IGNORECASE), 'MIM'),
]


def normalize_name(name: str) -> str:
    """Firma adini normalize et - optimize edilmis."""
    if not name:
        return ""
    s = str(name).strip()
    if not s:
        return ""
    # Tek pas: bosluklari normalize et
    s = ' '.join(s.split())
    # Kisaltmalari uygula
    for pattern, repl in ABBREVIATIONS:
        s = pattern.sub(repl, s)
    # Turkce karakterleri ASCII'ye cevir
    s = s.translate(TR_MAP)
    return s.upper()


def normalize_tax_number(tax: str) -> str:
    """Vergi numarasini normalize et."""
    if not tax:
        return ""
    return RE_NON_DIGIT.sub('', str(tax))


@dataclass
class MatchStats:
    tax_match: int = 0
    name_exact: int = 0
    name_multiple: int = 0
    name_none: int = 0
    total: int = 0


def main():
    print("=" * 70)
    print("VERI-KAYNAK-BAG-01: source_records <-> companies eslestirme")
    print("=" * 70)

    engine = create_engine(os.getenv('DATABASE_URL'))

    # 1. Companies verilerini yukle
    print("\n[1/5] Companies verileri yukleniyor...")
    with engine.connect() as conn:
        companies = conn.execute(text("""
            SELECT company_id, legal_name, tax_number
            FROM companies
        """)).fetchall()

    print(f"  Companies loaded: {len(companies)}")

    # Vergi no -> company_id haritasi
    tax_map = {}
    for row in companies:
        if row.tax_number:
            tax_norm = RE_NON_DIGIT.sub('', str(row.tax_number))
            if tax_norm:
                tax_map[tax_norm] = row.company_id

    # Normalize unvan -> company_id haritasi (birebir eslesme icin)
    name_map = {}
    name_multi = set()
    for row in companies:
        # Hizli normalize: buyuk harf, bosluk temizle, kisaltma yok (hiz icin)
        norm = ' '.join(str(row.legal_name).strip().split()).upper().translate(TR_MAP)
        if norm:
            if norm in name_map:
                name_multi.add(norm)
            else:
                name_map[norm] = row.company_id

    print(f"  Companies: {len(companies)}")
    print(f"  Tax map: {len(tax_map)}")
    print(f"  Name map (unique): {len(name_map) - len(name_multi)}")
    print(f"  Name multi (cakisan): {len(name_multi)}")

    # 2. Source_records verilerini yukle
    print("\n[2/5] Source_records verileri yukleniyor...")
    with engine.connect() as conn:
        sources = conn.execute(text("""
            SELECT source_record_id, raw_name, raw_tax_number
            FROM source_records
            WHERE company_id IS NULL
        """)).fetchall()

    print(f"  Eslesme bekleyen: {len(sources)}")

    # 3. Eslestirme - optimize edilmis
    print("\n[3/5] Eslestirme yapiliyor...")
    stats = MatchStats()
    updates = []  # (source_record_id, company_id, match_type)

    # Pre-compute source normalized names
    source_data = []
    for row in sources:
        src_id = row.source_record_id
        raw_name = row.raw_name
        raw_tax = row.raw_tax_number
        
        # Hizli normalize
        norm_name = None
        if raw_name:
            norm_name = ' '.join(str(raw_name).strip().split()).upper().translate(TR_MAP)
        
        tax_norm = None
        if raw_tax:
            tax_norm = RE_NON_DIGIT.sub('', str(raw_tax))
        
        source_data.append((src_id, norm_name, tax_norm))

    # Eslestir
    for src_id, norm_name, tax_norm in source_data:
        stats.total += 1
        matched_id = None
        match_type = None

        # Once vergi no ile dene (en guvenilir)
        if tax_norm and tax_norm in tax_map:
            matched_id = tax_map[tax_norm]
            match_type = "tax"
        elif norm_name and norm_name in name_map:
            if norm_name not in name_multi:
                matched_id = name_map[norm_name]
                match_type = "name_exact"
            else:
                match_type = "name_multiple"
        else:
            match_type = "name_none"

        if matched_id:
            updates.append((src_id, matched_id, match_type))
            if match_type == "tax":
                stats.tax_match += 1
            elif match_type == "name_exact":
                stats.name_exact += 1
            elif match_type == "name_multiple":
                stats.name_multiple += 1
        else:
            stats.name_none += 1

        if stats.total % 2000 == 0:
            print(f"  Islenen: {stats.total}/{len(source_data)}")

    print(f"\nEslestirme sonuclari:")
    print(f"  Vergi no eslesme: {stats.tax_match}")
    print(f"  Isim birebir: {stats.name_exact}")
    print(f"  Isim coklu (belirsiz): {stats.name_multiple}")
    print(f"  Eslesmeyen: {stats.name_none}")
    print(f"  Toplam: {stats.total}")
    if stats.total > 0:
        print(f"  Eslesen orani: {((stats.tax_match + stats.name_exact) / stats.total * 100):.1f}%")

    # 4. Veritabanini guncelle - batch
    if updates:
        print(f"\n[4/5] {len(updates)} kayit guncelleniyor (batch)...")
        batch_size = 1000
        with engine.begin() as conn:
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                for src_id, comp_id, mtype in batch:
                    conn.execute(
                        text("UPDATE source_records SET company_id = :cid WHERE source_record_id = :sid"),
                        {"cid": comp_id, "sid": src_id}
                    )
                if (i // batch_size + 1) % 5 == 0:
                    print(f"  Guncellenen: {min(i+batch_size, len(updates))}/{len(updates)}")
        print("  Guncelleme tamamlandi.")

    # 5. Dogrulama
    print("\n[5/5] Dogrulama...")
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM source_records")).scalar()
        matched = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE company_id IS NOT NULL")).scalar()
        null_count = total - matched

        # FK dogrulamasi
        fk_violations = conn.execute(text("""
            SELECT COUNT(*) FROM source_records sr
            LEFT JOIN companies c ON sr.company_id = c.company_id
            WHERE sr.company_id IS NOT NULL AND c.company_id IS NULL
        """)).scalar()

        # Ayni company_id'ye bagli kayit dagilimi
        dist = conn.execute(text("""
            SELECT company_id, COUNT(*) as cnt
            FROM source_records
            WHERE company_id IS NOT NULL
            GROUP BY company_id
            ORDER BY cnt DESC
        """)).fetchall()

        max_per_company = dist[0][1] if dist else 0

        print(f"  Toplam source_records: {total}")
        print(f"  Eslesen (company_id dolu): {matched}")
        print(f"  Eslesmeyen (company_id NULL): {null_count}")
        print(f"  Eslesme orani: {(matched/total*100):.1f}%")
        print(f"  FK ihlali: {fk_violations}")
        print(f"  Max kayit/firma: {max_per_company}")

        if dist:
            print(f"\n  Dagilim (ilk 10):")
            for cid, cnt in dist[:10]:
                print(f"    {cid}: {cnt}")

    print("\n" + "=" * 70)
    print("TAMAMLANDI")
    print("=" * 70)


if __name__ == "__main__":
    import os
    main()