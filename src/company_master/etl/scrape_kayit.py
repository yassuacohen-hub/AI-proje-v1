# -*- coding: utf-8 -*-
"""Scrape kayit katmani — 0050 semasinin TEK yazma kapisi.

D-310: kazima araci degil, merkezi kaydin servisi. Bu modul yalnizca
*kanit yazar*: ham icerik, SHA256 content_hash ve audit kaydi.

Neden ayri modul (olcuk):
    Onceki durumda hicbir kaziyici bu tablolari yazmiyordu —
    grep `scrape_pages` -> sadece scripts/_kazima_dogrula.py.
    Uc tablo canli Supabase'de 0 satir duruyordu. Uc kaziyicinin her
    birine ayri INSERT yazmak D-211 ikiz yapisidir; tek yazma kapisi
    (D-246/D-249 mantigi) tek buradadir.

Sozlesme:
    * `content_hash` = SHA256(ham icerik). Zaman damgasi icermez ->
      ayni icerik ayni hash -> UNIQUE(source_url, content_hash) ile
      yinelenmez (D-261).
    * `cost_usd` DAIMA 0. 0050'de CHECK (cost_usd = 0) var; odemeli
      fallback varsayilan KAPALI (SKILL.md B-3.2).
    * `llm_used` DAIMA false — bu yol LLM-less'tir (SKILL.md B-1).

SEMA NOTU (olcildi, 0050:77-92):
    `scrape_errors` icin `source_name`/`source_url` kolonlari YOKTUR.
    Bag `audit_id` (FK) ve `page_id` (FK) uzerinden kurulur. Ilk yazim
    bu kolonlari varsaymis; canli sema onlari reddetti. D-267/1 deseni:
    sozlugun kendisi tutmazsa `.get()` sessizce bos gecer.

Ilgili Nodlar:
    [[D-310]] — kazima merkezi kaydin servisi
    [[D-261]] — content_hash UNIQUE dedup
    [[D-267]] — olcum / sozluk uyusmazligi
    [[D-246]] — dogrulama tek kapidan gecer
    [[D-235]] — kaziyici sayfalama sablonu
    [[scripts/_kazima_dogrula]] — 0050 sema mandali
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from sqlalchemy import text

from company_master.db.connection import get_engine

logger = logging.getLogger(__name__)

# Varsayilan yeniden deneme penceresi (SKILL.md B-3.1: kota tukenince kuyruga al)
VARSAYILAN_RETRY_SAAT = 24


def icerik_hash(ham: str | bytes) -> str:
    """SHA256(ham icerik). Zaman damgasi YOK — ayni icerik ayni hash.

    D-261: hash degisken bir alan (zaman damgasi/satir kimligi) iceriyorsa
    her kosuda yeni satir acilir ve UNIQUE kisiti ise yaramaz.
    """
    veri = ham.encode("utf-8") if isinstance(ham, str) else ham
    return hashlib.sha256(veri).hexdigest()


def url_hash(url: str) -> str:
    """SHA256(source_url)."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


@dataclass
class KazimaSonuc:
    """Bir kosunun olculur ozeti. `yazilan` = eklendi, `atlanan` = zaten vardi."""

    yazilan_sayfa: int = 0
    yazilan_audit: int = 0
    yazilan_hata: int = 0
    atlanan: int = 0
    hatali_url: list[str] = field(default_factory=list)

    def ozet(self) -> str:
        return (
            f"sayfa +{self.yazilan_sayfa} (atlanan {self.atlanan}) | "
            f"audit +{self.yazilan_audit} | hata +{self.yazilan_hata}"
        )


class KazimaYazici:
    """0050 tablo kumesinin TEK yazicisi (D-310 katman 5 / D-246).

    Idempotens: ayni URL + ayni icerik ikinci kez yazilmaz
    (ON CONFLICT DO NOTHING). Ikinci kosuda `yazilan_sayfa == 0` ve
    `atlanan == 1` olur — bu kabul kriteridir.
    """

    def __init__(self, kaynak_adi: str, *, task_id: str | None = None) -> None:
        self.kaynak_adi = kaynak_adi
        self.task_id = task_id
        self.sonuc = KazimaSonuc()

    # ---- sayfa (icerik + hash) ----
    def sayfa_kaydet(
        self,
        url: str,
        ham: str,
        alanlar: dict[str, Any] | None = None,
        *,
        parse_ms: float | None = None,
    ) -> bool:
        """Ham icerigi + cikarilan alanlari yazar. True = yeni satir eklendi."""
        h = icerik_hash(ham)
        alan_json = json.dumps(alanlar or {}, ensure_ascii=False)
        with get_engine().begin() as c:
            n = c.execute(
                text(
                    "INSERT INTO scrape_pages "
                    "(source_url, url_hash, content_hash, raw_content, "
                    " raw_content_length, extracted_fields, "
                    " llm_used, llm_model, cost_usd, parsing_duration_ms) "
                    "VALUES (:url, :uh, :ch, :ham, :len, "
                    "        CAST(:fields AS jsonb), "
                    "        false, NULL, 0.00, :ms) "
                    "ON CONFLICT (source_url, content_hash) DO NOTHING "
                    "RETURNING page_id"
                ),
                {
                    "url": url,
                    "uh": url_hash(url),
                    "ch": h,
                    "ham": ham,
                    "len": len(ham),
                    "fields": alan_json,
                    "ms": parse_ms,
                },
            ).fetchone()
        if n:
            self.sonuc.yazilan_sayfa += 1
            logger.info("sayfa eklendi %s (hash=%s)", url, h[:12])
            return True
        self.sonuc.atlanan += 1
        logger.info("sayfa zaten var, atlandi %s (hash=%s)", url, h[:12])
        return False

    # ---- audit ----
    def audit_kaydet(
        self,
        url: str,
        *,
        action: str = "fetch",
        status: str = "success",
        bayt: int | None = None,
        ms: float | None = None,
        hata: str | None = None,
        llm_model: str | None = None,
    ) -> None:
        """Her fetch/parse denemesi denetim kaydi birakir (D-310 katman 5)."""
        with get_engine().begin() as c:
            c.execute(
                text(
                    "INSERT INTO scrape_audit_log "
                    "(source_name, source_url, task_id, action, status, "
                    " bytes_fetched, duration_ms, error_msg, llm_used, "
                    " llm_model, cost_usd) "
                    "VALUES (:src, :url, :task, :act, :st, :bayt, :ms, "
                    "        :err, false, :model, 0.00)"
                ),
                {
                    "src": self.kaynak_adi,
                    "url": url,
                    "task": self.task_id,
                    "act": action,
                    "st": status,
                    "bayt": bayt,
                    "ms": ms,
                    "err": hata,
                    "model": llm_model,
                },
            )
        self.sonuc.yazilan_audit += 1

    # ---- hata kuyrugu (olculmus sema) ----
    def hata_kaydet(
        self,
        *,
        error_code: str,
        error_message: str,
        audit_id: int | None = None,
        page_id: int | None = None,
        retry_saat: int = VARSAYILAN_RETRY_SAAT,
    ) -> None:
        """Hata/retry kuyrugu (SKILL.md B-3.1).

        0050 semasinda `source_name`/`source_url` kolonlari YOK; kaynak
        yalnizca `audit_id` FK'si uzerinden tasinir. `audit_kaydet()`
        `audit_id` dondurmedigi icin hata kaydi audit_id'siz yazilir.
        """
        with get_engine().begin() as c:
            c.execute(
                text(
                    "INSERT INTO scrape_errors "
                    "(audit_id, page_id, error_code, error_message, "
                    " retry_count, next_retry_at, fallback_tried) "
                    "VALUES (:aid, :pid, :kod, :msg, 0, "
                    "        now() + make_interval(hours => :saat), false)"
                ),
                {
                    "aid": audit_id,
                    "pid": page_id,
                    "kod": error_code[:50],
                    "msg": error_message[:2000],
                    "saat": retry_saat,
                },
            )
        self.sonuc.yazilan_hata += 1

    def url_hata_kaydet(self, url: str, hata_turu: str, mesaj: str) -> None:
        """URL bilinen hata: once audit'e yaz (kaynak adini korur), sonra hata.

        `scrape_errors.audit_id` FK'si sayesinde hata kaydi hangi kaynaktan
        geldigine ulasir — bu yuzden kaynak yalniz `scrape_audit_log`'da tutulur.
        """
        with get_engine().begin() as c:
            aid = c.execute(
                text(
                    "INSERT INTO scrape_audit_log "
                    "(source_name, source_url, task_id, action, status, "
                    " error_msg, llm_used, llm_model, cost_usd) "
                    "VALUES (:src, :url, :task, 'fetch', 'error', "
                    "        :err, false, NULL, 0.00) RETURNING audit_id"
                ),
                {
                    "src": self.kaynak_adi,
                    "url": url,
                    "task": self.task_id,
                    "err": mesaj[:2000],
                },
            ).scalar()
        self.sonuc.yazilan_audit += 1
        self.hata_kaydet(error_code=hata_turu, error_message=mesaj, audit_id=aid)
        self.sonuc.hatali_url.append(url)

    # ---- izin (router tek kapi) ----
    @staticmethod
    def izin_var(url: str) -> tuple[bool, str]:
        """Merkezi router kapisi (D-310 katman 4).

        SKILL.md'nin `get_router(domain)` / `can_fetch()` cagrisi YANLIS;
        olcum: get_router() parametre almaz, API `check(url) -> Decision`.
        """
        from company_master.utils.scraping_permission_router import get_router

        d = get_router().check(url)
        return d.allowed, d.reason

    @staticmethod
    def rate_limit_bekle(url: str) -> float:
        """Domain bazli minimum araligi bekler; beklenen sureyi doner."""
        from company_master.utils.scraping_permission_router import get_router

        return get_router().rate_limit(urlsplit(url).netloc)


__all__ = [
    "KazimaYazici",
    "KazimaSonuc",
    "icerik_hash",
    "url_hash",
    "VARSAYILAN_RETRY_SAAT",
]
