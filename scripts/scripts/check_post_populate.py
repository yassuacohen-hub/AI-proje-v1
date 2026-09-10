import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
with engine.connect() as conn:
    r = conn.execute(text('''
        SELECT c.primary_phone, c.vergi_no, c.web_sitesi, c.nace_validity, c.osb_parsel, c.website_domain,
               c.source_record_id, sr.raw_payload
        FROM companies c
        JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara = TRUE
        LIMIT 3
    ''')).fetchall()
    for i, row in enumerate(r):
        print(f'--- Firma {i} ---')
        print(f'  primary_phone: {row[0]}')
        print(f'  vergi_no: {row[1]}')
        print(f'  web_sitesi: {row[2]}')
        print(f'  nace_validity: {row[3]}')
        print(f'  osb_parsel: {row[4]}')
        print(f'  website_domain: {row[5]}')
        if row[7]:
            payload = json.loads(row[7]) if isinstance(row[7], str) else row[7]
            print(f'  payload telefonler: {payload.get("telefonler")}')
            print(f'  payload vergi_no: {payload.get("vergi_no")}')
            print(f'  payload web_sitesi: {payload.get("web_sitesi")}')
            print(f'  payload nace_code: {payload.get("nace_code")}')
            print(f'  payload adres: {payload.get("adres")}')
            print(f'  payload osb_parsel: {payload.get("osb_parsel")}')
            print(f'  payload sektor: {payload.get("sektor")}')