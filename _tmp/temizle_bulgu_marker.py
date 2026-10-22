#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bulgu_defteri.md merge marker'larini temizle (append-only log: her iki taraf korunur)."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

p = Path("data/orchestrator/bulgu_defteri.md")
L = p.read_text(encoding="utf-8").splitlines()

MARKERS = {
    "<<<<<<< Updated upstream",
    "<<<<<<< HEAD",
    "=======",
    ">>>>>>> Stashed changes",
    ">>>>>>> origin/main",
}

out = [l for l in L if l.strip() not in MARKERS]

p.write_text("\n".join(out) + "\n", encoding="utf-8")

print(f"OK: {len(L)} -> {len(out)} satir")
kalan = [i + 1 for i, l in enumerate(out) if l.strip().startswith("<<<<<<") or l.strip() == "=======" or l.strip().startswith(">>>>>>")]
print("KALAN MARKER:", kalan if kalan else "YOK")
print("SON 3:")
for l in out[-3:]:
    print("  ", " | ".join(l.split("|")[:3]))
