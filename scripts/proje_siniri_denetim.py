# -*- coding: utf-8 -*-
"""Proje Sınırı Denetimi (AGENTS.md "Proje Sınırı Kuralı", 2026-09-15).

Üst dizinde (repo kökünün bir üstü) projeye ait dosya/klasör kalıp kalmadığını
ve repo kökünde geçici artık dosya bulunup bulunmadığını raporlar. Salt okunur;
hiçbir şeyi taşımaz/silmez. Çıkış kodu: 0 temiz, 1 ihlal var.

Kullanım:
    python scripts/proje_siniri_denetim.py            # rapor
    python scripts/proje_siniri_denetim.py --json     # makine okunur
"""
from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UST = ROOT.parent

# Üst dizinde tolere edilen araç kalıntıları (projeye ait değil)
UST_IZINLI: tuple[str, ...] = (".pytest_cache", ".mypy_cache", "__pycache__", "desktop.ini", "Thumbs.db")

# Kökte yasak geçici dosya desenleri (bkz. .gitignore REPO-HIJYEN-01 bloğu)
KOK_YASAK_DESEN: tuple[str, ...] = ("_*.py", "__*.py", "*.bak", "*.base", "_*.txt", "hello.txt", "temp_*.json", "tmp_*")

# Ürün Sahibi referans/konum notu adayları — ihlal değil, taşıma emri
KONUM_NOTU_DESEN: tuple[str, ...] = ("KONUM_NOTU*", "konum_notu*", "REFERANS*", "referans*")


def ust_dizin_ihlalleri() -> list[dict[str, str]]:
    bulgular: list[dict[str, str]] = []
    if not UST.is_dir():
        return bulgular
    for p in sorted(UST.iterdir()):
        if p.resolve() == ROOT.resolve() or p.name in UST_IZINLI:
            continue
        tur = "konum_notu" if any(fnmatch.fnmatch(p.name, d) for d in KONUM_NOTU_DESEN) else "dis_oge"
        bulgular.append({"tur": tur, "yol": str(p), "kind": "dir" if p.is_dir() else "file"})
    return bulgular


def kok_ihlalleri() -> list[dict[str, str]]:
    bulgular: list[dict[str, str]] = []
    for p in sorted(ROOT.iterdir()):
        if not p.is_file():
            continue
        if any(fnmatch.fnmatch(p.name, d) for d in KOK_YASAK_DESEN):
            bulgular.append({"tur": "kok_gecici", "yol": str(p.relative_to(ROOT)), "kind": "file"})
    return bulgular


def main() -> int:
    ust = ust_dizin_ihlalleri()
    kok = kok_ihlalleri()
    ihlal = [b for b in ust if b["tur"] == "dis_oge"] + kok
    notlar = [b for b in ust if b["tur"] == "konum_notu"]

    if "--json" in sys.argv:
        print(json.dumps({"ust": ust, "kok": kok, "ihlal_sayisi": len(ihlal)}, ensure_ascii=False, indent=2))
        return 1 if ihlal else 0

    print(f"Repo kökü : {ROOT}")
    print(f"Üst dizin : {UST}")
    if notlar:
        print("\n[TAŞIMA EMRİ] Ürün Sahibi konum notu bulundu — oku, hedefe taşı, dış kopyayı kaldır:")
        for b in notlar:
            print(f"  - {b['yol']}")
    if not ihlal:
        print("\nTEMİZ: üst dizinde proje öğesi yok, kökte geçici artık yok.")
        return 0
    print(f"\nİHLAL ({len(ihlal)}): AGENTS.md 'Proje Sınırı Kuralı' — silme, içeri taşı ve raporla.")
    for b in ihlal:
        etiket = "DIŞ DİZİN" if b["tur"] == "dis_oge" else "KÖK GEÇİCİ"
        print(f"  - [{etiket}] {b['yol']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
