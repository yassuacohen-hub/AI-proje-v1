# -*- coding: utf-8 -*-
"""Hayalet kayıt temizleme scripti.
Veritabanındaki aynı legal_name'e sahip tekrarlayan kayıtları birleştirir.
"""
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import text
from company_master.db.connection import get_engine


@dataclass
class CompanyRecord:
    company_id: str
    legal_name: str
    trade_name: Optional[str]
    company_type: Optional[str]
    tax_number: Optional[str]
    mersis_number: Optional[str]
    establishment_date: Optional[str]
    status: Optional[str]
    status_confidence: Optional[float]
    employee_count: Optional[int]
    website_domain: Optional[str]
    primary_phone: Optional[str]
    primary_email: Optional[str]
    description: Optional[str]
    is_ankara: Optional[bool]
    is_osb_member: Optional[bool]
    osb_id: Optional[str]
    nace_validity: Optional[str]
    quarantine_reason: Optional[str]
    data_quality_score: Optional[float]
    entity_confidence: Optional[float]
    osb_parcel: Optional[str]
    first_seen_at: Optional[str]
    last_verified_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    def filled_field_count(self) -> int:
        """Dolu alan sayısını hesaplar."""
        count = 0
        for field in [
            "trade_name", "company_type", "tax_number", "mersis_number",
            "establishment_date", "status", "status_confidence", "employee_count",
            "website_domain", "primary_phone", "primary_email", "description",
            "is_ankara", "is_osb_member", "osb_id", "nace_validity",
            "quarantine_reason", "data_quality_score", "entity_confidence",
            "osb_parcel", "first_seen_at",
            "last_verified_at", "created_at", "updated_at"
        ]:
            val = getattr(self, field)
            if val is not None and val != "":
                count += 1
        return count

    def has_tax_number(self) -> bool:
        """Doğrulanmış VKN var mı? (D-254: tek kaynak `tax_number`)"""
        return bool(self.tax_number and self.tax_number.strip())


def select_keeper(records: list[CompanyRecord]) -> CompanyRecord:
    """Aynı legal_name grubunda hangi kaydın kalacağını seçer.

    Sıralama:
    1. tax_number dolu olan
    2. En çok alanı dolu olan
    3. En küçük company_id
    """
    def sort_key(r: CompanyRecord):
        return (
            not r.has_tax_number(),  # False (0) önce gelir
            -r.filled_field_count(),  # Azalan (daha çok dolu önce)
            r.company_id  # Artan (küçük ID önce)
        )
    return min(records, key=sort_key)


def merge_records(keeper: CompanyRecord, duplicates: list[CompanyRecord]) -> CompanyRecord:
    """Kopyalardaki dolu alanları keeper'a birleştirir."""
    for dup in duplicates:
        for field in [
            "trade_name", "company_type", "tax_number", "mersis_number",
            "establishment_date", "status", "status_confidence", "employee_count",
            "website_domain", "primary_phone", "primary_email", "description",
            "is_ankara", "is_osb_member", "osb_id", "nace_validity",
            "quarantine_reason", "data_quality_score", "entity_confidence",
            "osb_parcel", "first_seen_at",
            "last_verified_at", "created_at", "updated_at"
        ]:
            keeper_val = getattr(keeper, field)
            dup_val = getattr(dup, field)
            if (keeper_val is None or keeper_val == "") and (dup_val is not None and dup_val != ""):
                setattr(keeper, field, dup_val)
    return keeper


def get_companies_by_legal_name(engine) -> dict[str, list[CompanyRecord]]:
    """Tüm companies kayıtlarını legal_name'e göre gruplar."""
    query = text("""
        SELECT company_id, legal_name, trade_name, company_type, tax_number,
               mersis_number, establishment_date, status, status_confidence,
               employee_count, website_domain, primary_phone, primary_email,
               description, is_ankara, is_osb_member, osb_id, nace_validity,
               quarantine_reason, data_quality_score, entity_confidence,
               osb_parcel, first_seen_at, last_verified_at,
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
            osb_parcel=row.osb_parcel,
            first_seen_at=str(row.first_seen_at) if row.first_seen_at else None,
            last_verified_at=str(row.last_verified_at) if row.last_verified_at else None,
            created_at=str(row.created_at) if row.created_at else None,
            updated_at=str(row.updated_at) if row.updated_at else None,
        )
        groups.setdefault(record.legal_name, []).append(record)

    return groups


def get_related_records(engine, company_ids: list[str]) -> dict[str, list[dict]]:
    """İlgili tablolardaki kayıtları getirir."""
    if not company_ids:
        return {}

    placeholders = ",".join([f"'{cid}'" for cid in company_ids])

    related = {}

    # company_industries
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT company_id, company_industry_id, nace_code, nace_version, nace_level,
                   is_primary, source_id, confidence, verified_at
            FROM company_industries
            WHERE company_id IN ({placeholders})
        """))
        for row in result:
            cid = str(row.company_id)
            related.setdefault(cid, []).append({
                "table": "company_industries",
                "data": dict(row._mapping)
            })

    # source_records
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT sr.*, c.company_id
            FROM source_records sr
            JOIN companies c ON sr.source_id = c.company_id
            WHERE c.company_id IN ({placeholders})
        """))
        for row in result:
            cid = str(row.company_id)
            related.setdefault(cid, []).append({
                "table": "source_records",
                "data": dict(row._mapping)
            })

    # company_identifiers
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT company_id, identifier_id, identifier_type, identifier_value,
                   source_id, confidence, verified_at
            FROM company_identifiers
            WHERE company_id IN ({placeholders})
        """))
        for row in result:
            cid = str(row.company_id)
            related.setdefault(cid, []).append({
                "table": "company_identifiers",
                "data": dict(row._mapping)
            })

    # company_locations
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT company_id, location_id, location_type, address_line, district,
                   neighborhood, city, postal_code, latitude, longitude,
                   geocode_confidence, osb_id, is_primary, source_id, verified_at
            FROM company_locations
            WHERE company_id IN ({placeholders})
        """))
        for row in result:
            cid = str(row.company_id)
            related.setdefault(cid, []).append({
                "table": "company_locations",
                "data": dict(row._mapping)
            })

    # company_contacts
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT company_id, contact_id, contact_type, value, is_public,
                   source_id, confidence, verified_at
            FROM company_contacts
            WHERE company_id IN ({placeholders})
        """))
        for row in result:
            cid = str(row.company_id)
            related.setdefault(cid, []).append({
                "table": "company_contacts",
                "data": dict(row._mapping)
            })

    # company_products
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT company_id, company_product_id, product_id, relation_type,
                   evidence_id, confidence, first_seen_at, last_seen_at
            FROM company_products
            WHERE company_id IN ({placeholders})
        """))
        for row in result:
            cid = str(row.company_id)
            related.setdefault(cid, []).append({
                "table": "company_products",
                "data": dict(row._mapping)
            })

    return related


def backup_to_jsonl(backup_path: Path, records: list[CompanyRecord], related: dict[str, list[dict]]) -> int:
    """Silinecek kayıtları JSONL formatında yedekler."""
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
                    "osb_parcel": record.osb_parcel,
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


def run_cleanup(dry_run: bool = False, backup_path: Path | None = None) -> dict:
    """Ana temizleme fonksiyonu."""
    engine = get_engine()

    print("Companies tablosu taranıyor...")
    groups = get_companies_by_legal_name(engine)

    # Tekrarlayan grupları bul
    duplicate_groups = {name: recs for name, recs in groups.items() if len(recs) > 1}
    print(f"Toplam {len(groups)} farklı legal_name, {len(duplicate_groups)} tekrarlayan grup bulundu.")

    if not duplicate_groups:
        print("Tekrarlayan kayıt yok.")
        return {"deleted": 0, "merged": 0, "backup_path": None}

    total_to_delete = sum(len(recs) - 1 for recs in duplicate_groups.values())
    print(f"Silinecek toplam kayıt: {total_to_delete}")

    # Yedek dosyası
    if backup_path is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        backup_path = Path(f"yedekler/hayalet_{timestamp}.jsonl")

    all_to_delete = []
    all_related = {}

    # Her grup için işlem yap
    for legal_name, records in duplicate_groups.items():
        keeper = select_keeper(records)
        duplicates = [r for r in records if r.company_id != keeper.company_id]

        print(f"\n{legal_name}:")
        print(f"  Kalacak: {keeper.company_id} (vkn: {keeper.has_tax_number()}, alan: {keeper.filled_field_count()})")
        for dup in duplicates:
            print(f"  Silinecek: {dup.company_id} (vkn: {dup.has_tax_number()}, alan: {dup.filled_field_count()})")

        # Alanları birleştir
        merge_records(keeper, duplicates)

        # Keeper'ı güncelle
        if not dry_run:
            update_query = text("""
                UPDATE companies SET
                    trade_name = COALESCE(NULLIF(:trade_name, ''), trade_name),
                    company_type = COALESCE(NULLIF(:company_type, ''), company_type),
                    -- D-254: buradaki tax_number yeni kimlik uretmez; zaten
                    -- defterle arindirilmis bir kopyadan devralinir.
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
                    osb_parcel = COALESCE(NULLIF(:osb_parcel, ''), osb_parcel),
                    first_seen_at = COALESCE(:first_seen_at, first_seen_at),
                    last_verified_at = COALESCE(:last_verified_at, last_verified_at),
                    updated_at = NOW()
                WHERE company_id = :company_id
            """)
            with engine.begin() as conn:
                conn.execute(update_query, {
                    "trade_name": keeper.trade_name, "company_type": keeper.company_type,
                    "tax_number": keeper.tax_number, "mersis_number": keeper.mersis_number,
                    "establishment_date": keeper.establishment_date, "status": keeper.status,
                    "status_confidence": keeper.status_confidence, "employee_count": keeper.employee_count,
                    "website_domain": keeper.website_domain, "primary_phone": keeper.primary_phone,
                    "primary_email": keeper.primary_email, "description": keeper.description,
                    "is_ankara": keeper.is_ankara, "is_osb_member": keeper.is_osb_member,
                    "osb_id": keeper.osb_id, "nace_validity": keeper.nace_validity,
                    "quarantine_reason": keeper.quarantine_reason, "data_quality_score": keeper.data_quality_score,
                    "entity_confidence": keeper.entity_confidence,
                    "osb_parcel": keeper.osb_parcel,
                    "first_seen_at": keeper.first_seen_at, "last_verified_at": keeper.last_verified_at,
                    "company_id": keeper.company_id
                })

        # İlgili kayıtları keeper'a taşı
        all_dup_ids = [d.company_id for d in duplicates]
        related = get_related_records(engine, all_dup_ids)

        if not dry_run and related:
            for cid, rel_list in related.items():
                for rel in rel_list:
                    table = rel["table"]
                    data = rel["data"]

                    # company_id'yi keeper'a güncelle
                    pk_col = {
                        "company_industries": "company_industry_id",
                        "source_records": "source_record_id",
                        "company_identifiers": "identifier_id",
                        "company_locations": "location_id",
                        "company_contacts": "contact_id",
                        "company_products": "company_product_id",
                    }[table]

                    with engine.begin() as conn:
                        conn.execute(
                            text(f"UPDATE {table} SET company_id = :cid WHERE {pk_col} = :pk"),
                            {"cid": keeper.company_id, "pk": data[pk_col]}
                        )

        all_to_delete.extend(duplicates)
        all_related.update(related)

    # Yedek al — dry-run diske YAZMAZ (D-243)
    if not dry_run:
        print(f"\nYedek alınıyor: {backup_path}")
        backup_count = backup_to_jsonl(backup_path, all_to_delete, all_related)
        print(f"Yedeklenen kayıt: {backup_count}")
        if backup_count != len(all_to_delete):
            raise RuntimeError(
                f"Yedek eksik: {backup_count} != {len(all_to_delete)} — silme iptal"
            )

    # Sil
    if not dry_run:
        deleted_ids = [r.company_id for r in all_to_delete]
        # 1000'lik parti: placeholder sayısı sürücü limitine dayanmasın.
        # Üretim PostgreSQL/Supabase (limit 65535) — 4591 geçer; ama test/yerel
        # SQLite yolunda limit 999 ve aynı kod oradan da geçmek zorunda.
        # Tüm partiler TEK engine.begin() içinde: yarım silme olmaz.
        with engine.begin() as conn:
            for i in range(0, len(deleted_ids), 1000):
                batch = deleted_ids[i:i + 1000]
                placeholders = ",".join(f":cid_{j}" for j in range(len(batch)))
                params = {f"cid_{j}": cid for j, cid in enumerate(batch)}
                conn.execute(
                    text(f"DELETE FROM companies WHERE company_id IN ({placeholders})"),
                    params,
                )
        print(f"Silinen kayıt: {len(deleted_ids)}")

    return {
        "deleted": len(all_to_delete),
        "merged": len(duplicate_groups),
        "backup_path": None if dry_run else str(backup_path),
        "dry_run": dry_run
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hayalet kayıt temizleme")
    parser.add_argument("--dry-run", action="store_true", help="Sadece raporla, silme")
    parser.add_argument("--yes", action="store_true", help="Onay sormadan çalıştır")
    args = parser.parse_args()

    if not args.yes and not args.dry_run:
        print("Bu işlem GERİ ALINAMAZ!")
        print("Yedek alınacak ve 4591 kayıt silinecek.")
        onay = input("Devam etmek için 'EVET' yazın: ")
        if onay != "EVET":
            print("İptal edildi.")
            sys.exit(1)

    result = run_cleanup(dry_run=args.dry_run)

    if args.dry_run:
        print("\n[DRY RUN] Gerçek silme yapılmadı.")
        print(f"Silinecek: {result['deleted']}, Birleştirilecek grup: {result['merged']}")
    else:
        print("\nİşlem tamamlandı.")
        print(f"Silinen: {result['deleted']}, Birleştirilen grup: {result['merged']}")
        print(f"Yedek: {result['backup_path']}")


if __name__ == "__main__":
    main()
