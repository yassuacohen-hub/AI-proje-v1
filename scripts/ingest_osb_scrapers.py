#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ivedik ve Baskent scraper ciktilarini DB'ye yazar."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine  # noqa: E402

FILES = [
    ROOT / "data" / "ivedik" / "firmalar.jsonl",
    ROOT / "data" / "baskent" / "firmalar.jsonl",
]


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def main() -> int:
    all_records = []
    for path in FILES:
        recs = load_records(path)
        all_records.extend(recs)
        print(f"{path.name}: {len(recs)} kayit", flush=True)

    if not all_records:
        print("Hic kayit bulunamadi.", flush=True)
        return 0

    engine = get_engine()
    matched = 0
    inserted = 0
    updated = 0
    skipped = 0
    batch = []
    BATCH_SIZE = 100

    def flush_batch(conn):
        nonlocal matched, inserted, updated
        if not batch:
            return
        names = [r["name"] for r in batch]
        rows = conn.execute(
            text("SELECT company_id, LOWER(TRIM(COALESCE(trade_name, legal_name))) AS key FROM companies "
                 "WHERE LOWER(TRIM(COALESCE(trade_name, legal_name))) = ANY(:names)"),
            {"names": names},
        ).fetchall()
        existing = {r[1]: r[0] for r in rows}

        for rec in batch:
            unvan = rec["name"]
            phone = rec["phone"]
            email = rec["email"]
            web = rec["web"]
            adres = rec["adres"]
            sektor = rec["sektor"]

            if unvan in existing:
                conn.execute(
                    text("UPDATE companies SET "
                         "legal_name = COALESCE(:legal_name, legal_name), "
                         "trade_name = COALESCE(:trade_name, trade_name), "
                         "website_domain = COALESCE(:web, website_domain), "
                         "primary_phone = COALESCE(:phone, primary_phone), "
                         "primary_email = COALESCE(:email, primary_email), "
                         "nace_name = COALESCE(:sektor, nace_name), "
                         "is_ankara = TRUE, is_osb_member = TRUE, "
                         "updated_at = NOW() "
                         "WHERE company_id = :cid"),
                    {
                        "legal_name": unvan,
                        "trade_name": unvan,
                        "web": web,
                        "phone": phone,
                        "email": email,
                        "sektor": sektor,
                        "cid": existing[unvan],
                    },
                )
                updated += 1
            else:
                import uuid
                company_id = str(uuid.uuid4())
                conn.execute(
                    text("INSERT INTO companies "
                         "(company_id, legal_name, trade_name, website_domain, primary_phone, "
                         "primary_email, nace_name, is_ankara, is_osb_member, created_at, updated_at) "
                         "VALUES (:cid, :legal_name, :trade_name, :web, :phone, :email, :sektor, TRUE, TRUE, NOW(), NOW())"),
                    {
                        "cid": company_id,
                        "legal_name": unvan,
                        "trade_name": unvan,
                        "web": web,
                        "phone": phone,
                        "email": email,
                        "sektor": sektor,
                    },
                )
                inserted += 1
            matched += 1
        batch.clear()

    with engine.connect() as conn:
        for i, rec in enumerate(all_records):
            unvan = (rec.get("unvan") or "").strip()
            if not unvan:
                skipped += 1
                continue

            phone = None
            email = None
            web = None
            adres = None
            sektor = None

            if rec.get("telefonlar"):
                phone = str(rec["telefonlar"][0])[:30]
            if rec.get("emailler"):
                email = str(rec["emailler"][0])[:120]
            if rec.get("web_sitesi"):
                web = str(rec["web_sitesi"])[:255]
            if rec.get("adres"):
                adres = str(rec["adres"])[:500]
            if rec.get("sektor"):
                sektor = str(rec["sektor"])[:255]

            batch.append({
                "name": unvan,
                "phone": phone,
                "email": email,
                "web": web,
                "adres": adres,
                "sektor": sektor,
            })

            if len(batch) >= BATCH_SIZE:
                flush_batch(conn)
                conn.commit()
                print(f"Ilerleme: {i+1}/{len(all_records)}", flush=True)

        flush_batch(conn)
        conn.commit()

    print(f"Toplam: {len(all_records)} | Eslesen: {matched} | Yeni: {inserted} | Guncellenen: {updated} | Atlanan: {skipped}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
