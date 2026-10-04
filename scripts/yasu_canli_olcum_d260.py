"""D-238 canlı ölçüm: entity_matches, api_usage_daily, nace_codes doluluk.

Yol: projenin kendi get_engine()'i (postgresql+psycopg).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402

out = []
eng = get_engine()

SORULAR = [
    ("entity_matches TABLO VAR MI", "SELECT to_regclass('entity_matches')"),
    ("entity_matches satir", "SELECT COUNT(*) FROM entity_matches"),
    ("entity_matches match_type dagilimi",
     "SELECT match_type, COUNT(*) FROM entity_matches GROUP BY 1 ORDER BY 2 DESC"),
    ("entity_matches similarity min/ort/max",
     "SELECT MIN(similarity_score), AVG(similarity_score)::numeric(6,4), "
     "MAX(similarity_score) FROM entity_matches"),
    ("entity_matches fuzzy (optimizer'in okudugu)",
     "SELECT COUNT(*) FROM entity_matches WHERE match_type='fuzzy'"),
    ("entity_matches bos created_at",
     "SELECT COUNT(*) FROM entity_matches WHERE created_at IS NULL"),
    ("api_usage_daily TABLO VAR MI", "SELECT to_regclass('api_usage_daily')"),
    ("api_usage_daily satir", "SELECT COUNT(*) FROM api_usage_daily"),
    ("api_usage_daily tarih min/max/gun",
     "SELECT MIN(date), MAX(date), COUNT(DISTINCT date) FROM api_usage_daily"),
    ("api_usage_daily tier dagilimi",
     "SELECT tier, COUNT(*) FROM api_usage_daily GROUP BY 1 ORDER BY 2 DESC"),
    ("nace_codes satir", "SELECT COUNT(*) FROM nace_codes"),
    ("nace_codes title BOS",
     "SELECT COUNT(*) FROM nace_codes WHERE title IS NULL OR title=''"),
    ("nace_codes parent ORPHAN",
     "SELECT COUNT(*) FROM nace_codes WHERE parent_code IS NOT NULL "
     "AND parent_code<>'' AND parent_code NOT IN (SELECT nace_code FROM nace_codes)"),
    ("nace_codes version dagilimi",
     "SELECT version, COUNT(*) FROM nace_codes GROUP BY 1 ORDER BY 2 DESC"),
    ("nace_codes SUTUNLARI (dil var mi)",
     "SELECT string_agg(column_name, ', ' ORDER BY ordinal_position) "
     "FROM information_schema.columns WHERE table_name='nace_codes'"),
    ("companies.nace_code dolu",
     "SELECT COUNT(*) FROM companies WHERE nace_code IS NOT NULL AND nace_code<>''"),
    ("companies.nace_name dolu (D-268 dusuruldu)",
     "SELECT COUNT(*) FROM companies WHERE nace_name IS NOT NULL AND nace_name<>''"),
    ("company_industries dolu", "SELECT COUNT(*) FROM company_industries"),
]

for etiket, sql in SORULAR:
    try:
        with eng.connect() as c:
            r = c.execute(text(sql)).fetchall()
        if len(r) == 1 and len(r[0]) == 1:
            out.append(f"{etiket:<46} = {r[0][0]}")
        else:
            out.append(f"{etiket:<46} = " +
                       " | ".join(str(x) for x in r)[:200])
    except Exception as e:
        out.append(f"{etiket:<46} ! {str(e).splitlines()[0][:100]}")

pathlib.Path(r"C:\Users\yasin\AppData\Local\Temp\live.txt").write_text(
    "\n".join(out), encoding="utf-8")
print("\n".join(out))

