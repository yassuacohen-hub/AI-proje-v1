# -*- coding: utf-8 -*-
"""PO: 'sag altta secim alani yok, 9Router yaziyor'. Olculecek 3 sey:
 (1) config.toml'da AKTIF model ne (GUI her secimde buraya yazar)
 (2) o model GUI'nin kendi kataloğunda var mi? YOKSA GUI 'Ozel' etiketi gosterir
 (3) aktif model CANLI mi (alias uzerinden cevap geliyor mu)
Anahtar degeri yazilmaz (D-380)."""
import json
import tomllib
import urllib.request
from pathlib import Path

K = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
CFG = Path.home() / ".codex" / "config.toml"
KATALOG = Path(r"c:\Huginn Data Projesi\_tmp\dbg_models.json")

with open(CFG, "rb") as f:
    d = tomllib.load(f)
prov, model = d.get("model_provider"), d.get("model")
print(f"[1] config.toml AKTIF: sag altta gorunen = {model}  (saglayici {prov})")

if KATALOG.exists():
    k = json.loads(KATALOG.read_text(encoding="utf-8"))
    modlar = k["models"] if isinstance(k, dict) and "models" in k else k
    sluglar = {m.get("slug"): m.get("display_name") for m in modlar}
    var_mi = model in sluglar
    print(f"[2] GUI kataloğunda bu isim var mi: {'VAR' if var_mi else 'YOK'}")
    print("    -> YOK ise arayuz modeli tanimayip 'Ozel' yazar (gizli/ozel etiketi)")
    gorunur = [f"{s} ({a})" for s, a in sluglar.items() if a]
    print(f"    GUI'nin tanidigi {len(sluglar)} isim: "
          + ", ".join(s for s in sluglar)[:220])
else:
    print("[2] katalog olcum dosyasi yok")


def canli(m: str) -> str:
    govde = {"model": m, "input": "Reply with exactly: OK", "stream": False}
    req = urllib.request.Request(
        "http://localhost:20128/v1/responses", data=json.dumps(govde).encode(),
        headers={"Authorization": "Bearer " + K,
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:  # noqa: BLE001
        return f"HATA {str(e)[:40]}"
    metin = " ".join([(c.get("text") or c.get("value") or "")
                      for it in (j.get("output") or [])
                      for c in (it.get("content") or [])]).strip()
    if not metin and "choices" in j:
        metin = (j["choices"][0].get("message", {}).get("content") or "").strip()
    return f"{j.get('status')} / metin: {metin[:20] or 'BOS'}"


print(f"\n[3] AKTIF model canli mi: {canli(model)}")
