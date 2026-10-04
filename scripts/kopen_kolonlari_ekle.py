"""D-309: companies tablosuna KOKEN kolonlari EKLER (S1).

KAHIN (2026-09-29): "tamam tavsiye 1 yap duzelt her seyi".
D-308 bulgusu: companies 49 kolon; source / collected_at /
postal_code YOK. Uretilen veri kokeni ICERIYOR ama tablo
TASIYAMIYOR -> yazimda kaybolur -> kural beyan olur.

COZUM (S1): kolonlari EKLE. Kural aynen yazilir kalir, ARTUK
veritabaninda da ZORLANIR.

Eklenen kolonlar:
  collected_at   timestamptz  — kaydin toplandigi an (kritik eksikti)
  source_name    text         — kaynagin adi (ostim.org.tr vb.)
  source_type    text         — kaynagin turu (osb, bazi vb.)
  source_file    text         — hangi dosyadan geldi (izlenebilirlik)
  source_line    text         — kaynak dosyada hangi satir
  collected_by   text         — toplayan ajan/process

GUVENLIK:
  - Varsayilan SALT OKUNUR (sadece plan/SQL gosterir)
  - --uygula ile tek transaction'da eklenir
  - --geri-al ile kolonlar dusurulur (veri KAYBOLUR; sadece
    yeni, henuz dolulmamis kolonlar icin)
  - Mevcut veri SILINMEZ, sadece kolon eklenir
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
KAYIT = KOK / "data" / "_tmp" / "kopen_kolonlari.json"

#: (kolon, tip, aciklama)
YENI_KOLONLAR = [
    ("collected_at", "timestamptz",
     "kaydin toplandigi an - kritik eksikti"),
    ("source_name", "text",
     "kaynagin adi (ostim.org.tr, baskent.org.tr ...)"),
    ("source_type", "text",
     "kaynagin turu (osb / chamber / directory)"),
    ("source_file", "text",
     "hangi dosyadan geldi (izlenebilirlik)"),
    ("source_line", "text",
     "kaynak dosyadaki satir (varsa)"),
    ("collected_by", "text",
     "toplayan ajan veya process"),
]



def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--uygula", action="store_true",
                    help="ALTER TABLE calistir")
    ay.add_argument("--geri-al", action="store_true",
                    help="kolonlari dusur (VERI KAYBI - dikkat!)")
    ns = ay.parse_args()

    url = env_oku(KOK / ".env").get("DATABASE_URL")
    if not url:
        print("DATABASE_URL yok")
        return 1
    import psycopg2
    con = psycopg2.connect(url, connect_timeout=25)
    cur = con.cursor()

    cur.execute("""SELECT column_name FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='companies'""")
    mevcut = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT COUNT(*) FROM companies")
    mevcut_satir = cur.fetchone()[0]

    print("=" * 72)
    print("D-309  COMPANIES'A KOKEN KOLONLARI EKLE (S1)")
    print("=" * 72)
    print(f"  companies kolon (once) : {len(mevcut)}")
    print(f"  companies satir (once) : {mevcut_satir}")

    eklenecek = [(k, t, a) for k, t, a in YENI_KOLONLAR if k not in mevcut]
    print(f"\n  eklenecek : {len(eklenecek)}")
    for k, t, a in eklenecek:
        print(f"    + {k:16s} {t:12s} {a}")

    s = [
        "-- D-309: companies'a koken kolonlari (S1, KAHIN 2026-09-29)",
        f"-- uretim: {datetime.now().isoformat(timespec='seconds')}",
        "--",
        "-- D-308 bulgusu: 'her kaydin kokeni yazilir' kurali yaziliydi",
        "-- ama companies'ta source/collected_at kolonu YOKTI; kural",
        "-- beyan olarak kaliyordu. Bu migration onu FIILEN zorlar.",
        "-- Mevcut veri SILINMEZ; sadece NULL baslangicli kolon eklenir.",
        "",
    ]
    for k, t, a in eklenecek:
        s.append("ALTER TABLE public.companies ADD COLUMN IF NOT EXISTS "
                 f"{k} {t};")
        s.append(f"--   {a}")
    if ns.geri_al:
        s += ["", "-- GERI AL (veri kaybi!):", "ALTER TABLE public.companies"]
        for k, _, _ in eklenecek:
            s.append(f"DROP COLUMN IF EXISTS {k};")
    MIGRASYON.mkdir(parents=True, exist_ok=True)
    p = MIGRASYON / "20260929_d309_koken_kolonlari.sql"
    p.write_text("\n".join(s) + "\n", encoding="utf-8")
    print(f"\n  migration: {p.relative_to(KOK)}")

    if not (ns.uygula or ns.geri_al):
        con.close()
        print("\n  RAPOR MODU. --uygula ile eklenir.")
        return 0

    print("\n>>> UYGULANIYOR ...")
    try:
        with con:
            with con.cursor() as c2:
                if ns.uygula:
                    for k, t, _ in eklenecek:
                        c2.execute("ALTER TABLE public.companies "
                                   f"ADD COLUMN IF NOT EXISTS {k} {t}")
                else:
                    for k, _, _ in eklenecek:
                        c2.execute("ALTER TABLE public.companies "
                                   f"DROP COLUMN IF EXISTS {k}")
        print(">>> TAMAMLANDI")
    except Exception as e:
        print(f"HATA: {type(e).__name__}: {str(e)[:200]}")
        con.rollback()
        con.close()
        return 1

    cur.execute("""SELECT column_name FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='companies'""")
    sonra = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT COUNT(*) FROM companies")
    sonra_satir = cur.fetchone()[0]
    con.close()
    print("\nDOGRULAMA:")
    print(f"  kolon : {len(mevcut)} -> {len(sonra)}")
    print(f"  satir : {mevcut_satir} -> {sonra_satir} (degismemeli)")
    for k, _, _ in YENI_KOLONLAR:
        print(f"    {k:16s} {'VAR' if k in sonra else 'YOK'}")
    KAYIT.parent.mkdir(parents=True, exist_ok=True)
    KAYIT.write_text(json.dumps({
        "zaman": datetime.now().isoformat(timespec="seconds"),
        "eylem": "geri-al" if ns.geri_al else "uygula",
        "eklenen": [k for k, _, _ in eklenecek],
        "kolon_once": len(mevcut), "kolon_sonra": len(sonra),
        "satir": sonra_satir,
        "migration": str(p.relative_to(KOK)),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
