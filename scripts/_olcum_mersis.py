# -*- coding: utf-8 -*-
"""MERSIS ikiz olcumu: mevcut mersis_number ne durumda? (gecici betik)

0025 gocu `mersis_no` diye YENI bir kolon aciyordu; sema zaten `mersis_number`
tasiyor. Ikinci kolon = ikiz (SEMA-IKIZ-01). Once mevcut kolonun doluluk ve
bicim durumunu olcuyoruz; 16 hane kisiti bugunku veriyi kirar mi?
"""
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from company_master.db.connection import get_engine  # noqa: E402

SORGU = """
SELECT
  count(*)                                                        AS toplam,
  count(mersis_number)                                            AS dolu,
  count(*) FILTER (WHERE mersis_number ~ '^[0-9]{16}$')            AS onaltihane,
  count(DISTINCT mersis_number)                                   AS farkli
FROM companies
"""


def main() -> None:
    with get_engine().connect() as c:
        toplam, dolu, onalti, farkli = c.execute(text(SORGU)).one()
        print(f"toplam firma      : {toplam}")
        print(f"mersis_number dolu: {dolu}")
        print(f"  16 hane uygun   : {onalti}")
        print(f"  farkli deger    : {farkli}")

        if dolu:
            print("\n  ornek degerler (ilk 10):")
            for (v,) in c.execute(text(
                    "SELECT DISTINCT mersis_number FROM companies "
                    "WHERE mersis_number IS NOT NULL LIMIT 10")):
                print(f"    {v!r}  (uzunluk={len(v)})")

        # D-251 mandali: 16 hane kisiti mevcut veriyi kirmamali.
        assert dolu == onalti, (
            f"KISIT VERIYI KIRAR: {dolu - onalti} deger 16 hane degil. "
            "Kisit eklenmeden once temizlik gerekir.")
        print("\n  MANDAL YESIL: 16 hane kisiti mevcut veriyi kirmaz.")


if __name__ == "__main__":
    main()
