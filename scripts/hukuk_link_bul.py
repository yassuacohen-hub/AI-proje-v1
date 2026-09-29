"""D-281: Dogru yasal metin ve VKN adreslerini BULUR (tahmin etmez).

Onceki turda URL'ler tahmin edildi ve 404/soft-404 dondu. Bu arac:
  1. Ana sayfa HTML'inden gercek linkleri cikarir (portal menusunden)
  2. Adaylari tek tek dener
  3. Soft-404 tespiti yapar (HTTP 200 ama icerik ana sayfayla ayni)

Kullanim: python scripts/hukuk_link_bul.py
"""
from __future__ import annotations

import json
import pathlib
import re

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "hukuk_link_bul.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: (etiket, ana sayfa)
KOKLER = [
    ("OSTIM", "https://ostim.org.tr/"),
    ("ATO", "https://www.atonet.org.tr/"),
    ("ASO", "https://www.aso.org.tr/"),
]

#: Aranacak kelimeler (hedef: sart/kosul/gizlilik/kvkk/uyum)
HEDEF = re.compile(
    r"(?:sart|sözl?[öo]?[sş]ü|ko[şs]ul|gizlilik|kvkk|aydinlatma|aydınlatma"
    r"|uyum|mevzuat|politika|r[üu]h[üu]s|dis)",
    re.I,
)


def duz(html: str) -> str:
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()


def bagli_linkler(html: str, kok: str) -> list[str]:
    tum = re.findall(r'href="([^"#]+)"', html, re.I)
    cikti = []
    for u in tum:
        if u.startswith("http"):
            if kok not in u:
                continue
            u = u
        elif not u.startswith("/"):
            continue
        if HEDEF.search(u):
            cikti.append(u)
    return sorted(set(cikti))


def soft404(kok_html: str, aday_html: str) -> bool:
    """HTTP 200 ama icerik ana sayfayla AYNI mi? (yapisal soft-404)

    D-282 DUZELTME: ilk surum ilk 400 karakteri karsilastiriyordu; ATO/ASO
    sablon sayfalarinda ortak menu blogu ayni oldugu icin **yanlis pozitif**
    uretiyordu. Artik baslik ve govde *benzersizligi* olcuyoruz.
    """
    a, b = duz(kok_html), duz(aday_html)
    if not b or len(b) < 200:
        return True
    if a[:400] == b[:400]:
        return True
    # Benzersizlik: aday sayfada kok sayfada OLMAYAN anlamli bir cumle var mi?
    parcalar = [p for p in re.split(r"[|.]", b) if 40 < len(p) < 200]
    yeni = [p for p in parcalar if p not in a]
    return len(yeni) < 2


if __name__ == "__main__":
    rapor = {}
    for ad, kok in KOKLER:
        kayit = {"kok": kok, "hedef_linkler": [], "test_edilen": []}
        try:
            r0 = httpx.get(kok, timeout=30, headers={"User-Agent": UA},
                           follow_redirects=True)
            h0 = r0.text
            adaylar = bagli_linkler(h0, kok)
            kayit["hedef_linkler"] = adaylar[:25]
            for u in adaylar[:25]:
                tam = u if u.startswith("http") else kok.rstrip("/") + u
                try:
                    r = httpx.get(tam, timeout=20, headers={"User-Agent": UA},
                                  follow_redirects=True)
                    t = duz(r.text)
                    kayit["test_edilen"].append(
                        {
                            "url": tam,
                            "http": r.status_code,
                            "bayt": len(r.content),
                            "metin": len(t),
                            "soft404": soft404(h0, r.text),
                            "kavramlar": {
                                k: bool(re.search(k, t, re.I))
                                for k in (
                                    r"ticari", r"kopyala", r"izin", r"ücret|ucret",
                                    r"KVKK", r"6698", r"otomasyon|robot|scrap",
                                )
                            },
                            "ornek": t[:300],
                        }
                    )
                except Exception as e:
                    kayit["test_edilen"].append(
                        {"url": tam, "hata": str(e)[:80]}
                    )
        except Exception as e:
            kayit["hata"] = str(e)[:120]
        rapor[ad] = kayit
        print("=" * 50, ad)
        for t in kayit["test_edilen"][:8]:
            print("  ", t.get("http"), t["url"][:88],
                  "soft404" if t.get("soft404") else "ICERIK_OK")
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print(CIKTI)
