"""Tek goc dosyasi uygular. Kullanim: python scripts/_goc_uygula.py 0024_..."""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402

ad = sys.argv[1]
yol = KOK / "src/company_master/schema/migrations" / f"{ad}.sql"
with get_engine().begin() as c:
    c.execute(text(yol.read_text(encoding="utf-8")))
print(f"{ad} uygulandi")
