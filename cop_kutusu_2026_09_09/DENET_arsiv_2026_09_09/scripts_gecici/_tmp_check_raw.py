import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
conn = engine.connect()
for alan in ["adres", "web_sitesi", "vergi_no", "osb_parsel", "sektor", "nace_code"]:
    sql = f"SELECT COUNT(*) FROM source_records WHERE raw_payload ? '{alan}' AND NULLIF(raw_payload->>'{alan}', '') IS NOT NULL"
    r = conn.execute(text(sql)).scalar()
    print(f"{alan}: {r}")
