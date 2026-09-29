#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MANDAL-SAHNE-01 (D-301): kazara toplu sahneleme kapisi.

Olculmus olay: D-299'un kestigi `tests/test_admin_quality.py` ve
`tests/test_admin_sistem_quality.py`, yasu'nun `fix(ivedik): gercek kod 401...`
commit'ine karisti. Uc ajan ayni agacta calisiyor; `git add -A` kimin neyi
kestigini silen tek harekettir.

Mevcut mandal (`kodlama_denetim.py`) `git add -A`'yi *betiklerde* yakalar;
ajanin elle yazdigi komutu yakalamaz -- D-301'de olculdu, varsayilmadi.

Bu kapi niyeti degil **sonucu** olcer: tek commit'te sahnelenen dosya sayisi.
Amac kazayi yakalamak, ajani engellemek degil -- bu yuzden tek esik, tek sayi,
kacis yolu acik (`SAHNE_TAVAN` ile yukselt, gerekcesi commit mesajina yazilir).

ponytail: sahnelenen yol kumesi ile commit kapsamini karsilastirmak daha kesin
olurdu; "kapsam beyani" diye bir alan yok, uydurmak yerine sayi esigi kondu.
Beyan alani dogarsa (ornegin commit mesaji trailer'i) kiyas buraya eklenir.
"""
from __future__ import annotations

import os
import subprocess
import sys

# D-301: esik olculdu, varsayilmadi. Son 49 commit: ortanca 8 dosya; 20 ustu 12
# commit (%24), 20-30 arasi yalnizca 2, 30-40 arasi 0 -- dagilimda ucurum var.
# 20 ustundekiler: 2 otomasyon commit'i (352 ve 50 dosya, `git add -A` ile),
# 8 buyuk D-kaydi refactor'u, ve olayin kendisi: `7343cec` **22 dosya** --
# D-299'un iki testini yutan commit. Esik 20, olculmus olayi yakaladigi icin
# secildi; ilk yazdigim "20 ustu yalnizca otomasyonda gorulur" iddiasi
# olcumde YANLIS cikti ve burada duzeltildi (D-260: beyan kanit degildir).
TAVAN = int(os.environ.get("SAHNE_TAVAN", "20"))


def sahnelenen() -> list[str]:
    """Commit'e girecek yollar (staged). Silinenler de sayilir."""
    cikti = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    return [s for s in cikti.splitlines() if s.strip()]


def main() -> int:
    yollar = sahnelenen()
    if len(yollar) <= TAVAN:
        return 0
    print(f"MANDAL-SAHNE-01: tek commit'te {len(yollar)} dosya (tavan {TAVAN}).")
    print("`git add -A` kazasi mi? Uc ajan ayni agacta -- baskasinin isini")
    print("commit'ine katmis olabilirsin (D-299'da oldu).")
    print("")
    for y in yollar[:30]:
        print(f"  {y}")
    if len(yollar) > 30:
        print(f"  ... +{len(yollar) - 30} dosya daha")
    print("")
    print("Kasitliysa: SAHNE_TAVAN=<sayi> git commit ...  (gerekce commit mesajina)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
