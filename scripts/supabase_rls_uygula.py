"""D-306: Supabase guvenligi - Veri API'yi KALICI KAPAT ve RLS'i ac.

KAHIN 2026-09-29: "yani bu sorunu kesin cozelim yoksa api kullandirmayacal"

OLCULEN GERCEK (scripts/supabase_guvenlik_denetim.py):
  - 52 tablo, 52'sinde RLS KAPALI, 0 policy
  - 54 tabloda anon GRANT'i VAR -> Veri API (PostgREST) su an
    ANON OLARAK ERISILEBILIR
  - EN TEHLIKELI acik kolonlar: users.password_hash, users.api_key,
    admin_mfa.secret_key, admin_mfa_*_tokens.mfa_token,
    kvkk_bireysel_email_yedek.primary_email

COZUM (KAHIN karari: API kullanilmayacak):
  1) RLS'i tum tablolarda ACIK ET -> parola sizsa bile PostgREST
     uzerinden satir okunamaz (savunma derinligi).
  2) anon + authenticated rollerine TUM yetkileri GERI AL
     -> Veri API tamamen kapanir. Bu zaten KAHIN'in istediği.
  3) service_role DOKUNULMAZ -> backend/panel calismaya devam eder.
  4) Gelecek tablolar icin (30 Ekim kurali): migration'lara GRANT
     EKLENMEYECEK. Supabase 30 Ekim'de GRANT'siz yeni tablolari
     otomatik API'ye kapatacak; biz de ayni sonucu isteriz.

GUVENLIK: script varsayilan SALT OKUNUR. Yazma icin --uygula
bayragi gerekir. --geri-al ile tam tersi uygulanabilir.
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
KAYIT = KOK / "data" / "_tmp" / "supabase_rls_uygulama.json"

#: Bu roller Veri API uzerinden gelir. Kapatilacak.
API_ROLLERI = ("anon", "authenticated")


def tablolari_al(cur) -> list[str]:
    cur.execute("""SELECT table_name FROM information_schema.tables
                   WHERE table_schema='public' AND table_type='BASE TABLE'
                   ORDER BY table_name""")
    return [r[0] for r in cur.fetchall()]


def rls_durumu(cur) -> dict[str, bool]:
    cur.execute("""SELECT c.relname, c.relrowsecurity
                   FROM pg_class c JOIN pg_namespace a
                     ON a.oid=c.relnamespace
                   WHERE a.nspname='public' AND c.relkind='r'""")
    return {t: bool(r) for t, r in cur.fetchall()}


def migration_yaz(tablo: list[str]) -> pathlib.Path:
    s = [
        "-- D-306: Veri API kapatma + RLS (KAHIN 2026-09-29)",
        f"-- uretim: {datetime.now().isoformat(timespec='seconds')}",
        "-- service_role DOKUNULMAZ: backend/panel calisir.",
        "",
        "-- 1) RLS'i tum tablolarda ac. Parola sizsa bile PostgREST",
        "--    uzerinden satir okunamaz.",
    ]
    s += [f'ALTER TABLE public."{t}" ENABLE ROW LEVEL SECURITY;'
          for t in tablo]
    s.append("")
    s.append("-- 2) API rollerinden yetkileri geri al -> Veri API kapanir.")
    for r in API_ROLLERI:
        s.append(f"REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {r};")
        s.append(f"REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM {r};")
        s.append(f"REVOKE ALL ON SCHEMA public FROM {r};")
    s += [
        "",
        "-- 3) Gelecek migration'lara GRANT EKLEMEYIN. 30 Ekim 2026",
        "--    sonrasi Supabase zaten GRANT'siz yeni tablolari API'ye",
        "--    kapatacak; bu bizim istegimizle ayni sonuc verir.",
    ]
    MIGRASYON.mkdir(parents=True, exist_ok=True)
    p = MIGRASYON / "20260929_d306_rls_ac_api_kapat.sql"
    p.write_text("\n".join(s) + "\n", encoding="utf-8")
    return p


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--uygula", action="store_true",
                    help="DEGISIKLIK YAP (varsayilan: sadece rapor)")
    ay.add_argument("--geri-al", action="store_true",
                    help="RLS'i kapat + GRANT'i geri ver")
    ns = ay.parse_args()

    d = env_oku(KOK / ".env")
    url = d.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL yok")
        return 1
    import psycopg2
    con = psycopg2.connect(url, connect_timeout=25)
    cur = con.cursor()

    tablo = tablolari_al(cur)
    rls = rls_durumu(cur)

    print("=" * 72)
    print("D-306  SUPABASE GUVENLIK — API KAPATMA + RLS")
    print("=" * 72)
    print(f"  tablo        : {len(tablo)}")
    print(f"  RLS acik     : {sum(rls.values())}")
    print(f"  RLS kapali   : {len(tablo) - sum(rls.values())}")

    dosya = migration_yaz(tablo)
    print(f"\n  migration taslagi: {dosya.relative_to(KOK)}")

    if not (ns.uygula or ns.geri_al):
        con.close()
        print("\n  RAPOR MODU. Yazmak icin: --uygula")
        print("  Geri almak icin    : --geri-al")
        return 0

    print("\n  >>> UYGULANIYOR (tek transaction) ...")
    try:
        with con:
            with con.cursor() as c2:
                for t in tablo:
                    if ns.uygula:
                        c2.execute(f'ALTER TABLE public."{t}" '
                                   "ENABLE ROW LEVEL SECURITY")
                    else:
                        c2.execute(f'ALTER TABLE public."{t}" '
                                   "DISABLE ROW LEVEL SECURITY")
                for r in API_ROLLERI:
                    if ns.uygula:
                        c2.execute("REVOKE ALL ON ALL TABLES IN SCHEMA "
                                   f"public FROM {r}")
                        c2.execute("REVOKE ALL ON ALL SEQUENCES IN SCHEMA "
                                   f"public FROM {r}")
                        c2.execute(f"REVOKE ALL ON SCHEMA public FROM {r}")
                    else:
                        c2.execute("GRANT SELECT ON ALL TABLES IN SCHEMA "
                                   f"public TO {r}")
                        c2.execute(f"GRANT USAGE ON SCHEMA public TO {r}")
        print("  >>> TAMAMLANDI")
    except Exception as e:
        print(f"  HATA: {type(e).__name__}: {str(e)[:160]}")
        con.rollback()
        con.close()
        return 1

    # --- DOGRULAMA
    yeni = rls_durumu(cur)
    cur.execute("""SELECT count(DISTINCT table_name)
                   FROM information_schema.role_table_grants
                   WHERE table_schema='public' AND grantee='anon'""")
    anon_grant = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies")
    companies = cur.fetchone()[0]
    con.close()

    print(f"\n  DOGRULAMA:")
    print(f"    RLS acik        = {sum(yeni.values())}/{len(yeni)}")
    print(f"    anon GRANT tablo= {anon_grant}")
    print(f"    companies satir = {companies}  (degismemeli)")
    KAYIT.parent.mkdir(parents=True, exist_ok=True)
    KAYIT.write_text(json.dumps({
        "zaman": datetime.now().isoformat(timespec="seconds"),
        "eylem": "uygula" if ns.uygula else "geri-al",
        "rls_acsiz": sum(yeni.values()), "tablo": len(yeni),
        "anon_grantli_tablo": anon_grant, "companies": companies,
        "migration": str(dosya.relative_to(KOK)),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
