"""KALITE-SKOR-01 kaniti: %100 dolu skor kolonlari gercek deger mi, varsayilan mi?"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402

KOLONLAR = [
    "data_freshness_score", "phone_format_score", "social_media_score",
    "source_diversity_score", "job_postings_score", "employee_count_score",
    "email_validity_score", "job_postings_count", "employee_count_estimate",
    "data_quality_score",
]

with get_engine().connect() as c:
    n = c.execute(text("SELECT COUNT(*) FROM companies")).scalar()
    print(f"companies: {n} satir\n")
    for k in KOLONLAR:
        ilk = c.execute(text(f"""
            SELECT {k} AS d, COUNT(*) AS a FROM companies
            GROUP BY {k} ORDER BY a DESC LIMIT 3
        """)).mappings().all()
        farkli = c.execute(text(f"SELECT COUNT(DISTINCT {k}) FROM companies")).scalar()
        hakim = ilk[0]
        print(f"{k:<26} farkli={farkli:<5} en cok gecen: {hakim['d']!r} "
              f"x{hakim['a']} ({100 * hakim['a'] / n:.1f}%)")
        if farkli > 1:
            print("      " + "  ".join(f"{r['d']!r}x{r['a']}" for r in ilk[1:]))
