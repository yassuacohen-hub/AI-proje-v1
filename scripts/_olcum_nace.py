# -*- coding: utf-8 -*-
"""OLCUM-NACE-01 + GOC-DEFTER-01 kaniti (gecici betik).

Iki soru:
A) Goc defteri yalan mi soyluyor? (0014-0025'in eseri semada var mi?)
B) NACE anatomisi: kod + acilim + coklu kod + "yapabilir vs yapiyor" ayrimi
   bugun semada nasil tutuluyor?
"""
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from company_master.db.connection import get_engine  # noqa: E402

# Goc dosyasi -> semada olmasi gereken iz (tablo, kolon|None)
GOC_IZI = {
    "0012_users_and_catalog": ("users", None),
    "0014_packages_marketing": ("packages", None),
    "0015_data_log": ("data_log", None),
    "0016_users_last_login": ("users", "last_login_at"),
    "0017_user_activity_log": ("user_activity_log", None),
    "0018_visibility_layer": ("companies", None),  # ayarlar tablosuna bakilir
    "0019_admin_mfa": ("users", "mfa_secret"),
    "0021_missing_tables": ("schema_migrations", None),
    "0023_source_records_company_id": ("source_records", "company_id"),
    "0025_kimlik_dosyasi_alanlari": ("companies", "kimlik_tamligi"),
}


def main() -> None:
    with get_engine().connect() as c:
        tablolar = {t for (t,) in c.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public'"))}

        def kolon_var(t: str, k: str) -> bool:
            return bool(c.execute(text(
                "SELECT 1 FROM information_schema.columns WHERE table_schema='public' "
                "AND table_name=:t AND column_name=:k"), {"t": t, "k": k}).first())

        defter = {f.replace(".sql", "") for (f,) in c.execute(text(
            "SELECT filename FROM schema_migrations"))}

        print("=" * 70)
        print("A) GOC DEFTERI KANITI  (defterde yok ama semada VAR = defter yalan)")
        print("=" * 70)
        for goc, (t, k) in sorted(GOC_IZI.items()):
            semada = (t in tablolar) if k is None else kolon_var(t, k)
            defterde = goc in defter
            if defterde and semada:
                d = "tutarli (uygulandi)"
            elif not defterde and semada:
                d = ">>> DEFTER YALAN: uygulanmis, kayit yok"
            elif not defterde and not semada:
                d = "tutarli (uygulanmadi)"
            else:
                d = ">>> DAHA KOTU: kayit var, sema yok"
            iz = t if k is None else f"{t}.{k}"
            print(f"  {goc:36} iz={iz:28} {d}")

        print()
        print("=" * 70)
        print("B) NACE ANATOMISI")
        print("=" * 70)

        print("\n  B1) NACE ile ilgili tablolar:")
        for t in sorted(x for x in tablolar
                        if "nace" in x or "industr" in x or "sektor" in x):
            n = c.execute(text(f'SELECT count(*) FROM "{t}"')).scalar()
            print(f"     {t:32} satir={n}")

        print("\n  B2) companies uzerindeki NACE kolonlari:")
        for k in ("nace_code", "nace_name", "nace_source", "nace_validity"):
            if kolon_var("companies", k):
                dolu = c.execute(text(
                    f"SELECT count(*) FROM companies WHERE {k} IS NOT NULL "
                    f"AND btrim({k}::text) <> ''")).scalar()
                farkli = c.execute(text(
                    f"SELECT count(DISTINCT {k}) FROM companies")).scalar()
                print(f"     {k:16} dolu={dolu:6} farkli_deger={farkli}")
            else:
                print(f"     {k:16} YOK")

        toplam = c.execute(text("SELECT count(*) FROM companies")).scalar()
        print(f"\n     (toplam firma: {toplam})")

        print("\n  B3) 'yapabilir vs yapiyor' ayrimi: coklu NACE tutuluyor mu?")
        if "company_industries" in tablolar:
            kolonlar = [k for (k,) in c.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='company_industries' "
                "ORDER BY ordinal_position"))]
            print(f"     company_industries kolonlari: {kolonlar}")
            print("     firma basina NACE sayisi dagilimi:")
            for kac, firma in c.execute(text("""
                SELECT kac, count(*) FROM (
                    SELECT company_id, count(*) AS kac
                    FROM company_industries GROUP BY company_id) s
                GROUP BY kac ORDER BY kac""")):
                print(f"       {kac} kod -> {firma} firma")
            if "is_primary" in kolonlar:
                print("     is_primary dagilimi:")
                for v, n in c.execute(text(
                        "SELECT is_primary, count(*) FROM company_industries "
                        "GROUP BY is_primary ORDER BY 1")):
                    print(f"       {v!r} -> {n}")
        else:
            print("     >>> company_industries TABLOSU YOK")

        print("\n  B4) NACE acilimi (kod -> isim) sozlugu var mi, tam mi?")
        for t in ("nace_codes", "nace_code_details"):
            if t in tablolar:
                kolonlar = [k for (k,) in c.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name=:t "
                    "ORDER BY ordinal_position"), {"t": t})]
                print(f"     {t}: {kolonlar}")

        print("\n  B5) companies.nace_code sozlukte bulunuyor mu? (kopuk bag)")
        kopuk = c.execute(text("""
            SELECT count(*) FROM companies co
            WHERE co.nace_code IS NOT NULL AND btrim(co.nace_code) <> ''
              AND NOT EXISTS (SELECT 1 FROM nace_codes nc
                              WHERE nc.nace_code = co.nace_code)""")).scalar()
        print(f"     sozlukte OLMAYAN nace_code'lu firma: {kopuk}")
        print("     nace_codes seviye dagilimi (acilim derinligi):")
        for lvl, n in c.execute(text(
                "SELECT level, count(*) FROM nace_codes GROUP BY level ORDER BY 1")):
            print(f"       level {lvl} -> {n} kod")
        print("     nace_codes.title bos olan:", c.execute(text(
            "SELECT count(*) FROM nace_codes WHERE title IS NULL "
            "OR btrim(title)=''")).scalar())

        print("\n  B6) en sik 10 nace_code + sozlukteki acilimi:")
        for kod, n, title, sg in c.execute(text("""
            SELECT co.nace_code, count(*) AS n, max(nc.title), max(nc.sector_group)
            FROM companies co LEFT JOIN nace_codes nc ON nc.nace_code = co.nace_code
            WHERE co.nace_code IS NOT NULL AND btrim(co.nace_code) <> ''
            GROUP BY co.nace_code ORDER BY n DESC LIMIT 10""")):
            print(f"     {kod:10} n={n:5}  {str(title)[:40]:42} [{sg}]")

        print("\n  B7) companies.nace_code hane uzunlugu (seviye tutarliligi):")
        for uz, n in c.execute(text("""
            SELECT length(btrim(nace_code)) AS uz, count(*) FROM companies
            WHERE nace_code IS NOT NULL AND btrim(nace_code) <> ''
            GROUP BY uz ORDER BY uz""")):
            print(f"       {uz} hane -> {n} firma")

        print("\n  B8) nace_source + nace_validity dagilimi (guven ayrimi):")
        for s, v, n in c.execute(text(
                "SELECT nace_source, nace_validity, count(*) FROM companies "
                "GROUP BY 1,2 ORDER BY 3 DESC")):
            print(f"       {str(s)[:24]:26} / {str(v)[:20]:22} -> {n}")


if __name__ == "__main__":
    main()
