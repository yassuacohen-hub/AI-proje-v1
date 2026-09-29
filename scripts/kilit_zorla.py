# -*- coding: utf-8 -*-
"""Commit aninda dosya kilidini ZORLAR (beyan degil, kapi).

`data/orchestrator/file_locks.json` D-281'e kadar yalnizca *kaydediliyordu*;
okuyan 48 yer vardi, **zorlayan yoktu** (D-261: zorlayani olmayan kayit beyandir).
Bu betik `scripts/hooks/pre-commit`ten cagrilir: staged dosya baskasinin
kilidindeyse commit durur.

Kimlik sirasi: `git config huginn.ajan` > `user.name` icinde gecen bilinen ajan.
ponytail: kimlik cozulemezse UYARIR ve gecer — ucu birden bloke etmemek icin.
Yukseltme: her ajan `git config huginn.ajan <ad>` kurdugunda burasi `return 1` olur.

    python scripts/kilit_zorla.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
# D-243: yikici/durduran isin yolu enjekte edilebilir olur (prova canliya dokunmaz)
KILIT = Path(os.environ.get("HUGINN_KILIT_YOL")
             or KOK / "data" / "orchestrator" / "file_locks.json")
AJANLAR = ("yasu", "utku", "ihsan", "salih", "orkestrator")


def _git(*arg: str) -> str:
    cp = subprocess.run(["git", *arg], cwd=KOK, capture_output=True,
                        text=True, errors="replace")
    return cp.stdout.strip()


def ajan_kimligi() -> str | None:
    """Kilit sahipligiyle karsilastirilabilir ajan adi (yoksa None)."""
    if ad := _git("config", "huginn.ajan"):
        return ad.strip().lower()
    adi = _git("config", "user.name").lower()
    return next((a for a in AJANLAR if a in adi), None)


def ihlaller(staged: list[str], ben: str | None,
             kilitler: dict) -> list[tuple[str, dict]]:
    """Staged yollardan `ben` disinda bir ajanin kilidinde olanlar."""
    return [(y, kilitler[y]) for y in staged
            if y in kilitler and kilitler[y]["sahip"] != ben]


def main() -> int:
    if not KILIT.is_file():
        return 0
    kilitler = json.loads(KILIT.read_text(encoding="utf-8"))
    staged = [y for y in _git("diff", "--cached", "--name-only").splitlines() if y]
    ben = ajan_kimligi()
    ihlal = ihlaller(staged, ben, kilitler)
    if not ihlal:
        return 0
    for yol, k in ihlal:
        print(f"[kilit] {yol} -> {k['sahip']} ({k['task_id']})", file=sys.stderr)
    if ben is None:
        print("[kilit] UYARI: ajan kimligi yok, gecildi. Kur: "
              "git config huginn.ajan <ad>", file=sys.stderr)
        return 0
    print(f"[kilit] DURDU: {len(ihlal)} dosya {ben} disinda bir ajanin kilidinde. "
          "Kilit sahibiyle konus veya 'orchestrator_internal.py birak' ile devret.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
