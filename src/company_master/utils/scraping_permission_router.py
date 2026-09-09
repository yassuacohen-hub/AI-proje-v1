# -*- coding: utf-8 -*-
"""OSINT Scraper Motoru â€” Izin/Rate-Limit Router (merkezi).

Her scraper'in ayri ayri robots.txt okumasi yerine tek merkez:
  - robots.txt Disallow kontrolu (domain bazli, TTL'li cache)
  - KVKK guvenli domain listesi (sadece isletme verisi)
  - Domain bazli rate limiting (son istek zamani + minimum aralik)

Kullanim:
    from company_master.engine.permission_router import get_router

    router = get_router()
    dec = router.check("https://www.ostim.org.tr/firmalar")
    if not dec.allowed:
        raise PermissionError(dec.reason)
    router.rate_limit(dec.domain)   # istek oncesi bekle
    ... requests.get(...) ...
"""
from __future__ import annotations

import logging
import threading
import time
import urllib.robotparser
from dataclasses import dataclass
from urllib.parse import urlsplit

import requests

logger = logging.getLogger(__name__)

USER_AGENT = "OSINT-Scraper-Motoru/1.0 (+Ankara B2B Company Master)"
ROBOTS_TTL = 3600  # robots.txt cache suresi (sn)


@dataclass
class SourcePolicy:
    """Tek bir kaynak domain'inin politika tanimi."""

    domain: str
    min_interval: float = 2.0      # istekler arasi min. bekleme (sn)
    kvkk_safe: bool = False        # True: sadece isletme verisi, kisisel veri yok
    respect_robots: bool = True    # robots.txt Disallow uygulanir
    note: str = ""


@dataclass
class Decision:
    """check() sonucu."""

    url: str
    domain: str
    allowed: bool
    reason: str


@dataclass
class _RobotsCacheEntry:
    parser: urllib.robotparser.RobotFileParser | None
    fetched_at: float


# KVKK acisindan guvenli: sadece ticari/isletme bilgisi sunan, kisisel veri
# listelemeyen resmi/kurumsal dizinler. Yeni kaynak eklenmeden once KVKK
# degerlendirmesi yapilmalidir (V10/07_referanslar).
KVKK_SAFE_DOMAINS: frozenset[str] = frozenset(
    {
        "www.ostim.org.tr",
        "ostim.org.tr",
        "www.aso.org.tr",
        "aso.org.tr",
        "www.gib.gov.tr",
        "gib.gov.tr",
    }
)
class PermissionRouter:
    """Merkezi izin + rate-limit yoneticisi (thread-safe)."""

    def __init__(self) -> None:
        self._policies: dict[str, SourcePolicy] = {}
        self._robots: dict[str, _RobotsCacheEntry] = {}
        self._last_request: dict[str, float] = {}
        self._lock = threading.Lock()
        self._session = requests.Session()
        self._session.headers["User-Agent"] = USER_AGENT

    # ---- politika kaydi ----
    def register(self, policy: SourcePolicy) -> None:
        with self._lock:
            self._policies[policy.domain] = policy

    def _policy_for(self, domain: str) -> SourcePolicy:
        return self._policies.get(domain, SourcePolicy(domain=domain))

    # ---- robots.txt (TTL'li cache) ----
    def _robots_ok(self, url: str, policy: SourcePolicy) -> tuple[bool, str]:
        if not policy.respect_robots:
            return True, "robots kontrol atlandi (politika)"
        split = urlsplit(url)
        base = f"{split.scheme}://{split.netloc}"
        now = time.time()
        with self._lock:
            entry = self._robots.get(base)
            if entry is None or now - entry.fetched_at > ROBOTS_TTL:
                parser = urllib.robotparser.RobotFileParser()
                try:
                    resp = self._session.get(f"{base}/robots.txt", timeout=15)
                    if resp.status_code == 200:
                        parser.parse(resp.text.splitlines())
                    else:
                        logger.info(
                            "robots.txt %s -> HTTP %s (izin varsayilir)",
                            base,
                            resp.status_code,
                        )
                except requests.RequestException as exc:
                    logger.warning("robots.txt alinamadi %s: %s", base, exc)
                entry = _RobotsCacheEntry(parser=parser, fetched_at=now)
                self._robots[base] = entry
        if entry.parser is None:
            return True, "robots.txt yok/alinamadi (izin varsayildi)"
        allowed = entry.parser.can_fetch(USER_AGENT, url)
        return allowed, "robots.txt Disallow" if not allowed else "robots.txt OK"

    # ---- ana API ----
    def check(self, url: str) -> Decision:
        split = urlsplit(url)
        domain = split.netloc
        policy = self._policy_for(domain)

        if domain not in KVKK_SAFE_DOMAINS and not policy.kvkk_safe:
            logger.warning(
                "KVKK: %s guvenli listede degil â€” kisisel veri toplanmamali",
                domain,
            )

        robots_ok, reason = self._robots_ok(url, policy)
        if not robots_ok:
            return Decision(url, domain, False, reason)
        return Decision(url, domain, True, reason)

    def rate_limit(self, domain: str) -> float:
        """Domain icin min. interval kadar bekle; beklenen sureyi dondur."""
        policy = self._policy_for(domain)
        with self._lock:
            last = self._last_request.get(domain)
            wait = 0.0
            if last is not None:
                wait = max(0.0, policy.min_interval - (time.time() - last))
            if wait > 0:
                time.sleep(wait)
            self._last_request[domain] = time.time()
        return wait

    def status(self) -> dict[str, dict]:
        """Tanili kaynaklarin politika/durum ozeti (izleme icin)."""
        with self._lock:
            return {
                d: {
                    "min_interval": p.min_interval,
                    "kvkk_safe": d in KVKK_SAFE_DOMAINS or p.kvkk_safe,
                    "last_request_age": round(time.time() - self._last_request[d], 1)
                    if d in self._last_request
                    else None,
                }
                for d, p in self._policies.items()
            }


# Varsayilan kaynak politikalari (kayit: V10/10_ankara_osb_sentez.md + Job Intelligence)
DEFAULT_POLICIES: tuple[SourcePolicy, ...] = (
    SourcePolicy("www.ostim.org.tr", 2.5, kvkk_safe=True,
                 note="OSTIM uyeler; robots.txt kontrol edilir"),
    SourcePolicy("ostim.org.tr", 2.5, kvkk_safe=True),
    SourcePolicy("www.aso.org.tr", 2.0, kvkk_safe=True,
                 note="ASO firma rehberi API"),
    SourcePolicy("aso.org.tr", 2.0, kvkk_safe=True),
    SourcePolicy("www.gib.gov.tr", 1.0, kvkk_safe=True,
                 note="GIB vergi no sorgu (VKN dogrulama)"),
    SourcePolicy("gib.gov.tr", 1.0, kvkk_safe=True),
    SourcePolicy("www.ivedikosb.org.tr", 2.5, note="Ivedik OSB"),
    SourcePolicy("www.baskentosb.org.tr", 2.5, note="Baskent OSB"),
    # ============================================================
    # JOB INTELLIGENCE POLITIKALARI
    # ============================================================
    SourcePolicy("www.iskur.gov.tr", 2.0, kvkk_safe=True,
                 note="İŞKUR resmi istihdam kurumu; sadece isletme verisi"),
    SourcePolicy("iskur.gov.tr", 2.0, kvkk_safe=True),
    SourcePolicy("www.kariyer.net", 3.0, kvkk_safe=False,
                 note="İş ilanı sitesi; kisisel veri olabilir, sadece isletme bilgisi toplanmali"),
    SourcePolicy("kariyer.net", 3.0, kvkk_safe=False),
    # company-career-pages icin dinamik policy runtime'da eklenecek
    # (companies.website_domain'lerden türetilir)
)

_router: PermissionRouter | None = None


def get_router() -> PermissionRouter:
    """Tekil router (ilk cagride varsayilan politikalari kaydeder)."""
    global _router
    if _router is None:
        _router = PermissionRouter()
        for p in DEFAULT_POLICIES:
            _router.register(p)
    return _router
