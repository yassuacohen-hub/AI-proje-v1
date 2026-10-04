# -*- coding: utf-8 -*-
"""OSTIM pilot firma secimi (VERI-OSTIM-HREF-FILTRE-01, KAHIN 2026-10-03 talebi).

KAHIN: *"firma turu anonim sirket a.s. olsun"*, *"buyuk olsun"*, *"uzay ve
havacilik sektoru olabilir"*.

Neden kalici bir arac:
    Onceki secim tek seferlik `python -c` ile yapildi ve **iki hatayi
    beraber goturdu**:
      1. ASCII regex (`ANONIM|SIRKETI`) Turkce "ANONIM SIRKETI" yazimini
         gormedi -> 991 adaydan 385'i secildi, 606 A.S. firma elendi.
      2. Sube kaydi ("... - Ankara Subesi") ana kayit sanildi -> 100
         satirin 1'i gercek A.S. degildi.
    Her ikisi de olcum hatasidir (D-224: olcmeden karar yok).

Kullanim:
    python -X utf8 scripts/ostim_pilot_firma_sec.py
    python -X utf8 scripts/ostim_pilot_firma_sec.py --adet 100 --cikti data/_tmp/x.jsonl

Idempotent: girdiyi yalniz okur, yalniz `--cikti` yoluna yazar.
"""
import argparse
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
VARSAYILAN_GIRD = ROOT / "data" / "ostim" / "firmalar_full.jsonl"
VARSAYILAN_CIKTI = ROOT / "data" / "_tmp" / "ostim_pilot_as_girdi.jsonl"

# "A.S." ve "ANONIM SIRKETI" — Turkce harfler normalize edildikten sonra.
AS_DESEN = re.compile(r"\bA\. ?S\.|ANONIM ?SIRKETI")

# Sube/şube kaydi ana firma degildir (KAHİN "buyuk firma" dedi, şube degil).
SUBE_DESEN = re.compile(r"\bSUBE|\b\S+\s+SUBESI\b")

# Havacilik/uzay/savunma odakli unvanlar — KAHIN sektor tercihi.
SEKTOR_ANAHTAR = (
    "SAVUNMA", "HAVACILIK", "UZAY", "ROKET", "HAVA", "ASKERI", "SAVUN",
    "AEROSPACE", "AERONAUT", "UYDU", "SATELLITE", "DRONE", "ISTIHAK",
)
# Buyuklik sinyalizasyonu: unvandaki sinif ifadeleri (en cok olcum).
OLCEK_ANAHTAR = ("ANONIM SIRKETI", "A. S.", "A. S")


def normalize(metin: str) -> str:
    """Turkce harfleri ASCII'ye indirger, buyuk harfe cevirir."""
    if not metin:
        return ""
    duz = unicodedata.normalize("NFKD", metin)
    return "".join(c for c in duz if not unicodedata.combining(c)).upper()


def uygun(kayit: dict) -> bool:
    n = normalize(kayit.get("unvan"))
    if not n:
        return False
    if not AS_DESEN.search(n):
        return False
    if SUBE_DESEN.search(n):
        return False
    return True


def sektor_puan(kayit: dict) -> int:
    n = normalize(kayit.get("unvan"))
    return sum(1 for a in SEKTOR_ANAHTAR if a in n)


def olce_puan(kayit: dict) -> int:
    """Unvandaki sinif ifadesi sayisi — buyuklik sinyalizasyonu (proxy)."""
    n = normalize(kayit.get("unvan"))
    return sum(n.count(a) for a in OLCEK_ANAHTAR)


def main() -> int:
    ap = argparse.ArgumentParser(description="OSTIM pilot A.S. firma secimi")
    ap.add_argument("--girdi", default=str(VARSAYILAN_GIRD))
    ap.add_argument("--cikti", default=str(VARSAYILAN_CIKTI))
    ap.add_argument("--adet", type=int, default=100)
    ap.add_argument("--sektor-oncelik", type=int, default=24,
                    help="KAHIN: kac firma sektor odakli olsun")
    a = ap.parse_args()

    kayitlar = []
    for line in io.open(a.girdi, encoding="utf-8-sig"):
        line = line.strip()
        if line:
            kayitlar.append(json.loads(line))

    uygunlar = [m for m in kayitlar if uygun(m)]
    sektorluler = sorted(
        (m for m in uygunlar if sektor_puan(m) > 0),
        key=lambda m: (-sektor_puan(m), -olce_puan(m), m.get("unvan") or ""),
    )
    kalan = a.adet - min(len(sektorluler), a.sektor_oncelik)
    digerleri = sorted(
        (m for m in uygunlar if sektor_puan(m) == 0),
        key=lambda m: (-olce_puan(m), m.get("unvan") or ""),
    )
    secilen = sektorluler[: a.sektor_oncelik] + digerleri[:kalan]

    Path(a.cikti).parent.mkdir(parents=True, exist_ok=True)
    with io.open(a.cikti, "w", encoding="utf-8") as f:
        for m in secilen:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    print(f"girdi satir        : {len(kayitlar)}")
    print(f"A.S. uygun kayit   : {len(uygunlar)}  (sube/ana kayit elendi)")
    print(f"sektor odakli      : {len(sektorluler)}")
    print(f"secilen            : {len(secilen)}")
    print(f"cikti              : {a.cikti}")
    print("\n--- sektor odakli ilk 12 ---")
    for m in secilen[:12]:
        print(f"  {m.get('slug')} | {(m.get('unvan') or '')[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
