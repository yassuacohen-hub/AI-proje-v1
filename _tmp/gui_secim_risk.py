# -*- coding: utf-8 -*-
"""RISK OLCUMU: GUI listesinde ekledigim Evren model id'leri 9Router'da da var mi?
GUI secince model AKIF saglayiciya (9router) gider; 9Router'da yoksa 404 yer."""
import json
import urllib.request

K9 = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
ARANAN = ["gpt-5.6-luna", "gpt-5.6-terra", "fullclaude",
          "openrouter/nvidia/nemotron-3.5-lightning:free",
          "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
          "bzl/auto:free", "deepseek-v4.1-flash", "glm-5.3", "qwen3.8-flash-next"]

req = urllib.request.Request("http://localhost:20128/v1/models",
                             headers={"Authorization": "Bearer " + K9})
with urllib.request.urlopen(req, timeout=40) as r:
    idler = {m.get("id") for m in json.load(r).get("data", [])}
print("9Router model sayisi:", len(idler))
for a in ARANAN:
    var = a in idler
    print(("VAR  " if var else "YOK  ") + a)
    if not var:
        # benzer seyler oner
        parca = a.split("/")[-1]
        aday = [i for i in idler if parca.split(":")[0] in str(i)][:4]
        print("     benzer:", ", ".join(map(str, aday)) or "-")
