import pathlib, sys
K = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.path.insert(0, str(K / "src"))
from company_master.db.connection import get_engine
from sqlalchemy import text
c = get_engine().connect()
sql = "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_name IN ('kullanim_log','kredi_hareket') ORDER BY table_name, ordinal_position"
rows = c.execute(text(sql)).fetchall()
cur = None
for r in rows:
    if r[0] != cur:
        print(); print(r[0]); cur = r[0]
    print('  ', r[1], r[2])
