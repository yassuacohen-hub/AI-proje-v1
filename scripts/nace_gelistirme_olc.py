# -*- coding: utf-8 -*-
"""NACE gelistirme potansiyeli — KAHIN sorusu (2026-09-30):

"Bizdeki NACE kodu cok az; lonca.gov.tr bir kaynak olarak NACE
eslestirme yapabilir mi?"

Bu dosya SADECE olcer:
  1) Bizim verimizde NACE dolulugu (Supabase, salt okunur)
  2) lonca.gov.tr NACE sozlugunun bize ne verebilecegi
  3) Iki tarafin kesisimi — yani gercekten kacak firma eslestirilebilir

Supabase'e YAZMA YOK. Cevap yoksa 'bilinmiyor' yazilir (D-217).
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(KOK / ".env", override=True)

CIKTI = KOK / "data" / "pilots" / "VERI-LONCA-FIRMA-01"
CIKTI.mkdir(parents=True, exist_ok=True)

LONCA_KODLAR = CIKTI.parent / "VERI-TOBB2B-KESISIM-01" / "lonca_nace_kodlari.json"
SOZLUK = KOK / "data" / "sektor" / "sektor_sozluk.json"


def bizim_nace() -> dict:
    """companies tablosunda NACE dolulugu (SALT OKUNUR)."""
    import psycopg
    dsn = os.environ["DATABASE_URL"]
    with psycopg.connect(dsn) as cx:
        with cx.cursor() as c:
            c.execute("""
                SELECT count(*) AS toplam,
                       count(*) FILTER (WHERE nace_code IS NOT NULL
                                          AND nace_code <> '') AS nace_dolu,
                       count(*) FILTER (WHERE nace_source IS NOT NULL
                                          AND nace_source <> '') AS kaynak_dolu,
                       count(DISTINCT nace_code) FILTER (
                           WHERE nace_code IS NOT NULL AND nace_code <> '') AS cesit
                FROM companies
            """)
            t, d, k, c = c.fetchone()
    return {"toplam": t, "nace_dolu": d, "nace_dolu_yuzde": round(100 * d / t, 3) if t else 0,
            "nace_cesit": c, "kaynak_dolu": k}


def bizim_unvanlar(limit: int = 40) -> list[str]:
    import psycopg
    dsn = os.environ["DATABASE_URL"]
    with psycopg.connect(dsn) as cx:
        with cx.cursor() as c:
            c.execute("SELECT legal_name FROM companies "
                      "WHERE legal_name IS NOT NULL AND legal_name <> '' "
                      "ORDER BY random() LIMIT %s", (limit,))
            return [r[0] for r in c.fetchall()]


def lonca_sozlugu() -> dict:
    d = json.loads(LONCA_KODLAR.read_text(encoding="utf-8"))
    return {"kod": d["kod_sayisi"], "bolum": len(d["bolumler"]),
            "kodlar": d["kodlar"], "bolumler": d["bolumler"]}


def bizim_sozluk() -> dict:
    d = json.loads(SOZLUK.read_text(encoding="utf-8"))
    ipuclu = [x for x in d if x.get("nace_ipucu")]
    return {"toplam": len(d), "nace_ipucu_dolu": len(ipuclu),
            "yuzde": round(100 * len(ipuclu) / len(d), 1) if d else 0}


if __name__ == "__main__":
    print("== 1) BİZİM VERİMİZDE NACE ==")
    b = bizim_nace()
    for k, v in b.items():
        print("   %-20s %s" % (k, v))

    print("\n== 2) BİZİM SEKTÖR SÖZLÜĞÜ ==")
    s = bizim_sozluk()
    for k, v in s.items():
        print("   %-20s %s" % (k, v))

    print("\n== 3) LONCA NACE SÖZLÜĞÜ ==")
    l = lonca_sozlugu()
    print("   kod:", l["kod"], "| bolum:", l["bolum"])
    print("   bolumler:", " ".join(l["bolumler"]))

    print("\n== 4) ASIL SORU: firmaya NACE nasil atanir? ==")
    print("   lonca /FirmaBilgisi 7 alan veriyor (unvan,il,adres,tel,faks,mail,web)")
    print("   + urun katalogu (9 satir ornek).")
    print("   AMA: sayfada NACE kodu YOK. Urun katalogu URETIM URUNLERI,")
    print("        NACE degil. Yani dogrudan NACE atanamaz.")
    print("   Tek yol: urun adi -> NACE eslestirmesi (metin eslestirme).")

    print("\n== 5) KESİŞİM ÖLÇÜMÜ: unvan eşleşmesi yapılabilir mi? ==")
    ornekler = bizim_unvanlar(12)
    print("   ornek unvanlar (%d):" % len(ornekler))
    for u in ornekler:
        print("     ", u[:64])
    print("   NOT: unvan -> NACE, ancak lonca'da unvan aramasi POST /Ara ile")
    print("   yapiliyor ve POST WAF'ta 3/3 reddediliyor. Id uretimi yolu")
    print("   olcummedi -> ARAMA KAPALI.")

    if "--nace" not in sys.argv:
        raise SystemExit(0)

    print("\n== 6) NACE KOD DAGILIMI (canli) ==")
    import psycopg
    with psycopg.connect(os.environ["DATABASE_URL"]) as cx:
        with cx.cursor() as c:
            c.execute("""SELECT nace_code, count(*) AS n FROM companies
                         WHERE nace_code IS NOT NULL AND nace_code <> ''
                         GROUP BY 1 ORDER BY n DESC LIMIT 15""")
            for k, n in c.fetchall():
                print("   %-12s %d" % (k, n))

            print("\n== 7) NACE KAYNAKLARI (nace_source) ==")
            c.execute("""SELECT nace_source, count(*) FROM companies
                         GROUP BY 1 ORDER BY 2 DESC LIMIT 8""")
            for a, n in c.fetchall():
                print("   %-30s %d" % (a, n))

            print("\n== 8) LONCA SOZLUĞU ILE KESISIM ==")
            c.execute("""SELECT count(DISTINCT c.nace_code)
                         FROM companies c
                         WHERE c.nace_code IS NOT NULL
                           AND split_part(c.nace_code, '.', 1) = ANY(%s)""",
                      (l["bolumler"],))
            kesisim = c.fetchone()[0]
            print("   bizim kullandigimiz NACE bolumlerinin lonca kapsaminda olan sayisi:",
                  kesisim)
            print("   lonca bolumleri:", " ".join(l["bolumler"]))

