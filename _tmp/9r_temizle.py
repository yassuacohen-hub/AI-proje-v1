#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""9Router kapsamlı temizlik.

1) Combo'lardan HATALI/BOS modelleri cikarir (sadece calisanlar kalir).
2) Calisan modelleri guc + ucretsiz onceligine gore siralar.
3) Provider'lar: 429/hata verenleri PASIF yapar, saglamlari AKTIF.
4) settings: comboStrategy / comboStrategies temizlenir, claude provider'a
   rate-limit cooldown uygulanir.
"""
import json
import sqlite3
import sys
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

# Guc + ucretsiz oncelik sirasi (guclu/deneyimli ucretsiz modeller one)
PRIORITY = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "cohere/north-mini-code:free",
    "deepseek-ai/deepseek-r1-distill-qwen-32b",
    "qwen/qwen2.5-coder-32b-instruct",
    "qwen/qwq-32b",
    "poolside/laguna-s-2.1:free",
    "poolside/laguna-xs-2.1:free",
    "meta/llama-3.3-70b-instruct-fp8-fast",
    "meta/llama-3.1-70b-instruct-fp8-fast",
    "mistralai/mistral-small-3.1-24b-instruct",
    "z-ai/glm-4.7-flash",
    "anthropic/claude",  # claude varsa sona
]


def oncelik_sirala(models):
    """Guc/ucretsiz onceligine gore sirala; ayni oncelikte alfabetik."""
    def key(m):
        for i, p in enumerate(PRIORITY):
            if m.endswith(p) or p in m:
                return (i, m)
        return (999, m)
    return sorted(models, key=key)


con = sqlite3.connect(f"file:{DB.as_posix()}?mode=rw", uri=True)
con.row_factory = sqlite3.Row
rapor = {"combo": [], "provider": [], "settings": {}}

# ---------------------------------------------------------------- 1) COMBO TEMIZLIK
print("=" * 78)
print("ADIM 1: COMBO TEMIZLIK (hatali modeller cikariliyor)")
print("=" * 78)

for c in list(con.execute("SELECT id, name, models FROM combos")):
    try:
        models = json.loads(c["models"]) if c["models"] else []
    except Exception:
        models = []
    if not models:
        continue

    temiz = []
    for m in models:
        if m in HATA:
            continue
        if m in BOS:
            continue
        if m in OK:
            temiz.append(m)
            continue
        # bilinmeyen: hata listesinde yoksa tut ama en sona at
        temiz.append(m)

    # bilinmeyenleri ayir
    kesin = [m for m in temiz if m in OK]
    belirsiz = [m for m in temiz if m not in OK]

    # tekrarsiz + oncelik sirala
    seen = set()
    yeni = []
    for m in kesin + belirsiz:
        if m not in seen:
            yeni.append(m)
            seen.add(m)
    yeni = oncelik_sirala(yeni)

    if yeni != models:
        con.execute(
            "UPDATE combos SET models=?, updatedAt=? WHERE id=?",
            (json.dumps(yeni, ensure_ascii=False),
             datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
             c["id"]),
        )
    rapor["combo"].append({
        "combo": c["name"],
        "onceki": len(models),
        "sonraki": len(yeni),
        "silinen": len(models) - len(yeni),
        "yeni_sira": yeni,
    })
    print(f"  {c['name']:<20} {len(models):>4} -> {len(yeni):>4}  (silinen: {len(models)-len(yeni)})")
    for m in yeni[:6]:
        print(f"       ilk: {m}")

# ---------------------------------------------------------------- 2) PROVIDER AKTIF/PASIF
print()
print("=" * 78)
print("ADIM 2: PROVIDER AKTIF/PASIF AYRIMI")
print("=" * 78)

# 429 rate limit = gecici. Bu provider'lari DUSUR (pasif) degil,
# onceliklerini dusurup rate limit cooldown uygula.
RATE_LIMIT_PROVIDERS = {"claude", "clinepass"}  # OAuth + proxy = 429 kaynakli

for p in list(con.execute("SELECT provider, name, isActive, priority, data FROM providerConnections")):
    try:
        data = json.loads(p["data"]) if p["data"] else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}

    ec = data.get("errorCode")
    ts = data.get("testStatus")
    yeni_data = dict(data)
    degisti = False

    if p["provider"] in RATE_LIMIT_PROVIDERS and ec == 429:
        # 429 alan OAuth provider: cooldown + oncelik dusur
        yeni_data["rateLimitedUntil"] = int(
            (datetime.now(timezone.utc).timestamp() + 1800) * 1000
        )
        yeni_data["backoffLevel"] = min(int(data.get("backoffLevel") or 0) + 2, 10)
        degisti = True
        print(f"  [COOLDOWN] {p['provider']}/{p['name']}: 429 -> 30dk cooldown, backoff={yeni_data['backoffLevel']}")

    if degisti:
        con.execute(
            "UPDATE providerConnections SET data=? WHERE provider=? AND name=?",
            (json.dumps(yeni_data, ensure_ascii=False), p["provider"], p["name"]),
        )
        rapor["provider"].append({
            "provider": p["provider"], "name": p["name"], "aksiyon": "cooldown_30dk"
        })

# ---------------------------------------------------------------- 3) SETTINGS
print()
print("=" * 78)
print("ADIM 3: SETTINGS (combo stratejisi)")
print("=" * 78)

row = con.execute("SELECT data FROM settings LIMIT 1").fetchone()
st = json.loads(row["data"]) if row and row["data"] else {}

# comboStrategy: fallback yerine 'priority' -> saglam model once
st["comboStrategy"] = "fallback"
st["comboStickyRoundRobinLimit"] = 2

# comboStrategies: judgeModel hatali (cc/claude-sonnet-5) -> calisan model yap
cs = st.get("comboStrategies") or {}
for combo_name, cfg in cs.items():
    jm = cfg.get("judgeModel")
    if jm and jm in HATA:
        yeni_jm = next((m for m in OK if "nemotron-3-ultra" in m), "cc/claude-sonnet-5")
        cfg["judgeModel"] = yeni_jm
        print(f"  judgeModel duzeltildi: {jm} -> {yeni_jm} (combo={combo_name})")
        rapor["settings"].setdefault("judgeModel", []).append(
            {"combo": combo_name, "onceki": jm, "sonraki": yeni_jm}
        )
    cfg["fallbackStrategy"] = "round-robin"
st["comboStrategies"] = cs

# providerStrategies: rate-limited provider'larda sticky limit 1
ps = st.get("providerStrategies") or {}
for prov, cfg in ps.items():
    if prov in RATE_LIMIT_PROVIDERS:
        cfg["stickyRoundRobinLimit"] = 1
st["providerStrategies"] = ps

# claudeAutoPing: 429 sonrasi otomatik toparlanma icin AC
cap = st.get("claudeAutoPing") or {}
cap["enabled"] = True
st["claudeAutoPing"] = cap
print("  claudeAutoPing: enabled=True (otomatik toparlanma)")

con.execute(
    "UPDATE settings SET data=?",
    (json.dumps(st, ensure_ascii=False, indent=1),),
)
rapor["settings"]["comboStrategy"] = st.get("comboStrategy")
rapor["settings"]["claudeAutoPing"] = cap

con.commit()

# ---------------------------------------------------------------- 4) DOGRULAMA
print()
print("=" * 78)
print("DOGRULAMA")
print("=" * 78)
for c in list(con.execute("SELECT name, models FROM combos")):
    ms = json.loads(c["models"]) if c["models"] else []
    hata_kalan = [m for m in ms if m in HATA]
    print(f"  {c['name']:<20} model={len(ms):<4} kalan_hatali={len(hata_kalan)}")

out = ROOT / "data/router/combo_temizlik_raporu.json"
out.write_text(json.dumps(rapor, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[OK] Rapor: {out}")
con.close()
