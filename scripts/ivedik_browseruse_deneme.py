"""D-300: IVEDIK erisimi - Browser-Use ile TEK SAYFA kanit denemesi.

KAHIN sordu: "Playwright / cerez-tarayici taklidi / brave use cozmez mi?"

CEVAP: Browser-Use SDK `.env`'de KURULU ve API anahtari GEÇERLI.
Bu betik TEK bir sayfayi acmayi dener:
  1. Cloudflare "I'm not a robot" ekrani gecilebiliyor mu?
  2. Geciliyorsa gercekten FIRMA SAYISI okunabiliyor mu?
MALIYET: gecmis kosuda 1 sayfa = 0,016 USD (~2 dk) olculmustu.
Bu yuzden once TEK SAYFA; sonucu olcmeden toplu cekim YAPILMAZ.

ONCEDEN BILINEN (D-270 raporu): tarayici ajani sayfayi 200 ile acabilir
ama ICERIGI CEKMEYEBILIR. Bu yuzden yalniz HTTP koduna degil, GOVDE
icerigine bakilir.

Kullanim: python scripts/ivedik_browseruse_deneme.py
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "ivedik" / "browseruse_deneme.json"
URL = "https://www.ivedikosb.org.tr/firmalar/"

TASLAK = (
    "Open {url} and report ONLY these facts, no speculation:\n"
    "1. Did a Cloudflare 'I am not a robot' / security verification page "
    "appear, or did the company list load directly?\n"
    "2. What is the TOTAL number of companies shown (any counter like "
    "'Toplam N sonuc')?\n"
    "3. How many company cards are visible on this first page?\n"
    "4. Quote the first 3 company names EXACTLY as written.\n"
    "If the page is blocked or empty, say BLOCKED and nothing else."
)


def _anahtar() -> str:
    env = KOK / ".env"
    if env.is_file():
        for satir in env.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
            if satir.strip().startswith("BROWSER_USE_API_KEY"):
                deger = satir.split("=", 1)[1].strip().strip("\"'")
                if deger:
                    return deger
    for k in ("BROWSER_USE_API_KEY", "BROWSERUSE_API_KEY"):
        if os.environ.get(k):
            return os.environ[k]
    return ""


def main() -> int:
    api = _anahtar()
    if not api:
        print("HATA: BROWSER_USE_API_KEY yok (.env veya ortam degiskeni)")
        return 1
    print(f"API anahtari: {api[:10]}... (uzunluk {len(api)})")

    try:
        from browser_use_sdk import BrowserUse
    except ImportError as e:
        print(f"HATA: browser-use-sdk kurulu degil ({e})")
        return 1

    print(f"Hedef: {URL}")
    print("Tek sayfa deneniyor (maliyet: gecmis olcumde ~0,016 USD)...")
    t0 = time.time()
    try:
        bu = BrowserUse(api_key=api, timeout=180.0)
        sonuc = bu.run(
            TASLAK.format(url=URL),
            start_url=URL,
            max_steps=8,
            allowed_domains=["ivedikosb.org.tr"],
        )
    except Exception as e:
        print(f"HATA ({type(e).__name__}): {e}")
        return 2
    sure = time.time() - t0

    # Sonucu olce
    metin = json.dumps(sonuc, ensure_ascii=False, default=str)
    if isinstance(sonuc, dict):
        for k in ("final_result", "result", "output", "text", "extracted"):
            if isinstance(sonuc.get(k), str):
                metin = sonuc[k]
                break
    print("\n" + "=" * 62)
    print(f"SONUC ({sure:.0f} sn)")
    print("=" * 62)
    print(str(metin)[:1500])

    # ENGEL KONTROLU: govdede gercekten firma var mi?
    govde = str(metin)
    engelli = bool(re.search(r"robot|verification|cloudflare|blocked|"
                             r"güvenlik|doğrulama", govde, re.I))
    firma = bool(re.search(r"(\d{2,6})\s*(sonuç|sonuc|firma|result)",
                           govde, re.I))
    rakam = re.findall(r"\b(\d{2,6})\b", govde)

    karar = {
        "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "url": URL,
        "sure_saniye": round(sure, 1),
        "engel_isareti": engelli,
        "firma_sayisi_bulundu": firma,
        "cikan_rakamlar": rakam[:15],
        "ham_sonuc": str(metin)[:3000],
    }
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(json.dumps(karar, ensure_ascii=False, indent=2),
                     encoding="utf-8")

    print("\n=== DEGERLENDIRME ===")
    if engelli and not firma:
        print("  SONUÇ: ENGEL KALDI. Browser-Use da gecemedi.")
    elif firma:
        print("  SONUÇ: SAYFA ACILDI ve firma sayisi bulundu -> "
              "TEKILLASTIRMA YOLU VAR.")
        print("  DIKKAT (D-270): 200 donmesi icerik cekildigi anlamina "
              "gelmez; yukaridaki rakamlar GOVDEN okundu.")
    else:
        print("  SONUÇ: BELIRSIZ. Sayfa acildi mi belirsiz - "
              "rapor dosyasina bak.")
    print(f"\n{CIKTI}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
