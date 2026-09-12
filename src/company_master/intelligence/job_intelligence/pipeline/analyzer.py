# -*- coding: utf-8 -*-
"""Job Intelligence — Signal Analyzer.

job_postings tablosundan company_signals tablosuna sinyal üretir.
Scraper -> ingest_job_postings -> job_postings -> analyze_job_signals -> company_signals
-> scorer (score_all_companies) -> company_intelligence_scores

Sinyal türleri ve alt tipleri:
  - growth          : hiring_surge, expansion_hiring
  - risk            : layoff_risk, contraction_risk
  - tech_transformation : tech_modernization, stack_upgrade
  - investment      : executive_hiring, critical_hire
  - geo_expansion   : new_location
  - org_change      : new_department, restructuring
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import text

from company_master.db.connection import get_engine

# ChatEnricher opsiyonel ve çift-import desenli (embedder.py ile aynı):
# - scripts (ROOT/src sys.path'te) -> src.company_master.* çalışır
# - pytest (src sys.path'te)       -> company_master.* çalışır
try:
    from src.company_master.intelligence.job_intelligence.pipeline.chat_enricher import (  # noqa: E501
        ChatEnricher,
        EnrichResult,
        BELIRSIZ_SEKTOR,
        build_default_enricher,
    )
except ImportError:
    try:
        from company_master.intelligence.job_intelligence.pipeline.chat_enricher import (  # noqa: E501
            ChatEnricher,
            EnrichResult,
            BELIRSIZ_SEKTOR,
            build_default_enricher,
        )
    except ImportError:
        ChatEnricher = None  # type: ignore[assignment,misc]
        EnrichResult = None  # type: ignore[assignment,misc]
        BELIRSIZ_SEKTOR = "GENEL / BELİRSİZ"
        build_default_enricher = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

RISK_KEYWORDS: list[str] = [
    "kısıtlama",
    "kısma",
    "indirim",
    "elverişsiz",
    "kapanış",
    "feshedilme",
    "downsize",
    "restructur",
    "redundan",
    "layoff",
    "termination",
    "azaltma",
    "kısıtlama programı",
    "işten çıkarma",
    "freelance",
    "kontrat sonu",
    "geçici iş",
]

CRITICAL_DEPARTMENTS: list[str] = [
    "cto",
    "cfo",
    "ceo",
    "coo",
    "cio",
    "chief",
    "müdür",
    "yönetici",
    "genel müdür",
    "direktör",
    "başkan",
    "şube şefi",
]

CRITICAL_SENIORITY = {"director", "c-level", "vp", "head", "manager"}

MODERN_TECH_KEYWORDS: list[str] = [
    "kubernetes",
    "docker",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "microserv",
    "graphql",
    "rest api",
    "grpc",
    "ci/cd",
    "ml",
    "ai",
    "pytorch",
    "tensorflow",
    "pandas",
    "numpy",
    "bigdata",
    "spark",
    "kafka",
    "airflow",
    "dbt",
    "next.js",
    "react",
    "vue",
    "angular",
    "svelte",
    "fastapi",
    "nest",
    "django",
    "flask",
    "terraform",
    "ansible",
    "jenkins",
    "grafana",
    "prometheus",
]

# 9R-03: chat zenginleştirme için kullanılacak yetenek anahtar sözlüğü
# (MODERN_TECH_KEYWORDS'e opsiyonel ek becerilerle birlikte). Regex fallback
# için de aynı sözlük kullanılır (chat devre dışıyken bile tutarlı çıktı).
ENRICH_SKILL_KEYWORDS: list[str] = list(MODERN_TECH_KEYWORDS) + [
    "python",
    "javascript",
    "typescript",
    "java",
    "c#",
    "c++",
    "sql",
    "excel",
    "sap",
    "erp",
    "crm",
    "satış",
    "pazarlama",
    "ihracat",
    "muhasebe",
    "raporlama",
]

SIG_WINDOW_DAYS = 90
GROWTH_WINDOW_DAYS = 30
GROWTH_MIN_POSTINGS = 3
SIGNAL_TTL_DAYS = 90


class SignalAnalyzer:
    """İş ilanlarından ticari sinyaller çıkarır."""

    def __init__(
        self,
        window_days: int = SIG_WINDOW_DAYS,
        enrich_with_chat: bool = False,
    ) -> None:
        self.window_days = window_days
        self._enrich_chat_aktif = bool(enrich_with_chat)
        self._engine = get_engine()
        self._enricher: Any | None = None
        if self._enrich_chat_aktif:
            self._enricher = self._chat_enricher_build()

    def _load_job_postings(self) -> list[dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.window_days)
        query = text("""
            SELECT
                jp.job_posting_id,
                jp.company_id,
                jp.title,
                jp.description,
                jp.department,
                jp.seniority_level,
                jp.location_city,
                jp.location_country,
                jp.technologies,
                jp.employment_type,
                jp.posted_at,
                jp.collected_at
            FROM job_postings jp
            WHERE jp.company_id IS NOT NULL
              AND (jp.posted_at >= :cutoff OR jp.collected_at >= :cutoff)
            ORDER BY jp.company_id, jp.posted_at DESC NULLS LAST
        """)
        with self._engine.connect() as conn:
            rows = conn.execute(query, {"cutoff": cutoff}).mappings().all()
        return [dict(r) for r in rows]

    def _load_company_tech_profile(self, company_id: UUID) -> dict[str, Any]:
        query = text("""
            SELECT technologies FROM company_tech_profile WHERE company_id = :cid
        """)
        with self._engine.connect() as conn:
            row = conn.execute(query, {"cid": company_id}).mappings().first()
        if row:
            try:
                return json.loads(row["technologies"]) if row["technologies"] else {}
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def _load_existing_locations(self, company_id: UUID) -> set[str]:
        query = text("""
            SELECT DISTINCT location_city FROM job_postings
            WHERE company_id = :cid
              AND location_city IS NOT NULL
              AND (posted_at < :cutoff OR posted_at IS NULL)
        """)
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.window_days)
        with self._engine.connect() as conn:
            rows = conn.execute(query, {"cid": company_id, "cutoff": cutoff}).fetchall()
        return {str(r[0]) for r in rows if r[0]}

    def _load_existing_departments(self, company_id: UUID) -> set[str]:
        query = text("""
            SELECT DISTINCT department FROM job_postings
            WHERE company_id = :cid
              AND department IS NOT NULL
              AND (posted_at < :cutoff OR posted_at IS NULL)
        """)
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.window_days)
        with self._engine.connect() as conn:
            rows = conn.execute(query, {"cid": company_id, "cutoff": cutoff}).fetchall()
        return {str(r[0]) for r in rows if r[0]}

    @staticmethod
    def _parse_technologies(raw: Any) -> list[str]:
        if not raw:
            return []
        if isinstance(raw, list):
            return [str(t).lower().strip() for t in raw if t]
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(t).lower().strip() for t in parsed if t]
            except (json.JSONDecodeError, TypeError):
                pass
            stripped = raw.lower().strip()
            return [stripped] if stripped else []
        return []

    @staticmethod
    def _parse_posted_at(raw: Any) -> datetime | None:
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    def _detect_growth(
        self, postings: list[dict[str, Any]], company_id: UUID
    ) -> dict[str, Any] | None:
        """Hiring surge signal: 3+ postings in 30-day window, upward trend."""
        now = datetime.now(timezone.utc)
        cutoff_30d = now - timedelta(days=GROWTH_WINDOW_DAYS)
        cutoff_90d = now - timedelta(days=self.window_days)

        postings_30d = [
            p
            for p in postings
            if (posted_at := self._parse_posted_at(p.get("posted_at")))
            and cutoff_30d <= posted_at <= now
        ]
        postings_90d = [
            p
            for p in postings
            if (posted_at := self._parse_posted_at(p.get("posted_at")))
            and cutoff_90d <= posted_at <= now
        ]

        count_30d = len(postings_30d)
        count_90d = len(postings_90d)

        if count_30d < GROWTH_MIN_POSTINGS:
            return None

        avg_90d_per_30d = count_90d / 3 if count_90d > 0 else 0
        trend_ratio = (
            (count_30d / GROWTH_WINDOW_DAYS) / (avg_90d_per_30d / GROWTH_WINDOW_DAYS)
            if avg_90d_per_30d > 0
            else 2.0
        )

        if trend_ratio < 1.0 and count_30d < GROWTH_MIN_POSTINGS:
            return None

        score = min(100.0, count_30d * 20 + (trend_ratio - 1.0) * 10)
        score = max(20.0, score)
        confidence = min(100.0, 70 + count_30d * 5)

        posting_ids = [str(p["job_posting_id"]) for p in postings_30d]
        date_range = (
            (
                min(
                    self._parse_posted_at(p["posted_at"])
                    for p in postings_30d
                    if self._parse_posted_at(p.get("posted_at"))
                ).isoformat()
                if postings_30d
                else None
            ),
            (
                max(
                    self._parse_posted_at(p["posted_at"])
                    for p in postings_30d
                    if self._parse_posted_at(p.get("posted_at"))
                ).isoformat()
                if postings_30d
                else None
            ),
        )

        subtype = "hiring_surge"
        if trend_ratio >= 2.0:
            subtype = "expansion_hiring"

        return {
            "company_id": company_id,
            "signal_type": "growth",
            "signal_subtype": subtype,
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "evidence": {
                "job_posting_ids": posting_ids,
                "date_range": {"start": date_range[0], "end": date_range[1]},
                "postings_30d": count_30d,
                "postings_90d": count_90d,
                "trend_ratio": round(trend_ratio, 2),
            },
            "valid_until": (now + timedelta(days=SIGNAL_TTL_DAYS)).isoformat(),
            "metadata": {
                "detector": "signal_analyzer",
                "window_days": self.window_days,
            },
        }

    def _detect_risk(
        self, postings: list[dict[str, Any]], company_id: UUID
    ) -> dict[str, Any] | None:
        """Risk signal: layoff/restructuring keywords in job postings."""
        risk_matches: list[str] = []
        matched_postings: list[str] = []

        for p in postings:
            text_lower = (
                (p.get("title") or "") + " " + (p.get("description") or "")
            ).lower()
            for kw in RISK_KEYWORDS:
                if kw in text_lower:
                    risk_matches.append(kw)
                    matched_postings.append(str(p["job_posting_id"]))
                    break

        if not risk_matches:
            return None

        score = min(100.0, len(risk_matches) * 25 + 15)
        confidence = min(100.0, 60 + len(set(risk_matches)) * 10)

        return {
            "company_id": company_id,
            "signal_type": "risk",
            "signal_subtype": "layoff_risk",
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "evidence": {
                "job_posting_ids": list(set(matched_postings)),
                "matched_keywords": list(set(risk_matches)),
                "match_count": len(risk_matches),
            },
            "valid_until": (
                datetime.now(timezone.utc) + timedelta(days=SIGNAL_TTL_DAYS)
            ).isoformat(),
            "metadata": {"detector": "signal_analyzer"},
        }

    def _detect_tech_transformation(
        self, postings: list[dict[str, Any]], company_id: UUID
    ) -> dict[str, Any] | None:
        """Tech signal: modern tech keywords in postings, new vs existing profile."""
        all_tech: set[str] = set()
        posting_ids: list[str] = []

        for p in postings:
            posting_ids.append(str(p["job_posting_id"]))
            for t in self._parse_technologies(p.get("technologies")):
                all_tech.add(t.lower().strip())
            desc = p.get("description") or ""
            desc_lower = desc.lower()
            for kw in MODERN_TECH_KEYWORDS:
                if kw in desc_lower:
                    all_tech.add(kw.strip())

        modern_tech_found = all_tech & {t.lower().strip() for t in MODERN_TECH_KEYWORDS}
        if not modern_tech_found:
            return None

        existing_profile = self._load_company_tech_profile(company_id)
        existing_tech = {k.lower().strip() for k in existing_profile.keys()}
        new_tech = modern_tech_found - existing_tech

        if not new_tech:
            return None

        score = min(100.0, len(new_tech) * 15 + len(modern_tech_found) * 5)
        confidence = min(100.0, 65 + len(new_tech) * 5)

        return {
            "company_id": company_id,
            "signal_type": "tech_transformation",
            "signal_subtype": "tech_modernization",
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "evidence": {
                "job_posting_ids": posting_ids,
                "modern_technologies": sorted(modern_tech_found),
                "new_technologies": sorted(new_tech),
                "existing_technologies": sorted(existing_tech),
            },
            "valid_until": (
                datetime.now(timezone.utc) + timedelta(days=SIGNAL_TTL_DAYS)
            ).isoformat(),
            "metadata": {"detector": "signal_analyzer"},
        }

    def _detect_investment(
        self, postings: list[dict[str, Any]], company_id: UUID
    ) -> dict[str, Any] | None:
        """Investment signal: critical/senior hires."""
        critical_hires: list[dict[str, Any]] = []

        for p in postings:
            seniority = (p.get("seniority_level") or "").lower().strip()
            dept = (p.get("department") or "unknown").lower().strip()
            title = (p.get("title") or "").lower()

            is_critical = (
                seniority in CRITICAL_SENIORITY
                or any(kw in title for kw in CRITICAL_DEPARTMENTS)
                or any(kw in dept for kw in CRITICAL_DEPARTMENTS)
            )

            if is_critical:
                critical_hires.append(
                    {
                        "job_posting_id": str(p["job_posting_id"]),
                        "title": p.get("title"),
                        "seniority_level": seniority,
                        "department": dept,
                        "location_city": p.get("location_city"),
                    }
                )

        if not critical_hires:
            return None

        score = min(100.0, len(critical_hires) * 20 + 10)
        confidence = min(100.0, 80 + len(critical_hires) * 5)

        return {
            "company_id": company_id,
            "signal_type": "investment",
            "signal_subtype": "executive_hiring",
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "evidence": {
                "job_posting_ids": [h["job_posting_id"] for h in critical_hires],
                "critical_hires": critical_hires,
                "hire_count": len(critical_hires),
            },
            "valid_until": (
                datetime.now(timezone.utc) + timedelta(days=SIGNAL_TTL_DAYS)
            ).isoformat(),
            "metadata": {"detector": "signal_analyzer"},
        }

    def _detect_geo_expansion(
        self, postings: list[dict[str, Any]], company_id: UUID
    ) -> dict[str, Any] | None:
        """Geo expansion signal: new cities in job postings."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=self.window_days)

        recent_cities: set[str] = set()
        recent_posting_ids: list[str] = []

        for p in postings:
            posted_at = self._parse_posted_at(p.get("posted_at"))
            if posted_at and posted_at < cutoff:
                continue
            city = p.get("location_city")
            if city:
                recent_cities.add(str(city).strip())
                recent_posting_ids.append(str(p["job_posting_id"]))

        existing_cities = self._load_existing_locations(company_id)
        new_cities = (
            recent_cities - existing_cities if existing_cities else recent_cities
        )

        if not new_cities:
            return None

        posting_ids = list(set(recent_posting_ids))
        score = min(100.0, len(new_cities) * 20 + 10)
        confidence = min(100.0, 70 + len(new_cities) * 10)

        return {
            "company_id": company_id,
            "signal_type": "geo_expansion",
            "signal_subtype": "new_location",
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "evidence": {
                "job_posting_ids": posting_ids,
                "new_locations": sorted(new_cities),
                "all_recent_locations": sorted(recent_cities),
            },
            "valid_until": (now + timedelta(days=SIGNAL_TTL_DAYS)).isoformat(),
            "metadata": {"detector": "signal_analyzer"},
        }

    def _detect_org_change(
        self, postings: list[dict[str, Any]], company_id: UUID
    ) -> dict[str, Any] | None:
        """Org change signal: new departments appearing in job postings."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=self.window_days)

        recent_departments: set[str] = set()
        recent_posting_ids: list[str] = []

        for p in postings:
            posted_at = self._parse_posted_at(p.get("posted_at"))
            if posted_at and posted_at < cutoff:
                continue
            dept = p.get("department")
            if dept:
                recent_departments.add(str(dept).strip().lower())
                recent_posting_ids.append(str(p["job_posting_id"]))

        existing_departments = self._load_existing_departments(company_id)
        new_departments = (
            recent_departments - existing_departments
            if existing_departments
            else recent_departments
        )

        if not new_departments:
            return None

        posting_ids = list(set(recent_posting_ids))
        score = min(100.0, len(new_departments) * 20 + 10)
        confidence = min(100.0, 70 + len(new_departments) * 10)

        return {
            "company_id": company_id,
            "signal_type": "org_change",
            "signal_subtype": "new_department",
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "evidence": {
                "job_posting_ids": posting_ids,
                "new_departments": sorted(new_departments),
                "all_recent_departments": sorted(recent_departments),
            },
            "valid_until": (now + timedelta(days=SIGNAL_TTL_DAYS)).isoformat(),
            "metadata": {"detector": "signal_analyzer"},
        }

    def _group_by_company(
        self, postings: list[dict[str, Any]]
    ) -> dict[UUID, list[dict[str, Any]]]:
        grouped: dict[UUID, list[dict[str, Any]]] = {}
        for p in postings:
            cid = p.get("company_id")
            if cid is None:
                continue
            if not isinstance(cid, UUID):
                try:
                    cid = UUID(str(cid))
                except (ValueError, TypeError):
                    continue
            grouped.setdefault(cid, []).append(p)
        return grouped

    def _save_signals(self, signals: list[dict[str, Any]]) -> int:
        if not signals:
            return 0

        with self._engine.begin() as conn:
            for sig in signals:
                company_id = sig["company_id"]
                sig_type = sig["signal_type"]
                sig_subtype = sig["signal_subtype"]

                conn.execute(
                    text("""
                        DELETE FROM company_signals
                        WHERE company_id = :cid
                          AND signal_type = :st
                          AND signal_subtype = :ss
                    """),
                    {"cid": company_id, "st": sig_type, "ss": sig_subtype},
                )

                conn.execute(
                    text("""
                        INSERT INTO company_signals
                            (company_id, signal_type, signal_subtype, score,
                             confidence, evidence, detected_at, valid_until, metadata)
                        VALUES
                            (:company_id, :signal_type, :signal_subtype, :score,
                             :confidence, :evidence, NOW(), :valid_until, :metadata)
                    """),
                    {
                        "company_id": str(sig["company_id"]),
                        "signal_type": sig_type,
                        "signal_subtype": sig_subtype,
                        "score": sig["score"],
                        "confidence": sig["confidence"],
                        "evidence": json.dumps(sig["evidence"], ensure_ascii=False),
                        "valid_until": sig["valid_until"],
                        "metadata": json.dumps(sig["metadata"], ensure_ascii=False),
                    },
                )

        return len(signals)

    @staticmethod
    def _chat_enricher_build() -> Any | None:
        """ChatEnricher kurar; modül/istemci yoksa None döner (graceful)."""
        if build_default_enricher is None or ChatEnricher is None:
            logger.info("ChatEnricher devre dışı (modül bulunamadı)")
            return None
        try:
            return build_default_enricher(skill_keywords=ENRICH_SKILL_KEYWORDS)
        except Exception as exc:  # noqa: BLE001 — istemci kurulum hatası tolere edilir
            logger.warning("ChatEnricher kurulamadı: %s", _kisa_hata(exc))
            return None

    def enrich_with_chat(self, postings: list[dict[str, Any]]) -> dict[str, Any]:
        """İlan listesini 9Router chat() ile zenginleştirir.

        Regresyon riskini sıfırlamak için mevcut ``analyze()`` akışına
        dokunmaz; bağımsız istatistik döndürür. 9Router yoksa regex fallback
        çalışır (katalog/9R-03 sözleşmesi).
        """
        sonuc = self._enricher
        if not sonuc:
            sonuc = self._chat_enricher_build() or ChatEnricher()

        stats: dict[str, Any] = {
            "ilan_sayisi": len(postings),
            "kaynak": {"chat": 0, "fallback": 0},
            "hata": 0,
            "zenginlestirilen": 0,
            "detay": [],
        }
        if not postings:
            return stats

        for posting in postings:
            try:
                r = sonuc.enrich(posting)
            except Exception as exc:  # noqa: BLE001 — tek ilan hatası akışı durdurmaz
                stats["hata"] += 1
                logger.warning("İlan zenginleştirme hatası: %s", _kisa_hata(exc))
                continue
            stats["detay"].append({"title": posting.get("title", ""), **r.to_dict()})
            stats["kaynak"][r.kaynak] = stats["kaynak"].get(r.kaynak, 0) + 1
            stats["zenginlestirilen"] += 1

        return stats

    @staticmethod
    def _sonuc_detayi(title: str, r: Any) -> dict[str, Any]:
        """Chat enricher çıktısını sözlüğe normalize eder (test kolaylığı)."""
        if r is not None and hasattr(r, "to_dict"):
            return {"title": title, **r.to_dict()}
        return {"title": title}

    def analyze(self) -> dict[str, Any]:
        """Ana analiz: job_postings'ten sinyaller çıkar ve kaydet."""
        logger.info("Signal analyzer başlatılıyor (window=%d gün)", self.window_days)

        postings = self._load_job_postings()
        logger.info("job_postings yüklendi: %d kayıt", len(postings))

        grouped = self._group_by_company(postings)
        logger.info("Şirket bazında gruplandırıldı: %d şirket", len(grouped))

        all_signals: list[dict[str, Any]] = []
        stats = {
            "companies_processed": 0,
            "signals_generated": 0,
            "by_type": {},
        }

        for company_id, comp_postings in grouped.items():
            comp_signals: list[dict[str, Any]] = []

            detectors = [
                self._detect_growth(comp_postings, company_id),
                self._detect_risk(comp_postings, company_id),
                self._detect_tech_transformation(comp_postings, company_id),
                self._detect_investment(comp_postings, company_id),
                self._detect_geo_expansion(comp_postings, company_id),
                self._detect_org_change(comp_postings, company_id),
            ]

            for sig in detectors:
                if sig is not None:
                    comp_signals.append(sig)
                    sig_type = sig["signal_type"]
                    stats["by_type"][sig_type] = stats["by_type"].get(sig_type, 0) + 1

            if comp_signals:
                all_signals.extend(comp_signals)

            stats["companies_processed"] += 1

        saved = self._save_signals(all_signals)
        stats["signals_generated"] = saved

        logger.info(
            "Sinyal analizi tamamlandı: %d şirket, %d sinyal kaydedildi",
            stats["companies_processed"],
            saved,
        )

        return stats


def _kisa_hata(exc: Exception) -> str:
    """İstisna mesajını tek satıra sıkıştırır (log güvenliği)."""
    msg = str(exc) or exc.__class__.__name__
    return " ".join(msg.split())[:200]


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    import argparse

    parser = argparse.ArgumentParser(description="Job Intelligence Signal Analyzer")
    parser.add_argument(
        "--enrich-chat",
        action="store_true",
        help="9Router chat() ile sektör/pozisyon/skill zenginleştirme açık",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=SIG_WINDOW_DAYS,
        help="Analiz penceresi (gün); varsayılan: %d" % SIG_WINDOW_DAYS,
    )
    args = parser.parse_args()

    analyzer = SignalAnalyzer(
        window_days=args.window_days,
        enrich_with_chat=args.enrich_chat,
    )
    result = analyzer.analyze()

    if analyzer._enrich_chat_aktif:
        result["zenginlestirme"] = analyzer.enrich_with_chat(
            analyzer._load_job_postings()
        )

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
