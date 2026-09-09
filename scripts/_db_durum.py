# -*- coding: utf-8 -*-
"""DB durum ozeti (Y2 oncesi)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

e = get_engine()
with e.connect() as c:
    print("companies:", c.execute(text("SELECT COUNT(*) FROM companies")).scalar())
    print("source_records:", c.execute(text("SELECT COUNT(*) FROM source_records")).scalar())
    print("sources:", [tuple(r) for r in c.execute(text("SELECT source_name, source_type FROM sources ORDER BY source_name"))])
    cols = [r[0] for r in c.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='companies' ORDER BY 1"))]
    print("companies kolon var mi [source_name/adres/vergi_no/osb_parsel/web_sitesi]:",
          [k for k in ("source_name", "adres", "vergi_no", "osb_parsel", "web_sitesi") if k in cols])
