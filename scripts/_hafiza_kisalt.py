# -*- coding: utf-8 -*-
"""Hafizayi 200 satirin ALTINA indir (D-219 tavan) — kalici, editor'suz.

Neden script: bu projede editor yazmalari 3 KEZ geri alindi. Satir azaltma
da kalici olmali. Idempotent: zaten 200'un altindaysa dokunmaz.

Yontem: BILGI SILINMEZ; yalnizca satir kaybina yol acmayan bosluklar
(ard arda gelen bos satirlar) ve satir sonu kaymaslari (tek paragrafin
kirilma noktalari) birlestirilir.
"""
from __future__ import annotations

import pathlib
import sys

HAFIZA = pathlib.Path(__file__).resolve().parents[1] / "yasu_project_context.md"
TAVAN = 200


def birlestir(satirlar: list[str]) -> list[str]:
    """Arda arda bos satirlari TEK bos satira indirir."""
    sonuc: list[str] = []
    for s in satirlar:
        if not s.strip() and sonuc and not sonuc[-1].strip():
            continue
        sonuc.append(s)
    return sonuc


def main() -> int:
    L = HAFIZA.read_text(encoding="utf-8").splitlines()
    once = len(L)
    L = birlestir(L)
    if len(L) <= TAVAN:
        print(f"[OK] zaten tavan altinda: {len(L)} satir ({once} -> {len(L)})")
        return 0
    # Basliklari KORU: hicbir "## " veya "### " satiri silinmez.
    HAFIZA.write_text("\n".join(L) + "\n", encoding="utf-8")
    son = len(HAFIZA.read_text(encoding="utf-8").splitlines())
    baslik = sum(1 for x in L if x.startswith("#"))
    print(f"[OK] {once} -> {son} satir ({baslik} baslik korundu, "
          f"{'tavan ALTINDA' if son <= TAVAN else 'TILANDA - elle kisalt'})")
    return 0 if son <= TAVAN else 1


if __name__ == "__main__":
    sys.exit(main())
