"""OSB/ATO listelerinin ARKA PLAN ucunu bulur (D-281).

Tespit: sayfa HTML'inde `tablo_satir=0` → firma listesi **JavaScript ile
yukleniyor**. Bu, otomasyon icin aslında IYI haber: JSON/API ucu varsa
tarama cok hizli ve yasal olur.

Yontem: sayfanin script'lerini ve inline JS'i tarayip API/fetch/ajax
ucu ipuclarini cikaririz. Sadece OKUMA — sayfaya istek atilmaz.

Kullanim: python scripts/osb_api_avla.py
"""
from __future__ import annotations

import json
import pathlib
import re

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "osb_api_adaylari.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

HEDEFLER = [
    ("OSTIM firmalar", "https://ostim.org.tr/firmalar"),
    ("ATO uye sirketleri", "https://www.atonet.org.tr/uye-sirketler"),
]

#: JS icinde aranan desenler: REST/API ucu, fetch/ajax cagrisi.
API_DESEN = re.compile(
    r"""(?:https?://[^\s"'<>]+|/[\w\-/]+)"""
    r"""(?:api|Api|API)[\w/\-.]*"""
    r"""|[\w\-./]*(?:firma|uye|member|sirket|kurum|search|ara)[\w\-./]*\.(?:json|aspx|ashx|ashx|php|asmx)""",
    re.I,
)
FETCH_DESEN = re.compile(
    r"""(?:fetch|axios|ajax|\$\.get|\$\.post)\s*\(\s*['"`]([^'"`]{4,140})['"`]""",
    re.I,
)
DATA_DESEN = re.compile(
    r"""(?:var|let|const)\s+(\w*(?:data|Data|liste|Liste|firm|uye|items|sonuc)\w*)\s*=""",
)


def scriptler(html: str) -> list[str]:
    """Sayfadaki tum script govdelerini birlestirir."""
    parcalar = re.findall(r"<script[^>]*>(.*?)</script>", html,
                          re.S | re.I)
    return [p for p in parcalar if p.strip()]


def src_scriptler(html: str) -> list[str]:
    return re.findall(r'<script[^>]+src="([^"]+)"', html, re.I)


def analiz(ad: str, url: str) -> dict:
    o = {"ad": ad, "url": url}
    try:
        r = httpx.get(url, timeout=30, headers={"User-Agent": UA},
                      follow_redirects=True)
        html = r.text
        o["http"] = r.status_code
        inline = scriptler(html)
        o["inline_script_adedi"] = len(inline)
        o["harici_script"] = src_scriptler(html)[:10]

        tum = "\n".join(inline)
        o["api_adaylari"] = sorted(set(API_DESEN.findall(tum)))[:25]
        o["fetch_cagrilari"] = sorted(set(FETCH_DESEN.findall(tum)))[:25]
        o["data_degiskenleri"] = sorted(set(DATA_DESEN.findall(tum)))[:15]
        o["ajax_kw"] = {
            k: tum.lower().count(k)
            for k in ("fetch", "axios", "ajax", "datatable", "axios.post")
        }
        # Web servis (.asmx/.ashx/.svc) izleri
        o["servis_izleri"] = sorted(
            set(re.findall(r'["\']([\w/\-.]+\.(?:asmx|ashx|svc|php))["\']',
                           html, re.I))
        )[:15]
    except Exception as e:
        o["hata"] = f"{type(e).__name__}: {e}"
    return o


if __name__ == "__main__":
    sonuclar = [analiz(a, u) for a, u in HEDEFLER]
    CIKTI.write_text(json.dumps(sonuclar, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    for s in sonuclar:
        print("=" * 60)
        print(s["ad"], "| inline script:", s.get("inline_script_adedi"))
        print("  api adaylari :", s.get("api_adaylari")[:8])
        print("  fetch cagrilari:", s.get("fetch_cagrilari")[:8])
        print("  servis izleri  :", s.get("servis_izleri")[:6])
        print("  ajax kw       :", s.get("ajax_kw"))
    print(CIKTI)
