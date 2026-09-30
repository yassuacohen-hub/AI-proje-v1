# -*- coding: utf-8 -*-
"""VERI-LONCA-FIRMA-01 — /FirmaBilgisi alan cikarimi (id etiketleriyle).

Sayfanin KENDI id etiketleri kullanilir (regex tahmini DEGIL):
  #firmaAdi #ilAdi #firmaAdresi #firmaTel #firmaFaks ...

D-216: bulunamayan alan None yazilir, uydurulmaz.
KAHIN 2026-09-30 izin verdi: tam tarama yapilabilir.
"""
from __future__ import annotations

import html as _html
import json
import pathlib
import re
import sys
import time
from datetime import datetime, timezone

import httpx

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

TABAN = "https://lonca.gov.tr"
CIKTI = KOK / "data" / "pilots" / "VERI-LONCA-FIRMA-01"
CIKTI.mkdir(parents=True, exist_ok=True)

#: KAHIN'in ekran goruntusunden kopyaladigi TAM Id (URL-kodlu).
ID_TAM = ("GUlaiBriA%2BpzS%2FLpqr6uYKPmeSqOSPYFlh3E5OjL5tlhbihfLlr0VvuqySlFUOW7e"
          "kyZcaf3tzXUOXSik827xVYC286iPnapNecagyOWGfmbbbNxVi6WbytSGLQgDZQkuXq1Oco%3D")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
HDR = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

#: Sayfadaki alan id'leri (ham HTML'den olculdu, 2026-09-30).
ALAN_ID = {
    "unvan": "firmaAdi",
    "il": "ilAdi",
    "adres": "firmaAdresi",
    "telefon": "firmaTel",
    "faks": "firmaFaks",
    "eposta": "firmaEposta",
    "web": "firmaWeb",
}


def _coz(h: str) -> str:
    return _html.unescape(h)


def _metin(h: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s).replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


def _cx() -> httpx.Client:
    return httpx.Client(timeout=40, follow_redirects=True, headers=HDR)


def id_metni(h: str, kimlik: str) -> str | None:
    m = re.search(rf'id="{kimlik}"[^>]*>(.*?)</', h, re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def alanlar(h: str) -> dict:
    """7 alan, sayfanin kendi id etiketleriyle."""
    out = {k: id_metni(h, v) for k, v in ALAN_ID.items()}
    # Yedek: e-posta/web id farkli ise metinden yakala
    if not out["eposta"]:
        m = re.search(r"([\w.\-]+@[\w.\-]+\.\w{2,})", h)
        out["eposta"] = m.group(1) if m else None
    if not out["web"]:
        m = re.search(r"(www\.[\w.\-]+\.\w{2,4})", h)
        out["web"] = m.group(1) if m else None
    return out


def urun_katalogu(h: str) -> list[list[str]]:
    """#tbl satirlari = firmanin URETIM URUNLERI."""
    out = []
    m = re.search(r'id="tbl".*?</table>', h, re.S | re.I)
    if not m:
        return out
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), re.S | re.I):
        hucre = [re.sub(r"\s+", " ", _metin(x)).strip()
                 for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
        hucre = [x for x in hucre if x]
        if hucre:
            out.append(hucre)
    return out


def firma_ac(gid: str) -> dict:
    with _cx() as cx:
        cx.get(TABAN)
        t0 = time.time()
        r = cx.get(f"{TABAN}/FirmaBilgisi?Id={gid}")
        sn = round(time.time() - t0, 2)
    h = _coz(r.text)
    return {"id": gid, "http": r.status_code, "bayt": len(r.text),
            "sure_sn": sn, "alanlar": alanlar(h),
            "urun_katalogu": urun_katalogu(h),
            "tablo": len(re.findall(r"<table", h, re.I)),
            "zaman": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    o = firma_ac(ID_TAM)
    print("== /FirmaBilgisi TAM Id ==")
    print("HTTP %d | %d bayt | %.2f sn | tablo=%d"
          % (o["http"], o["bayt"], o["sure_sn"], o["tablo"]))
    print("\n--- ALANLAR ---")
    for k in ("unvan", "il", "adres", "telefon", "faks", "eposta", "web"):
        print("   %-8s %s" % (k, o["alanlar"].get(k) or "(YOK)"))
    print("\n--- URUN KATALOGU: %d satir ---" % len(o["urun_katalogu"]))
    for s in o["urun_katalogu"]:
        print("   ", " | ".join(s)[:110])

    (CIKTI / "firma_ornek_alanlar.json").write_text(
        json.dumps(o, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nkaydedildi:", CIKTI / "firma_ornek_alanlar.json")
