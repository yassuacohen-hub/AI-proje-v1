"""0025 uygulandi mi? (gecici)"""
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from company_master.db.connection import get_engine  # noqa: E402

with get_engine().connect() as c:
    print("-- uygulanan gocler:")
    for (f,) in c.execute(text(
            "SELECT filename FROM schema_migrations ORDER BY filename")):
        print("  ", f)
