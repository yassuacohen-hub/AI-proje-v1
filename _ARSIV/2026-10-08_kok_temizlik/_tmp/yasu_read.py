# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pathlib
BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")
L = (BASE / "tests/test_sayfa_iskeleti.py").read_text(encoding="utf-8").splitlines()
print(chr(10).join(f"{i+1}| {L[i]}" for i in range(81, 136)))
