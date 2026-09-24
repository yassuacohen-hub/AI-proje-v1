# -*- coding: utf-8 -*-
"""Y7 ek temizlik: telefon/e-posta icindeki newline/CR karakterleri."""
import sys
sys.path.insert(0, 'src')
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
with engine.begin() as conn:
    n_email = conn.execute(text("""
        UPDATE companies SET primary_email = replace(replace(primary_email, chr(10), ''), chr(13), ''), updated_at = CURRENT_TIMESTAMP
        WHERE primary_email ~ chr(10) OR primary_email ~ chr(13)
    """)).rowcount
    n_phone = conn.execute(text("""
        UPDATE companies SET primary_phone = replace(replace(primary_phone, chr(10), ''), chr(13), ''), updated_at = CURRENT_TIMESTAMP
        WHERE primary_phone ~ chr(10) OR primary_phone ~ chr(13)
    """)).rowcount
print(f"email newline temizlenen: {n_email}")
print(f"phone newline temizlenen: {n_phone}")
