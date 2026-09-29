"""Gecici: ankara_osb_listesi.csv ile companies/osb envanterini karsilastir.

KAHIN 2026-09-29: "diper osbler bunlar, bunlardan da filtrelenmis duzgun
verileri alip sonra sistemde database'de eksik olanlarla doldurmamiz
gerekiyor. Temelde amac VERI TAZELIGI."

SALT OKUNUR. Hicbir sey yazmaz.
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import sqlite3

KOK = pathlib.Path(r"C:\Huginn Data Projesi\Huginn Data Insights")
CSV = pathlib.Path(r"C:\Huginn Data Projesi\workflows\huginn-muninn"
                   r"\ankara_osb_listesi.csv")

#: CSV'deki adi -> veri tabaninda/veri dosyalarinda aranan anahtar kelimeler
ESANLAMLAR: dict[str, list[str]] = {
    "Ankara Sanayi Odası 1. OSB": ["aso", "ankara sanayi odasi", "1. osb"],
    "ASO 2. ve 3. OSB": ["aso2", "aso 2", "2. osb", "3. osb"],
    "Başkent OSB": ["baskent", "başkent"],
    "Anadolu OSB": ["anadolu"],
    "Ostim OSB": ["ostim"],
    "İvedik OSB": ["ivedik"],
    "Polatlı OSB": ["polatli", "polatlı"],
    "Polatlı Ticaret Odası OSB": ["polatli ticaret", "ptoosb"],
    "Şereflikoçhisar OSB": ["sereflikochisar", "şereflikoçhisar"],
    "Ankara Uzay ve Havacılık İhtisas OSB (HAB)": [
        "hab", "kazan", "uzay", "havacilik"],
    "Ankara Dökümcüler İhtisas OSB": ["dokumcu", "dökümcü"],
    "Elmadağ Mobilyacılar İhtisas OSB": ["elmadag", "elmadağ", "mobilya"],
    "Ankara-Çubuk TDİ (Besi) OSB": ["cubuk", "çubuk"],
}

VERI_DOSYALARI = [
    "data/ostim/OSTIM_TEMIZ.jsonl",
    "data/ostim/firmalar_full.jsonl",
    "data/ivedik/firmalar.jsonl",
    "data/baskent/firmalar.jsonl",
    "data/aso/aso_full.jsonl",
    "data/merged/multi_osb_merged.jsonl",
]


def norm(s: str) -> str:
    t = (s or "").lower()
    for a, b in (("ı", "i"), ("ş", "s"), ("ğ", "g"), ("ü", "u"),
                 ("ö", "o"), ("ç", "c"), ("İ", "i"), ("Ş", "s"),
                 ("Ğ", "g"), ("Ü", "u"), ("Ö", "o"), ("Ç", "c")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "", t)


def db_incele() -> None:
    """HANGI db dosyasi var ve icinde companies tablosu nerede?"""
    aday = [
        "company_master.db", "data/app.db", "data/company_master.db",
        "workspace/company_master.db", "src/company_master.db",
    ]
    ayrica = [p for p in KOK.rglob("*.db")
              if ".git" not in p.parts and "node_modules" not in p.parts]
    gorulen = set()
    print("=" * 70)
    print("DB ENVANTERI (salt okunur)")
    print("=" * 70)
    for ad in aday:
        p = KOK / ad
        if p.is_file() and p not in gorulen:
            gorulen.add(p)
            _tablo_listele(p)
    for p in ayrica:
        if p not in gorulen:
            gorulen.add(p)
            _tablo_listele(p)


def _tablo_listele(p: pathlib.Path) -> None:
    try:
        con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        cur = con.cursor()
        t = [r[0] for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        if not t:
            con.close()
            return
        print(f"\n--- {p.relative_to(KOK)}  ({p.stat().st_size / 1024:.0f} KB)")
        for tb in t:
            try:
                n = cur.execute(f'SELECT COUNT(*) FROM "{tb}"').fetchone()[0]
            except sqlite3.Error:
                n = "?"
            isaret = " <== companies" if tb == "companies" else ""
            print(f"      {tb[:40]:42s} {n}{isaret}")
        con.close()
    except sqlite3.Error as e:
        print(f"\n--- {p.relative_to(KOK)}  HATA: {e}")


def sema_incele() -> None:
    """Yedek DB'deki companies/osbs semasi (SALT OKUNUR)."""
    p = KOK / "backups" / "company_master_pre_dedup_20260908_090326.db"
    if not p.is_file():
        print("yedek db yok")
        return
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    cur = con.cursor()
    for tb in ("companies", "osbs", "quarantine_firms"):
        cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{tb}")')]
        n = cur.execute(f'SELECT COUNT(*) FROM "{tb}"').fetchone()[0]
        print(f"\n=== {tb}  ({n} satir, {len(cols)} kolon)")
        print("   " + ", ".join(cols))
        if tb != "companies" and n:
            for r in cur.execute(f'SELECT * FROM "{tb}" LIMIT 5'):
                print("   ORN:", str(r)[:150])
    # companies ornegi
    print("\n=== companies ORNEK (ilk 2 satir)")
    cols = [r[1] for r in cur.execute('PRAGMA table_info("companies")')]
    for r in cur.execute("SELECT * FROM companies LIMIT 2"):
        for k, v in zip(cols, r):
            print(f"   {k:22s} = {str(v)[:60]}")
        print("   " + "-" * 40)
    con.close()


def main() -> None:
    satirlar = list(csv.DictReader(
        CSV.open(encoding="utf-8-sig")))
    print("=" * 70)
    print(f"CSV: {len(satirlar)} OSB")
    print("=" * 70)

    # --- companies tablosunda osb dagilimi (YEDEK db - yasayan db BOST)
    db = KOK / "backups" / "company_master_pre_dedup_20260908_090326.db"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    cur = con.cursor()
    companies = cur.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    dagilim: dict[str, int] = {}
    for osb_id, adet in cur.execute(
            "SELECT osb_id, COUNT(*) FROM companies GROUP BY 1 "
            "ORDER BY 2 DESC"):
        dagilim[str(osb_id)] = adet
    con.close()
    print(f"\ncompanies SATIR (yedek db): {companies}")
    print("DB'deki osb_id dagilimi:")
    for k, v in sorted(dagilim.items(), key=lambda x: -x[1]):
        print(f"   {str(k)[:34]:36s} {v}")

    # --- veri dosyalarinda karsilastirma
    print("\n" + "=" * 70)
    print("OSB BAZINDA KARSILASTIRMA")
    print("=" * 70)
    bulunan: list[dict] = []
    for s in satirlar:
        ad = s["OSB Adı"]
        anahtarlar = ESANLAMLAR.get(ad, [ad])
        n_kayit = 0
        dosyalar: list[str] = []
        for yol in VERI_DOSYALARI:
            p = KOK / yol
            if not p.is_file():
                continue
            adet = 0
            for satir in p.read_text(encoding="utf-8").splitlines():
                if not satir.strip():
                    continue
                n = norm(satir)
                if any(norm(a) in n for a in anahtarlar):
                    adet += 1
            if adet:
                dosyalar.append(f"{p.name}:{adet}")
                n_kayit += adet
        # DB'de var mi
        db_var = None
        for k, v in dagilim.items():
            if any(norm(a) in norm(k) for a in anahtarlar):
                db_var = (k, v)
                break
        bulunan.append({
            "osb": ad, "ilce": s["Konum / İlçe"], "tur": s["Tür"],
            "web": s["Web Sitesi"], "kayit": n_kayit,
            "dosyalar": dosyalar, "db": db_var,
        })
        durum = "VERI VAR" if n_kayit else "EKSIK"
        print(f"\n[{durum:8s}] {ad}")
        print(f"            ilce={s['Konum / İlçe']} | tur={s['Tür']}")
        print(f"            dosya={dosyalar if dosyalar else '-'}")
        print(f"            db={db_var if db_var else '-'}")

    (KOK / "data" / "_tmp" / "osb_envanteri.json").write_text(
        json.dumps(bulunan, ensure_ascii=False, indent=2), encoding="utf-8")
    var = sum(1 for b in bulunan if b["kayit"])
    print("\n" + "=" * 70)
    print(f"SONUC: {var}/{len(bulunan)} OSB icin yerel veri var, "
          f"{len(bulunan) - var} eksik")
    print("Rapor: data/_tmp/osb_envanteri.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
