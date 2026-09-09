import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json
from sqlalchemy import text
import uuid
from company_master.db.connection import get_engine

engine = get_engine()
ROOT = Path("C:/Projeler/Huginn Data Insights")

def extract_phone(phone_data):
    if not phone_data:
        return None
    if isinstance(phone_data, dict):
        return phone_data.get("no")
    if isinstance(phone_data, list) and phone_data:
        p = phone_data[0]
        if isinstance(p, dict):
            return p.get("no")
        return str(p)
    return str(phone_data)

def extract_email(email_data):
    if not email_data:
        return None
    if isinstance(email_data, list) and email_data:
        return email_data[0]
    return str(email_data)

def main():
    input_file = ROOT / "data" / "aso" / "aso_full.jsonl"
    lines = input_file.read_text(encoding="utf-8").strip().split("\n")
    print(f"ASO dosyasi: {len(lines)} kayit")
    
    inserted = 0
    updated = 0
    errors = 0
    
    with engine.begin() as conn:
        for i, line in enumerate(lines[:10]):  # First 10 for debugging
            try:
                rec = json.loads(line)
                tradename = (rec.get("unvan") or "")[:255]
                tax = rec.get("vergiNo") or rec.get("ticaretSicilNo")
                nace = rec.get("naceKod")
                phones = extract_phone(rec.get("telefonlar"))
                email = extract_email(rec.get("eposta"))
                web = rec.get("web_sitesi") or None
                
                print(f"[{i}] Name: '{tradename}'")
                print(f"    Tax: '{tax}' (type: {type(tax)})")
                print(f"    NACE: '{nace}'")
                print(f"    Phones: {phones}")
                print(f"    Email: {email}")
                print(f"    Web: {web}")
                
                if not tradename: 
                    print("    Skipping - empty name")
                    continue
                
                # Check if already exists by tax_number
                exists = None
                if tax:
                    r = conn.execute(text("SELECT company_id FROM companies WHERE tax_number = :tax"), {"tax": tax}).fetchone()
                    if r: exists = r[0]
                
                company_id = exists or str(uuid.uuid4())
                
                if exists:
                    print(f"    Updating existing: {exists}")
                    sql = text("""
                        UPDATE companies SET trade_name=:tn, nace_code=:nace, nace_validity=:nace,
                            primary_phone=COALESCE(primary_phone, :phone),
                            primary_email=COALESCE(primary_email, :email),
                            web_sitesi=COALESCE(web_sitesi, :web), updated_at=NOW()
                        WHERE company_id=:cid
                    """)
                    params = {"cid": company_id, "tn": tradename, "nace": nace, "phone": phones, "email": email, "web": web}
                else:
                    print(f"    Inserting new: {company_id}")
                    sql = text("""
                        INSERT INTO companies (company_id, legal_name, trade_name, tax_number, nace_code, nace_validity,
                            primary_phone, primary_email, website_domain, web_sitesi, is_ankara, is_osb_member)
                        VALUES (:cid, :lname, :tn, :tax, :nace, :nace, :phone, :email, :web, :web, TRUE, TRUE)
                    """)
                    params = {"cid": company_id, "lname": tradename, "tn": tradename, "tax": tax, "nace": nace, "phone": phones, "email": email, "web": web}
                
                print(f"    Executing SQL...")
                result = conn.execute(sql, params)
                print(f"    Success: {result.rowcount} rows affected")
                if exists:
                    updated += 1
                else:
                    inserted += 1
                    
            except Exception as e:
                print(f"    ERROR: {type(e).__name__}: {e}")
                errors += 1
                import traceback
                traceback.print_exc()
                continue
    
    print(f"\nASO ingest tamamlandi (debug):")
    print(f"  Yeni eklendi: {inserted}")
    print(f"  Guncellendi: {updated}")
    print(f"  Hata: {errors}")

if __name__ == "__main__":
    main()