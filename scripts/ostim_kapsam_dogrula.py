"""D-286: OSTIM liste kapsam dogrulamasi (8.473 vs 8.313 farki).

Dilekce yazilirken olculdu: site 'Toplam 8473 sonuç bulundu' diyor,
bizim listemizde 8.313 kayit var (8.313 BENZERSIZ slug, tekrar yok).
160 firma farki nereden geliyor? Izin dilekcesi YANLIS RAKAM
icermemeli; once farkin kaynagi bulunur.

TEKNIK KONTROL: yalnizca liste sayfalari okunur (robots.txt izinli).
Detay sayfalari TIKLANMAZ. Kullanim:
    python scripts/ostim_kapsam_dogrula.py
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import time
from typing import Optional

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
LISTE = KOK / "data" / "ostim" / "firmalar_full.jsonl"
CIKTI = KOK / "data" / "ostim" / "kapsam_dogrulama.json"
TABAN = "https://ostim.org.tr/firmalar"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
SAGNUME = re.compile(r"Toplam\s*([\d.,]+)\s*sonu")
LINK = re.compile(r'href="(/firmalar/([a-z0-9][a-z0-9\-]*))"')


def slugleri(html_metni: str) -> set[str]:
    """Sayfadaki firma detay linklerinden slug kumesi."""
    return {m[1] for m in LINK.findall(html_metni)}


def sayfala(c: httpx.Client, sayfa: int) -> Optional[set[str]]:
    try:
        r = c.get(TABAN, params={"page": sayfa})
    except Exception as e:
        print(f"  sayfa {sayfa}: HATA {type(e).__name__}")
        return None
    if r.status_code != 200:
        print(f"  sayfa {sayfa}: HTTP {r.status_code}")
        return None
    return slugleri(html.unescape(r.text))


def main() -> int:
    kayitlar = [json.loads(x) for x in LISTE.read_text(
        encoding="utf-8").splitlines() if x.strip()]
    bizim = {k.get("slug") for k in kayitlar if k.get("slug")}
    print(f"Bizim liste: {len(kayitlar)} kayit | {len(bizim)} benzersiz slug")

    bulunan: dict[str, set[str]] = {}
    ilan_sayisi: Optional[int] = None
    with httpx.Client(headers={"User-Agent": UA}, timeout=30,
                      follow_redirects=True) as c:
        r = c.get(TABAN)
        m = SAGNUME.search(html.unescape(r.text))
        if m:
            ilan_sayisi = int(m.group(1).replace(".", ""))
            print(f"Site ilani (1. sayfa): 'Toplam {ilan_sayisi} sonuç'")

        print("Örnek sayfalar taranıyor (28, 29, 30 — listenin sonu):")
        for pg in (28, 29, 30):
            s = sayfala(c, pg)
            if s is None:
                continue
            bulunan[pg] = s
            yeni = s - bizim
            print(f"  sayfa {pg}: {len(s)} slug | bizde olmayan: {len(yeni)}")
            for sl in sorted(yeni)[:5]:
                print(f"      YENI: {sl}")
            time.sleep(2.0)          # P-3 nazik gecikme

    tum_canli = set().union(*bulunan.values()) if bulunan else set()
    rapor = {
        "bizim_kayit": len(kayitlar),
        "bizim_benzersiz_slug": len(bizim),
        "site_ilan_sayisi": ilan_sayisi,
        "fark": (ilan_sayisi - len(bizim)) if ilan_sayisi else None,
        "kontrol_edilen_sayfalar": {str(k): len(v)
                                    for k, v in bulunan.items()},
        "kontrol_sayfalarda_bizde_olmayan":
            sorted(tum_canli - bizim)[:50],
        "kontrol_sayfa_sayisi": len(bulunan),
    }
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    print(f"\nFARK: {rapor['fark']} firma")
    print(CIKTI)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
