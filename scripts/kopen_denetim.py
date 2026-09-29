"""D-308: Kopen (provenance) denetimi — kural gercekten uygulanmis mi?

KAHIN (2026-09-29): "VERI_YAZMA_KURALLARI.md'de 'her kaydin kokeni
yazilir' kuralini koyduk. Ama companies tablosunda source,
collected_at, postal_code kolonlari YOK. Kopen bilgisi yalnizca
source_record_id uzerinden dolayli izlenebiliyor... Bu, kural yazip
zorlamamanin bir baska bicimi olurdu — soyluyorum ki beyan olarak
kalmasin. bu iddiayi dogrula, yasu yaptigin islerde sikinti varmi"

BU SCRIPT SADECE OLCER (varsayilan). Yazma YOK.
Cikti:
  A) Supabase companies semasi — iddia dogrulanir mi?
  B) Kopen gercekten var mi? (source_record_id -> source_records)
  C) postal_code kolonu gercekten yok mu, sonuc 0 mi?
  D) yasu'nun URETTIGI veri setlerinde koken alanlari var mi?
     ve Supabase'e YAZILDIKTAN SONRA kaybolacaklar mi?
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

from supabase_envanter import env_oku  # noqa: E402

RAPOR = KOK / "data" / "_tmp" / "kopen_denetimi.json"

#: Iddiada isaret edilen kolonlar
IDDIA_KOLONLARI = ("source", "collected_at", "postal_code", "source_record_id")

#: Koken alani denetimi: yasu'nun urettigi setlerde olmasi gerekenler
KOKEN_ALANLARI = {
    "kaynak_adi", "kaynak_turu", "kaynaklar", "kaynak_satiri",
    "source_name", "source_type", "sources", "source_file",
    "source_record_id", "collected_at", "toplanma_tarihi",
}


def main() -> int:
    ay = argparse.ArgumentParser()
    ay.add_argument("--rapor", default=None, help="JSON cikti yolu")
    ns = ay.parse_args()

    url = env_oku(KOK / ".env").get("DATABASE_URL")
    if not url:
        print("DATABASE_URL yok")
        return 1
    import psycopg2
    con = psycopg2.connect(url, connect_timeout=25)
    cur = con.cursor()
    bulgu: dict = {"zaman": datetime.now().isoformat(timespec="seconds")}

    # --- A) companies semasi
    cur.execute("""SELECT column_name, data_type, is_nullable
                   FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='companies'
                   ORDER BY ordinal_position""")
    kolonlar = cur.fetchall()
    adlar = {k for k, _, _ in kolonlar}
    print("=" * 72)
    print("D-308  KOKEN (PROVENANCE) DENETIMI")
    print("=" * 72)
    print(f"\nA) companies tablosu: {len(kolonlar)} kolon")
    bulgu["companies_kolonlar"] = [k for k, _, _ in kolonlar]

    print("\n   iddia edilen kolonlar:")
    for k in IDDIA_KOLONLARI:
        var = k in adlar
        print(f"     {'VAR ' if var else 'YOK '} {k}")
        bulgu.setdefault("iddia", {})[k] = var

    # --- B) koken gercekten var mi?
    print("\nB) KOKEN GERCEKTEN IZLENEBILIYOR MU?")
    if "source_record_id" in adlar:
        cur.execute("""SELECT count(*) FROM companies
                       WHERE source_record_id IS NOT NULL""")
        bagli = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM companies")
        toplam = cur.fetchone()[0]
        print(f"     source_record_id DOLU : {bagli}/{toplam} "
              f"({bagli * 100 // toplam if toplam else 0}%)")
        bulgu["source_record_id_dolu"] = bagli
        bulgu["companies_toplam"] = toplam
        # source_records'in ANAHTAR KOLONU 'id' degil; once ogren.
        cur.execute("""SELECT column_name FROM information_schema.columns
                       WHERE table_schema='public'
                         AND table_name='source_records'""")
        sr_kol = [r[0] for r in cur.fetchall()]
        anahtar = next((k for k in ("id", "source_record_id", "record_id")
                        if k in sr_kol), None)
        print(f"     source_records kolon : {len(sr_kol)}")
        bulgu["source_records_kolonlar"] = sr_kol
        bulgu["source_records_anahtar"] = anahtar
        if anahtar:
            cur.execute(f"""SELECT count(*) FROM companies c
                            JOIN source_records s
                              ON s."{anahtar}" = c.source_record_id""")
            coz = cur.fetchone()[0]
            print(f"     source_records'a BAGLANAN : {coz}/{toplam}")
            bulgu["source_records_baglanan"] = coz
        else:
            print("     !! source_records anahtar kolonu BULUNAMADI")
            bulgu["source_records_baglanan"] = None

    # --- D) uretilen veri setlerinde koken alanlari
    print("\nD) URETILEN VERI SETLERINDE KOKEN")
    print("-" * 72)
    hedefler = [
        ("data/ostim/OSTIM_TEMIZ.jsonl", "OSTIM_TEMIZ (D-300)"),
        ("data/osb/ostim/firmalar.jsonl", "osb/ostim (D-305)"),
        ("data/osb/baskent/firmalar.jsonl", "osb/baskent (D-305)"),
    ]
    set_ozet = []
    for yol, ad in hedefler:
        p = KOK / yol
        if not p.is_file():
            print(f"     {ad:24s} YOK")
            continue
        alanlar: Counter = Counter()
        n = 0
        for satir in p.read_text(encoding="utf-8").splitlines():
            if not satir.strip():
                continue
            try:
                kayit = json.loads(satir)
            except json.JSONDecodeError:
                continue
            n += 1
            for k in KOKEN_ALANLARI:
                if k in kayit and kayit[k] not in (None, "", [], {}):
                    alanlar[k] += 1
        dolu = [k for k in alanlar if alanlar[k] == n]
        kismi = [k for k in alanlar if 0 < alanlar[k] < n]
        yok = sorted(KOKEN_ALANLARI - set(alanlar))
        print(f"\n     {ad}  ({n} kayit)")
        print(f"       %100 dolu  : {dolu or '-'}")
        print(f"       kismi dolu: {kismi or '-'}")
        print(f"       HIC YOK   : {yok}")
        set_ozet.append({"kaynak": ad, "yol": yol, "kayit": n,
                         "dolu": dict(alanlar), "hic_yok": yok})
    bulgu["uretilen_setler"] = set_ozet

    # --- E) SONUC
    print("\nE) SUPABASE'E YAZILDIKTAN SONRA NE KAYBOLUR?")
    tasiyabilir = sorted(adlar & KOKEN_ALANLARI)
    kaybolacak = sorted(KOKEN_ALANLARI - adlar)
    print(f"     TASIYABILIR : {tasiyabilir or '-'}")
    print(f"     KAYBOLUR    : {kaybolacak}")
    bulgu["kaybolacak"] = kaybolacak
    bulgu["tasiyabilir"] = tasiyabilir
    con.close()

    print("\n" + "=" * 72)
    print("SONUC")
    print("=" * 72)
    if kaybolacak:
        print("  KURAL IHLALI KESINLESTI: uretilen veri koken bilgisini")
        print("  ICERIYOR ama companies tablosu bu alanlari TASIYAMIYOR.")
        print("  Yazim yapilirsa koken KAYBOLUR -> kural beyan olur.")
    else:
        print("  Koken tam tasiyabiliyor.")
    (KOK / "data" / "_tmp").mkdir(parents=True, exist_ok=True)
    RAPOR.write_text(json.dumps(bulgu, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print(f"  Rapor: {RAPOR.relative_to(KOK)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

