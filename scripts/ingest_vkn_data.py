#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""VKN ekli dosyalari DB'ye yazar."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine

FILES = [
    ROOT / "data" / "ostim" / "firmalar_vkn_ekli.jsonl",
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
        print(f"{path.name}: {len(recs)} kayit")

    if not all_records:
        print("Hic kayit bulunamadi.")
        return 0

    engine = get_engine()
    updated = 0
    skipped = 0

    with engine.connect() as conn:
        for rec in all_records:
            vergi_no = rec.get("vergi_no")
            if not vergi_no:
                skipped += 1
                continue

            web = rec.get("web_sitesi")
            if web and not web.startswith(("http://", "https://")):
                web = "https://" + web

            result = conn.execute(
                text("""
                    UPDATE companies 
                    SET vergi_no = :vergi_no,
                        website_domain = COALESCE(:web, website_domain),
                        updated_at = NOW()
                    WHERE company_id = (
                        SELECT c.company_id 
                        FROM companies c
                        JOIN source_records sr ON sr.source_record_id = c.source_record_id
                        WHERE sr.raw_name = :unvan
                        LIMIT 1
                    )
                """),
                {
                    "vergi_no": vergi_no,
                    "web": web,
                    "unvan": rec.get("unvan"),
                },
            )
            updated += result.rowcount

        conn.commit()

    print(f"Toplam: {len(all_records)} | Guncellenen: {updated} | Atlanan: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
