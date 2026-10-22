import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine
with get_engine().connect() as c:
    print(c.execute(text("SELECT origin, count(*), min(seq_no), max(seq_no) FROM public.field_dictionary GROUP BY origin ORDER BY 3")).fetchall())
