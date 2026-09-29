# -*- coding: utf-8 -*-
"""Tek seferlik olcum: KARAR C yazma kapisi + NACE kolon okuyucu. Bitince silinir (D-241)."""
import re
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
KOKLER = ("src", "scripts", "web_dashboard", "web_app.py", "app.py")
ARSIV = ("_ARSIV", "site-packages", "node_modules", ".venv", "tests")

YAZ = re.compile(r"\b(INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|TRUNCATE|ALTER\s+TABLE|CREATE\s+TABLE|COPY\s+\w+)\b", re.I)
MOTOR = re.compile(r"\b(get_engine|create_engine)\b")
BAGLAN = re.compile(r"\b(engine\.begin|engine\.connect|conn\.execute|session\.)\b")


def dosyalar():
    for k in KOKLER:
        p = KOK / k
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in p.rglob("*.py"):
                if not any(a in str(f) for a in ARSIV):
                    yield f


motor, yazan, yazan_motorsuz, create = [], [], [], []
for f in dosyalar():
    m = f.read_text("utf-8", errors="replace")
    r = str(f.relative_to(KOK))
    if MOTOR.search(m):
        motor.append(r)
    if "create_engine" in m:
        create.append(r)
    if YAZ.search(m) and BAGLAN.search(m):
        yazan.append(r)
        if not MOTOR.search(m):
            yazan_motorsuz.append(r)

print(f"motor cagiran dosya      = {len(motor)}")
print(f"YAZAN dosya (SQL+execute)= {len(yazan)}")
print(f"create_engine dogrudan   = {len(create)}")
for r in sorted(create):
    print("   ", r)
print(f"yazan ama motorsuz       = {len(yazan_motorsuz)}")
print("yazanlarin dagilimi:")
for kok in ("src/", "scripts/", "web_dashboard/"):
    print(f"   {kok:16s} {sum(1 for r in yazan if r.replace(chr(92), '/').startswith(kok))}")
