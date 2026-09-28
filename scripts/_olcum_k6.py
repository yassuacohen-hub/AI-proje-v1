# -*- coding: utf-8 -*-
"""K-6 olcumu: tax_number / vergi_no degerlerini kimlik_no kurali ile siniflandir.

Amac: VERI_KALITE_SOZLESMESI.md ve D-246 icindeki sayilari canli veriden dogrulamak.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from company_master.db.connection import get_engine  # noqa: E402
from company_master.etl.kimlik_no import kimlik_dogrula  # noqa: E402
from sqlalchemy import text  # noqa: E402

with get_engine().connect() as c:
    print("firma sayisi:", c.execute(text("SELECT count(*) FROM companies")).scalar())
    for kol in ("tax_number", "vergi_no", "coalesce(vergi_no, tax_number)"):
        rows = c.execute(text(f"""
            SELECT {kol} d, count(*) n FROM companies
            WHERE {kol} IS NOT NULL AND trim({kol}) != '' GROUP BY {kol}
        """)).fetchall()
        sayac = {"vkn": 0, "tckn": 0, "gecersiz": 0}
        uzunluk = {}
        for deger, n in rows:
            tur = kimlik_dogrula(deger)[1]
            sayac[tur] += n
            if tur == "gecersiz":
                t = str(deger).strip()
                etiket = f"{len(t)} hane" if t.isdigit() else "rakam disi"
                uzunluk[etiket] = uzunluk.get(etiket, 0) + n
        toplam = sum(sayac.values())
        print(f"\n=== {kol} ===")
        print(f"  dolu kayit                  : {toplam}")
        print(f"  10 hane gecerli VKN (tuzel) : {sayac['vkn']}")
        print(f"  11 hane gecerli TCKN (sahis): {sayac['tckn']}")
        print(f"  GECERSIZ (vergi no degil)   : {sayac['gecersiz']}"
              + (f"  (%{100 * sayac['gecersiz'] / toplam:.1f})" if toplam else ""))
        print("  gecersizlerin anatomisi:")
        for e, n in sorted(uzunluk.items(), key=lambda x: -x[1]):
            print(f"      {e}: {n}")
