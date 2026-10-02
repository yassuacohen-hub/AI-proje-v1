"""VERI-TSG-ESLEME-CASE-01 — canlı geri doldurma ölçümü (salt okuma).

Bulgu: eşleme düzeltmesi **koda** girdi ama `company_events` tablosundaki
407 kayıt **eski (hatalı) eşlemeyle** yazılmış durumda. `tsg_yazici`
`source_guid`'i mevcut sayıp yeni kayıtları atladığı için (ölçüm: 407/407)
yeniden koşmak hiçbir şeyi düzeltmez — D-261 dersi: "kod yazıldı" ile
"kod koşturuldu ve veritabanına yansıdı" ayrı iki olaydır.

Bu betik **yalnız ölçer**. Hiçbir şey yazmaz (D-243: prova diske/DB'ye yazmaz).
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)

from skills.services.ticaret_sicili_kanit import olay_esle  # noqa: E402

#: Kanıt dosyasından kanonik `source_guid` üreten aynı işlev (ikiz yazılmaz).
from src.company_master.etl.tsg_yazici import _source_guid_olustur  # noqa: E402


def main() -> int:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(KOK, ".env"))
    import psycopg

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("HATA: DATABASE_URL yok")
        return 1

    # --- 1) Kanıttan beklenen eşleme ---
    from src.company_master.etl.tsg_yazici import kanit_dosyalarini_oku

    beklenen: dict[str, tuple] = {}
    for k in kanit_dosyalarini_oku():
        guid = _source_guid_olustur(k)
        et, dr = olay_esle(k.get("il_turu"))
        beklenen[guid] = (et, dr, k.get("il_turu"))

    print(f"Kanittan hesaplanan kayit: {len(beklenen)}")
    etiketli = {g: v for g, v in beklenen.items() if v[0]}
    print(f"  bunlarin etiketlenen: {len(etiketli)}")
    print(f"  etiketlenmeyen (il_turu bos): {len(beklenen) - len(etiketli)}")

    # --- 2) Canlı DB'deki durum ---
    with psycopg.connect(dsn, connect_timeout=20) as bag:
        with bag.cursor() as cur:
            cur.execute(
                "select source_guid, event_type, direction from public.company_events "
                "where source_guid is not null"
            )
            canli = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
            cur.execute(
                "select count(*) from public.company_events where event_type is null"
            )
            toplam_null = cur.fetchone()[0]
            cur.execute("select count(*) from public.company_events")
            toplam = cur.fetchone()[0]

    print(f"\nCanli company_events: {toplam} satir, event_type IS NULL: {toplam_null}")
    print(f"Canli source_guid sayisi: {len(canli)}")

    ortak = set(canli) & set(beklenen)
    print(f"Kanit ile eslesen source_guid: {len(ortak)}")

    # --- 3) Düzeltilecek satırlar ---
    duzeltilecek = []
    for g in sorted(ortak):
        canli_et, canli_dr = canli[g]
        bek_et, bek_dr, tur = beklenen[g]
        if canli_et != bek_et or canli_dr != bek_dr:
            duzeltilecek.append((g, canli_et, canli_dr, bek_et, bek_dr, tur))
    zaten_dogru = len(ortak) - len(duzeltilecek)

    print(f"\nZaten dogru: {zaten_dogru}")
    print(f"DUZELTILECEK: {len(duzeltilecek)}")
    for g, c_et, c_dr, b_et, b_dr, tur in duzeltilecek[:25]:
        t = (tur or "")[:44]
        print(f"  {g[:44]:44s} {str(c_et):22s}->{b_et:22s} {c_dr}->{b_dr}  | {t}")

    # --- 4) Kanıtta var ama DB'de olmayan (yeni yazılacak) ---
    yeni = set(beklenen) - set(canli)
    print(f"\nKanitta var, DB'de YOK (yeni yazilacak): {len(yeni)}")
    etiketli_yeni = [g for g in yeni if beklenen[g][0]]
    print(f"  bunlarin etiketli olani: {len(etiketli_yeni)}")

    # --- 5) DB'de var ama kanıtta yok ---
    kanitsiz = set(canli) - set(beklenen)
    print(f"DB'de var, kanitta YOK: {len(kanitsiz)}")

    # --- 6) Kanıt dosyası (D-244) ---
    yedek = os.path.join(KOK, "yedekler", "company_events_esleme_20261002.jsonl")
    os.makedirs(os.path.dirname(yedek), exist_ok=True)
    with open(yedek, "w", encoding="utf-8") as f:
        for g, c_et, c_dr, b_et, b_dr, tur in duzeltilecek:
            f.write(json.dumps({
                "source_guid": g,
                "event_type_onceki": c_et,
                "direction_onceki": c_dr,
                "event_type_yeni": b_et,
                "direction_yeni": b_dr,
                "il_turu": tur,
            }, ensure_ascii=False) + "\n")
    print(f"\nYedek kanit (D-244): {yedek} ({len(duzeltilecek)} satir)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
