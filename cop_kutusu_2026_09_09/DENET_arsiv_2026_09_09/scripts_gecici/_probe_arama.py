# -*- coding: utf-8 -*-
"""Y9 test yazimi oncesi canli davranis probu (gecici)."""
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from web_app import app

try:
    from web_app import MAX_COMPANIES_LIMIT
    print("MAX_COMPANIES_LIMIT =", MAX_COMPANIES_LIMIT)
except ImportError:
    print("MAX_COMPANIES_LIMIT tanimli degil")

c = TestClient(app)


def q(s):
    d = c.get("/api/companies", params={"limit": 3, "search": s}).json()
    return d["total"], [i["legal_name"][:44] for i in d["items"]]


for t in ["dogan", "doğan", "inno", "ınno", "radikal", "RADİKAL", "ltd", "ŞTİ"]:
    x, y = q(t)
    print(repr(t), "->", x, y[:2])

r = c.get("/api/sources").json()
srcs = [s["source_name"] for s in r]
print("SOURCES:", [(s["source_name"], s["record_count"]) for s in r][:8])

d = c.get("/api/companies", params={"limit": 10000}).json()
print("LIMIT_CLAMP_ITEMS =", len(d["items"]), "TOTAL =", d["total"])

for s in srcs[:4]:
    t2 = c.get("/api/companies", params={"limit": 1, "sources": s}).json()["total"]
    t3 = c.get("/api/companies", params={"limit": 1, "source": s}).json()["total"]
    print("SRC", s, "sources=", t2, "source=", t3)

if len(srcs) >= 2:
    two = c.get("/api/companies", params={"limit": 1, "sources": ",".join(srcs[:2])}).json()["total"]
    print("IKI_KAYNAK_TOPLAM =", two)
