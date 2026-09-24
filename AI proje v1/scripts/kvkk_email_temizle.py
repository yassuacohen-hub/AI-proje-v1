# -*- coding: utf-8 -*-
"""Y7: Bireysel e-posta temizligi (KVKK politika §3.1 + §5 uyumu).
1) Yedek tabloya kopyala (geri alinabilirlik)
2) primary_email'i NULL yap
"""
import sys
sys.path.insert(0, 'src')
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import text
from company_master.db.connection import get_engine

RE_PERSONAL = "(gmail|hotmail|yahoo|yandex|outlook|icloud)\\.[a-z]{2,3}"
engine = get_engine()

with engine.begin() as conn:
    # 1) Yedek tablo (ayni kayitlarin email degerlerini sakla)
    conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS kvkk_bireysel_email_yedek AS
        SELECT company_id, legal_name, primary_email, CURRENT_TIMESTAMP as kayit_zamani
        FROM companies
        WHERE primary_email IS NOT NULL AND primary_email != ''
          AND primary_email ~* '{RE_PERSONAL}'
    """))
    backed = conn.execute(text("SELECT COUNT(*) FROM kvkk_bireysel_email_yedek")).scalar()

    # 2) NULL'la (politika §5: "Bireysel email -> Hemen, Otomatik NULL")
    res = conn.execute(text(f"""
        UPDATE companies
        SET primary_email = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE primary_email IS NOT NULL AND primary_email != ''
          AND primary_email ~* '{RE_PERSONAL}'
    """))

    # 3) Kontrol: kalan bireysel e-posta
    remaining = conn.execute(text(f"""
        SELECT COUNT(*) FROM companies
        WHERE primary_email IS NOT NULL AND primary_email != ''
          AND primary_email ~* '{RE_PERSONAL}'
    """)).scalar()

print(f"Yedeklenen: {backed}")
print(f"NULL'lanan: {res.rowcount}")
print(f"Kalan bireysel e-posta: {remaining}")
print("OK" if remaining == 0 else "UYARI: hala kalan var!")
