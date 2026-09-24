#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ASO rehber verisini DB'ye ingest et (H001 / P1-3).

data/aso/aso_full.jsonl -> companies tablosu (idempotent upsert).

Kullanim:
    python scripts/aso_ingest.py            # tam ingest
    python scripts/aso_ingest.py --limit 10 # ilk N kayit (smoke test)

Notlar:
- vergiNo alani yoksa ticaretSicilNo fallback kullanilir (P1-3 ile ayni semantik).
- Upsert anahtari: tax_number; bos alanlar COALESCE ile dolar.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402

INPUT_FILE = ROOT / "data" / "aso" / "aso_full.jsonl"


def extract_phone(phone_data) -> str | None:
    """telefonlar alanini tek birincil telefon string'ine indirger."""
    if not phone_data:
        return None
    if isinstance(phone_data, dict):
        return phone_data.get("no")
    if isinstance(phone_data, list) and phone_data:
        p = phone_data[0]
        return p.get("no") if isinstance(p, dict) else str(p)
    return str(phone_data)


def extract_email(email_data) -> str | None:
    if not email_data:
        return None
    if isinstance(email_data, list) and email_data:
        return email_data[0]
    return str(email_data)


def has_column(conn, table: str, column: str) -> bool:
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :t AND column_name = :c"
        ),
        {"t": table, "c": column},
    ).fetchone()
    return r is not None

UPSERT_UPDATE = text(
    "UPDATE companies SET trade_name = :tn, "
    "nace_code = COALESCE(nace_code, :nace), "
    "nace_validity = COALESCE(nace_validity, :nace), "
    "primary_phone = COALESCE(primary_phone, :phone), "
    "primary_email = COALESCE(primary_email, :email), "
    "web_sitesi = COALESCE(web_sitesi, :web), "
    "website_domain = COALESCE(website_domain, :web), "
    "updated_at = NOW() WHERE company_id = :cid"
)

INSERT_BASE = (
    "INSERT INTO companies (company_id, legal_name, trade_name, tax_number, "
    "nace_code, nace_validity, primary_phone, primary_email, "
    "website_domain, web_sitesi, is_ankara, is_osb_member) "
    "VALUES (:cid, :lname, :tn, :tax, :nace, :nace, :phone, :email, "
    ":web, :web, TRUE, TRUE"
)


def main() -> None:
    ap = argparse.ArgumentParser(description="ASO JSONL -> companies ingest")
    ap.add_argument("--limit", type=int, default=0, help="Ilk N kayit (0=tumu)")
    args = ap.parse_args()

    if not INPUT_FILE.exists():
        print(f"HATA: Girdi dosyasi yok: {INPUT_FILE}")
        sys.exit(1)

    lines = [
        ln for ln in INPUT_FILE.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    if args.limit:
        lines = lines[: args.limit]
    print(f"ASO dosyasi: {len(lines)} kayit islenecek")

    inserted = updated = skipped = errors = 0
    engine = get_engine()
    with engine.begin() as conn:
        adres_var = has_column(conn, "companies", "adres")
        for i, line in enumerate(lines):
            try:
                rec = json.loads(line)
                tradename = (rec.get("unvan") or "").strip()[:255]
                if not tradename:
                    skipped += 1
                    continue
                tax = rec.get("vergiNo") or rec.get("ticaretSicilNo") or None
                params = {
                    "tn": tradename,
                    "nace": rec.get("naceKod") or None,
                    "phone": extract_phone(rec.get("telefonlar")),
                    "email": extract_email(rec.get("eposta")),
                    "web": rec.get("web_sitesi") or None,
                }
                params["tax"] = str(tax)[:20] if tax else None

                exists = None
                if params["tax"]:
                    r = conn.execute(
                        text("SELECT company_id FROM companies WHERE tax_number = :tax"),
                        {"tax": params["tax"]},
                    ).fetchone()
                    if r:
                        exists = r[0]

                if exists:
                    conn.execute(UPSERT_UPDATE, {**params, "cid": str(exists)})
                    updated += 1
                else:
                    sql = INSERT_BASE
                    p = {"cid": str(uuid.uuid4()), "lname": tradename, **params}
                    adres = (rec.get("adres") or "").strip() or None
                    if adres_var and adres:
                        sql = sql + ", :adres"
                        p["adres"] = adres
                    conn.execute(text(sql + ")"), p)
                    inserted += 1
            except Exception as e:  # noqa: BLE001 — kayit bazli hata izolasyonu
                errors += 1
                print(f"[{i}] HATA ({type(e).__name__}): {e}")
                if errors >= 50:
                    print("50 hatayi asti, durduruluyor.")
                    break

    print("\nASO ingest tamamlandi:")
    print(f"  Yeni eklendi : {inserted}")
    print(f"  Guncellendi  : {updated}")
    print(f"  Atlandi      : {skipped}")
    print(f"  Hata         : {errors}")


if __name__ == "__main__":
    main()

