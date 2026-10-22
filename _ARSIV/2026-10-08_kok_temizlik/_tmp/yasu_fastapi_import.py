# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
L = io.open(r"c:\HUGINN~1\HUGINN~1\web_app.py", encoding="utf-8").read().splitlines()
for i, s in enumerate(L, 1):
    if "fastapi" in s and "import" in s:
        print(i, ":", s)
