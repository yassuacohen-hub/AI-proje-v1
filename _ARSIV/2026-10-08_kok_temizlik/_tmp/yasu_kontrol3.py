# -*- coding: utf-8 -*-
import pathlib
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")

g = BASE / "scripts" / "gorev_kutusu.py"
print("=== gorev_kutusu.py teslim/hafiza/hub ilgili satirlar ===")
if g.exists():
    anahtar = ["def teslim", "def _teslim", "hafiza", "Kapanan", "kapandi", "hub", "B-14", "def onayla", "def main", "add_argument"]
    for i, s in enumerate(g.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        for a in anahtar:
            if a in s:
                print(f"{i}: {s.strip()[:120]}")
                break
else:
    print("(yok)")


