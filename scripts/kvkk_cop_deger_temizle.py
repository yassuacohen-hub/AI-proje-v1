# -*- coding: utf-8 -*-
"""Y7 ek temizlik 2: primary_email/phone'daki JSON copekleri ('[]', '{}', 'null')."""
import sys
sys.path.insert(0, 'src')
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import text
from company_master.db.connection import get_engine

GECERSIZ = "('[]','{}','[ ]','null','NULL','None','-',',')"
engine = get_engine()
with engine.begin() as conn:
    n_e = conn.execute(text(f"""
        UPDATE companies SET primary_email = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE primary_email IS NOT NULL AND primary_email IN {GECERSIZ}
    """)).rowcount
    n_p = conn.execute(text(f"""
        UPDATE companies SET primary_phone = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE primary_phone IS NOT NULL AND primary_phone IN {GECERSIZ}
    """)).rowcount
    # @ icermeyen e-postalar da gecersiz (maske testinde tespit edildi)
    n_at = conn.execute(text("""
        UPDATE companies SET primary_email = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE primary_email IS NOT NULL AND primary_email != '' AND position('@' in primary_email) = 0
    """)).rowcount
print(f"cop email NULL'lanan: {n_e}")
print(f"cop phone NULL'lanan: {n_p}")
print(f"@-siz email NULL'lanan: {n_at}")
