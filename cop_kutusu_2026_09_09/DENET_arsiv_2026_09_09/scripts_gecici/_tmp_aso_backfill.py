import json, sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
conn = engine.connect()

with open("data/aso/aso_full.jsonl", "r", encoding="utf-8") as f:
    aso = [json.loads(l) for l in f if l.strip()]

rows = conn.execute(text("SELECT company_id, legal_name FROM companies WHERE is_ankara = TRUE")).fetchall()
db_names = {name: cid for cid, name in rows}

updates = {"adres": 0, "nace_code": 0, "nace_name": 0, "email": 0, "phone": 0}
for rec in aso:
    unvan = rec.get("unvan", "").strip()
    cid = db_names.get(unvan)
    if not cid:
        continue
    adres = (rec.get("adres") or "").strip()
    nace_kod = (rec.get("naceKod") or "").strip()
    nace_detay = (rec.get("naceDetay") or "").strip()
    eposta = (rec.get("eposta") or "").strip()
    telefonlar = rec.get("telefonlar") or []
    telefon = ""
    if telefonlar:
        t = telefonlar[0]
        if isinstance(t, dict):
            telefon = t.get("no", "")
        else:
            telefon = str(t)
    if adres:
        r = conn.execute(text("UPDATE companies SET adres = :adres, updated_at = NOW() WHERE company_id = :cid AND (adres IS NULL OR adres = :empty)"), {"adres": adres[:500], "cid": cid, "empty": ""})
        updates["adres"] += r.rowcount
    if nace_kod:
        r = conn.execute(text("UPDATE companies SET nace_code = :nace, nace_source = :src, updated_at = NOW() WHERE company_id = :cid AND (nace_code IS NULL OR nace_code = :empty)"), {"nace": nace_kod, "src": "aso", "cid": cid, "empty": ""})
        updates["nace_code"] += r.rowcount
    if nace_detay:
        r = conn.execute(text("UPDATE companies SET nace_name = :name, updated_at = NOW() WHERE company_id = :cid AND (nace_name IS NULL OR nace_name = :empty)"), {"name": nace_detay[:500], "cid": cid, "empty": ""})
        updates["nace_name"] += r.rowcount
    if eposta:
        r = conn.execute(text("UPDATE companies SET primary_email = :email, updated_at = NOW() WHERE company_id = :cid AND (primary_email IS NULL OR primary_email = :empty)"), {"email": eposta, "cid": cid, "empty": ""})
        updates["email"] += r.rowcount
    if telefon:
        r = conn.execute(text("UPDATE companies SET primary_phone = :phone, updated_at = NOW() WHERE company_id = :cid AND (primary_phone IS NULL OR primary_phone = :empty)"), {"phone": telefon, "cid": cid, "empty": ""})
        updates["phone"] += r.rowcount

conn.commit()
print("ASO backfill updates:", updates)
