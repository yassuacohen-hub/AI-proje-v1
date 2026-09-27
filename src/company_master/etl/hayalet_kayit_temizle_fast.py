#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hayalet kayıt temizleme - Hızlı/Sessiz versiyon.
Sadece özet rapor verir, her satır için çıktı vermez.
"""

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, text

# .env yükle
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL environment variable not set")

PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class CompanyRecord:
    company_id: str
    legal_name: str
    trade_name: Optional[str] = None
    company_type: Optional[str] = None
    tax_number: Optional[str] = None
    mersis_number: Optional[str] = None
    establishment_date: Optional[str] = None
    status: Optional[str] = None
    status_confidence: Optional[float] = None
    employee_count: Optional[int] = None
    website_domain: Optional[str] = None
    primary_phone: Optional[str] = None
    primary_email: Optional[str] = None
    description: Optional[str] = None
    is_ankara: Optional[bool] = None
    is_osb_member: Optional[bool] = None
    osb_id: Optional[str] = None
    nace_validity: Optional[str] = None
    quarantine_reason: Optional[str] = None
    data_quality_score: Optional[float] = None
    entity_confidence: Optional[float] = None
    web_sitesi: Optional[str] = None
    vergi_no: Optional[str] = None
    osb_parsel: Optional[str] = None
    first_seen_at: Optional[str] = None
    last_verified_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def filled_field_count(self) -> int:
        count = 0
        for field in [
            "trade_name", "company_type", "tax_number", "mersis_number",
            "establishment_date", "status", "status_confidence", "employee_count",
            "website_domain", "primary_phone", "primary_email", "description",
            "is_ankara", "is_osb_member", "osb_id", "nace_validity",
            "quarantine_reason", "data_quality_score", "entity_confidence",
            "web_sitesi", "vergi_no", "osb_parsel", "first_seen_at",
            "last_verified_at", "created_at", "updated_at"
        ]:
            val = getattr(self, field)
            if val is not None and val != "":
                count += 1
        return count

    def has_tax_number(self) -> bool:
        return bool(self.tax_number and self.tax_number.strip()) or bool(self.vergi_no and self.vergi_no.strip())


def select_keeper(records: list[CompanyRecord]) -> CompanyRecord:
    def sort_key(r: CompanyRecord):
        return (
            not r.has_tax_number(),
            -r.filled_field_count(),
            r.company_id
        )
    return min(records, key=sort_key)


def merge_records(keeper: CompanyRecord, duplicates: list[CompanyRecord]) -> CompanyRecord:
    for dup in duplicates:
        for field in [
            "trade_name", "company_type", "tax_number", "mersis_number",
            "establishment_date", "status", "status_confidence", "employee_count",
            "website_domain", "primary_phone", "primary_email", "description",
            "is_ankara", "is_osb_member", "osb_id", "nace_validity",
            "quarantine_reason", "data_quality_score", "entity_confidence",
            "web_sitesi", "vergi_no", "osb_parsel", "first_seen_at",
            "last_verified_at", "created_at", "updated_at"
        ]:
            keeper_val = getattr(keeper, field)
            dup_val = getattr(dup, field)
            if (keeper_val is None or keeper_val == "") and (dup_val is not None and dup_val != ""):
                setattr(keeper, field, dup_val)
    return keeper


def get_companies_by_legal_name(engine) -> dict[str, list[CompanyRecord]]:
    query = text("""
        SELECT company_id, legal_name, trade_name, company_type, tax_number,
               mersis_number, establishment_date, status, status_confidence,
               employee_count, website_domain, primary_phone, primary_email,
               description, is_ankara, is_osb_member, osb_id, nace_validity,
               quarantine_reason, data_quality_score, entity_confidence,
               web_sitesi, vergi_no, osb_parsel, first_seen_at, last_verified_at,
               created_at, updated_at
        FROM companies
        ORDER BY legal_name, company_id
    """)
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()
    
    groups: dict[str, list[CompanyRecord]] = {}
    for row in rows:
        record = CompanyRecord(
            company_id=str(row.company_id),
            legal_name=row.legal_name,
            trade_name=row.trade_name,
            company_type=row.company_type,
            tax_number=row.tax_number,
            mersis_number=row.mersis_number,
            establishment_date=str(row.establishment_date) if row.establishment_date else None,
            status=row.status,
            status_confidence=float(row.status_confidence) if row.status_confidence else None,
            employee_count=row.employee_count,
            website_domain=row.website_domain,
            primary_phone=row.primary_phone,
            primary_email=row.primary_email,
            description=row.description,
            is_ankara=row.is_ankara,
            is_osb_member=row.is_osb_member,
            osb_id=str(row.osb_id) if row.osb_id else None,
            nace_validity=row.nace_validity,
            quarantine_reason=row.quarantine_reason,
            data_quality_score=float(row.data_quality_score) if row.data_quality_score else None,
            entity_confidence=float(row.entity_confidence) if row.entity_confidence else None,
            web_sitesi=row.web_sitesi,
            vergi_no=row.vergi_no,
            osb_parsel=row.osb_parsel,
            first_seen_at=str(row.first_seen_at) if row.first_seen_at else None,
            last_verified_at=str(row.last_verified_at) if row.last_verified_at else None,
            created_at=str(row.created_at) if row.created_at else None,
            updated_at=str(row.updated_at) if row.updated_at else None,
        )
        groups.setdefault(record.legal_name, []).append(record)
    
    return groups


def get_related_records(engine, company_ids: list[str]) -> dict[str, list[dict]]:
    if not company_ids:
        return {}
    
    placeholders = ",".join([f":cid_{i}" for i in range(len(company_ids))])
    params = {f"cid_{i}": cid for i, cid in enumerate(company_ids)}
    
    related = {}
    
    tables = [
        "company_industries", "source_records", "company_identifiers",
        "company_locations", "company_contacts", "company_products"
    ]
    
    for table in tables:
        pk_col = {
            "company_industries": "company_industry_id",
            "source_records": "source_record_id",
            "company_identifiers": "identifier_id",
            "company_locations": "location_id",
            "company_contacts": "contact_id",
            "company_products": "company_product_id",
        }[table]
        
        with engine.connect() as conn:
            if table == "source_records":
                # source_records has source_id, need to join companies
                result = conn.execute(text(f"""
                    SELECT sr.*, c.company_id
                    FROM source_records sr
                    JOIN companies c ON sr.source_id = c.company_id
                    WHERE c.company_id IN ({placeholders})
                """), params)
            else:
                result = conn.execute(text(f"""
                    SELECT company_id, {pk_col}
                    FROM {table}
                    WHERE company_id IN ({placeholders})
                """), params)
            
            for row in result:
                cid = str(row.company_id)
                related.setdefault(cid, []).append({
                    "table": table,
                    "pk_col": pk_col,
                    "pk_val": row[pk_col]
                })
    
    return related


def backup_to_jsonl(backup_path: Path, records: list[CompanyRecord], related: dict[str, list[dict]]) -> int:
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(backup_path, "w", encoding="utf-8") as f:
        for record in records:
            cid = record.company_id
            backup_obj = {
                "company": {
                    "company_id": record.company_id,
                    "legal_name": record.legal_name,
                    "trade_name": record.trade_name,
                    "company_type": record.company_type,
                    "tax_number": record.tax_number,
                    "mersis_number": record.mersis_number,
                    "establishment_date": record.establishment_date,
                    "status": record.status,
                    "status_confidence": record.status_confidence,
                    "employee_count": record.employee_count,
                    "website_domain": record.website_domain,
                    "primary_phone": record.primary_phone,
                    "primary_email": record.primary_email,
                    "description": record.description,
                    "is_ankara": record.is_ankara,
                    "is_osb_member": record.is_osb_member,
                    "osb_id": record.osb_id,
                    "nace_validity": record.nace_validity,
                    "quarantine_reason": record.quarantine_reason,
                    "data_quality_score": record.data_quality_score,
                    "entity_confidence": record.entity_confidence,
                    "web_sitesi": record.web_sitesi,
                    "vergi_no": record.vergi_no,
                    "osb_parsel": record.osb_parsel,
                    "first_seen_at": record.first_seen_at,
                    "last_verified_at": record.last_verified_at,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                },
                "related": related.get(cid, []),
                "deleted_at": datetime.now().isoformat()
            }
            f.write(json.dumps(backup_obj, ensure_ascii=False) + "\n")
            count += 1
    return count


def run_cleanup() -> dict:
    engine = create_engine(DB_URL)
    
    print("[1/6] Companies tablosu taranıyor...")
    groups = get_companies_by_legal_name(engine)
    
    duplicate_groups = {name: recs for name, recs in groups.items() if len(recs) > 1}
    print(f"[2/6] {len(duplicate_groups)} tekrarlayan grup bulundu.")
    
    if not duplicate_groups:
        print("Tekrarlayan kayıt yok.")
        return {"deleted": 0, "merged": 0, "backup_path": None}
    
    total_to_delete = sum(len(recs) - 1 for recs in duplicate_groups.values())
    print(f"[3/6] Silinecek toplam kayıt: {total_to_delete}")
    
    timestamp = datetime.now().strftime("%Y%m%d")
    backup_path = PROJECT_ROOT / "data" / "backup" / f"hayalet_{timestamp}.jsonl"
    
    all_to_delete = []
    all_related = {}
    keeper_updates = []  # (keeper_company_id, field_values_dict)
    
    # Her grup için işlem yap
    for i, (legal_name, records) in enumerate(duplicate_groups.items(), 1):
        if i % 100 == 0:
            print(f"  İşlenen grup: {i}/{len(duplicate_groups)}")
        
        keeper = select_keeper(records)
        duplicates = [r for r in records if r.company_id != keeper.company_id]
        
        # Alanları birleştir
        merge_records(keeper, duplicates)
        
        # Keeper güncellemesi için topla
        keeper_updates.append({
            "company_id": keeper.company_id,
            "trade_name": keeper.trade_name,
            "company_type": keeper.company_type,
            "tax_number": keeper.tax_number,
            "mersis_number": keeper.mersis_number,
            "establishment_date": keeper.establishment_date,
            "status": keeper.status,
            "status_confidence": keeper.status_confidence,
            "employee_count": keeper.employee_count,
            "website_domain": keeper.website_domain,
            "primary_phone": keeper.primary_phone,
            "primary_email": keeper.primary_email,
            "description": keeper.description,
            "is_ankara": keeper.is_ankara,
            "is_osb_member": keeper.is_osb_member,
            "osb_id": keeper.osb_id,
            "nace_validity": keeper.nace_validity,
            "quarantine_reason": keeper.quarantine_reason,
            "data_quality_score": keeper.data_quality_score,
            "entity_confidence": keeper.entity_confidence,
            "web_sitesi": keeper.web_sitesi,
            "vergi_no": keeper.vergi_no,
            "osb_parsel": keeper.osb_parsel,
            "first_seen_at": keeper.first_seen_at,
            "last_verified_at": keeper.last_verified_at,
        })
        
        # İlgili kayıtları topla
        all_dup_ids = [d.company_id for d in duplicates]
        related = get_related_records(engine, all_dup_ids)
        
        # İlişkili kayıtları keeper'a taşı (UPDATE)
        if related:
            for cid, rel_list in related.items():
                for rel in rel_list:
                    table = rel["table"]
                    pk_col = rel["pk_col"]
                    pk_val = rel["pk_val"]
                    with engine.begin() as conn:
                        conn.execute(
                            text(f"UPDATE {table} SET company_id = :cid WHERE {pk_col} = :pk"),
                            {"cid": keeper.company_id, "pk": pk_val}
                        )
        
        all_to_delete.extend(duplicates)
        all_related.update(related)
    
    # Yedek al
    print(f"[4/6] Yedek alınıyor: {backup_path}")
    backup_count = backup_to_jsonl(backup_path, all_to_delete, all_related)
    print(f"    Yedeklenen kayıt: {backup_count}")
    
    # Keeper'ları güncelle (batch)
    print("[5/6] Keeper kayıtları güncelleniyor...")
    update_query = text("""
        UPDATE companies SET
            trade_name = COALESCE(NULLIF(:trade_name, ''), trade_name),
            company_type = COALESCE(NULLIF(:company_type, ''), company_type),
            tax_number = COALESCE(NULLIF(:tax_number, ''), tax_number),
            mersis_number = COALESCE(NULLIF(:mersis_number, ''), mersis_number),
            establishment_date = COALESCE(:establishment_date, establishment_date),
            status = COALESCE(NULLIF(:status, ''), status),
            status_confidence = COALESCE(:status_confidence, status_confidence),
            employee_count = COALESCE(:employee_count, employee_count),
            website_domain = COALESCE(NULLIF(:website_domain, ''), website_domain),
            primary_phone = COALESCE(NULLIF(:primary_phone, ''), primary_phone),
            primary_email = COALESCE(NULLIF(:primary_email, ''), primary_email),
            description = COALESCE(NULLIF(:description, ''), description),
            is_ankara = COALESCE(:is_ankara, is_ankara),
            is_osb_member = COALESCE(:is_osb_member, is_osb_member),
            osb_id = COALESCE(:osb_id, osb_id),
            nace_validity = COALESCE(NULLIF(:nace_validity, ''), nace_validity),
            quarantine_reason = COALESCE(NULLIF(:quarantine_reason, ''), quarantine_reason),
            data_quality_score = COALESCE(:data_quality_score, data_quality_score),
            entity_confidence = COALESCE(:entity_confidence, entity_confidence),
            web_sitesi = COALESCE(NULLIF(:web_sitesi, ''), web_sitesi),
            vergi_no = COALESCE(NULLIF(:vergi_no, ''), vergi_no),
            osb_parsel = COALESCE(NULLIF(:osb_parsel, ''), osb_parsel),
            first_seen_at = COALESCE(:first_seen_at, first_seen_at),
            last_verified_at = COALESCE(:last_verified_at, last_verified_at),
            updated_at = NOW()
        WHERE company_id = :company_id
    """)
    
    with engine.begin() as conn:
        for update in keeper_updates:
            conn.execute(update_query, update)
    print(f"    Güncellenen keeper: {len(keeper_updates)}")
    
    # Sil
    print("[6/6] Hayalet kayıtlar siliniyor...")
    deleted_ids = [r.company_id for r in all_to_delete]
    if deleted_ids:
        batch_size = 500
        for i in range(0, len(deleted_ids), batch_size):
            batch = deleted_ids[i:i+batch_size]
            placeholders = ",".join([f":cid_{j}" for j in range(len(batch))])
            params = {f"cid_{j}": cid for j, cid in enumerate(batch)}
            with engine.begin() as conn:
                conn.execute(text(f"DELETE FROM companies WHERE company_id IN ({placeholders})"), params)
            if i % 2000 == 0:
                print(f"    Silinen: {min(i+batch_size, len(deleted_ids))}/{len(deleted_ids)}")
    
    print(f"    Toplam silinen: {len(deleted_ids)}")
    
    return {
        "deleted": len(deleted_ids),
        "merged": len(duplicate_groups),
        "backup_path": str(backup_path),
        "dry_run": False
    }


def main():
    print("=" * 60)
    print("VERI-HAYALET-TEMIZ-01: Hayalet Kayıt Temizleme (Hızlı Mod)")
    print("=" * 60)
    
    result = run_cleanup()
    
    print("\n" + "=" * 60)
    print("TAMAMLANDI")
    print("=" * 60)
    print(f"Silinen: {result['deleted']}")
    print(f"Birleştirilen grup: {result['merged']}")
    print(f"Yedek: {result['backup_path']}")
    
    # Doğrulama
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        total, distinct = conn.execute(text("SELECT count(*), count(distinct legal_name) FROM companies")).fetchone()
        print(f"\nDoğrulama: total={total}, distinct legal_name={distinct}")
        print(f"Eşit mi? {'EVET' if total == distinct else 'HAYIR'}")
        
        vergi_no_count = conn.execute(text("SELECT count(*) FROM companies WHERE vergi_no IS NOT NULL AND vergi_no != ''")).scalar()
        print(f"vergi_no dolu: {vergi_no_count}")


if __name__ == "__main__":
    main()
