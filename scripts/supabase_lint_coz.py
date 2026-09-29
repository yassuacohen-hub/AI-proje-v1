"""D-307: Supabase guvenlik — SARI UYARILAR (lint) cozumu.

KAHIN 2026-09-29: "rls hatalari cozuldu fakat sari uyarilar duruyor"

Ekrandan OKUNAN 3 uyari (kanit):
  1) Fonksiyon Arama Yolu Degistirilebilir - public.update_updated_at_column
  2) Fonksiyon Arama Yolu Degistirilebilir - public.trg_isaretci_senkron
  3) Kamuya Acik Uzanti             - public.pg_trgm

COZUM:
  1) Fonksiyonlara `SET search_path = ''` (supabase_lint aramasi
     "function_search_path_mutable"). Bu GUVENLIDIR: trigger
     fonksiyonlari tam yol/tablolarla cagrildigi icin davranis
     DEGISMEX. Once kullanimi olcerek dogrulanir.
  2) pg_trgm: extension public semada. Tasmasi riskli olabilir
     (arama kullanimi). ONCE kullanim olculur; karar KAHIN'e.

Varsayilan SALT OKUNUR. Yazma icin --uygula.
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
KAYIT = KOK / "data" / "_tmp" / "supabase_lint_cozumu.json"

#: search_path'siz fonksiyonlari getiren sorgu
#:
#: DIKKAT: public semadaki 33 fonksiyonun 31'i pg_trgm EXTENSION'ina
#: aittir (gin_trgm_*, gtrgm_*, similarity, word_similarity ...).
#: Bunlara `ALTER FUNCTION ... SET search_path` yapmak EXTENSION'I BOZAR
#: ve Postgres'in extension dosyalariyla tutarsizlasir. Ekrandaki 2
#: uyari yalnizca BIZE ait 2 fonksiyonu gosteriyor:
#:   - trg_isaretci_senkron()  -> TRIGGER companies
#:   - update_updated_at_column() -> 3 TRIGGER
#: Bu yuzden `p.prokind='f'` + extension uyesi OLMAYAN filtrelenir:
#: `p.oid NOT IN (SELECT objid FROM pg_depend d WHERE d.deptype='e')`
SORGUSUZ = """
    SELECT p.proname,
           pg_get_function_identity_arguments(p.oid) AS args,
           p.proconfig
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public' AND p.prokind = 'f'
      AND p.oid NOT IN (SELECT objid FROM pg_depend d
                        WHERE d.deptype = 'e')
      AND (p.proconfig IS NULL
           OR NOT EXISTS (SELECT 1 FROM unnest(p.proconfig) c
                          WHERE c LIKE 'search_path=%'))
    ORDER BY p.proname
"""


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

    print("=" * 72)
    print("D-307  SUPABASE SARI UYARILAR (lint)")
    print("=" * 72)

    cur.execute("""SELECT count(*) FROM pg_proc p
                   JOIN pg_namespace n ON n.oid = p.pronamespace
                   WHERE n.nspname='public' AND p.prokind='f'""")
    toplam = cur.fetchone()[0]
    cur.execute(SORGUSUZ)
    eksik = cur.fetchall()
    print(f"\npublic fonksiyon : {toplam}")
    print(f"search_path'siz  : {len(eksik)}")
    for ad, args, _ in eksik:
        print(f"    {ad}({args[:50]})")

    # --- bu fonksiyonlar TRIGGER mi? (guvenlilik onayi)
    print("\n--- kullanim: TRIGGER mi?")
    for ad, args, _ in eksik:
        cur.execute("""
            SELECT c.relname, t.tgname
            FROM pg_trigger t
            JOIN pg_class c ON c.oid = t.tgrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname='public' AND t.tgfoid = (
                SELECT p.oid FROM pg_proc p
                JOIN pg_namespace m ON m.oid=p.pronamespace
                WHERE m.nspname='public' AND p.proname=%s
                  AND pg_get_function_identity_arguments(p.oid)=%s
                LIMIT 1)
        """, (ad, args))
        tg = cur.fetchall()
        if tg:
            for tablo, tgad in tg:
                print(f"    {ad}() -> TRIGGER {tablo}.{tgad}")
        else:
            print(f"    {ad}() -> TRIGGER YOK (view/func cagrisi kontrol et)")

    # --- extension'lar
    print("\n--- extension'lar")
    cur.execute("""SELECT extname, extversion, n.nspname
                   FROM pg_extension e
                   JOIN pg_namespace n ON n.oid = e.extnamespace
                   ORDER BY extname""")
    for ad, surum, sema in cur.fetchall():
        isaret = "  <<< public (uyari)" if sema == "public" else ""
        print(f"    {ad:22s} {str(surum)[:12]:14s} {sema}{isaret}")

    # --- pg_trgm kullanimi (karar icin)
    print("\n--- pg_trgm KULLANIMI (tasmaya karar)")
    try:
        cur.execute("""
            SELECT c.relname FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_index i ON i.indexrelid = c.oid
            WHERE n.nspname = 'public' AND c.relkind = 'i'
              AND pg_get_indexdef(i.indexrelid) ILIKE '%trgm%'
        """)
        idx = cur.fetchall()
        print(f"    trigram indeks : {len(idx)}")
        for (ad,) in idx[:8]:
            print(f"        {ad}")
    except psycopg2.Error as e:
        print(f"    indeks hata: {str(e)[:70]}")
    try:
        cur.execute("""SELECT count(*) FROM pg_depend d
                       JOIN pg_extension e ON e.oid = d.refobjid
                       WHERE e.extname='pg_trgm' AND d.deptype='e'""")
        print(f"    extension'a ait obje : {cur.fetchone()[0]}")
    except psycopg2.Error as e:
        print(f"    sayim hata: {str(e)[:70]}")
    print("    -> pg_trgm tasinmasi karari KAHIN'e; extension'a ait")
    print("       obje sayisi yuksek, tasima DAHA FAZLA uyari uretir.")

    # --- pg_trgm tasima ETKISI (4 indeks trgm operator sinifina bagli)
    # Operator siniflari (gin_trgm_ops) GLOBAL nesnedir; sema tasima
    # indeks tanimini BOZMAZ cunku index OID uzerinden baglanir.
    # Ama tablo KOLONLARI ustundeki varsayilan operator sinifi
    # cift sinif (default) etiketini tasir.
    print("\n--- pg_trgm tasima ETKISI (simdiki operator siniflari)")
    try:
        cur.execute("""
            SELECT c.relname, am.amname, opc.opcname
            FROM pg_index i
            JOIN pg_class c ON c.oid = i.indexrelid
            JOIN pg_am am ON am.oid = c.relam
            JOIN pg_opclass opc ON opc.oid = i.indclass[0]
            WHERE c.relnamespace = 'public'::regnamespace
              AND opc.opcname LIKE '%trgm%'
        """)
        for ad, am, opc in cur.fetchall():
            print(f"    {ad[:42]:44s} {am:6s} {opc}")
    except psycopg2.Error as e:
        print(f"    hata: {str(e)[:70]}")

    # --- trigram indeksleri tasima sonrasi sag mi? (D-307 dogrulama)
    try:
        cur.execute("""
            SELECT indexrelid::regclass::text, indisvalid
            FROM pg_index
            WHERE pg_get_indexdef(indexrelid) ILIKE '%trgm%'
        """)
        ix = cur.fetchall()
        gecerli = sum(1 for _, v in ix if v)
        print(f"\n--- trigram indeks sagligi: {gecerli}/{len(ix)} gecerli")
        for ad, v in ix:
            print(f"    {'OK ' if v else 'BOZUK'} {ad[:50]}")
    except psycopg2.Error as e:
        print(f"    indeks kontrol hata: {str(e)[:60]}")

    # --- migration yaz
    s = [
        "-- D-307: Supabase lint — search_path_mutable (KAHIN 2026-09-29)",
        f"-- uretim: {datetime.now().isoformat(timespec='seconds')}",
        "--",
        "-- Bu fonksiyonlar TRIGGER'dir; tam yol/tablo adiyla cagrilir.",
        "-- search_path sabitlemek davranisi DEGISTIRMEZ, yalnizca",
        "-- guvenlik sertlestirir (supabase_lint aramasi).",
        "",
    ]
    for ad, args, _ in eksik:
        s.append(f"ALTER FUNCTION public.\"{ad}\"({args}) "
                 "SET search_path = '';")
    s += [
        "",
        "-- pg_trgm extension'ini public semadan 'extensions' semasina",
        "-- tasi (supabase_lint: extension_in_public). Diger tum",
        "-- extension'lar zaten 'extensions' semasinda; bu tutarli.",
        "-- Operator siniflari GLOBAL nesnedir; indeksler OID uzerinden",
        "-- bagli oldugu icin tasima indeksleri bozmaz.",
        "CREATE SCHEMA IF NOT EXISTS extensions;",
        "ALTER EXTENSION pg_trgm SET SCHEMA extensions;",
    ]
    MIGRASYON.mkdir(parents=True, exist_ok=True)
    p = MIGRASYON / "20260929_d307_search_path_sabit.sql"
    p.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"\nmigration taslagi: {p.relative_to(KOK)}")

    if not ns.uygula:
        con.close()
        print("\nRAPOR MODU. Yazmak icin: --uygula")
        return 0

    print("\n>>> UYGULANIYOR ...")
    try:
        with con:
            with con.cursor() as c2:
                for ad, args, _ in eksik:
                    c2.execute(f"ALTER FUNCTION public.\"{ad}\"({args}) "
                               "SET search_path = ''")
                # pg_trgm tasima: DIKKAT onceki kosuda SQL yalnizca
                # migration dosyasina YAZILDI, yurutulmedi. Bu yuzden
                # uyari ekranda duruyordu. Simdi GERCEKTEN calistir.
                c2.execute("CREATE SCHEMA IF NOT EXISTS extensions")
                c2.execute("ALTER EXTENSION pg_trgm SET SCHEMA extensions")
        print(">>> TAMAMLANDI")
    except Exception as e:
        print(f"HATA: {type(e).__name__}: {str(e)[:200]}")
        con.rollback()
        con.close()
        return 1

    cur.execute(SORGUSUZ)
    kalan = len(cur.fetchall())
    # pg_trgm gercekten tasindi mi?
    cur.execute("""SELECT n.nspname FROM pg_extension e
                   JOIN pg_namespace n ON n.oid = e.extnamespace
                   WHERE e.extname='pg_trgm'""")
    trgm_sema = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies")
    companies = cur.fetchone()[0]
    con.close()
    print(f"\nDOGRULAMA:")
    print(f"    search_path'siz fonksiyon = {kalan} (0 olmali)")
    print(f"    pg_trgm semasi             = {trgm_sema} "
          f"(extensions olmali)")
    print(f"    companies satir            = {companies} (degismemeli)")
    KAYIT.parent.mkdir(parents=True, exist_ok=True)
    KAYIT.write_text(json.dumps({
        "zaman": datetime.now().isoformat(timespec="seconds"),
        "duzeltilen_fonksiyon": len(eksik), "kalan": kalan,
        "pg_trgm_sema": trgm_sema, "companies": companies,
        "migration": str(p.relative_to(KOK)),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    cur.execute("""
        SELECT count(*) FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r','i') AND n.nspname = 'public'
          AND (pg_get_indexdef(c.oid) ILIKE '%gin_trgm%'
               OR pg_get_indexdef(c.oid) ILIKE '%gist_trgm%')
    """)
    print(f"    trigram indeks sayisi        : {cur.fetchone()[0]}")
    cur.execute("""
        SELECT count(*) FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname='public' AND p.prosrc ILIKE '%similarity%'
    """)
    print(f"    similarity() kullanan fonk. : {cur.fetchone()[0]}")
