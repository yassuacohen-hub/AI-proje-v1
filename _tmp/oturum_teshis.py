# -*- coding: utf-8 -*-
"""CHATGPT WORK vs CODEX ayrimi — oturum kaniti.
DEGERLER YAZILMAZ (D-380): yalniz alan adlari, token tipi ve son-kullanim/sure bilgisi."""
import base64
import datetime as dt
import json
import time
from pathlib import Path

AUTH = Path.home() / ".codex" / "auth.json"
d = json.loads(AUTH.read_text(encoding="utf-8"))
print("auth.json ALANLARI:", sorted(d.keys()))
for k, v in d.items():
    if isinstance(v, dict):
        print(f"  {k} -> alt alanlar: {sorted(v.keys())}")

tok = None
for yol in [("tokens", "id_token"), ("tokens", "access_token")]:
    try:
        tok = d[yol[0]][yol[1]]
        kaynak = ".".join(yol)
        break
    except Exception:  # noqa: BLE001
        continue

if not tok:
    print("OKUNABILIR JWT YOK (API key ile mi girildi?) -> alan: OPENAI_API_KEY var mi:",
          bool(d.get("OPENAI_API_KEY")))
else:
    parca = tok.split(".")[1]
    parca += "=" * (-len(parca) % 4)
    claims = json.loads(base64.urlsafe_b64decode(parca))
    simdi = int(time.time())
    print(f"JWT kaynagi: {kaynak}")
    print("  claim adlari:", sorted(claims.keys()))
    for ad in ("exp", "iat", "auth_time"):
        if ad in claims:
            t = dt.datetime.fromtimestamp(claims[ad])
            print(f"  {ad}: {t:%Y-%m-%d %H:%M}  ({'SÜRESİ DOLMUŞ' if ad == 'exp' and claims[ad] < simdi else 'gecerli'})")
    yetkiler = claims.get("authorization", {}).get("scopes") or claims.get("scope")
    print("  yetkiler:", yetkiler)
    org = claims.get("https://api.openai.com/organization") or {}
    print("  org plan alanlari:", sorted(org.keys()) if isinstance(org, dict) else "-")
    plan = claims.get("https://api.openai.com/profile") or {}
    print("  profil alanlari:", sorted(plan.keys()) if isinstance(plan, dict) else "-")
    ws = claims.get("https://api.openai.com/work_space") or {}
    print("  calisma-alani alanlari:", sorted(ws.keys()) if isinstance(ws, dict) else "-")

print("\nson islem zamani auth.json:",
      dt.datetime.fromtimestamp(AUTH.stat().st_mtime).strftime("%Y-%m-%d %H:%M"))
