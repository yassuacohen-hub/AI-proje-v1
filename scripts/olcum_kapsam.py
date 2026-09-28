"""Mevcut semadaki tablo/kolon envanteri + gercek doluluk (hedef kapsam kiyasi).

Kullanim: python scripts/_olcum_kapsam.py
"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402

eng = get_engine()
with eng.connect() as c:
    satirlar = c.execute(text("""
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position
    """)).fetchall()

    tablolar: dict[str, list[str]] = {}
    for t, k in satirlar:
        tablolar.setdefault(t, []).append(k)

    print(f"TABLO: {len(tablolar)}   KOLON: {len(satirlar)}\n")

    for t, kolonlar in tablolar.items():
        n = c.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
        print(f"== {t}  ({n} satir, {len(kolonlar)} kolon)")
        if not n:
            print("   (bos)\n")
            continue
        secim = ", ".join(
            f'COUNT(NULLIF(TRIM("{k}"::text),\'\')) AS "{k}"' for k in kolonlar
        )
        dolu = c.execute(text(f'SELECT {secim} FROM "{t}"')).mappings().one()
        for k in kolonlar:
            d = dolu[k]
            print(f"   {k:<34} {d:>7} / {n}  ({100 * d / n:5.1f}%)")
        print()
