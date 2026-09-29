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

D-271: defter adi her ifadede ACIKCA nitelendirilir (`public.`), asla
`search_path`e birakilmaz. Olcum (2026-09-28): canli DB'de
`schema_migrations` adi UC semada birden var -- public, auth, realtime.
auth/realtime Supabase'in kendi defterleridir, bizim degil (borc iptal).
Bugun dogru defter aciliyor cunku `search_path` = `"$user", public,
extensions`; ama bunu garanti eden bir sey yok. Ayar degisirse arac
sessizce BASKA bir defteri duzenlerdi -- ve bunu kimse fark etmezdi.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# D-254: yol calisma dizinine degil dosyanin yerine baglidir. Mandal
# pre-commit'te git kokunden kosar; "src" goreli yolu orada bos cikardi
# ve defter TUM goclere "hayalet" derdi.
KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine  # noqa: E402

GOC_DIZINI = KOK / "src/company_master/schema/migrations"

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
# 0031 gibi "kisit koy" gocleri tablo/kolon/indeks uretmez; izi kisit adidir.
# Ayristirilmazsa goc IZSIZ kalir = defter onu dogrulayamaz.
RE_KISIT = re.compile(r"ADD\s+CONSTRAINT\s+([\w]+)", re.I)
RE_DEFAULT_DUSUR = re.compile(r"ALTER\s+COLUMN\s+([\w]+)\s+DROP\s+DEFAULT", re.I)
# 0030 gibi "kolonu pasiflestir" gocleri de tablo/kolon/indeks uretmez; izi
# kolon yorumudur (pg_description). Ayristirilmazsa goc IZSIZ kalir.
RE_YORUM = re.compile(
    r"COMMENT\s+ON\s+COLUMN\s+(?:[\w]+\.)?([\w]+)\.([\w]+)\s+IS", re.I
)
# Sonraki bir goc bu gocun izini degistirdiyse (RENAME/DROP) burada bildirilir.
# D-245: "iz yok" demek yetmez, neden yok yazili olmali.
# D-268: DROP-only goc (0036) tablo/kolon URETMEZ, izi kolonun YOKLUGUDUR.
# Arac bunu ayristirmayinca goc IZSIZ kaliyordu; yanlis alarm yarinki gercek
# alarmi gizler. Dusurme de dogrulanabilir bir izdir: kolon hala duruyorsa
# goc uygulanmamistir.
RE_DROP_KOLON = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?([\w.]+)\s+DROP\s+COLUMN\s+"
    r"(?:IF\s+EXISTS\s+)?([\w]+)",
    re.I,
)
RE_USTUNDEN = re.compile(r"ustunden-gecen:\s*([\w.]+)", re.I)
# D-254: dosyanin TAMAMI degil, TEK izi eskidiginde kullanilir. 0001_core
# gibi hala gecerli 20 iz tasiyan bir goce "ustunden-gecen" yazmak defteri
# kor ederdi; burada yalniz adi gecen iz aranmaz.
#     -- dusen-iz: companies.vergi_no       (kolon)
#     -- dusen-iz: idx_companies_adres      (indeks)
RE_DUSEN_IZ = re.compile(r"dusen-iz:\s*([\w.]+)", re.I)
# D-267: 0032 gibi SAF VERI goclerinin semada izi yoktur, olmasi da gerekmez.
# Bunlar "IZSIZ" (= arac dogrulayamadi) diye raporlaniyordu. Bugunku yanlis
# alarm, yarinki gercek alarmi gizler. Iz birakmayan goc, iz birakmadigini
# KENDI yazar; aracin sessizce varsaymasi degil:
#     -- veri-gocu: 23 satir status='liquidation' isaretlendi
RE_VERI_GOCU = re.compile(r"veri-gocu:\s*(.+)", re.I)


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
        veri = RE_VERI_GOCU.search(ham)
        izler[yol.name] = {
            "tablo": {_ad(t) for t in RE_TABLO.findall(s)},
            "kolon": {(_ad(t), k.lower()) for t, k in RE_KOLON.findall(s)},
            "indeks": {i.lower() for i in RE_INDEKS.findall(s)},
            "kisit": {k.lower() for k in RE_KISIT.findall(s)},
            "varsayilansiz": varsayilansiz,
            "yorum": {(t.lower(), k.lower()) for t, k in RE_YORUM.findall(s)},
            "ustunden": ustunden.group(1) if ustunden else None,
            "veri": veri.group(1).strip() if veri else None,
            "dusen": {d.lower() for d in RE_DUSEN_IZ.findall(ham)},
            "drop_kolon": {(_ad(t), k.lower()) for t, k in RE_DROP_KOLON.findall(s)},
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
        # Kisit adlari (0031 tipi "kisit koy" goclerinin izi)
        "kisit": {
            r[0]
            for r in conn.execute(
                text(
                    "SELECT conname FROM pg_constraint c "
                    "JOIN pg_namespace n ON n.oid = c.connamespace "
                    "WHERE n.nspname='public'"
                )
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
        # Yorumu olan kolonlar (0030 tipi "pasiflestir" goclerinin izi)
        "yorum": {
            (r[0], r[1])
            for r in conn.execute(
                text(
                    "SELECT c.relname, a.attname FROM pg_description d "
                    "JOIN pg_class c ON c.oid = d.objoid "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "JOIN pg_attribute a ON a.attrelid = c.oid "
                    "AND a.attnum = d.objsubid "
                    "WHERE n.nspname='public' AND d.objsubid > 0"
                )
            )
        },
    }


def degerlendir(izler, sema):
    """Her goc icin (durum, eksik_izler).

    TAM     = butun izleri semada duruyor
    EKSIK   = izlerinin bir kismi yok -> goc uygulanmamis olabilir
    ESKIMIS = sonraki bir goc uzerinden gecti, izi aranmaz (dosyada yazili)
    VERI    = saf veri gocu, semada izi OLMAMASI dogru (dosyada yazili)
    IZSIZ   = ayristirilabilir iz yok, sebebi de yazili degil -> elle bakilir
    """
    sonuc = {}
    for dosya, iz in izler.items():
        if iz["ustunden"]:
            sonuc[dosya] = ("ESKIMIS", [f"ustunden gecen: {iz['ustunden']}"])
            continue
        eksik = []
        toplam = 0
        for tur in ("tablo", "kolon", "indeks", "kisit", "varsayilansiz", "yorum"):
            for x in sorted(iz[tur], key=str):
                # "dusen-iz" ile bildirilen iz aranmaz; geri kalani aranir.
                ad = ".".join(x) if isinstance(x, tuple) else x
                if ad in iz["dusen"]:
                    continue
                toplam += 1
                if x not in sema[tur]:
                    eksik.append(f"{tur}:{x}")
        # D-268: dusurme izi TERS dogrulanir: kolon HALA duruyorsa goc
        # uygulanmamistir. Ekleme izleriyle ayni sayaca girer ki DROP-only
        # goc IZSIZ gorunmesin.
        # Ayni dosyada dusurulup GERI KURULAN kolon (0027: search_text) drop
        # izi saymaz; nihai iz eklemedir ve yukarida zaten arandi.
        for t_k in sorted(iz["drop_kolon"] - iz["kolon"]):
            toplam += 1
            if t_k in sema["kolon"]:
                eksik.append(f"dusurulmemis kolon:{t_k}")
        if toplam == 0 and iz["veri"]:
            sonuc[dosya] = ("VERI", [iz["veri"]])
        elif toplam == 0:
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
            r[0]
            for r in conn.execute(
                text("SELECT filename FROM public.schema_migrations")  # D-271
            )
        }
        sonuc = degerlendir(izler, sema)

        satirlar = [f"Diskte {len(izler)} goc, defterde {len(defter)} kayit.", ""]
        yazilacak = []
        for dosya, (durum, eksik) in sonuc.items():
            d = "defterde" if dosya in defter else "DEFTERDE YOK"
            satirlar.append(f"{dosya:45s} {durum:6s} {d}")
            if eksik:
                etiket = "beyan" if durum == "VERI" else "eksik iz"
                satirlar.append(f"      {etiket}: " + ", ".join(eksik[:6]))
            if dosya not in defter and durum == "TAM":
                yazilacak.append(dosya)

        satirlar.append("")
        satirlar.append(f"Deftere yazilacak (semada izi tam): {len(yazilacak)}")

        if esitle and yazilacak:
            # ON CONFLICT DO NOTHING -> ikinci calismada sessiz gecer (D-251/5).
            conn.execute(
                text(
                    "INSERT INTO public.schema_migrations (filename) VALUES (:f) "
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
                "INSERT INTO public.schema_migrations (filename) VALUES (:f) "
                "ON CONFLICT (filename) DO NOTHING"
            ),
            {"f": dosya},
        )
    print(f"UYGULANDI + DEFTERE YAZILDI: {dosya}")


def uygula_tumu() -> None:
    """Diskteki tum gocleri sirayla uygular (kurulum/deploy yolu, D-265).

    Eskiden bu is `migrate.py --apply` idi; o yol DB defterine YAZMIYORDU,
    bu yuzden ikinci bir defter dogurdu. Her goc idempotent (`IF NOT EXISTS`)
    oldugu icin bastan calistirilabilir.
    """
    for yol in sorted(GOC_DIZINI.glob("[0-9][0-9][0-9][0-9]_*.sql")):
        uygula(yol.name)


if __name__ == "__main__":
    # D-264: taninmayan arguman sessizce baska bir dala dusemez. argparse
    # bilinmeyeni exit 2 ile reddeder; elle yazilan filtre gereksiz.
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--esitle", action="store_true", help="izi tam gocleri deftere yaz")
    ap.add_argument("--uygula", metavar="DOSYA.sql", help="tek goc calistir + deftere yaz")
    ap.add_argument("--uygula-tumu", action="store_true", help="tum gocleri sirayla uygula")
    arg = ap.parse_args()

    if arg.uygula_tumu:
        uygula_tumu()
    elif arg.uygula:
        uygula(arg.uygula)
    calistir(arg.esitle)
