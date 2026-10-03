# -*- coding: utf-8 -*-
"""Paket tablosu ölçümü — packages, company_packages, `plan` kolonları, kaynak kapısı.

Kullanım (Huginn Data Insights kökünden):
    python scripts\\paket_olc.py            # tablo özeti
    python scripts\\paket_olc.py <company_id>   # o firmanın izinli haber kaynakları

D-260: beyan kanıt değil; bu betik DB'yi okur, yazmaz.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402
from company_master.paketler import PAKET_KAYNAKLARI, firma_haber_kaynaklari  # noqa: E402


def ozet() -> None:
    with get_engine().connect() as c:
        print("== packages ==")
        satirlar = list(c.execute(text(
            "select name, price, features, is_active from packages order by name")).mappings())
        for r in satirlar:
            print(f"  {r['name']:<14} {r['price']!s:>10} aktif={r['is_active']} kaynak={','.join(PAKET_KAYNAKLARI.get(r['name'], ()))} features={r['features']}")
        if not satirlar:
            print("  (boş) — fiyat_katalogu() ile senkron değil; scripts/sync_paket_fiyatlari.py")
        n, firma = c.execute(text(
            "select count(*), count(distinct company_id) from company_packages")).fetchone()
        print(f"== company_packages == satır={n} firma={firma}")
        kolonlar = c.execute(text(
            "select table_name from information_schema.columns where column_name='plan'")).fetchall()
        for (t,) in kolonlar:
            dolu = c.execute(text(f"select count(*) from {t} where plan is not null and plan<>''")).scalar()
            print(f"== {t}.plan == dolu={dolu}")


def main(argv: list[str]) -> int:
    if argv:
        print(sorted(firma_haber_kaynaklari(argv[0])))
        return 0
    ozet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
