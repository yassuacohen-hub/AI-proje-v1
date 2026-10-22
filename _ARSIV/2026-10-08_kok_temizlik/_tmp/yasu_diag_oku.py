# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.load(io.open(r"C:/HUGINN~1/_tmp/diag.json", encoding="utf-8"))
print("anahtarlar:", list(d.keys()))
for t in d.get("testResults", []):
    print("test:", t.get("name"))
    print("mesaj:", (t.get("message") or "")[:2500])
    for k in ("assertionResults", "stdout", "stderr"):
        v = t.get(k)
        if v:
            print(k, ":", json.dumps(v, ensure_ascii=False)[:1500])

