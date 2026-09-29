"""Gecici: Supabase'deki GERCEK firma sayisini olcer (SALT OKUNUR).

KAHIN 2026-09-29: "yedekleri bos var supabase bak"

GUVENLIK: anahtar degerleri ASLA ekrana basilmaz; yalnizca
anahtar ADLARI ve satir sayisi raporlanir.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

KOK = pathlib.Path(r"C:\Huginn Data Projesi\Huginn Data Insights")


def env_oku(dosya: pathlib.Path) -> dict[str, str]:
    if not dosya.is_file():
        return {}
    out: dict[str, str] = {}
    for satir in dosya.read_text(encoding="utf-8", errors="replace").splitlines():
        s = satir.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        v = v.strip().strip('"').strip("'")
        out[k.strip()] = v
    return out


def main() -> None:
    print("=" * 70)
    print("SUPABASE ENV INVENTORI (degerler YAZDIRILMAZ)")
    print("=" * 70)
    for ad in (".env", ".env.vault", ".env.example",
               ".env.yedek-2026-09-17"):
        p = KOK / ad
        if not p.is_file():
            continue
        d = env_oku(p)
        sup = {k: v for k, v in d.items()
               if "SUPABASE" in k.upper() or "POSTGRES" in k.upper()
               or "DATABASE" in k.upper()}
        print(f"\n--- {ad}  ({len(d)} anahtar, {len(sup)} supabase/db)")
        for k, v in sorted(sup.items()):
            # deger sadece UZUNLUK ve HOST olarak, sifre gosterilmez
            host = ""
            m = re.search(r"https?://([^/\s]+)", v)
            if m:
                host = m.group(1)
            uzunluk = len(v)
            print(f"    {k:34s} uzunluk={uzunluk:5d}  host={host or '-'}")

    # --- canli sorgu
    print("\n" + "=" * 70)
    print("CANLI SUPABASE SORGUSU (salt okunur)")
    print("=" * 70)
    d = env_oku(KOK / ".env")
    d.update({k: v for k, v in env_oku(KOK / ".env.vault").items()
              if k not in d})
    # SIFRE GOSTERILMEZ: DATABASE_URL parcalanir, sadece SEMA + host
    url = d.get("DATABASE_URL") or d.get("SUPABASE_URL")
    if not url:
        print("DATABASE_URL yok")
        return
    m = re.match(r"^([a-z0-9+.\-]+)://([^:@/]+):([^@]*)@([^/]+)/(.+)$", url)
    if m:
        sema, user, sifre, host, yol = m.groups()
        print("\n--- HEDEF (sifre MASKELI)")
        print(f"    sema    = {sema}")
        print(f"    user    = {user}")
        print(f"    sifre   = {'*' * len(sifre)} (uzunluk {len(sifre)})")
        print(f"    host    = {host}")
        print(f"    db yolu = {yol}")
    else:
        print(f"  URL bicimi taninmadi (uzunluk {len(url)})")
        return

    print("\n" + "=" * 70)
    print("CANLI SUPABASE SORGUSU — SALT OKUNUR (SELECT only)")
    print("=" * 70)
    try:
        import psycopg2
    except ImportError:
        print("  psycopg2 yok")
        return
    try:
        con = psycopg2.connect(url, connect_timeout=25)
        cur = con.cursor()
        # DIKKAT: set_session(readonly=True) yerine sorgu bazinda
        # koruma kullanilir. readonly setme, supabase pooler'da
        # "cannot execute ... in a read-only transaction" verip
        # OTURUMU ASILDIK; sonraki SELECT'ler de komut oncesi
        # calismiyordu. Salt-okunurluk KURALLA saglanir: yalniz
        # SELECTInformation_schema sorgulari calistirilir.
        cur.execute("SELECT version()")
        print("  sunucu: " + cur.fetchone()[0][:60])
        cur.execute("SHOW transaction_read_only")
        ro = cur.fetchone()[0]
        print(f"  transaction_read_only: {ro}")
        cur.execute("""SELECT table_name FROM information_schema.tables
                       WHERE table_schema='public' ORDER BY 1""")
        tablolar = [r[0] for r in cur.fetchall()]
        print(f"\n  {len(tablolar)} tablo:")
        for tb in tablolar:
            cur.execute(f'SELECT COUNT(*) FROM "{tb}"')
            print(f"    {tb[:40]:42s} {cur.fetchone()[0]}")

        if "companies" in tablolar:
            # DIKKAT: osb_id UUID tipinde; COALESCE(osb_id,'(NULL)') text
            # cast'i basarisiz oldu. Once tipi sor, sonra dagilimi al.
            cur.execute("""SELECT data_type FROM information_schema.columns
                           WHERE table_name='companies' AND
                                 column_name='osb_id'""")
            tip = cur.fetchone()
            print(f"\n--- companies.osb_id tipi: "
                  f"{tip[0] if tip else '?'}")
            print("\n--- companies osb_id dagilimi")
            try:
                cur.execute("""SELECT osb_id, COUNT(*) FROM companies
                               GROUP BY 1 ORDER BY 2 DESC LIMIT 30""")
                for k, v in cur.fetchall():
                    print(f"    {str(k)[:34]:36s} {v}")
            except psycopg2.Error as e:
                print(f"    HATA {str(e)[:90]}")
                con.rollback()
                con.set_session(readonly=True, autocommit=True)
            # osbs tablosu ile birlestir
            if "osbs" in tablolar:
                try:
                    cur.execute("""SELECT o.osb_id, o.name, o.district,
                                          COUNT(c.company_id)
                                   FROM osbs o
                                   LEFT JOIN companies c
                                     ON c.osb_id = o.osb_id
                                   GROUP BY 1,2,3 ORDER BY 4 DESC""")
                    print("\n--- osbs tablosu + companies sayimi")
                    for oid, ad, ilce, adet in cur.fetchall():
                        print(f"    {str(oid)[:12]:14s} {str(ad)[:30]:32s} "
                              f"{str(ilce)[:16]:18s} {adet}")
                except psycopg2.Error as e:
                    print(f"    HATA {str(e)[:90]}")
                    con.rollback()
                    con.set_session(readonly=True, autocommit=True)
            print("\n--- companies doluluk")
            for kolon in ("legal_name", "primary_phone", "primary_email",
                          "website_domain", "adres", "vergi_no", "osb_id",
                          "company_id"):
                try:
                    cur.execute(
                        f"""SELECT COUNT(*) FROM companies
                            WHERE "{kolon}" IS NOT NULL
                              AND "{kolon}"::text <> ''""")
                    print(f"    {kolon:18s} {cur.fetchone()[0]}")
                except psycopg2.Error as e:
                    con.rollback()
                    con.set_session(readonly=True, autocommit=True)
                    print(f"    {kolon:18s} HATA {str(e)[:40]}")
        con.close()
    except Exception as e:
        print(f"  BAGLANTI HATASI: {type(e).__name__}: {str(e)[:200]}")


if __name__ == "__main__":
    main()
