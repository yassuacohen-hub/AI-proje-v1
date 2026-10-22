# -*- coding: utf-8 -*-
import sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\bulgu_defteri.md")
ham = p.read_bytes()
print("boyut:", len(ham))
try:
    ham.decode("utf-8")
    print("UTF-8 OK")
except UnicodeDecodeError as e:
    print("HATA:", e)
    b = e.start
    print("bolge (latin-1):", ham[max(0, b - 120):b + 120].decode("latin-1"))
    print("bolge (cp1254):", ham[max(0, b - 120):b + 120].decode("cp1254", errors="replace"))
    # kac hatali byte var?
    bad = [(i, c) for i, c in enumerate(ham) if c >= 0x80 and not _utf8_at(ham, i)] if False else None
