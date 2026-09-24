# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from rapidfuzz import fuzz

from company_master.db.connection import get_engine
from sqlalchemy import text

logger = logging.getLogger(__name__)

__all__ = ["CompanyMatcher", "MatchResult", "extract_domain"]

_DOMAIN_RE = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}$")
_NAME_CLEAN_RE = re.compile(r"[^a-z0-9]+")


def extract_domain(url: str | None) -> str | None:
    """URL string'inden domain cikarir (scheme/path/query olmadan, kucuk harf)."""
    if not url:
        return None
    raw = url.strip().lower()
    if not raw:
        return None
    if "://" not in raw:
        raw = "http://" + raw
    try:
        parsed = urlparse(raw)
    except ValueError:
        return None
    host = (parsed.hostname or "").strip().lower()
    if host.startswith("www."):
        host = host[4:]
    if not host or not _DOMAIN_RE.match(host):
        return None
    return host


def _normalize_name(name: str | None) -> str:
    """Fuzzy karsilastirma icin isim normalizasyonu."""
    if not name:
        return ""
    s = name.strip().lower()
    s = s.replace("ı", "i").replace("İ", "i")
    s = s.replace("ğ", "g").replace("Ğ", "g")
    s = s.replace("ü", "u").replace("Ü", "u")
    s = s.replace("ş", "s").replace("Ş", "s")
    s = s.replace("ö", "o").replace("Ö", "o")
    s = s.replace("ç", "c").replace("Ç", "c")
    s = _NAME_CLEAN_RE.sub("", s)
    return s


@dataclass
class MatchResult:
    company_id: str | None = None
    matched_name: str | None = None
    match_type: str = "no_match"
    confidence: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class CompanyMatcher:
    """DB'deki companies kayitlariyla cok asamali eslestirme.

    Sira: tax_number (exact) > mersis (exact) > domain > fuzzy legal_name.
    Sirket listesi ilk cagriramada yuklenir ve cache'lenir.
    """

    def __init__(self, fuzzy_threshold: float = 85.0) -> None:
        self.fuzzy_threshold = float(fuzzy_threshold)
        self._companies: list[dict[str, Any]] | None = None

    def _load_companies(self) -> None:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT company_id, legal_name, tax_number, mersis_number, "
                    "website_domain FROM companies"
                )
            ).mappings().all()
        companies = []
        for row in rows:
            d = dict(row)
            d["_norm_name"] = _normalize_name(d.get("legal_name"))
            d["_domain"] = extract_domain(d.get("website_domain"))
            companies.append(d)
        self._companies = companies
        logger.info("CompanyMatcher: %d sirket yuklendi", len(companies))

    def _ensure_loaded(self) -> None:
        if self._companies is None:
            self._load_companies()

    def invalidate_cache(self) -> None:
        self._companies = None

    def match(
        self,
        raw_name: str | None = None,
        domain: str | None = None,
        tax_number: str | None = None,
        mersis: str | None = None,
    ) -> MatchResult:
        self._ensure_loaded()
        assert self._companies is not None

        if tax_number:
            tn = str(tax_number).strip()
            if tn:
                for c in self._companies:
                    if str(c.get("tax_number") or "").strip() == tn:
                        return MatchResult(
                            company_id=str(c["company_id"]),
                            matched_name=c.get("legal_name"),
                            match_type="tax_number",
                            confidence=1.0,
                            details={"tax_number": tn},
                        )

        if mersis:
            m = str(mersis).strip()
            if m:
                for c in self._companies:
                    if str(c.get("mersis_number") or "").strip() == m:
                        return MatchResult(
                            company_id=str(c["company_id"]),
                            matched_name=c.get("legal_name"),
                            match_type="mersis",
                            confidence=1.0,
                            details={"mersis": m},
                        )

        if domain:
            dom = extract_domain(domain)
            if dom:
                for c in self._companies:
                    if c.get("_domain") and c["_domain"] == dom:
                        return MatchResult(
                            company_id=str(c["company_id"]),
                            matched_name=c.get("legal_name"),
                            match_type="domain",
                            confidence=0.95,
                            details={"domain": dom},
                        )

        if raw_name:
            norm = _normalize_name(raw_name)
            if len(norm) > 3:
                best: dict[str, Any] | None = None
                best_score = 0.0
                for c in self._companies:
                    cn = c.get("_norm_name") or ""
                    if not cn:
                        continue
                    score = fuzz.ratio(norm, cn)
                    if score > best_score:
                        best_score = score
                        best = c
                if best is not None and best_score >= self.fuzzy_threshold:
                    return MatchResult(
                        company_id=str(best["company_id"]),
                        matched_name=best.get("legal_name"),
                        match_type="fuzzy_name",
                        confidence=round(best_score / 100.0, 4),
                        details={"score": best_score, "raw_name": raw_name},
                    )
                if best is not None:
                    return MatchResult(
                        company_id=None,
                        matched_name=raw_name,
                        match_type="fuzzy_below_threshold",
                        confidence=round(best_score / 100.0, 4),
                        details={"best_candidate": best.get("legal_name"), "score": best_score},
                    )

        return MatchResult(
            company_id=None,
            matched_name=None,
            match_type="no_match",
            confidence=0.0,
            details={"raw_name": raw_name, "domain": domain},
        )
