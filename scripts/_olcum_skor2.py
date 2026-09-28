"""KALITE-SKOR-01 kok neden: 5 olu skorun sebebi ayni mi?"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402

with get_engine().connect() as c:
    print("== 1) source_diversity: mevcut sorgu (companies.source_record_id)")
    r = c.execute(text("""
        SELECT COUNT(DISTINCT s.source_id) AS k, COUNT(*) AS firma FROM (
          SELECT c.company_id, sr.source_id
          FROM companies c JOIN source_records sr
            ON sr.source_record_id = c.source_record_id
        ) s GROUP BY s.company_id
    """)).mappings().all()
    from collections import Counter
    print("   kaynak sayisi dagilimi:", Counter(x["k"] for x in r))

    print("\n== 2) source_diversity: DOGRU sorgu (source_records.company_id)")
    r2 = c.execute(text("""
        SELECT COUNT(DISTINCT source_id) AS k
        FROM source_records WHERE company_id IS NOT NULL
        GROUP BY company_id
    """)).scalars().all()
    print("   kaynak sayisi dagilimi:", Counter(r2))
    print(f"   kapsanan firma: {len(r2)} / 9412")

    print("\n== 3) job_postings: gercek veri")
    print("   job_postings satir:",
          c.execute(text("SELECT COUNT(*) FROM job_postings")).scalar())
    print("   farkli firma:",
          c.execute(text("SELECT COUNT(DISTINCT company_id) FROM job_postings")).scalar())

    print("\n== 4) employee_count: gercek veri")
    print("   dolu:", c.execute(text(
        "SELECT COUNT(employee_count) FROM companies")).scalar())
