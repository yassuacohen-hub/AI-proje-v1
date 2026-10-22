#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SSH port-forward ile VDS 9Router'a erisim testi (A yolunun saglam hali).

Tunel (Cloudflare 1010) bot-engelli oldugu icin dogrudan HTTPS calismiyor.
SSH -L ile bu PC'de 20129 -> VDS:20128 portu acilir; ayarlar bu porta baglanir.
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

KEY = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
HOST = "huginn-vds"
YEREL_PORT = 20129  # lokal 9Router 20128'de; carismasin diye 20129 kullaniyoruz


def port_acik_mi():
    """Tunel zaten ayakta mi? (bosuna ikinci tuncel acma)"""
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{YEREL_PORT}/v1/models",
            headers={"Authorization": f"Bearer {KEY}"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status == 200
    except Exception:
        return False


def model_say(proxy_port):
    req = urllib.request.Request(
        f"http://127.0.0.1:{proxy_port}/v1/models",
        headers={"Authorization": f"Bearer {KEY}"},
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.loads(r.read().decode("utf-8"))
    ids = [m.get("id") for m in d.get("data", [])]
    combo = [i for i in ids if i in {
        "yasu-9router", "claude-claudecombo", "claude_sadece",
        "fullclaude", "mimir-dis", "fetch-combo", "search-combo"}]
    return ids, combo


print("=== 1) Tunel zaten acik mi? ===")
hazir = port_acik_mi()
print("ACIK" if hazir else "KAPALI - yeni tunel denenecek")

proc = None
if not hazir:
    print("\n=== 2) SSH -L tuneli aciliyor ===")
    proc = subprocess.Popen(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
         "-o", "ExitOnForwardFailure=yes", "-N",
         "-L", f"{YEREL_PORT}:127.0.0.1:20128", HOST],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    for i in range(12):
        time.sleep(1.5)
        if port_acik_mi():
            print(f"  tunel {i+1}s icinde AYAKTA")
            break
    else:
        err = b""
        try:
            proc.kill()
            _, err = proc.communicate(timeout=5)
        except Exception:
            pass
        print("  TUNEL ACILAMADI:", (err or b"")[:300].decode("utf-8", "ignore"))
        raise SystemExit(2)

print("\n=== 3) VDS modeli listesi (tunel uzerinden) ===")
try:
    ids, combo = model_say(YEREL_PORT)
    print(f"  VDS toplam model : {len(ids)}")
    print(f"  VDS combo'lar    : {combo}")
except Exception as e:
    print("  HATA:", type(e).__name__, str(e)[:200])
    raise SystemExit(3)

print("\n=== 4) Chat smoke testi (yasu-9router) ===")
body = json.dumps({
    "model": "yasu-9router",
    "messages": [{"role": "user", "content": "Tek kelimeyle yanitla: calisiyor mu?"}],
    "max_tokens": 20,
    "stream": False,
}).encode()
req = urllib.request.Request(
    f"http://127.0.0.1:{YEREL_PORT}/v1/chat/completions",
    data=body,
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.loads(r.read().decode("utf-8"))
    secilen = d.get("model")
    metin = ((d.get("choices") or [{}])[0].get("message") or {}).get("content", "")
    print(f"  OK | yanit model: {secilen} | metin: {str(metin)[:60]!r}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}:", e.read().decode("utf-8", "ignore")[:200])
except Exception as e:
    print("  HATA:", type(e).__name__, str(e)[:200])

print("\n(BILGI) Tunel su an acik: 127.0.0.1:%d -> VDS:20128" % YEREL_PORT)
if proc:
    print("Tunel bu script kapaninca KAPATILACAK (test modu).")
