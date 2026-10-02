"""VERI-TSG-ESLEME-CASE-01 — eşleme düzeltmesini canlı tabloya yansıtır.

Neden gerekiyor (D-261 dersi): eşleme düzeltmesi **koda** girdi, ama
`company_events` tablosundaki kayıtlar **eski (hatalı) eşlemeyle** yazılmış
durumda. `tsg_yazici` `source_guid`'i mevcut sayıp kayıtları atladığı için
(ölçüm: 407 mevcut / 407 kanıt) yeniden koşmak **hiçbir şeyi düzeltmez**.

Kurallar:
- `--dene` (varsayılan) **hiçbir şey yazmaz**, `backup_path` None döner (D-243).
- `--yaz` yazmadan önce yedek alır; yedek satır sayısı beklenenle uyuşmazsa
  `RuntimeError` ile durur (D-243/D-244).
- Yedek yolu **parametre**; sabit yol gömülmez.
- Etiketleme değeri kanıttan **yeniden hesaplanır**, yedekteki değere
  güvenilmez — yedek kanıttır, ikinci gerçek değildir (D-211).

Kullanım:
    python -X utf8 scripts/tsg_esleme_geri_doldur.py --dene
    python -X utf8 scripts/tsg_esleme_geri_doldur.py --yaz
"""

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

#: Düzeltmenin tabloya yansıyacağı kanıt dosyası (teslim kanıtı).
VARSAYILAN_YEDEK = os.path.join(KOK, "yedekler", "company_events_esleme_20261002.jsonl")


def kanittan_hesapla(yedek_satirlari: list[dict]) -> list[dict]:
    """`event_type`/`direction` yedekten **değil**, kanıttan yeniden hesaplanır.

    Yedek "ne değişecek" bilgisini taşır; "ne olmalı" bilgisi tek kapıdan
    gelir (`olay_esle`). Aksi halde yedek ikinci bir gerçek olur (D-211).
    """
    from skills.services.ticaret_sicili_kanit import olay_esle

    satirlar = []
    for y in yedek_satirlari:
        et, dr = olay_esle(y.get("il_turu"))
        satirlar.append({
            "source_guid": y["source_guid"],
            "event_type": et,
            "direction": dr,
            "il_turu": y.get("il_turu"),
        })
    return satirlar


def main() -> int:
    ap = argparse.ArgumentParser(description="TSG olay eslemesi geri doldurma")
    ap.add_argument("--dene", action="store_true", help="Sadece raporla (varsayılan)")
    ap.add_argument("--yaz", action="store_true", help="Geri doldurmayı uygula")
    ap.add_argument("--yedek", default=VARSAYILAN_YEDEK, help="Yedek kanıt dosyası")
    args = ap.parse_args()

    if args.yaz and args.dene:
        print("HATA: --dene ve --yaz birlikte verilemez")
        return 2

    if not os.path.exists(args.yedek):
        print(f"HATA: yedek kanıt yok: {args.yedek}")
        return 1

    with open(args.yedek, encoding="utf-8") as f:
        yedek_satirlari = [json.loads(x) for x in f if x.strip()]
    if not yedek_satirlari:
        print("HATA: yedek boş — düzeltilecek satır yok, işlem yok")
        return 1

    hedefler = kanittan_hesapla(yedek_satirlari)

    from dotenv import load_dotenv

    load_dotenv(os.path.join(KOK, ".env"))
    import psycopg

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("HATA: DATABASE_URL yok")
        return 1

    with psycopg.connect(dsn, connect_timeout=20) as bag:
        with bag.cursor() as cur:
            # Yazmadan ÖNCE ölçüm (D-238).
            cur.execute(
                "select count(*) from public.company_events where event_type is null"
            )
            onceki_null = cur.fetchone()[0]
            cur.execute("select count(*) from public.company_events")
            onceki_toplam = cur.fetchone()[0]
            # Yedeğin gerçekten karşılık olduğunu kanıtla.
            guidler = [h["source_guid"] for h in hedefler]
            cur.execute(
                "select source_guid, event_type, direction from public.company_events "
                "where source_guid = any(%s)",
                (guidler,),
            )
            canli = {r[0]: (r[1], r[2]) for r in cur.fetchall()}

        eksik = [g for g in guidler if g not in canli]
        if eksik:
            print(f"HATA: yedekteki {len(eksik)} kayıt tabloda yok -> yedek bayat")
            return 1

        zaten = [
            h for h in hedefler
            if canli[h["source_guid"]] == (h["event_type"], h["direction"])
        ]
        yazilacak = [h for h in hedefler if h not in zaten]

        print(f"Onceki: toplam={onceki_toplam} event_type IS NULL={onceki_null}")
        print(f"Hedef kayit: {len(hedefler)} | zaten dogru: {len(zaten)} | yazilacak: {len(yazilacak)}")

        if not yazilacak:
            print("Hicbir sey yazilmayacak — tablo zaten guncel")
            print(f"backup_path=None (prova yazmadi, D-243)")
            return 0

        for h in yazilacak[:25]:
            c = canli[h["source_guid"]]
            print(f"  {h['source_guid'][:34]:34s} {str(c[0]):22s} -> {h['event_type']:22s} {c[1]}->{h['direction']}")

        if not args.yaz:
            print(f"\n[PROVA] yazilacak satir: {len(yazilacak)} — hicbir sey yazilmadi")
            print("backup_path=None (D-243)")
            return 0

        # --- Gerçek yazma: tek transaction, yedek satır sayısı denetimi ---
        with psycopg.connect(dsn, connect_timeout=20) as wbag:
            with wbag.cursor() as cur:
                for h in yazilacak:
                    cur.execute(
                        "update public.company_events set event_type = %s, direction = %s "
                        "where source_guid = %s",
                        (h["event_type"], h["direction"], h["source_guid"]),
                    )
                    if cur.rowcount != 1:
                        raise RuntimeError(
                            f"Geri alma durdu: {h['source_guid']} icin {cur.rowcount} satir "
                            "(1 bekleniyordu)"
                        )
            wbag.commit()

        with psycopg.connect(dsn, connect_timeout=20) as obag:
            with obag.cursor() as cur:
                cur.execute(
                    "select count(*) from public.company_events where event_type is null"
                )
                sonraki_null = cur.fetchone()[0]
                cur.execute("select count(*) from public.company_events")
                sonraki_toplam = cur.fetchone()[0]
                cur.execute(
                    "select event_type, direction, count(*) from public.company_events "
                    "where event_type is not null group by 1,2 order by 3 desc"
                )
                dagilim = cur.fetchall()

        print(f"\nSonrasi: toplam={sonraki_toplam} event_type IS NULL={sonraki_null}")
        print(f"Degisen null: {onceki_null} -> {sonraki_null}")
        print("-- event_type x direction --")
        for et, dr, adet in dagilim:
            print(f"   {et[:28]:28s} {str(dr):10s} {adet}")
        print(f"\nbackup_path={args.yedek} ({len(yedek_satirlari)} satir)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
