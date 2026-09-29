"""D-290: Mevcut DB'yi KORUMA denetimi (tarama oncesi guvenlik).

KAHIN talebi: "eski database tekrar kirli ve hatali olmasini istemiyorum,
her turlu onlemi al". Bu betik tarama BASLAMADAN once durumu olcer ve
SONRAKI adimlarda neyin bozulabilecegini gosterir.

Kapsam (SADECE OKUMA - hicbir sey yazilmaz):
  1. Hangi dosyalar var, boyutlari, son degisim
  2. company_master / source_records DB'si: kayit sayilari, orfany
  3. OSTIM ciktilarinin birlestirme ile UYUMLULUK denetimi
  4. Tarama sirasinda DEGISEBILECEK dosyalar (beyaz liste / kara liste)

Kullanim: python scripts/ostim_veri_koruma.py
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sqlite3
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "ostim" / "veri_koruma_raporu.json"

#: Tarama ASLA dokunmamasi gereken dosyalar (beyaz liste disi).
#: Bunlar yazilirsa veri KIRPILIR.
KORUNACAK = [
    "data/ostim/firmalar_full.jsonl",        # ana liste (8.313)
    "data/ostim/firmalar_vkn_ekli.jsonl",    # mevcut detayli (5.040)
    "data/ostim/firmalar_birlestirilmis.jsonl",  # D-285 ciktisi
]


def dosya_bilgi(yol: pathlib.Path) -> dict:
    if not yol.is_file():
        return {"var": False}
    st = yol.stat()
    h = hashlib.sha256(yol.read_bytes()).hexdigest()[:16]
    satir = 0
    with yol.open("rb") as f:
        for _ in f:
            satir += 1
    return {
        "var": True,
        "boyut_bayt": st.st_size,
        "satir": satir,
        "sha256_16": h,
        "son_degisim": datetime.fromtimestamp(
            st.st_mtime).isoformat(timespec="seconds"),
    }


def db_tara() -> dict:
    """company_master DB'sini SALT OKUNUR inceler."""
    aday = [p for p in KOK.rglob("*.db")
            if ".git" not in p.parts and "node_modules" not in p.parts]
    sonuc = {}
    for db in aday:
        try:
            c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            cur = c.cursor()
            tablolar = [r[0] for r in cur.execute(
                "select name from sqlite_master where type='table'")]
            bilgi = {"yol": str(db.relative_to(KOK)), "tablolar": {}}
            for tb in tablolar:
                try:
                    n = cur.execute(f'select count(*) from "{tb}"').fetchone()[0]
                    bilgi["tablolar"][tb] = n
                except sqlite3.Error:
                    bilgi["tablolar"][tb] = "HATA"
            sonuc[str(db.relative_to(KOK))] = bilgi
            c.close()
        except sqlite3.Error as e:
            sonuc[str(db.relative_to(KOK))] = {"hata": str(e)}
    return sonuc


def main() -> int:
    rapor = {
        "zaman": datetime.now().isoformat(timespec="seconds"),
        "amac": "Tarama oncesi mevcut verinin korunmasi",
        "korunacak_dosyalar": {
            p: dosya_bilgi(KOK / p) for p in KORUNACAK
        },
        "veritabanlari": db_tara(),
    }

    # OSTIM ciktisi vs birlestirilmis uyumluluk
    bir = KOK / "data/ostim/firmalar_birlestirilmis.jsonl"
    if bir.is_file():
        kayitlar = [json.loads(x) for x in bir.read_text(
            encoding="utf-8").splitlines() if x.strip()]
        slug = [k.get("slug") for k in kayitlar if k.get("slug")]
        rapor["birlestirilmis"] = {
            "kayit": len(kayitlar),
            "tekil_slug": len(set(slug)),
            "tekrar_kayit": len(slug) - len(set(slug)),
        }

    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")

    print("KORUNACAK DOSYALAR")
    for p, b in rapor["korunacak_dosyalar"].items():
        if b.get("var"):
            print(f"  {p:48s} {b['satir']:>6} satir  "
                  f"sha={b['sha256_16']}")
        else:
            print(f"  {p:48s} YOK")
    print("\nVERITABANLARI")
    for yol, b in rapor["veritabanlari"].items():
        if "hata" in b:
            print(f"  {yol}: HATA {b['hata']}")
            continue
        print(f"  {yol}")
        for tb, n in sorted(b["tablolar"].items(),
                            key=lambda x: -x[1] if isinstance(x[1], int) else 0):
            if isinstance(n, int) and n:
                print(f"      {tb:32s} {n:>8}")
    if "birlestirilmis" in rapor:
        b = rapor["birlestirilmis"]
        print(f"\nBIRLESTIRILMIS: {b['kayit']} kayit | "
              f"tekil {b['tekil_slug']} | TEKRAR {b['tekrar_kayit']}")
    print(f"\n{CIKTI}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
