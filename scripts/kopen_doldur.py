"""D-310: kokeni kaynaktan dogru yere bagla (DUZELTILMIS).

D-310 ilk kosuda HATA YAPTI: source_name = source_records.raw_website
yazildi. raw_website FIRMANIN web adresidir, KAYNAK ADI degildir.
5.362 kayit yanlis etiketlendi. Dogru yol:
    source_records.source_id -> sources.<ad kolonu>

Bu surum yalniz dogru yolu kullanir. Varsayilan SALT OKUNUR.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

from supabase_envanter import env_oku  # noqa: E402

MIGRASYON = KOK / "supabase" / "migrations"
KAYIT = KOK / "data" / "_tmp" / "kopen_doldurma.json"
SR_ANAHTAR = "source_record_id"


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--uygula", action="store_true")
    ns = ay.parse_args()
    url = env_oku(KOK / ".env").get("DATABASE_URL")
    if not url:
        print("DATABASE_URL yok")
        return 1
    import psycopg2
    con = psycopg2.connect(url, connect_timeout=25)
    cur = con.cursor()
    bulgu = {"zaman": datetime.now().isoformat(timespec="seconds")}

    print("=" * 72)
    print("D-310  KOKENI DOGRU YERE BAGLA (duzeltilmis)")
    print("=" * 72)

    # --- 1) kaynak tablosu
    cur.execute("""SELECT column_name FROM information_schema.columns
                   WHERE table_schema='public'
                     AND table_name='sources'""")
    src_kol = [r[0] for r in cur.fetchall()]
    src_ad = next((k for k in ("name", "source_name", "title", "label",
                               "domain", "url") if k in src_kol), None)
    print(f"\nsources kolonlar : {src_kol}")
    print(f"kullanilacak ad  : {src_ad}")
    bulgu["sources_kolonlar"] = src_kol
    bulgu["sources_ad_kolon"] = src_ad
    if src_ad:
        cur.execute(f"""SELECT "{src_ad}", COUNT(*) FROM sources
                        GROUP BY 1 ORDER BY 2 DESC""")
        for ad, n in cur.fetchall():
            print(f"    {str(ad)[:44]:46s} {n}")

    # --- 2) companies semasi
    cur.execute("""SELECT column_name FROM information_schema.columns
                   WHERE table_schema='public'
                     AND table_name='companies'""")
    ck = {r[0] for r in cur.fetchall()}
    print(f"\nsource_id kolonu : "
          f"{'VAR' if 'source_id' in ck else 'YOK'}")

    # --- 3) SQL
    s = [
        "-- D-310: kokeni dogru yere bagla (KAHIN 2026-09-29)",
        f"-- uretim: {datetime.now().isoformat(timespec='seconds')}",
        "--",
        "-- DUZELTME: source_name = raw_website YANLISTI; raw_website",
        "-- firmanin kendi sitesidir, kaynagin adini tasimaz.",
        "-- Dogru yol: source_records.source_id -> sources.<ad>",
        "",
        "BEGIN;",
    ]
    if src_ad and "source_id" in ck:
        s += [
            "-- once hatali degeri temizle (yalnizca migration'in",
            "-- kendi yazdigi degerler; elle girilmis veri korunur)",
            "UPDATE public.companies",
            "SET source_name = NULL",
            "WHERE source_name = ANY (",
            "  SELECT raw_website FROM public.source_records",
            "  WHERE raw_website IS NOT NULL);",
            "",
            "-- dogru kaynak adi (anahtar: sources.source_id)",
            "UPDATE public.companies c",
            f"SET source_name = src.\"{src_ad}\"",
            "  FROM public.source_records sr",
            "  JOIN public.sources src",
            "    ON src.source_id = sr.source_id",
            f"  WHERE sr.\"{SR_ANAHTAR}\" = c.source_record_id",
            "    AND c.source_name IS NULL;",
        ]
    else:
        s.append("-- !! kaynak tablosu/sutun bulunamadi; ATLANDI")
    s += ["COMMIT;"]
    MIGRASYON.mkdir(parents=True, exist_ok=True)
    p = MIGRASYON / "20260929_d310b_koken_dogru_yol.sql"
    p.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"\nmigration: {p.relative_to(KOK)}")

    if not ns.uygula:
        con.close()
        print("\nRAPOR MODU. --uygula ile calistirilir.")
        return 0

    print("\n>>> UYGULANIYOR ...")
    try:
        with con:
            with con.cursor() as c2:
                c2.execute(
                    "UPDATE public.companies SET source_name = NULL "
                    "WHERE source_name = ANY ("
                    "  SELECT raw_website FROM public.source_records "
                    "  WHERE raw_website IS NOT NULL)")
                c2.execute(
                    "UPDATE public.companies c "
                    f"SET source_name = src.\"{src_ad}\" "
                    "FROM public.source_records sr "
                    "JOIN public.sources src "
                    "  ON src.source_id = sr.source_id "
                    f"WHERE sr.\"{SR_ANAHTAR}\" = c.source_record_id "
                    "AND c.source_name IS NULL")
        print(">>> TAMAMLANDI")
    except Exception as e:
        print(f"HATA: {type(e).__name__}: {str(e)[:180]}")
        con.rollback()
        con.close()
        return 1

    for kolon in ("collected_at", "source_name", "collected_by"):
        cur.execute(f"""SELECT count(*) FROM public.companies
                        WHERE "{kolon}" IS NOT NULL""")
        n = cur.fetchone()[0]
        bulgu[kolon] = n
        print(f"    {kolon:14s} dolu = {n}/9412")
    cur.execute("SELECT COUNT(*) FROM companies")
    bulgu["satir"] = cur.fetchone()[0]
    con.close()
    KAYIT.parent.mkdir(parents=True, exist_ok=True)
    KAYIT.write_text(json.dumps(bulgu, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
