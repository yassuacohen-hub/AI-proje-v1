"""ANA KURAL DB migrasyonu (HIZLI - executemany ile).

- legal_name -> BUYUK HARF
- trade_name -> ilk 2 KELIME (hece degil)
- Bos/NULL trade_name'leri yeniden uret

Supabase'e tek tek UPDATE yerine executemany (pipeline) kullanir.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from company_master.db.connection import get_engine
from company_master.etl.normalize import normalize_company_name, extract_trade_name
from sqlalchemy import text

BATCH = 500

def migrate():
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT company_id, legal_name, trade_name
            FROM companies
            WHERE is_ankara=TRUE AND is_osb_member=TRUE
        """)).mappings().all()
        print(f"Toplam firma: {len(rows)}", flush=True)

        # Yeni degerleri hesapla (sadece degisenler)
        updates = []
        for r in rows:
            old_legal = r["legal_name"] or ""
            old_trade = r["trade_name"] or ""
            new_legal = normalize_company_name(old_legal)
            new_trade = extract_trade_name(new_legal)
            if new_legal != old_legal or new_trade != old_trade:
                updates.append({
                    "legal": new_legal,
                    "trade": new_trade,
                    "cid": r["company_id"],
                })

        print(f"Guncellenecek: {len(updates)}", flush=True)
        updates_sql = text("""
            UPDATE companies
            SET legal_name = :legal, trade_name = :trade, updated_at = NOW()
            WHERE company_id = :cid
        """)

        # executemany: parcalar halinde pipeline ile
        for i in range(0, len(updates), BATCH):
            chunk = updates[i:i+BATCH]
            conn.execute(updates_sql, chunk)
            print(f"  ... {min(i+BATCH, len(updates))}/{len(updates)}", flush=True)

        print("ANA KURAL migrasyonu tamam.", flush=True)

if __name__ == "__main__":
    migrate()
