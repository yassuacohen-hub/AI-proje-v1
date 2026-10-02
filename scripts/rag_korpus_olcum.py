"""VERI-RAG-KORPUS-01 kabul olcumu (canli DB, D-238).

Uc varsayimi olcer:
  1) metin uzunlugu ortancasi >= 80 karakter
  2) kisisel veri sizintisi = 0
  3) 200 karakteri gecen metin orani (chunk gerekli mi)

Ayrica kabul kriteri 3 icin iki ayri sayi yazar:
  TEKIL FIRMA (distinct company_id) ve KAYIT (satir).

Idempotent: yalnizca SELECT yapar, hicbir sey yazmaz.
"""

import os
import random
import re
import statistics
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import psycopg  # noqa: E402

from company_master.vector.service import (  # noqa: E402
    KORPUS_ALANLARI,
    firma_korpus_metni,
    kisisel_veri_tara,
    KorpusHatasi,
)

ORNEK = 50
BOLGE = 200

KOLON_SQL = ", ".join(KORPUS_ALANLARI)


def main() -> int:
    con = psycopg.connect(os.environ["DATABASE_URL"])
    toplam_kayit, toplam_firma = con.execute(
        "SELECT count(*), count(DISTINCT company_id) FROM companies"
    ).fetchone()
    print(f" companies kayit : {toplam_kayit}")
    print(f" companies firma : {toplam_firma}")

    cur = con.execute(
        f"SELECT company_id::text, {KOLON_SQL} FROM companies "
        "WHERE legal_name IS NOT NULL AND btrim(legal_name) <> ''"
    )
    satirlar = cur.fetchall()
    print(f" korpusa uygun satir: {len(satirlar)}")

    rng = random.Random(42)  # noqa: NPY002 - tekrarlanabilirlik icin sabit tohum
    ornek = rng.sample(satirlar, min(ORNEK, len(satirlar)))

    uzunluklar: list[int] = []
    sizinti: list[tuple[str, str, str]] = []
    uzun_sayisi = 0
    basarisiz: list[str] = []
    olusan_firma: set[str] = set()

    for satir in ornek:
        kimlik = satir[0]
        veri = dict(zip(KORPUS_ALANLARI, satir[1:]))
        try:
            metin, _kunye = firma_korpus_metni(veri)
        except KorpusHatasi as exc:
            basarisiz.append(f"{kimlik}: {exc}")
            continue
        uzunluklar.append(len(metin))
        olusan_firma.add(kimlik)
        if len(metin) > BOLGE:
            uzun_sayisi += 1
        for tur in kisisel_veri_tara(metin):
            sizinti.append((kimlik, tur, ""))

    ortanca = statistics.median(uzunluklar) if uzunluklar else 0
    print()
    print(" --- VARSAYIM 1: metin uzunlugu ---")
    print(f"   olcum sayisi  : {len(uzunluklar)}")
    print(f"   ORTANCA       : {ortanca:.1f} karakter (esik >= 80)")
    print(f"   en kisa/en uzun: {min(uzunluklar)} / {max(uzunluklar)}")

    print()
    print(" --- VARSAYIM 2: kisisel veri sizintisi ---")
    print(f"   taranan metin : {len(uzunluklar)}")
    print(f"   ESLESME       : {len(sizinti)} (esik = 0)")
    for kimlik, tur, eslesme in sizinti[:5]:
        print(f"     {kimlik} | {tur}")

    print()
    print(" --- VARSAYIM 3: chunk gerekli mi ---")
    print(f"   {BOLGE} karakteri gecen: {uzun_sayisi} / {len(uzunluklar)}")
    print(f"   karar: {'CHUNK YAPILIR' if uzun_sayisi else 'CHUNK YAPILMAZ (YAGNI)'}")

    print()
    print(" --- TOPLU URETIM (tum satirlar) ---")
    tum_uzunluk: list[int] = []
    tum_sizinti = 0
    tum_firma: set[str] = set()
    hata_sayaci: Counter[str] = Counter()
    ornek_hatalar: list[str] = []
    for satir in satirlar:
        kimlik = satir[0]
        veri = dict(zip(KORPUS_ALANLARI, satir[1:]))
        try:
            metin, _kunye = firma_korpus_metni(veri)
        except KorpusHatasi as exc:
            hata_sayaci[type(exc).__name__] += 1
            if len(ornek_hatalar) < 5:
                ornek_hatalar.append(f"{kimlik}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - sessiz dusurme yasak
            hata_sayaci[type(exc).__name__] += 1
            if len(ornek_hatalar) < 5:
                ornek_hatalar.append(f"{kimlik}: {type(exc).__name__}: {exc}")
            continue
        tum_uzunluk.append(len(metin))
        tum_firma.add(kimlik)
        if kisisel_veri_tara(metin):
            tum_sizinti += 1

    print(f"   uretilen kayit      : {len(tum_uzunluk)}")
    print(f"   TEKIL FIRMA         : {len(tum_firma)}")
    print(f"   basarisiz kayit     : {sum(hata_sayaci.values())}")
    for tur, adet in hata_sayaci.most_common():
        print(f"     {tur}: {adet}")
    for h in ornek_hatalar:
        print(f"     ornek: {h}")
    print(f"   sizinti tasiyan kayit: {tum_sizinti}")
    if tum_uzunluk:
        print(
            f"   tam korpus ortanca   : {statistics.median(tum_uzunluk):.1f}"
            f" | {BOLGE} ustu: "
            f"{sum(1 for u in tum_uzunluk if u > BOLGE)}"
        )

    kon = psycopg.connect(os.environ["DATABASE_URL"])
    kon.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
