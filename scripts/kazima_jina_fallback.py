# -*- coding: utf-8 -*-
"""SCRAPE-003: 9Router Jina-Reader fallback (yapi bilinmeyen sayfalar).

NEDEN VAR
    Dogrudan `requests` bazi hedeflerdekirilir: DNS cozumlenmez, 403,
    zaman asimi. Kanit: `scrape_baskent` kosusunda 1 hata, sebep
    "ConnectionError". Bu hedefler **sessizce gecmez** (D-310/4) — ya
    9Router'in Jina-Reader'i ile yeniden denenir, ya da hata kuyruguna
    yazilir.

KAPSAM
    Bu bir kaziyici degil, **cekim kapisidir**: izin -> dogrudan fetch ->
    (basarisizsa) Jina fallback -> 0050'ye yaz. Ayristirma kanonik
    kaziyicinin isi olarak kalir; burada olculebilen tek sey ham icerik,
    `content_hash`, audit kaydi ve hangi yolun kullanildigi.

IZIN KURALI (D-246)
    Jina bir vekil sunucudur; **hedef site** icin izin kapisi yine
    AYNIDIR. Izin yoksa Jina denenmez. Aksi halde vekil, reddedilmis
    bir sayfayi getirirdi.

Idempotens: UNIQUE(source_url, content_hash) — ayni icerik 2. kosuda
    yazilmaz (`yazilan=0, atlanan=1`).

    python -X utf8 scripts/kazima_jina_fallback.py --kuru
    python -X utf8 scripts/kazima_jina_fallback.py <url> [<url> ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import requests  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from company_master.etl.scrape_kayit import KazimaYazici  # noqa: E402

TASK_ID = "SCRAPE-003-9ROUTER-JINA-FALLBACK"
KAYNAK_ADI = "9router/jina-reader"
TIMEOUT = 20
VARSAYILAN_MODEL = "jina-reader"


def _env_oku(ad: str) -> str:
    """Ortam degiskeni; yoksa `.env` satirinden (anahtar degeri basilmaz)."""
    deger = os.environ.get(ad, "").strip()
    if deger:
        return deger
    env = ROOT / ".env"
    if not env.is_file():
        return ""
    on = ad + "="
    for ln in env.read_text(encoding="utf-8-sig").splitlines():
        if ln.strip().startswith(on):
            return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def dogrudan_cek(url: str) -> tuple:
    """(metin, hata). Dogrudan HTTP cekme."""
    try:
        r = requests.get(url, timeout=TIMEOUT, headers={
            "User-Agent": "OSINT-Scraper-Motoru/1.0 (+Ankara B2B Company Master)"})
        r.raise_for_status()
        return r.text, ""
    except requests.RequestException as exc:
        return "", type(exc).__name__


def jina_cek(url: str, model: str = "") -> tuple:
    """(metin, hata). 9Router /v1/web/fetch uzerinden Jina-Reader."""
    taban = _env_oku("NINEROUTER_URL").rstrip("/")
    if not taban:
        return "", "NINEROUTER_URL_YOK"
    anahtar = _env_oku("NINEROUTER_KEY")
    basliklar = {"Content-Type": "application/json"}
    if anahtar:
        basliklar["Authorization"] = "Bearer " + anahtar
    govde = {"model": model or _env_oku("NINEROUTER_MODEL") or VARSAYILAN_MODEL,
             "url": url, "format": "markdown"}
    try:
        r = requests.post(taban + "/v1/web/fetch", json=govde,
                          headers=basliklar, timeout=TIMEOUT + 10)
        r.raise_for_status()
        veri = r.json()
    except requests.RequestException as exc:
        return "", type(exc).__name__
    except ValueError:
        return "", "GECERSIZ_JSON"
    if isinstance(veri, dict):
        for alan in ("content", "text", "markdown", "data"):
            if veri.get(alan):
                return str(veri[alan]), ""
    return "", "ICERIK_YOK"


def cek(url: str, model: str = "") -> dict:
    """Once dogrudan, olmazsa Jina. Doner: {yol, metin, hata}."""
    metin, hata = dogrudan_cek(url)
    if metin:
        return {"yol": "dogrudan", "metin": metin, "hata": ""}
    yedek, yedek_hata = jina_cek(url, model)
    if yedek:
        return {"yol": "jina-fallback", "metin": yedek, "hata": hata}
    return {"yol": "", "metin": "", "hata": hata + " | jina: " + yedek_hata}
def _olcule(metin: str) -> dict:
    """Ham metinden OLÇULEBILEN alanlar. Yapi bilinmede sayim yazilir.

    D-245: "0 firma" ile "yapi bilinmiyor" ayni degildir. Kart tipi
    tutulmazsa `kart_tipi=None` yazilir; sayi belirsiz birakilmaz.
    """
    soup = BeautifulSoup(metin, "html.parser")
    kart = soup.select("div.osb-list-card") or soup.select("div.col-lg-4.mb-3")
    return {
        "kart_tipi": "osb-list-card" if soup.select("div.osb-list-card")
                     else ("col-lg-4.mb-3" if kart else None),
        "kart_sayisi": len(kart),
        "baslik": (soup.title.get_text(strip=True) if soup.title else None),
        "metin_uzunluk": len(metin),
    }


def hedef_isle(url: str, yazici, model: str = "", kuru: bool = False) -> dict:
    """Tek hedef: izin -> cekim -> 0050 yazimi."""
    izin, sebep = KazimaYazici.izin_var(url)
    if not izin:
        # Vekil (Jina) icin de ayni kural: izin yoksa denenmez.
        if not kuru:
            yazici.url_hata_kaydet(url, "PermissionError", "robots: " + sebep)
        return {"url": url, "yol": "", "yazilan": 0, "hata": 1,
                "neden": "izin yok: " + sebep}

    sonuc = cek(url, model)
    if not sonuc["metin"]:
        if not kuru:
            yazici.url_hata_kaydet(url, "FetchError", sonuc["hata"][:300])
        return {"url": url, "yol": "", "yazilan": 0, "hata": 1,
                "neden": sonuc["hata"]}

    alanlar = _olcule(sonuc["metin"])
    alanlar["cek_yolu"] = sonuc["yol"]
    if kuru:
        return {"url": url, "yol": sonuc["yol"], "yazilan": 0, "hata": 0,
                "neden": "", "alanlar": alanlar}

    bekle = KazimaYazici.rate_limit_bekle(url)
    if bekle > 0:
        time.sleep(min(bekle, 3.0))
    yazici.audit_kaydet(url, action="fetch", status="success",
                        bayt=len(sonuc["metin"]), ms=0)
    yazildi = yazici.sayfa_kaydet(url, sonuc["metin"], alanlar)
    return {"url": url, "yol": sonuc["yol"], "yazilan": int(yazildi),
            "hata": 0, "neden": "", "alanlar": alanlar}


def main() -> int:
    p = argparse.ArgumentParser(description="9Router Jina-Reader fallback kazima")
    p.add_argument("hedef", nargs="*", help="hedef URL'ler")
    p.add_argument("--kuru", action="store_true",
                   help="hicbir seye yazmaz, yalniz sonucu gosterir")
    p.add_argument("--model", default="", help="9Router web fetch modeli")
    a = p.parse_args()

    yazici = KazimaYazici(KAYNAK_ADI, task_id=TASK_ID)
    sonuclar = [hedef_isle(u, yazici, a.model, a.kuru) for u in a.hedef]

    ozet = {
        "hedef": len(sonuclar),
        "yazilan": sum(s["yazilan"] for s in sonuclar),
        "hata": sum(s["hata"] for s in sonuclar),
        "jina_kullanildi": sum(1 for s in sonuclar if s["yol"] == "jina-fallback"),
        "dogrudan": sum(1 for s in sonuclar if s["yol"] == "dogrudan"),
        "kuru": bool(a.kuru),
        "sonuclar": sonuclar,
    }
    print(json.dumps(ozet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())