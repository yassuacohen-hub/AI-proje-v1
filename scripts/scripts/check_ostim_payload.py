import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Check raw_payload keys in OSTIM
    result = conn.execute(text('''
        SELECT raw_payload
        FROM source_records
        WHERE source_id = (SELECT source_id FROM sources WHERE source_name = 'ostim.org.tr')
        LIMIT 1
    '''))
    row = result.fetchone()
    if row:
        import json
        payload = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        print("Keys in raw_payload:", list(payload.keys()))
        print("Sample values:")
        for k in ['adres', 'unvan', 'sektor', 'telefonler', 'emailler', 'web_sitesi', 'vergi_no', 'osb_parsel', 'nace_code']:
            if k in payload:
                print(f"  {k}: {payload[k]}")
            else:
                print(f"  {k}: MISSING")