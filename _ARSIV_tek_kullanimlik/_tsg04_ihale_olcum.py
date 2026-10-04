from src.company_master.db import get_engine
from sqlalchemy import text

TBLS = (
    "ihale_kaynaklari", "ihale_ilgilendirme_alanlari", "ihale_ilanlari",
    "ihale_katilimcilar", "ihale_ekler", "ihale_takip",
)

with get_engine().connect() as c:
    for t in TBLS:
        cols = [r[0] for r in c.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name=:t ORDER BY ordinal_position"),
            {"t": t},
        ).fetchall()]
        n = c.execute(text(f"SELECT count(*) FROM {t}")).scalar()
        print(t, "rows=", n)
        print("  ", cols)
