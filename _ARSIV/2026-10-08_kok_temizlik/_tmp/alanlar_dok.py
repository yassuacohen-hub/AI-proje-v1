# -*- coding: utf-8 -*-
"""uret() -> (seq, blok, alan) Python literal; tobb_alan_haritasi.ALANLAR icin."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")
from tobb_alan_sozlugu_uret import uret
rows = [(n, b, f) for n, o, b, f, t, d in uret() if o == "tobb"]
print("ADET", len(rows), "BLOKLAR", sorted({b for _, b, _ in rows}))
for n, b, f in rows:
    print(f"    Alan({n}, {b!r}, {f!r}),")
