"""YASU: nace_codes ve companies kolon dogrulamasi (canli)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402

eng = get_engine()
out = []

QS = [
    ("nace_codes tam kolon listesi",
     "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
     "WHERE table_name='nace_codes' ORDER BY ordinal_position"),
    ("companies NACE kolonlari",
     "SELECT column_name, data_type FROM information_schema.columns "
     "WHERE table_name='companies' AND column_name LIKE 'nace%' "
     "ORDER BY ordinal_position"),
    ("nace_codes version x level",
     "SELECT version, level, COUNT(*) FROM nace_codes "
     "GROUP BY 1, 2 ORDER BY 1, 2"),
    ("nace_codes ornek satirlar",
     "SELECT nace_code, version, level, title FROM nace_codes "
     "ORDER BY version, nace_code LIMIT 6"),
    ("companies.nace_code bulunan ama nace_codes'ta olmayan",
     "SELECT COUNT(*) FROM companies c "
     "WHERE c.nace_code IS NOT NULL AND c.nace_code <> '' "
     "AND c.nace_code NOT IN (SELECT nace_code FROM nace_codes)"),
]

for et, sql in QS:
    out.append(f"### {et}")
    try:
        with eng.connect() as c:
            for r in c.execute(text(sql)).fetchall():
                out.append("    " + " | ".join(str(x) for x in r)[:150])
    except Exception as e:
        out.append(f"    ! {str(e).splitlines()[0][:110]}")
    out.append("")

pathlib.Path(r"C:\Users\yasin\AppData\Local\Temp\cols.txt").write_text(
    "\n".join(out), encoding="utf-8")
print("\n".join(out))
