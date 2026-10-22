# -*- coding: utf-8 -*-
"""Tek seferlik: defter satir 484-485 rol `codex` -> `nisa` (kilitli, yalniz bu 2 satir).
ponytail: tek kullanimlik; kalici gocte ayri komut gerekir.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Huginn Data Insights"
sys.path.insert(0, str(ROOT))
from scripts import bulgu_defteri as bd  # noqa: E402

dosya = ROOT / "data" / "orchestrator" / "bulgu_defteri.md"
with bd._kilit_ac(dosya):
    satirlar = dosya.read_text(encoding="utf-8").split("\n")
    n = 0
    for i, s in enumerate(satirlar):
        if s.startswith("2026-10-21 | MUSTERI-PANEL-TASARIM-01 | codex | "):
            satirlar[i] = s.replace(" | codex | ", " | nisa | ", 1)
            n += 1
    assert n == 2, f"beklenen 2, bulunan {n}"
    dosya.write_text("\n".join(satirlar), encoding="utf-8", newline="\n")
print("degisen", n)
