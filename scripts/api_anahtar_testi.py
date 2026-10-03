# -*- coding: utf-8 -*-
"""API anahtarlarinin canli/olu durumunu tek komutla test eder.

Kullanim:
    python scripts/api_anahtar_testi.py            # hepsini test et
    python scripts/api_anahtar_testi.py openrouter # tek saglayici

Cikti: her saglayici icin AKTIF / YETKISIZ / KOTA / YOK / HATA.
Anahtar DEGERLERI asla ekrana basilmaz (yalniz son 4 karakter).

ponytail: stdlib urllib yeterli (tek seferlik tani araci); istek sayisi
artarsa veya paralellik gerekirse httpx + asyncio'ya gecilir.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
ENV_DOSYA = KOK / ".env"
ZAMAN_ASIMI = 15


def env_oku(dosya: Path = ENV_DOSYA) -> dict[str, str]:
    """`.env` dosyasini ayristirir (python-dotenv bagimliligi olmadan)."""
    veri: dict[str, str] = {}
    if not dosya.exists():
        return veri
    for satir in dosya.read_text(encoding="utf-8", errors="replace").splitlines():
        satir = satir.strip()
        if not satir or satir.startswith("#") or "=" not in satir:
            continue
        ad, _, deger = satir.partition("=")
        veri[ad.strip()] = deger.strip().strip('"').strip("'")
    return veri


# (kimlik, env_adi, url, yontem, baslik_sablonu, govde)
SAGLAYICILAR: tuple[tuple[str, str, str, str, dict[str, str], dict | None], ...] = (
    ("openrouter", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1/key",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("deepseek", "DEEPSEEK_KEY", "https://api.deepseek.com/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("openai", "OPENAI_API_KEY", "https://api.openai.com/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("anthropic", "ANTHROPIC_API_KEY", "https://api.anthropic.com/v1/models",
     "GET", {"x-api-key": "{k}", "anthropic-version": "2023-06-01"}, None),
    ("groq", "GROQ_API_KEY", "https://api.groq.com/openai/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("together", "TOGETHER_API_KEY", "https://api.together.xyz/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("xai", "XAI_API_KEY", "https://api.x.ai/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("nvidia", "NVIDIA_API_KEY", "https://integrate.api.nvidia.com/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("moonshot", "MOONSHOT_API_KEY", "https://api.moonshot.ai/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("kimi", "KIMI_API_KEY", "https://api.moonshot.ai/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("perplexity", "PERPLEXITY_API_KEY", "https://api.perplexity.ai/chat/completions",
     "POST", {"Authorization": "Bearer {k}", "Content-Type": "application/json"},
     # ponytail: Perplexity max_tokens<16 -> HTTP 400 "must be at least 16"; 1 yalanci OLU veriyordu (2026-10-03)
     {"model": "sonar", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 16}),
    ("9router", "NINEROUTER_KEY", "{NINEROUTER_URL}/v1/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("brave", "BRAVE_API_KEY", "https://api.search.brave.com/res/v1/web/search?q=test&count=1",
     "GET", {"X-Subscription-Token": "{k}", "Accept": "application/json"}, None),
    ("tavily", "TAVILY_API_KEY", "https://api.tavily.com/search",
     "POST", {"Authorization": "Bearer {k}", "Content-Type": "application/json"},
     {"query": "test", "max_results": 1}),
    ("exa", "EXA_API_KEY", "https://api.exa.ai/search",
     "POST", {"x-api-key": "{k}", "Content-Type": "application/json"},
     {"query": "test", "numResults": 1}),
    ("firecrawl", "FIRECRAWL_API_KEY", "https://api.firecrawl.dev/v1/team/credit-usage",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("cloudflare", "CLOUDFLARE_API_TOKEN", "https://api.cloudflare.com/client/v4/user/tokens/verify",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("bazarlink", "BAZARLINK_API_KEY", "{BAZARLINK_API_URL}/models",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("github", "GH_TOKEN", "https://api.github.com/user",
     "GET", {"Authorization": "Bearer {k}", "Accept": "application/vnd.github+json"}, None),
    ("ollama", "OLLAMA_API_KEY", "{OLLAMA_BASE_URL}/api/tags",
     "GET", {"Authorization": "Bearer {k}"}, None),
    ("apify", "APIFY_TOKEN", "https://api.apify.com/v2/users/me",
     "GET", {"Authorization": "Bearer {k}"}, None),
)

DURUM_ACIKLAMA = {
    401: "YETKISIZ (anahtar gecersiz/iptal)",
    403: "YASAK (yetki yok veya plan kapali)",
    402: "ODEME GEREKLI (bakiye yukle)",
    429: "KOTA/HIZ SINIRI (anahtar gecerli, limit dolu)",
    404: "ENDPOINT YOK (URL degismis olabilir)",
}


def _kredi_notu(kimlik: str, govde: bytes) -> str:
    """OpenRouter /key yanitindan bakiye ozeti cikarir."""
    if kimlik != "openrouter":
        return ""
    try:
        d = json.loads(govde).get("data", {})
    except (json.JSONDecodeError, AttributeError):
        return ""
    limit, kullanim = d.get("limit"), d.get("usage")
    if limit is None:
        return f" | kullanim ${kullanim} · limit YOK (free katman)"
    return f" | kullanim ${kullanim} / limit ${limit}"


def test_et(kimlik: str, env_adi: str, url: str, yontem: str,
            basliklar: dict[str, str], govde: dict | None,
            env: dict[str, str]) -> tuple[str, str]:
    """Tek saglayiciyi test eder -> (durum_etiketi, aciklama)."""
    anahtar = env.get(env_adi, "")
    if not anahtar:
        return "YOK", f"{env_adi} .env'de tanimsiz/bos"

    for yer_tutucu in ("NINEROUTER_URL", "OLLAMA_BASE_URL", "BAZARLINK_API_URL"):
        if "{" + yer_tutucu + "}" in url:
            taban = env.get(yer_tutucu, "").rstrip("/").removesuffix("/v1")
            if not taban:
                return "YOK", f"{yer_tutucu} .env'de tanimsiz"
            url = url.replace("{" + yer_tutucu + "}", taban)

    veri = json.dumps(govde).encode() if govde else None
    istek = urllib.request.Request(
        url, data=veri, method=yontem,
        headers={a: d.format(k=anahtar) for a, d in basliklar.items()},
    )
    try:
        with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI) as yanit:
            return "AKTIF", f"HTTP {yanit.status}{_kredi_notu(kimlik, yanit.read())}"
    except urllib.error.HTTPError as hata:
        etiket = "KOTA" if hata.code in (402, 429) else "OLU"
        return etiket, DURUM_ACIKLAMA.get(hata.code, f"HTTP {hata.code}")
    except urllib.error.URLError as hata:
        return "HATA", f"aga ulasilamadi: {hata.reason} (VPN?)"
    except OSError as hata:  # zaman asimi vb.
        return "HATA", str(hata)


def main(argv: list[str]) -> int:
    env = env_oku()
    if not env:
        print(f"HATA: {ENV_DOSYA} okunamadi.")
        return 1

    secilen = {a.lower() for a in argv[1:]}
    kayitlar = [s for s in SAGLAYICILAR if not secilen or s[0] in secilen]
    if not kayitlar:
        print(f"Bilinmeyen saglayici. Secenekler: {', '.join(s[0] for s in SAGLAYICILAR)}")
        return 1

    print(f"{'SAGLAYICI':<13} {'ENV ADI':<24} {'SON4':<6} {'DURUM':<7} ACIKLAMA")
    print("-" * 100)
    sayac: dict[str, int] = {}
    for kimlik, env_adi, url, yontem, basliklar, govde in kayitlar:
        durum, aciklama = test_et(kimlik, env_adi, url, yontem, basliklar, govde, env)
        son4 = env.get(env_adi, "")[-4:] or "-"
        sayac[durum] = sayac.get(durum, 0) + 1
        print(f"{kimlik:<13} {env_adi:<24} {son4:<6} {durum:<7} {aciklama}")

    print("-" * 100)
    print("OZET: " + " · ".join(f"{d}={n}" for d, n in sorted(sayac.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
