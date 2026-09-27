# -*- coding: utf-8 -*-
"""VERI-KAYNAK-BAG-01 EK: NACE temizlik (7614 NN.NN, 675 altı haneli, 25 iki haneli, yetim kodlar).
Kaynak: source_records.raw_nace (company_id link kurulduktan sonra).
"""

import os
import re
from collections import defaultdict
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text


def normalize_nace(code: str) -> str:
    """NACE kodunu normalize et."""
    if not code:
        return ""
    code = str(code).strip()
    if '.' not in code and code.isdigit():
        if len(code) == 6:
            return f"{code[:2]}.{code[2:4]}.{code[4:]}"
        elif len(code) == 4:
            return f"{code[:2]}.{code[2:]}"
        elif len(code) == 2:
            return code
    return code


def extract_level(code: str) -> int:
    if not code:
        return 0
    code = str(code).strip()
    dots = code.count('.')
    if dots == 2:
        return 6
    elif dots == 1:
        return 4
    elif dots == 0 and code.isdigit():
        if len(code) == 2:
            return 2
        elif len(code) == 1:
            return 1
    return 0


def get_parent_code(code: str) -> str | None:
    if not code:
        return None
    code = str(code).strip()
    dots = code.count('.')
    if dots >= 2:
        parts = code.split('.')
        return '.'.join(parts[:2])
    elif dots == 1:
        return code.split('.')[0]
    elif code.isdigit() and len(code) == 2:
        return None
    return None


def main():
    print("=" * 70)
    print("VERI-KAYNAK-BAG-01: NACE temizlik (ek kapsam)")
    print("=" * 70)

    engine = create_engine(os.getenv('DATABASE_URL'))

    # 1. nace_codes sözlüğünü yükle (valid kodlar)
    print("\n[1/6] nace_codes sözlüğü yükleniyor...")
    with engine.connect() as conn:
        valid_codes = {row[0] for row in conn.execute(text("SELECT nace_code FROM nace_codes")).fetchall()}
    print(f"  Geçerli NACE kod sayısı: {len(valid_codes)}")

    # 2. Company_id dolu source_records'tan raw_nace çek
    print("\n[2/6] Source_records raw_nace çekiliyor (company_id dolu olanlar)...")
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT sr.company_id, sr.raw_nace
            FROM source_records sr
            WHERE sr.company_id IS NOT NULL
              AND sr.raw_nace IS NOT NULL
              AND sr.raw_nace <> ''
        """)).fetchall()

    # company_id -> raw_nace listesi
    company_raw_nace = defaultdict(list)
    for company_id, raw_nace in rows:
        company_raw_nace[company_id].append(raw_nace)

    print(f"  raw_nace olan company sayısı: {len(company_raw_nace)}")
    total_raw = sum(len(v) for v in company_raw_nace.values())
    print(f"  Toplam raw_nace kaydı: {total_raw}")

    # 3. Her company için en iyi NACE kodunu belirle
    print("\n[3/6] Her company için en iyi NACE kodu belirleniyor...")

    # nace_codes'tan valid kod seti
    valid_set = valid_codes

    # Her raw_nace'i parse et ve valid kodları topla
    company_candidates = defaultdict(lambda: defaultdict(int))  # company_id -> {nace_code: count}

    for company_id, raw_list in company_raw_nace.items():
        for raw in raw_list:
            if not raw:
                continue
            # raw_nace içinde birden fazla kod olabilir (virgül, noktalı virgül, pipe)
            # Basit ayırıcı: virgül, noktalı virgül, pipe, boşluk
            parts = re.split(r'[,\;\|\s]+', str(raw))
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                norm = normalize_nace(part)
                if norm in valid_set:
                    company_candidates[company_id][norm] += 1

    # Her company için en sık görülen valid kodu seç
    company_best_nace = {}
    for company_id, candidates in company_candidates.items():
        if candidates:
            best = max(candidates.items(), key=lambda x: x[1])[0]
            company_best_nace[company_id] = best

    print(f"  raw_nace'ten kod türetilen company: {len(company_best_nace)}")

    # 4. Mevcut companies nace_code durumunu analiz et
    print("\n[4/6] Mevcut nace_code analizi...")
    with engine.connect() as conn:
        # NN.NN format (4 haneli ama noktalı)
        nn_nn = conn.execute(text("""
            SELECT company_id, nace_code FROM companies
            WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}$'
        """)).fetchall()

        # 6 haneli
        six_digit = conn.execute(text("""
            SELECT company_id, nace_code FROM companies
            WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}\\.[0-9]{2}$'
        """)).fetchall()

        # 2 haneli
        two_digit = conn.execute(text("""
            SELECT company_id, nace_code FROM companies
            WHERE nace_code ~ '^[0-9]{2}$'
        """)).fetchall()

        # Yetim kodlar (nace_codes'ta yok)
        orphans = conn.execute(text("""
            SELECT c.company_id, c.nace_code
            FROM companies c
            LEFT JOIN nace_codes nc ON c.nace_code = nc.nace_code
            WHERE c.nace_code IS NOT NULL
              AND nc.nace_code IS NULL
        """)).fetchall()

    print(f"  NN.NN format (düzeltilecek): {len(nn_nn)}")
    print(f"  6 haneli (kırpılacak/NULL): {len(six_digit)}")
    print(f"  2 haneli (kırpılacak/NULL): {len(two_digit)}")
    print(f"  Yetim kodlar (eşlenecek/NULL): {len(orphans)}")

    # 5. Düzeltmeleri hazırla
    print("\n[5/6] Düzeltmeler hazırlanıyor...")
    updates = []  # (company_id, new_nace_code)

    # 5a. NN.NN format -> raw_nace'ten türet / valid 4 haneli varsa kullan / NULL
    for company_id, nace_code in nn_nn:
        # Önce raw_nace'ten türetilmiş varsa onu kullan
        if company_id in company_best_nace:
            updates.append((company_id, company_best_nace[company_id]))
        else:
            # 4 haneli valid parent'a kırp (örn: 29.10 -> 29.10 zaten 4 haneli ama format yanlış)
            # Burada NN.NN zaten 4 haneli noktalı formatta, ama nace_codes'ta yoksa NULL
            # nace_codes'ta varsa olduğu gibi kalsın (bazıları valid olabilir)
            if nace_code in valid_set:
                pass  # zaten valid, dokunma
            else:
                # Parent 2 haneli kontrol et
                parent2 = nace_code.split('.')[0] if '.' in nace_code else None
                if parent2 and f"{parent2}.00" in valid_set:
                    pass  # parent valid ama child yok
                updates.append((company_id, None))  # NULL'a çek

    # 5b. 6 haneli -> 4 haneli sınıfa kırp (validse) / NULL
    for company_id, nace_code in six_digit:
        parent4 = get_parent_code(nace_code)  # 4 haneli parent
        if parent4 and parent4 in valid_set:
            updates.append((company_id, parent4))
        else:
            updates.append((company_id, None))

    # 5c. 2 haneli -> 4 haneli varsa genişlet / NULL (98 gibi)
    for company_id, nace_code in two_digit:
        # 2 haneli kod için 4 haneli child ara
        children = [c for c in valid_set if c.startswith(nace_code + '.')]
        if len(children) == 1:
            updates.append((company_id, children[0]))  # tek child varsa o
        elif len(children) > 1:
            # birden fazla child var, belirsiz -> NULL
            updates.append((company_id, None))
        else:
            updates.append((company_id, None))

    # 5d. Yetim kodlar -> valid eşleşme ara / NULL
    for company_id, nace_code in orphans:
        # Benzer kod ara (prefix match)
        matches = [c for c in valid_set if c.startswith(nace_code[:4])] if len(nace_code) >= 4 else []
        if len(matches) == 1:
            updates.append((company_id, matches[0]))
        else:
            updates.append((company_id, None))

    print(f"  Toplam güncellenecek: {len(updates)}")

    # 6. Güncellemeyi uygula
    if updates:
        print("\n[6/6] Güncellemeler uygulanıyor...")
        with engine.begin() as conn:
            for company_id, new_nace in updates:
                conn.execute(
                    text("UPDATE companies SET nace_code = :nace WHERE company_id = :cid"),
                    {"nace": new_nace, "cid": company_id}
                )
        print("  Güncelleme tamamlandı.")

    # Doğrulama
    print("\n[Doğrulama]")
    with engine.connect() as conn:
        # NN.NN kalan
        nn = conn.execute(text("""
            SELECT COUNT(*) FROM companies
            WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}$'
        """)).scalar()
        print(f"NN.NN format kalan: {nn}")

        # 6 haneli kalan
        six = conn.execute(text("""
            SELECT COUNT(*) FROM companies
            WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}\\.[0-9]{2}$'
        """)).scalar()
        print(f"6 haneli kalan: {six}")

        # 2 haneli kalan
        two = conn.execute(text("""
            SELECT COUNT(*) FROM companies
            WHERE nace_code ~ '^[0-9]{2}$'
        """)).scalar()
        print(f"2 haneli kalan: {two}")

        # Yetim kod kalan
        orphan = conn.execute(text("""
            SELECT COUNT(*) FROM companies c
            LEFT JOIN nace_codes nc ON c.nace_code = nc.nace_code
            WHERE c.nace_code IS NOT NULL AND nc.nace_code IS NULL
        """)).scalar()
        print(f"Yetim kod kalan: {orphan}")

        # 10.11, 29.10 örnek firmaları
        for code in ['10.11', '29.10']:
            rows = conn.execute(text(f"SELECT company_id, nace_code FROM companies WHERE nace_code = '{code}' LIMIT 3")).fetchall()
            print(f"\n{code} örnek firmaları:")
            for r in rows:
                print(f"  {r[0]}: {r[1]}")

    print("\n" + "=" * 70)
    print("NACE TEMIZLIK TAMAMLANDI")
    print("=" * 70)


if __name__ == "__main__":
    import os
    main()
