"""GUVENLIK DENETIMI — Supabase RLS ve hassas veri (SALT OKUNUR).

KAHIN 2026-09-29: Supabase maili — "Table publicly accessible
(rls_disabled_in_public)" + "sensitive_columns_exposed".
Proje: huginn-company-master / kypoqtgbrxknyazwlhxq

BU SCRIPT HICBIR SEY YAZMAZ. Yalniz SELECT ile durumu olcer ve
onerir. Duzeltme (RLS acma, kolon kapatma) ayri ve onayli adimdir.

Raporlanacaklar:
  1) RLS acik kapali olan tablolar (pg_class.relrowsecurity)
  2) RLS'siz + ONCEKI YAZMA yetkisi olan tablolar (asili risk)
  3) Hassas kolon adlari (password, token, secret, email, tc, kvkk...)
  4) Force-RLS durumu
"""
from __future__ import annotations

import pathlib
import re
import sys

KOK = pathlib.Path(r"C:\Huginn Data Projesi\Huginn Data Insights")
sys.path.insert(0, str(KOK / "scripts"))

from supabase_envanter import env_oku  # noqa: E402

#: Hassas sayilan kolon desenleri
HASSAS = re.compile(
    r"password|passwd|secret|token|api[_-]?key|private|"
    r"tc_kimlik|kimlik_no|ssn|credit|card|"
    r"email|phone|kvkk|bireysel|kişisel|dogum|birth|"
    r"salary|maas|ucret", re.IGNORECASE)


def main() -> None:
    d = env_oku(KOK / ".env")
    url = d.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL yok")
        return
    import psycopg2
    con = psycopg2.connect(url, connect_timeout=25)
    cur = con.cursor()

    # --- 1) RLS DURUMU + yetkiler
    cur.execute("""
        SELECT c.relname,
               c.relrowsecurity,
               c.relforcerowsecurity,
               COALESCE(a.nspname, '?') AS schema
        FROM pg_class c
        JOIN pg_namespace a ON a.oid = c.relnamespace
        WHERE c.relkind = 'r' AND a.nspname = 'public'
        ORDER BY c.relrowsecurity, c.relname
    """)
    tablolar = cur.fetchall()
    rls_acsiz = [t[0] for t in tablolar if not t[1]]
    rls_acsiz_forced = [t[0] for t in tablolar if not t[2]]
    rls_acik = [t[0] for t in tablolar if t[1]]

    print("=" * 74)
    print("SUPABASE GUVENLIK DENETIMI — SALT OKUNUR")
    print(f"Proje: huginn-company-master")
    print("=" * 74)
    print(f"\nToplam tablo (public) : {len(tablolar)}")
    print(f"RLS ACIK             : {len(rls_acik)}")
    print(f"RLS KAPALI (risk!)   : {len(rls_acsiz)}")
    print(f"Force-RLS eksik      : {len(rls_acsiz_forced)}")

    # --- 2) satır sayılarıyla risk sıralaması
    print("\n" + "-" * 74)
    print("RISK SIRASI: RLS KAPALI tablolar (veri hacmine gore)")
    print("-" * 74)
    risk = []
    for tb in rls_acsiz:
        try:
            cur.execute(f'SELECT COUNT(*) FROM public."{tb}"')
            n = cur.fetchone()[0]
        except psycopg2.Error:
            n = -1
        risk.append((n, tb))
    for n, tb in sorted(risk, reverse=True):
        isaret = "  <<< VERI VAR" if n > 0 else "  (bos)"
        print(f"   {str(n):>8}  {tb[:44]:46s}{isaret}")

    # --- 3) HASSAS KOLONLAR
    print("\n" + "-" * 74)
    print("HASSAS KOLONLAR (RLS'siz tablolarda EN TEHLIKELI)")
    print("-" * 74)
    bulunan = []
    for tb in rls_acsiz:
        try:
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema='public' AND table_name=%s
            """, (tb,))
            for kolon, tip in cur.fetchall():
                if HASSAS.search(kolon):
                    bulunan.append((tb, kolon, tip))
        except psycopg2.Error:
            continue
    if bulunan:
        for tb, kolon, tip in bulunan:
            print(f"   {tb[:30]:32s} {kolon[:26]:28s} {tip[:20]}")
    else:
        print("   (eslesen kolon bulunamadi)")

    # --- 4) RLS policy sayisi
    print("\n" + "-" * 74)
    print("RLS POLICY SAYISI")
    print("-" * 74)
    try:
        cur.execute("""
            SELECT tablename, COUNT(*)
            FROM pg_policies WHERE schemaname='public'
            GROUP BY 1 ORDER BY 2 DESC
        """)
        pol = cur.fetchall()
        if pol:
            for tb, adet in pol:
                print(f"   {tb[:40]:42s} {adet} policy")
        else:
            print("   HICBIR RLS POLICY YOK")
    except psycopg2.Error as e:
        print("   HATA:", str(e)[:80])

    # --- 5) GRAND DURUMU (30 Ekim 2026 Supabase kurali)
    print("\n" + "-" * 74)
    print("TABLO GRANT DURUMU — 30 Ekim sonrasi yeni tablo icin zorunlu")
    print("-" * 74)
    try:
        cur.execute("""
            SELECT table_name, grantee, string_agg(privilege_type, ','
                                                   ORDER BY privilege_type)
            FROM information_schema.role_table_grants
            WHERE table_schema='public'
              AND grantee IN ('anon','authenticated','service_role')
            GROUP BY table_name, grantee
            ORDER BY table_name, grantee
        """)
        g = cur.fetchall()
        if not g:
            print("  HICBIR ROL GRANT'I YOK")
        else:
            # hangi tablolarda eksik
            cur.execute("""SELECT table_name FROM information_schema.tables
                           WHERE table_schema='public' AND
                                 table_type='BASE TABLE'""")
            tum = {r[0] for r in cur.fetchall()}
            var_olan = {}
            for tb, rol, priv in g:
                var_olan.setdefault(tb, {})[rol] = priv
            anonlu = [t for t, d in var_olan.items() if "anon" in d]
            print(f"  GRANT'i olan tablo : {len(var_olan)} / {len(tum)}")
            print(f"  anon GRANT'i olan  : {len(anonlu)}")
            eksik = sorted(tum - set(var_olan))
            print(f"  GRANT'I OLMAYAN     : {len(eksik)}")
            for t in eksik[:25]:
                print(f"      {t[:50]}")
            if len(eksik) > 25:
                print(f"      ... +{len(eksik) - 25} tablo daha")
            # veri olan + grant'i olmayan = en riskli
            riskli = []
            for t in eksik:
                try:
                    cur.execute(f'SELECT COUNT(*) FROM public."{t}"')
                    n = cur.fetchone()[0]
                except psycopg2.Error:
                    n = 0
                if n:
                    riskli.append((n, t))
            if riskli:
                print("\n  VERI OLAN + GRANT'I OLMAYAN (yeni tablo kurali icin):")
                for n, t in sorted(riskli, reverse=True)[:12]:
                    print(f"      {str(n):>7}  {t[:44]}")
    except psycopg2.Error as e:
        print("  HATA:", str(e)[:100])

    con.close()
    print("\n" + "=" * 74)
    print("SONUC: Bu bir RAPOR. Duzeltme (RLS/GRANT) icin KAHIN onayi gerekli.")
    print("=" * 74)


if __name__ == "__main__":
    main()
