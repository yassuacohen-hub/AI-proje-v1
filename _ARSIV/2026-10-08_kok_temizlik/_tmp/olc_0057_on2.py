# -*- coding: utf-8 -*-
"""0057/0058 oncesi canli kolon olcumu (D-238, D-254 ikiz kontrolu)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

with get_engine().connect() as c:
    for t in ("companies", "company_locations", "company_events", "key_personnel"):
        cols = [r[0] for r in c.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=:t ORDER BY ordinal_position"), {"t": t})]
        print(f"{t} ({len(cols)}): {cols}")
    print("ikiz adaylari companies:", [r[0] for r in c.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='companies' AND column_name ~ '(status|type|tsm|registry|capital|parent|start|closing|found)'"))])
    for t in ("company_capital", "company_legal_proceedings"):
        print(t, "var mi:", c.execute(text("SELECT to_regclass(:t)"), {"t": "public." + t}).scalar())
    print("companies.company_id tipi:", c.execute(text(
        "SELECT data_type FROM information_schema.columns WHERE table_name='companies' AND column_name='company_id'")).scalar())
    print("company_events.source_guid:", c.execute(text(
        "SELECT count(*) FROM information_schema.columns WHERE table_name='company_events' AND column_name IN ('source_guid','tsg_pdf_hash')")).scalar())
