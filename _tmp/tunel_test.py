#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VDS 9Router tünel adresini canlı test et (D-382: ölçüme dayalı)."""
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

KEY = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
TUNEL = "https://rd4l664.abc-tunnel.us/v1"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE  # tünel sertifika uyarısına takılma


def get(path, base=TUNEL):
    req = urllib.request.Request(
        base + path,
        headers={"Authorization": f"Bearer {KEY}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace"), dict(e.headers or {})
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}", {}


print("=== 1) Tünel /v1/models ===")
st, body, hdr = get("/models")
print("STATUS:", st)
print("BODY:", body[:400])
cmb = []
if st == 200:
    try:
        data = json.loads(body)
        ids = [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]
        cmb = [i for i in ids if i in {
            "yasu-9router", "claude-claudecombo", "claude_sadece",
            "fullclaude", "mimir-dis", "fetch-combo", "search-combo"}]
        print(f"TOPLAM MODEL: {len(ids)}")
        print(f"COMBO GÖRÜNEN: {cmb}")
    except Exception as e:
        print("parse hatası:", e)
else:
    print("Tünel /v1/models başarısız — A yolu için ERRİŞİM YOK")

print("\n=== 2) Tünel /api/health ===")
st2, body2, _ = get("/../api/health")
# urllib path normalizasyonu yapar; /v1../api/health -> deneme
st2b, body2b, _ = get("/health")  # /v1/health
print("STATUS /v1/health:", st2b, "| BODY:", body2b[:200])

print("\n=== 3) VDS /v1/models (karşılaştırma tabanı) ===")
# VDS içi değil; bu PC'den tünel üzerinden zaten aynı VDS. Lokal ile fark için
# ayrı local istem gerek — bunu senkron scripte bırak.
print("TAMAM")
