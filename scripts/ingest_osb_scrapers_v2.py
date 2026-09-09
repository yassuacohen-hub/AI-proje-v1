#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ivedik ve Baskent JSONL dosyalarini companies'a yazar (bulk)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine

FILES = [
    ("ivedik", ROOT / "data" / "ivedik" / "firmalar.jsonl"),
    ("baskent", ROOT / "data" / "baskent" / "firmalar.jsonl"),
]


def main() -> int:
    engine = get_engine()
    
    with engine.begin() as conn:
        for source_name, path in FILES:
            if not path.exists():
                print(f"{path.name}: dosya yok")
                continue
            
            records = []
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            
            print(f"{source_name}: {len(records)} kayit, bulk insert ediliyor...")
            
            # Build bulk insert
            values = []
            for rec in records:
                unvan = (rec.get("unvan") or "").strip()
                if not unvan:
                    continue
                
                payload = {
                    "adres": rec.get("adres"),
                    "web_sitesi": rec.get("web_sitesi"),
                    "telefonlar": rec.get("telefonlar", []),
                    "emailler": rec.get("emailler", []),
                }
                
                phone = (payload.get("telefonlar") or [None])[0]
                email = (payload.get("emailler") or [None])[0]
                
                values.append({
                    "unvan": unvan,
                    "adres": payload.get("adres"),
                    "web": payload.get("web_sitesi"),
                    "phone": phone,
                    "email": email,
                    "nace": rec.get("nace_code"),
                    "vergi": rec.get("vergi_no"),
                    "parsel": rec.get("osb_parsel"),
                })
            
            if not values:
                continue
            
            # Bulk insert with NULL source_record_id
            args = []
            params = {}
            for i, v in enumerate(values):
                args.append(f"(:unvan{i}, :unvan{i}, :adres{i}, :web{i}, :phone{i}, :email{i}, :nace{i}, :vergi{i}, :parsel{i})")
                params.update({
                    f"unvan{i}": v["unvan"],
                    f"adres{i}": v["adres"],
                    f"web{i}": v["web"],
                    f"phone{i}": v["phone"],
                    f"email{i}": v["email"],
                    f"nace{i}": v["nace"],
                    f"vergi{i}": v["vergi"],
                    f"parsel{i}": v["parsel"],
                })
            
            sql = f"""
                INSERT INTO companies
                (legal_name, trade_name, adres, website_domain, primary_phone, primary_email,
                 nace_code, vergi_no, osb_parsel, is_ankara, is_osb_member, source_record_id, created_at, updated_at)
                VALUES {', '.join(args)}
                ON CONFLICT DO NOTHING
            """
            
            result = conn.execute(text(sql), params)
            print(f"  {source_name}: {result.rowcount} yeni firma eklendi")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
