# -*- coding: utf-8 -*-
"""AG TESİSİ — masaüstü ChatGPT/Codex uygulaması OpenAI sunucularına ulaşıyor mu?
Küçük kardeş analojisi: mutfağa (9Router) giden yol açık, ama dışarıdaki
büyük markete (OpenAI) giden köprü kapaliysa sepette hiçbir şey görünmez.
Kimlik DOĞRULAMA uçları da ölçülür: 'authenticated account' hatası buradan gelir."""
import json
import ssl
import time
import urllib.request

UG = [
    ("9Router (yerel mutfak)", "http://localhost:20128/health"),
    ("Evren API (yerel ortak)", "https://evren-llmapi.ssyz.org.tr/v1/models"),
    ("OpenAI kimlik dogrulama", "https://auth.openai.com/.well-known/openid-configuration"),
    ("OpenAI ana sayfa", "https://chatgpt.com/cdn/robots.txt"),
    ("OpenAI API", "https://api.openai.com/v1/models"),
    ("OpenAI backend (Codex GUI)", "https://chatgpt.com/backend-api/codex/models"),
    ("Internet kontrol (cloudflare)", "https://1.1.1.1/cdn-cgi/trace"),
]

for ad, url in UG:
    t = time.time()
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            sn = round(time.time() - t, 1)
            print(f"ULASTI  {r.status:>3}  {sn:>5}s  {ad}")
    except urllib.error.HTTPError as e:
        sn = round(time.time() - t, 1)
        # 401/403 = sunucuya ULASILDI, kimlik istiyor (ag iyi demek)
        ulasildi = "ULASILDI(kimlik istiyor)" if e.code in (401, 403) else f"HTTP {e.code}"
        print(f"{ulasildi:<24} {sn:>5}s  {ad}")
    except Exception as e:  # noqa: BLE001
        sn = round(time.time() - t, 1)
        tip = type(e).__name__
        print(f"ULASILAMADI {tip:<18} {sn:>5}s  {ad}  {str(e)[:60]}")
