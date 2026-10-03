# -*- coding: utf-8 -*-
"""9Router web sağlayıcı ölçümü — tekrar koşulabilir (D-260: beyan kanıt değil, ölç).

Kullanım (proje kökünden):
    python scripts/saglayici_olc.py liste          # /v1/models/web gerçek kayıtlı sağlayıcılar
    python scripts/saglayici_olc.py ara            # her arama sağlayıcısı × soru
    python scripts/saglayici_olc.py getir          # her fetch sağlayıcısı × sayfa
    python scripts/saglayici_olc.py patent         # site:patents.google.com firma araması
    python scripts/saglayici_olc.py ara "kendi sorum"

Sonuç satırı biçimi: `AD  süre  n=sonuç  gov=.gov.tr sayısı  sag=combo'nun düştüğü sağlayıcı  ilk=ilk URL`.
Kredi uyarısı: `serper` ücretli (2.499 kredi, 2026-10-03); her koşu 1 kredi yer.
Son ölçüm raporu: docs/SAGLAYICI_OLCUMU_2026-10-03.md
"""
from __future__ import annotations

import io
import re
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "src")

from company_master.gateway.ninerouter_client import NineRouterError, get_client  # noqa: E402

ARAMA = ("search-combo", "brave", "tavily", "exa", "searchapi", "serper", "ollama-search")
FETCH = ("fetch-combo", "tavily", "firecrawl", "jina-reader", "exa")
SAYFALAR = {
    "DMO": "https://www.dmo.gov.tr/Ihale/Liste?type=1",
    "RG": "https://www.resmigazete.gov.tr/",
}


def _kisa(e: Exception) -> str:
    return str(e)[:110].replace("\n", " ")


def liste() -> None:
    nr = get_client()
    for m in nr.list_models("web"):
        print(f"{m.get('id'):22} {m.get('owned_by'):10} {m.get('kind')}")


def ara(soru: str, saglayicilar=ARAMA) -> None:
    nr = get_client()
    print("SORU:", soru)
    for p in saglayicilar:
        t = time.time()
        try:
            v = nr.web_search(soru, provider=p, max_results=5)
            urls = [r.get("url", "") for r in (v.get("results") or [])]
            gov = sum(".gov.tr" in u for u in urls)
            print(f"{p:14} {time.time()-t:5.1f}s n={len(urls)} gov={gov} sag={v.get('provider')} ilk={urls[:1]}")
        except NineRouterError as e:
            print(f"{p:14} HATA {_kisa(e)}")


def getir() -> None:
    nr = get_client()
    for ad, url in SAYFALAR.items():
        print("SAYFA:", ad, url)
        for p in FETCH:
            t = time.time()
            try:
                v = nr.web_fetch(url, provider=p, max_characters=20000)
                icerik = v.get("content") or ""
                ihale = len(set(re.findall(r"\b179\d\d\b", icerik)))  # DMO ihale no kalıbı
                print(f"  {p:14} {time.time()-t:5.1f}s kr={len(icerik):6} ihale={ihale} sag={v.get('provider')}")
            except NineRouterError as e:
                print(f"  {p:14} HATA {_kisa(e)}")


def patent(firma: str = "ASELSAN") -> None:
    # ponytail: SearchAPI'nin google_patents motoru 9Router'dan geçmiyor (engine düşüyor);
    # site: operatörü ile her sağlayıcıda çalışır. Doğrudan SearchAPI anahtarı 401 (2026-10-03).
    ara(f"site:patents.google.com {firma}", ("brave", "search-combo", "serper"))


def main(argv: list[str]) -> int:
    mod = argv[1] if len(argv) > 1 else "liste"
    arg = " ".join(argv[2:])
    if mod == "liste":
        liste()
    elif mod == "ara":
        ara(arg or "DMO ihale listesi ekim 2026")
    elif mod == "getir":
        getir()
    elif mod == "patent":
        patent(arg or "ASELSAN")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
