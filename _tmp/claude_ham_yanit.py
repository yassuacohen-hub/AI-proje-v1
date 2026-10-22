# -*- coding: utf-8 -*-
"""'Extra data: line 1 column 597' = sunucu 200 DONDU ama govde tek JSON degil.
Bu, 401'den iyi bir haber: kimlik dogru olabilir, akis (stream) govdesi olabilir.
Ham baytlari oku + 9Router'daki anahtar envanterini MASKELI listele.
Anahtar degerleri YAZILMAZ (D-380): yalniz son 4 hane + etiket."""
import json
import sqlite3
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DB = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
S = json.loads((Path.home() / ".claude" / "settings.json").read_text(encoding="utf-8"))
ENV = S.get("env", {})

print("[1] 9Router apiKeys tablosu (MASKELI)")
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cols = [r[1] for r in con.execute("PRAGMA table_info(apiKeys)")]
print("    kolonlar:", cols)
for r in con.execute("SELECT * FROM apiKeys"):
    d = dict(r)
    cikar = []
    for k, v in d.items():
        sv = str(v)
        if any(x in k.lower() for x in ("key", "token", "secret")):
            cikar.append(f"{k}=***{sv[-4:]}({len(sv)}b)")
        else:
            cikar.append(f"{k}={sv[:28]}")
    print("    " + " | ".join(cikar))

print("\n[2] /v1/messages HAM yanit (parser yok)")
govde = {"model": "claude-claudecombo", "max_tokens": 48,
         "messages": [{"role": "user", "content": "Say CLAUDE-OK"}]}
for etiket, deger in (("API_KEY", ENV.get("ANTHROPIC_API_KEY", "")),
                      ("AUTH", ENV.get("ANTHROPIC_AUTH_TOKEN", ""))):
    for hb in ("x-api-key", "bearer"):
        h = {"anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        h.update({"x-api-key": deger} if hb == "x-api-key"
                 else {"Authorization": "***" + deger})
        req = urllib.request.Request("http://127.0.0.1:20128/v1/messages",
                                     data=json.dumps(govde).encode(), headers=h,
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                ham = r.read().decode("utf-8", "replace")
                kod = r.status
            print(f"  {etiket}/{hb}: HTTP {kod} · {len(ham)}b · {ham[:150]!r}")
        except urllib.error.HTTPError as e:
            gov = e.read().decode("utf-8", "replace")[:160]
            print(f"  {etiket}/{hb}: HTTP {e.code} · govde={gov!r}")
        except Exception as e:  # noqa: BLE001
            print(f"  {etiket}/{hb}: {str(e)[:70]}")
