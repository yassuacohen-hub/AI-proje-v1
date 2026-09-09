#!/usr/bin/env python3
"""P45: Veri seti dogrulama ve duplicate temizleme - v3 (CASCADE)."""

import json
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

def main():
    print("P45: Veri seti dogrulama ve duplicate temizleme basliyor...")
    engine = get_engine()
    
    results = {
        "task": "P45",
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "total_companies_before": 0,
        "tax_number_duplicate_groups": 0,
        "tax_number_duplicate_records": 0,
        "tax_number_merged": 0,
        "tax_number_removed": 0,
        "legal_name_duplicate_groups": 0,
        "legal_name_duplicate_records": 0,
        "legal_name_merged": 0,
        "legal_name_removed": 0,
        "website_domain_duplicate_groups": 0,
        "website_domain_duplicate_records": 0,
        "website_domain_merged": 0,
        "website_domain_removed": 0,
        "duplicate_detected": 0,
        "duplicate_merged": 0,
        "duplicate_removed": 0,
        "invalid_records": {},
        "total_companies_after": 0,
        "merge_details": [],
        "errors": []
    }
    
    try:
        with engine.begin() as conn:
            results["total_companies_before"] = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
            print(f"Toplam sirket: {results['total_companies_before']}")
            
            print("Sirket verileri yukleniyor...")
            all_companies = conn.execute(text("""
                SELECT company_id::text, legal_name, trade_name, company_type, tax_number,
                       mersis_number, establishment_date, status, status_confidence,
                       employee_count, website_domain, primary_phone, primary_email,
                       description, data_quality_score, web_sitesi, vergi_no, osb_parsel,
                       adres, nace_name, nace_source, nace_code
                FROM companies
            """)).mappings().all()
            company_map = {c["company_id"]: c for c in all_companies}
            print(f"  {len(all_companies)} sirket yuklendi")
            
            all_removals = set()
            
            # 1. tax_number duplicate
            print("\n1. tax_number duplicate...")
            tax_groups = defaultdict(list)
            for c in all_companies:
                if c["tax_number"]:
                    tax_groups[c["tax_number"]].append(c["company_id"])
            tax_dup = {k: v for k, v in tax_groups.items() if len(v) > 1}
            results["tax_number_duplicate_groups"] = len(tax_dup)
            
            for tax_num, ids in tax_dup.items():
                best = max(ids, key=lambda cid: (
                    company_map[cid]["data_quality_score"] or 0,
                    sum(1 for f in ["legal_name", "tax_number", "website_domain", "primary_phone", "primary_email", "description", "adres", "web_sitesi", "vergi_no"] if company_map[cid].get(f))
                ))
                for rem_id in ids:
                    if rem_id != best:
                        all_removals.add(rem_id)
                        results["tax_number_duplicate_records"] += 1
                results["tax_number_merged"] += 1
                results["tax_number_removed"] += len(ids) - 1
            print(f"  {len(tax_dup)} grup, {results['tax_number_merged']} birlestirildi, {results['tax_number_removed']} silindi")
            
            # 2. legal_name duplicate
            print("\n2. legal_name duplicate...")
            name_groups = defaultdict(list)
            for c in all_companies:
                if c["legal_name"]:
                    name_groups[c["legal_name"]].append(c["company_id"])
            name_dup = {k: v for k, v in name_groups.items() if len(v) > 1}
            results["legal_name_duplicate_groups"] = len(name_dup)
            
            for name, ids in name_dup.items():
                best = max(ids, key=lambda cid: (
                    company_map[cid]["data_quality_score"] or 0,
                    sum(1 for f in ["legal_name", "tax_number", "website_domain", "primary_phone", "primary_email", "description", "adres", "web_sitesi", "vergi_no"] if company_map[cid].get(f))
                ))
                for rem_id in ids:
                    if rem_id != best:
                        all_removals.add(rem_id)
                        results["legal_name_duplicate_records"] += 1
                results["legal_name_merged"] += 1
                results["legal_name_removed"] += len(ids) - 1
            print(f"  {len(name_dup)} grup, {results['legal_name_merged']} birlestirildi, {results['legal_name_removed']} silindi")
            
            # 3. website_domain duplicate
            print("\n3. website_domain duplicate...")
            web_groups = defaultdict(list)
            for c in all_companies:
                if c["website_domain"]:
                    web_groups[c["website_domain"]].append(c["company_id"])
            web_dup = {k: v for k, v in web_groups.items() if len(v) > 1}
            results["website_domain_duplicate_groups"] = len(web_dup)
            
            for web, ids in web_dup.items():
                best = max(ids, key=lambda cid: (
                    company_map[cid]["data_quality_score"] or 0,
                    sum(1 for f in ["legal_name", "tax_number", "website_domain", "primary_phone", "primary_email", "description", "adres", "web_sitesi", "vergi_no"] if company_map[cid].get(f))
                ))
                for rem_id in ids:
                    if rem_id != best:
                        all_removals.add(rem_id)
                        results["website_domain_duplicate_records"] += 1
                results["website_domain_merged"] += 1
                results["website_domain_removed"] += len(ids) - 1
            print(f"  {len(web_dup)} grup, {results['website_domain_merged']} birlestirildi, {results['website_domain_removed']} silindi")
            
            # Birlestirme: en iyi kayda eksik alanlari ekle
            print(f"\nBirlestirme islemi ({len(all_removals)} kayit)...")
            merge_fields = [
                "trade_name", "company_type", "tax_number", "mersis_number",
                "establishment_date", "status", "status_confidence", "employee_count",
                "website_domain", "primary_phone", "primary_email", "description",
                "web_sitesi", "vergi_no", "osb_parsel", "adres",
                "nace_name", "nace_source", "nace_code"
            ]
            
            # Her keep_id icin hangi remove_id'ler birlesecek
            merge_map = defaultdict(set)
            # We need to re-derive keep_id from the duplicate groups
            # Since we already have all_removals, we need to know the keep_id for each
            # Let's rebuild from groups
            all_groups = []
            for tax_num, ids in tax_dup.items():
                best = max(ids, key=lambda cid: (
                    company_map[cid]["data_quality_score"] or 0,
                    sum(1 for f in ["legal_name", "tax_number", "website_domain", "primary_phone", "primary_email", "description", "adres", "web_sitesi", "vergi_no"] if company_map[cid].get(f))
                ))
                all_groups.append((best, [i for i in ids if i != best]))
            for name, ids in name_dup.items():
                best = max(ids, key=lambda cid: (
                    company_map[cid]["data_quality_score"] or 0,
                    sum(1 for f in ["legal_name", "tax_number", "website_domain", "primary_phone", "primary_email", "description", "adres", "web_sitesi", "vergi_no"] if company_map[cid].get(f))
                ))
                all_groups.append((best, [i for i in ids if i != best]))
            for web, ids in web_dup.items():
                best = max(ids, key=lambda cid: (
                    company_map[cid]["data_quality_score"] or 0,
                    sum(1 for f in ["legal_name", "tax_number", "website_domain", "primary_phone", "primary_email", "description", "adres", "web_sitesi", "vergi_no"] if company_map[cid].get(f))
                ))
                all_groups.append((best, [i for i in ids if i != best]))
            
            updates = []
            for keep_id, rem_ids in all_groups:
                best_data = dict(company_map[keep_id])
                merged_fields = []
                for rem_id in rem_ids:
                    rem_data = company_map[rem_id]
                    for field in merge_fields:
                        if not best_data.get(field) and rem_data.get(field):
                            best_data[field] = rem_data[field]
                            merged_fields.append(field)
                
                set_parts = []
                params = {"cid": keep_id}
                for field in merge_fields:
                    if best_data.get(field) is not None:
                        set_parts.append(f"{field} = :{field}")
                        params[field] = best_data[field]
                if set_parts:
                    updates.append((f"UPDATE companies SET {', '.join(set_parts)} WHERE company_id = :cid", params))
                
                results["merge_details"].append({
                    "keep_id": keep_id,
                    "removed_ids": rem_ids,
                    "merged_fields": list(set(merged_fields))
                })
            
            for sql_str, params in updates:
                conn.execute(text(sql_str), params)
            print(f"  {len(updates)} kayit guncellendi")
            
            # Silinecek kayitlari topla
            removal_list = list(all_removals)
            print(f"\n{len(removal_list)} duplicate kayit siliniyor...")
            
            # Batch silme (100'erli gruplar halinde)
            batch_size = 100
            for i in range(0, len(removal_list), batch_size):
                batch = removal_list[i:i+batch_size]
                delete_params = {f"id_{j}": rid for j, rid in enumerate(batch)}
                id_list = ", ".join([f":id_{j}" for j in range(len(batch))])
                conn.execute(text(f"DELETE FROM companies WHERE company_id IN ({id_list})"), delete_params)
            
            print(f"  {len(removal_list)} kayit silindi")
            
            # 4. Gecersiz kayitlar
            print("\n4. Gecersiz kayitlar tespit ediliyor...")
            invalid = {
                "empty_legal_name": 0,
                "invalid_tax_number_length": 0,
                "total_invalid": 0,
                "samples": []
            }
            
            result = conn.execute(text("""
                SELECT COUNT(*) FROM companies WHERE legal_name IS NULL OR legal_name = ''
            """)).scalar()
            invalid["empty_legal_name"] = result
            
            result = conn.execute(text("""
                SELECT COUNT(*) FROM companies
                WHERE tax_number IS NOT NULL AND tax_number != ''
                AND (LENGTH(tax_number) < 10 OR LENGTH(tax_number) > 11)
            """)).scalar()
            invalid["invalid_tax_number_length"] = result
            
            rows = conn.execute(text("""
                SELECT company_id::text, legal_name, tax_number
                FROM companies
                WHERE (legal_name IS NULL OR legal_name = '')
                   OR (tax_number IS NOT NULL AND tax_number != '' AND (LENGTH(tax_number) < 10 OR LENGTH(tax_number) > 11))
                LIMIT 10
            """)).fetchall()
            for row in rows:
                invalid["samples"].append({
                    "company_id": row[0],
                    "legal_name": row[1],
                    "tax_number": row[2]
                })
            
            invalid["total_invalid"] = invalid["empty_legal_name"] + invalid["invalid_tax_number_length"]
            results["invalid_records"] = invalid
            print(f"  Gecersiz kayitlar: {invalid['total_invalid']}")
            
            results["total_companies_after"] = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
            
            results["duplicate_detected"] = (
                results["tax_number_duplicate_records"] +
                results["legal_name_duplicate_records"] +
                results["website_domain_duplicate_records"]
            )
            results["duplicate_merged"] = (
                results["tax_number_merged"] +
                results["legal_name_merged"] +
                results["website_domain_merged"]
            )
            results["duplicate_removed"] = (
                results["tax_number_removed"] +
                results["legal_name_removed"] +
                results["website_domain_removed"]
            )
            
            results["status"] = "completed"
            results["finished_at"] = datetime.now().isoformat()
            
            print(f"\n=== Ozet ===")
            print(f"Once: {results['total_companies_before']} sirket")
            print(f"Sonra: {results['total_companies_after']} sirket")
            print(f"Duplicate tespit edildi: {results['duplicate_detected']}")
            print(f"Birlestirildi: {results['duplicate_merged']}")
            print(f"Silindi: {results['duplicate_removed']}")
            print(f"Gecersiz kayit: {results['invalid_records']['total_invalid']}")
            
    except Exception as e:
        results["status"] = "failed"
        results["errors"].append(str(e))
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
    
    output_path = Path("data/orchestrator/p45_result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSonuc kaydedildi: {output_path}")

if __name__ == "__main__":
    main()
