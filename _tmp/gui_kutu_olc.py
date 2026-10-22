# -*- coding: utf-8 -*-
"""SAG ALTI KUTUDA NEDEN TEK MODEL VAR? 3 olcum:
 (1) GUI'yi yeniden baslatabilmek icin ChatGPT.exe TAM yolu
 (2) models_cache'teki model objelerinin ERISIM alanlari (kisi: 'list' gorunur
     olsalar da bir baska alan secimi kilitleyebilir mi?)
 (3) oturum kartinda 'Work/plan' yetkisi var mi (scope alani) — GUI listesi
     OpenAI hesabindan geliyorsa bos scope = tek model demek
Degerler YAZILMAZ (D-380): yalniz alan adi + kisa tip/uzunluk bilgisi."""
import base64
import json
import subprocess
import tomllib
import urllib.request
from pathlib import Path

K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"

print("[1] Codex masaustu uygulamasinin tam yolu")
try:
    o = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process ChatGPT -ErrorAction SilentlyContinue | "
                        "Select-Object -ExpandProperty Path -Unique"],
                       capture_output=True, text=True, timeout=60)
    yollar = [s.strip() for s in o.stdout.splitlines() if s.strip()]
    print("    bulunan exe:", yollar or "YOK (calismiyor olabilir)")
except Exception as e:  # noqa: BLE001
    yollar = []
    print("    olcum hatasi:", str(e)[:60])

print("\n[2] models_cache model objelerinin alanlari (secimi kilitleyen alan var mi?)")
c = json.loads((Path.home() / ".codex/models_cache.json").read_text(encoding="utf-8"))
m0 = next((m for m in c["models"] if m.get("visibility") != "hide"), c["models"][0])
ILGINC = ["slug", "visibility", "supported_in_api", "availability_nux",
          "priority", "upgrade", "service_tiers", "additional_speed_tiers",
          "default_reasoning_level"]
for a in ILGINC:
    v = m0.get(a, "<YOK>")
    print(f"    {a:<24}{str(v)[:56]}")
print("    diger alan adlari:", [k for k in m0 if k not in ILGINC][:12])

print("\n[3] oturum kartinda yetki (scope) var mi")
d = json.loads((Path.home() / ".codex/auth.json").read_text(encoding="utf-8"))
tok = (d.get("tokens") or {}).get("id_token") or ""
if tok:
    parca = tok.split(".")[1]
    parca += "=" * (-len(parca) % 4)
    c2 = json.loads(base64.urlsafe_b64decode(parca))
    auth = c2.get("https://api.openai.com/auth") or {}
    print("    auth alanlari:", sorted(auth.keys()))
    print("    chatgpt_plan_type:", auth.get("chatgpt_plan_type", "<YOK>"))
    print("    scope/scope benzeri:", [k for k in c2 if "scope" in k.lower()] or "YOK")
else:
    print("    id_token yok")

print("\n[4] config: sag alttaki secim hangi saglayiciya bagli")
with open(Path.home() / ".codex/config.toml", "rb") as f:
    cf = tomllib.load(f)
print("    model_provider:", cf.get("model_provider"), "| model:", cf.get("model"))
print("    => GUI'de diger katalog modelleri secilebilir mi? Bunu GUI kararlastrir;")
print("       kanit icin tiklama sonrasi config'e ne yazildigini olceriz.")
