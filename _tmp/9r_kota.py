#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9Router ucretsiz modellerin kota durumunu inceleme."""
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("Huginn Data Insights")
ENV = ROOT / "data/router/model_envanter.json"
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"

env = json.loads(ENV.read_text(encoding="utf-8"))
OK = set(env.get("ok", []))
HATA = set(env.get("hata", []))
BOS = set(env.get("bos", []))

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row

print("=" * 78)
print("1. UCETSIZ MODELLERIN DURUMU (envanter)")
print("=" * 78)

# ucretsiz modeller = :free ile biten veya "free" iceren
ucretsiz_ok = sorted(m for m in OK if ":free" in m or "free" in m.lower())
ucretsiz_hata = sorted(m for m in HATA if ":free" in m or "free" in m.lower())
ucretsiz_bos = sorted(m for m in BOS if ":free" in m or "free" in m.lower())

print(f"\nCalisan ucretsiz: {len(ucretsiz_ok)}")
for m in ucretsiz_ok:
    print(f"  + {m}")
print(f"\nHatali ucretsiz: {len(ucretsiz_hata)}")
for m in ucretsiz_hata[:20]:
    print(f"  - {m}")
print(f"\nBos ucretsiz: {len(ucretsiz_bos)}")
for m in ucretsiz_bos:
    print(f"  ~ {m}")

print()
print("=" * 78)
print("1b. 'EVREN' PROVIDER ARAMASI")
print("=" * 78)
evren_bulundu = False
for p in list(con.execute("SELECT provider, name, data FROM providerConnections")):
    if "evren" in (p["provider"] or "").lower() or "evren" in (p["name"] or "").lower():
        evren_bulundu = True
        try:
            data = json.loads(p["data"]) if p["data"] else {}
        except Exception:
            data = {}
        print(f"  BULUNDU: provider={p['provider']} name={p['name']}")
        if isinstance(data, dict):
            for k in ("testStatus", "errorCode", "lastError", "backoffLevel", "rateLimitedUntil"):
                if data.get(k) is not None:
                    print(f"     {k} = {str(data.get(k))[:200]}")
            psd = data.get("providerSpecificData") or {}
            if isinstance(psd, dict) and psd:
                print(f"     providerSpecificData anahtarlari: {list(psd.keys())[:20]}")
if not evren_bulundu:
    print("  'evren' adiyla bir provider YOK.")
    print("  Tum provider listesi:")
    for p in con.execute("SELECT provider, name FROM providerConnections ORDER BY provider"):
        print(f"    - {p['provider']:<20} {p['name']}")

print()
print("=" * 78)
print("2. PROVIDER BAZLI UCETSIZ KULLANIM (son 500 kayit)")
print("=" * 78)

uh = [dict(r) for r in con.execute(
    "SELECT provider, model, endpoint, status, cost, promptTokens, completionTokens, timestamp "
    "FROM usageHistory ORDER BY id DESC LIMIT 500"
)]

# ucretsiz modelleri filtrele
ucretsiz_kullanim = defaultdict(lambda: {"call": 0, "success": 0, "error": 0, "cost": 0.0, "tokens": 0})
for r in uh:
    m = r["model"] or ""
    if ":free" not in m and "free" not in m.lower():
        continue
    prov = r["provider"]
    d = ucretsiz_kullanim[prov]
    d["call"] += 1
    if r["status"] == "success":
        d["success"] += 1
    else:
        d["error"] += 1
    d["cost"] += (r.get("cost") or 0.0)
    d["tokens"] += (r.get("promptTokens") or 0) + (r.get("completionTokens") or 0)

for prov in sorted(ucretsiz_kullanim, key=lambda p: -ucretsiz_kullanim[p]["call"]):
    d = ucretsiz_kullanim[prov]
    print(f"  {prov:<20} call={d['call']:<4} basari={d['success']:<4} hata={d['error']:<4} token={d['tokens']:<8}")

print()
print("=" * 78)
print("3. RATE LIMIT / QUOTA BILGILERI (providerConnections)")
print("=" * 78)

for p in list(con.execute("SELECT provider, name, data FROM providerConnections")):
    try:
        data = json.loads(p["data"]) if p["data"] else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        continue
    rl = data.get("rateLimitedUntil")
    ec = data.get("errorCode")
    bo = data.get("backoffLevel")
    psd = data.get("providerSpecificData") or {}
    quota = psd.get("quota") or psd.get("dailyQuota") or psd.get("monthlyQuota")
    if rl or ec or quota:
        print(f"  {p['provider']:<20} rateLimitUntil={rl} err={ec} backoff={bo} quota={quota}")

print()
print("=" * 78)
print("4. UCETSIZ MODeller KULLANIM ORANI (requestDetails)")
print("=" * 78)

rd = list(con.execute(
    "SELECT provider, model, status, data FROM requestDetails ORDER BY timestamp DESC LIMIT 200"
))
prov_status = defaultdict(lambda: {"success": 0, "error": 0})
for r in rd:
    m = r["model"] or ""
    if ":free" not in m and "free" not in m.lower():
        continue
    prov_status[r["provider"]][r["status"]] = prov_status[r["provider"]].get(r["status"], 0) + 1

for prov in sorted(prov_status, key=lambda p: -(prov_status[p]["success"] + prov_status[p]["error"])):
    d = prov_status[prov]
    toplam = d["success"] + d["error"]
    oran = (d["success"] / toplam * 100) if toplam else 0
    print(f"  {prov:<20} toplam={toplam:<4} basari={d['success']:<4} hata={d['error']:<4} oran={oran:.0f}%")

print()
print("=" * 78)
print("5. KOTA DOLUMU TESPITI (hata mesajlari)")
print("=" * 78)

for p in list(con.execute("SELECT provider, name, data FROM providerConnections")):
    try:
        data = json.loads(p["data"]) if p["data"] else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        continue
    le = data.get("lastError") or ""
    if not le:
        continue
    if any(k in le.lower() for k in ("limit", "quota", "exceeded", "doldu", "free", "kota", "daily")):
        print(f"  [{p['provider']}] {le[:150]}")

con.close()
print("\n[OK] Analiz tamamlandi")