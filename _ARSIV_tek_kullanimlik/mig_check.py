from sqlalchemy import text
from src.company_master.db import get_engine
with get_engine().connect() as c:
    rows = c.execute(text("SELECT filename FROM public.schema_migrations ORDER BY filename")).fetchall()
    print(len(rows))
    for r in rows[-8:]:
        print(r[0])
