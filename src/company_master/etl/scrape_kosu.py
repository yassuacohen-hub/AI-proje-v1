# -*- coding: utf-8 -*-
"""Uc OSB kaynaginin ortak kayit kosu iskeleti (D-310 katman 5).

NEDEN AYRI MODUL
    `scripts/kazima_ostim.py`, `kazima_ivedik.py`, `kazima_baskent.py` ayni
    dort adimi yapar: izin -> rate limit -> fetch -> 0050'ye yaz. Bu dort
    adim her birinde ayri yazilsa D-211 ikiz yapisidir. Burada TEK kez
    yazilir; sarmalayicilar yalnizca kendi kaynagini tanimlar.

KAPSAMIN SINIRI (bilinçli, D-211)
    Bu katman **firma cikarımı yapmaz**. Firma kaydi kanonik kaziyicinin
    (`src/company_master/etl/scrapers/*.py`) isidir; o dosyalara dokunulmaz
    (D-235 sayfalama sablonu, `sayfa_dongusu()` korunur).
    Buradaki is yalnizca **kanit yazmak**: ham icerik, SHA256 content_hash,
    audit kaydi, hata kuyrugu. `scrape_pages` bir ham icerik arsividir;
    ayristirma kanonik kaziyicinin isi olarak kalir.

    Bedeli olculmustur: ayni liste sayfasi bir kez kayit katmani, bir kez
    kanonik kaziyici tarafindan okunur. Iki okumanin yerine tek cekim
    yapilabilirdi, ama bu kanonik scraper'lara `son_istek` yakalama
    kancasini eklemeyi gerektirirdi; borc olarak kayitlidir (bkz. asagida).

D-310 BEŞ KATMAN
    Katman 4 (izin + rate limit)  -> `KazimaYazici.izin_var/rate_limit_bekle`
    Katman 5 (denetim izi)        -> `scrape_audit_log` + `scrape_errors`
    Katman 1 (kaynak tanimi)      -> `Kaynak` veri sinifi (ad + url + robots)
    Katman 2/3 (sema + butunluk) -> `scrape_kayit.KazimaYazici` (0050 kisitlari)

Idempotens: ayni URL + ayni icerik -> `ON CONFLICT DO NOTHING`.
Ikinci kosuda `yazilan_sayfa == 0`, `atlanan == 1` olur.

Ilgili Nodlar
    [[D-310]] kazima merkezi kaydin servisidir
    [[D-261]] content_hash UNIQUE dedup
    [[D-235]] kaziyici sayfalama sablonu
    [[src/company_master/etl/scrape_kayit]] 0050 tek yazma kapisi
    [[src/company_master/utils/scraping_permission_router]] izin + rate limit
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable

import requests
from bs4 import BeautifulSoup

from company_master.etl.scrape_kayit import KazimaYazici

logger = logging.getLogger(__name__)

USER_AGENT = "OSINT-Scraper-Motoru/1.0 (+Ankara B2B Company Master)"
VARSAYILAN_TIMEOUT = 20


@dataclass
class Kaynak:
    """Bir OSB kaynaginin tanimi. Sarmalayici yalnizca bunu doldurur."""

    ad: str                      # -> scrape_audit_log.source_name
    url: str                     # kanonik liste URL'si
    robots_url: str              # router bu adresi kontrol eder
    # ham HTML'den alanlari cikarir: (soup) -> dict. Varsayilan: kart sayimi.
    ayikla: Callable[[BeautifulSoup], dict] | None = None
    not_: str = ""
    task_id: str | None = None


def _varsayilan_ayikla(soup: BeautifulSoup) -> dict:
    """Yapi bilinmeden varsayilan: olculmus kart sayimi + baslik.

    D-235/D-224: "bilinen CSS secicisi" iddiasi olcumle dogrulanmadi.
    Olcum: OSTIM'de 0 `<table>`, 0 `tr.data`; Ivedik'te 15 `div.osb-list-card`.
    Bu yuzden varsayilan seyici listesi **olculmus** iki siniftan kurulur ve
    hangi sinifin tutuldugu `kart_tipi` alaninda yazilir — sayi kaynagi
    belirsiz birakilmaz (D-245: doluluk gecerlilik degildir).
    """
    kart = soup.select("div.osb-list-card")
    tip = "osb-list-card"
    if not kart:
        kart = soup.select("div.col-lg-4.mb-3")
        tip = "col-lg-4.mb-3"
    return {
        "kart_tipi": tip if kart else None,
        "kart_sayisi": len(kart),
        "baslik": (soup.title.get_text(strip=True) if soup.title else None),
    }


def kosu(kaynak: Kaynak) -> dict:
    """Bir kaynagin LLM-less kayit kosusunu yurutur ve 0050'ye yazar.

    Doner: {"yazilan", "atlanan", "hata", "firmalar", "izin", "neden"}
    """
    yazici = KazimaYazici(kaynak.ad, task_id=kaynak.task_id)

    # 1) izin — merkezi router (D-246 tek kapi). Once giris, sonra robots.
    for hedef in (kaynak.url, kaynak.robots_url):
        izin, sebep = KazimaYazici.izin_var(hedef)
        if not izin:
            logger.warning("IZIN YOK %s (%s)", hedef, sebep)
            yazici.url_hata_kaydet(kaynak.url, "PermissionError", f"robots: {sebep}")
            return {"yazilan": 0, "atlanan": 0, "hata": 1, "firmalar": 0,
                    "izin": False, "neden": sebep}
    logger.info("izin tamam %s", kaynak.ad)

    # 2) rate limit (domain bazli) + fetch
    bekle = KazimaYazici.rate_limit_bekle(kaynak.url)
    if bekle > 0:
        logger.debug("rate limit bekledi %.1f sn", bekle)
        time.sleep(min(bekle, 3.0))

    t0 = time.perf_counter()
    try:
        resp = requests.get(kaynak.url, headers={"User-Agent": USER_AGENT},
                            timeout=VARSAYILAN_TIMEOUT)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        resp.raise_for_status()
    except requests.RequestException as exc:
        ms = round((time.perf_counter() - t0) * 1000, 1)
        logger.error("FETCH HATA %s: %s", kaynak.url, exc)
        yazici.url_hata_kaydet(kaynak.url, type(exc).__name__, str(exc))
        return {"yazilan": 0, "atlanan": 0, "hata": 1, "firmalar": 0,
                "izin": True, "neden": type(exc).__name__}

    # 3) parse — LLM-less (BeautifulSoup), 9Router YOK
    t1 = time.perf_counter()
    soup = BeautifulSoup(resp.text, "html.parser")
    ayikla = kaynak.ayikla or _varsayilan_ayikla
    try:
        alanlar = ayikla(soup)
    except Exception as exc:  # noqa: BLE001 — ayiklayici kirilirsa kayit yine yazilir
        logger.warning("ayikla hata, varsayilana dusuldu: %s", exc)
        alanlar = _varsayilan_ayikla(soup)
        alanlar["ayiklayici_hata"] = f"{type(exc).__name__}: {exc}"[:200]
    parse_ms = round((time.perf_counter() - t1) * 1000, 1)

    # 4) DB yaz — UNIQUE(source_url, content_hash) idempotent
    yazici.audit_kaydet(kaynak.url, action="fetch", status="success",
                        bayt=len(resp.text), ms=ms)
    eklendi = yazici.sayfa_kaydet(kaynak.url, resp.text, alanlar, parse_ms=parse_ms)

    logger.info("%s -> %d bayt, %s", kaynak.ad, len(resp.text), alanlar)
    return {"yazilan": int(eklendi), "atlanan": int(not eklendi), "hata": 0,
            "firmalar": int(alanlar.get("kart_sayisi") or 0),
            "izin": True, "neden": "", "alanlar": alanlar}


__all__ = ["Kaynak", "kosu", "USER_AGENT", "VARSAYILAN_TIMEOUT"]
