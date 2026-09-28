# -*- coding: utf-8 -*-
"""Goc defteri dogrulayici ve esitleyici (GOC-DEFTER-01, D-251/3).

Defter `public.schema_migrations` semanin tek anlaticisidir. Bu arac
diskteki goc dosyalarini ayristirir, her birinin semadaki izini arar ve
defteri gercekle esitler.

    python scripts/goc_defteri.py             # sadece rapor (yazmaz)
    python scripts/goc_defteri.py --esitle    # izi bulunanlari deftere yazar
    python scripts/goc_defteri.py --uygula 0026_x.sql   # goc calistir + deftere yaz

Idempotent (D-251/5): ikinci calisma hicbir sey degistirmez.
D-251/4: DDL yalniz goc dosyasindan calisir; bu arac elle SQL kabul etmez.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, "src")

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402

GOC_DIZINI = Path("src/company_master/schema/migrations")

RE_TABLO = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.]+)", re.I)
RE_KOLON = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?([\w.]+)\s+ADD\s+COLUMN\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?([\w]+)",
    re.I,
)
RE_INDEKS = re.compile(
    r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:CONCURRENTLY\s+)?"
    r"(?:IF\s+NOT\s+EXISTS\s+)?([\w]+)",
    re.I,
)
# 0024 gibi "DEFAULT dusur" gocleri kolon/tablo uretmez; izi default'un
# yoklugudur. Ayristirilmazsa goc IZSIZ kalir = defterdeki kayit dogrulanamaz.
RE_ALTER = re.compile(r"ALTER\s+TABLE\s+(?:ONLY\s+)?([\w.]+)(.*?);", re.I | re.S)
RE_DEFAULT_DUSUR = re.compile(r"ALTER\s+COLUMN\s+([\w]+)\s+DROP\s+DEFAULT", re.I)
# Sonraki bir goc bu gocun izini degistirdiyse (RENAME/DROP) burada bildirilir.
# D-245: "iz yok" demek yetmez, neden yok yazili olmali.
RE_USTUNDEN = re.compile(r"ustunden-gecen:\s*([\w.]+)", re.I)


def _sqlsiz(metin: str) -> str:
    """Yorum satirlarini duser; yorumdaki ornek DDL iz sayilmasin."""
    metin = re.sub(r"/\*.*?\*/", " ", metin, flags=re.S)
    return "\n".join(s.split("--")[0] for s in metin.splitlines())


def _ad(x: str) -> str:
    return x.split(".")[-1].lower()


def goc_izleri() -> dict[str, dict[str, set]]:
    """Her goc dosyasi icin semada aranacak izler."""
    izler = {}
    for yol in sorted(GOC_DIZINI.glob("[0-9][0-9][0-9][0-9]_*.sql")):
        ham = yol.read_text(encoding="utf-8", errors="ignore")
        s = _sqlsiz(ham)
        varsayilansiz = set()
        for tablo, govde in RE_ALTER.findall(s):
            for kol in RE_DEFAULT_DUSUR.findall(govde):
                varsayilansiz.add((_ad(tablo), kol.lower()))
        ustunden = RE_USTUNDEN.search(ham)
        izler[yol.name] = {
            "tablo": {_ad(t) for t in RE_TABLO.findall(s)},
            "kolon": {(_ad(t), k.lower()) for t, k in RE_KOLON.findall(s)},
            "indeks": {i.lower() for i in RE_INDEKS.findall(s)},
            "varsayilansiz": varsayilansiz,
            "ustunden": ustunden.group(1) if ustunden else None,
        }
    return izler


def sema_durumu(conn) -> dict[str, set]:
    """Semanin tamami tek turda okunur (D-249: iz basina sorgu yok)."""
    return {
        "tablo": {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public'"
                )
            )
        },
        "kolon": {
            (r[0], r[1])
            for r in conn.execute(
                text(
                    "SELECT table_name, column_name FROM information_schema.columns "
                    "WHERE table_schema='public'"
                )
            )
        },
        "indeks": {
            r[0]
            for r in conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE schemaname='public'")
            )
        },
        # DEFAULT'u dusurulmus kolonlar (0024 tipi goclerin izi)
        "varsayilansiz": {
            (r[0], r[1])
            for r in conn.execute(
                text(
                    "SELECT table_name, column_name FROM information_schema.columns "
                    "WHERE table_schema='public' AND column_default IS NULL"
                )
            )
        },
    }


def degerlendir(izler, sema):
    """Her goc icin (durum, eksik_izler).

    TAM     = butun izleri semada duruyor
    EKSIK   = izlerinin bir kismi yok -> goc uygulanmamis olabilir
    ESKIMIS = sonraki bir goc uzerinden gecti, izi aranmaz (dosyada yazili)
    IZSIZ   = ayristirilabilir iz yok -> arac dogrulayamaz, elle bakilir
    """
    sonuc = {}
    for dosya, iz in izler.items():
        if iz["ustunden"]:
            sonuc[dosya] = ("ESKIMIS", [f"ustunden gecen: {iz['ustunden']}"])
            continue
        eksik = []
        toplam = 0
        for tur in ("tablo", "kolon", "indeks", "varsayilansiz"):
            for x in sorted(iz[tur], key=str):
                toplam += 1
                if x not in sema[tur]:
                    eksik.append(f"{tur}:{x}")
        if toplam == 0:
            sonuc[dosya] = ("IZSIZ", eksik)
        elif not eksik:
            sonuc[dosya] = ("TAM", eksik)
        else:
            sonuc[dosya] = ("EKSIK", eksik)
    return sonuc


def calistir(esitle: bool) -> int:
    izler = goc_izleri()
    with get_engine().begin() as conn:
        sema = sema_durumu(conn)
        defter = {
            r[0] for r in conn.execute(text("SELECT filename FROM schema_migrations"))
        }
        sonuc = degerlendir(izler, sema)

        satirlar = [f"Diskte {len(izler)} goc, defterde {len(defter)} kayit.", ""]
        yazilacak = []
        for dosya, (durum, eksik) in sonuc.items():
            d = "defterde" if dosya in defter else "DEFTERDE YOK"
            satirlar.append(f"{dosya:45s} {durum:6s} {d}")
            if eksik:
                satirlar.append("      eksik iz: " + ", ".join(eksik[:6]))
            if dosya not in defter and durum == "TAM":
                yazilacak.append(dosya)

        satirlar.append("")
        satirlar.append(f"Deftere yazilacak (semada izi tam): {len(yazilacak)}")

        if esitle and yazilacak:
            # ON CONFLICT DO NOTHING -> ikinci calismada sessiz gecer (D-251/5).
            conn.execute(
                text(
                    "INSERT INTO schema_migrations (filename) VALUES (:f) "
                    "ON CONFLICT (filename) DO NOTHING"
                ),
                [{"f": f} for f in yazilacak],  # toplu yazma, D-249
            )
            satirlar.append("ESITLENDI: " + ", ".join(yazilacak))
        elif esitle:
            satirlar.append("ESITLEME GEREKMEDI (defter zaten dogru).")

        # Mandal: defterdeki her kayit diskte var mi?
        hayalet = sorted(defter - set(izler))
        if hayalet:
            satirlar.append(f"UYARI hayalet kayit (diskte yok): {hayalet}")

    rapor = "\n".join(satirlar)
    print(rapor)
    Path("_goc_defteri_rapor.txt").write_text(rapor, encoding="utf-8")
    return len(yazilacak)


def uygula(dosya: str) -> None:
    """Goc dosyasini calistirir ve defterine yazar (D-251/3+4)."""
    yol = GOC_DIZINI / dosya
    if not yol.exists():
        raise SystemExit(f"Goc dosyasi yok: {yol}")
    with get_engine().begin() as conn:
        # Ham cursor: DDL icindeki ':' ve '%' bind parametresi sanilmasin
        # (migrate.py MIGRATE-EXEC-02 ile ayni sebep).
        conn.connection.cursor().execute(yol.read_text(encoding="utf-8"))
        conn.execute(
            text(
                "INSERT INTO schema_migrations (filename) VALUES (:f) "
                "ON CONFLICT (filename) DO NOTHING"
            ),
            {"f": dosya},
        )
    print(f"UYGULANDI + DEFTERE YAZILDI: {dosya}")


if __name__ == "__main__":
    if "--uygula" in sys.argv:
        uygula(sys.argv[sys.argv.index("--uygula") + 1])
    calistir("--esitle" in sys.argv)
