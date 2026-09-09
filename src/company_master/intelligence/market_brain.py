#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Market Brain Modulu - Pazar Analizi ve Sektor Istihbarati."""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

from company_master.db.connection import get_engine, get_session

logger = logging.getLogger(__name__)

_SECTOR_REVENUE_PER_EMPLOYEE = {
    "default": 350000.0,
    "Teknoloji ve Bilisim": 650000.0,
    "Imalat": 520000.0,
    "Savunma ve Havacilik": 850000.0,
    "Otomotiv": 720000.0,
    "Makine ve Techizat": 480000.0,
    "Metal Sanayi": 410000.0,
    "Plastik ve Kaucuk": 460000.0,
    "Elektrik ve Elektronik": 590000.0,
    "Kimya": 620000.0,
    "Gida": 380000.0,
    "Tekstil": 320000.0,
    "Insaat": 340000.0,
    "Lojistik": 420000.0,
    "Enerji": 780000.0,
}


class MarketBrain:
    def __init__(self, engine=None):
        self._engine = engine if engine is not None else get_engine()

    def _fetch_all(self, sql, params=None):
        session = get_session()
        try:
            statement = text(sql)
            if params:
                statement = statement.bindparams(**params)
            rows = session.execute(statement).mappings().all()
            return [dict(r) for r in rows]
        except Exception:
            logger.exception("MarketBrain sorgusu basarisiz")
            raise
        finally:
            session.close()

    @staticmethod
    def _safe_float(value, default=0.0):
        if value is None:
            return default
        try:
            r = float(value)
            return default if r != r else r
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_int(value, default=0):
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def sector_count(self):
        sql = (
            "SELECT COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) AS sektor, "
            "COUNT(*)::int AS company_count "
            "FROM companies c "
            "JOIN source_records sr ON c.source_record_id = sr.source_record_id "
            "GROUP BY COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) "
            "ORDER BY company_count DESC, sektor ASC"
        )
        rows = self._fetch_all(sql, None)
        total = sum(self._safe_int(r.get("company_count")) for r in rows) or 1
        for row in rows:
            c = self._safe_int(row.get("company_count"))
            row["company_count"] = c
            row["share_pct"] = round((c / total) * 100.0, 2)
        return rows

    def market_size_estimate(self, sector=None):
        params = {}
        sector_filter = ""
        if sector:
            sector_filter = "AND COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) = :sector"
            params["sector"] = sector
        sql = (
            "SELECT COUNT(*)::int AS company_count, "
            "COALESCE(SUM(c.employee_count), 0)::int AS total_employees, "
            "COALESCE(AVG(c.employee_count), 0)::float AS avg_employees, "
            "COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) AS sektor "
            "FROM companies c "
            "JOIN source_records sr ON c.source_record_id = sr.source_record_id "
            "WHERE 1=1 " + sector_filter + " "
            "GROUP BY COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) "
            "ORDER BY company_count DESC"
        )
        rows = self._fetch_all(sql, params if params else None)
        if not rows:
            return {"sector": sector, "company_count": 0, "total_employee_estimate": 0, "estimated_revenue_tl": 0.0, "method": "literature_coefficient_per_employee", "confidence": "low", "caveat": "Veri bulunamadi."}
        total_company = sum(self._safe_int(r.get("company_count")) for r in rows)
        total_employees = sum(self._safe_int(r.get("total_employees")) for r in rows)
        weighted = 0.0
        for r in rows:
            sektor = r.get("sektor") or "Bilinmiyor"
            cnt = self._safe_int(r.get("company_count"))
            avg_emp = self._safe_float(r.get("avg_employees"), 0.0)
            coef = _SECTOR_REVENUE_PER_EMPLOYEE.get(sektor, _SECTOR_REVENUE_PER_EMPLOYEE["default"])
            weighted += cnt * avg_emp * coef
        if total_company >= 100 and total_employees > 0:
            conf = "medium"
        elif total_company >= 10:
            conf = "low"
        else:
            conf = "very_low"
        return {"sector": sector, "company_count": total_company, "total_employee_estimate": total_employees, "estimated_revenue_tl": round(weighted, 2), "method": "literature_coefficient_per_employee", "confidence": conf, "caveat": "Tahmini deger; sektorel katsayilar TUIK/TOBB ortalamalarina dayanir."}

    def competitive_analysis(self, sektor, top_n=10):
        if not sektor or not str(sektor).strip():
            raise ValueError("sektor parametresi zorunludur ve bos olamaz.")
        params = {"sektor": str(sektor).strip(), "top_n": int(top_n)}
        summary_sql = (
            "SELECT COUNT(*)::int AS company_count, "
            "COALESCE(AVG(c.data_quality_score), 0)::float AS avg_quality, "
            "COALESCE(AVG(c.employee_count), 0)::float AS avg_employees, "
            "COALESCE(SUM(CASE WHEN c.is_ankara THEN 1 ELSE 0 END), 0)::int AS ankara_count, "
            "COALESCE(SUM(CASE WHEN c.is_osb_member THEN 1 ELSE 0 END), 0)::int AS osb_count "
            "FROM companies c "
            "JOIN source_records sr ON c.source_record_id = sr.source_record_id "
            "WHERE COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) = :sektor"
        )
        srows = self._fetch_all(summary_sql, params)
        s = srows[0] if srows else {}
        cc = self._safe_int(s.get("company_count"))
        aq = self._safe_float(s.get("avg_quality"))
        ae = self._safe_float(s.get("avg_employees"))
        ac = self._safe_int(s.get("ankara_count"))
        oc = self._safe_int(s.get("osb_count"))
        if cc == 0: density = "unknown"
        elif cc >= 200: density = "high"
        elif cc >= 50: density = "medium"
        else: density = "low"
        top_sql = (
            "SELECT c.legal_name, COALESCE(c.employee_count, 0)::int AS employee_count, "
            "COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) AS sektor "
            "FROM companies c "
            "JOIN source_records sr ON c.source_record_id = sr.source_record_id "
            "WHERE COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) = :sektor "
            "ORDER BY COALESCE(c.employee_count, 0) DESC, c.legal_name ASC LIMIT :top_n"
        )
        trows = self._fetch_all(top_sql, params)
        return {"sektor": params["sektor"], "company_count": cc, "avg_data_quality": round(aq, 2), "avg_employee_count": round(ae, 2), "ankara_ratio": round((ac / cc) * 100.0, 2) if cc else 0.0, "osb_member_ratio": round((oc / cc) * 100.0, 2) if cc else 0.0, "competition_density": density, "top_competitors": [{"legal_name": r.get("legal_name"), "employee_count": self._safe_int(r.get("employee_count")), "sektor": r.get("sektor")} for r in trows], "caveat": "Sektor bilgisi source_records.raw_payload->>sektor uzerinden okunur."}

    def trending_sectors(self, limit=10, min_companies=3):
        params = {"min_companies": int(min_companies)}
        sql = (
            "SELECT COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) AS sektor, "
            "COUNT(*)::int AS company_count, "
            "COALESCE(AVG(c.data_quality_score), 0)::float AS avg_quality, "
            "COALESCE(AVG(c.employee_count), 0)::float AS avg_employees "
            "FROM companies c "
            "JOIN source_records sr ON c.source_record_id = sr.source_record_id "
            "GROUP BY COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) "
            "HAVING COUNT(*) >= :min_companies "
            "ORDER BY company_count DESC"
        )
        rows = self._fetch_all(sql, params)
        if not rows:
            return []
        max_count = max(self._safe_int(r.get("company_count")) for r in rows) or 1
        results = []
        for r in rows:
            cnt = self._safe_int(r.get("company_count"))
            aq = self._safe_float(r.get("avg_quality"))
            nc = cnt / max_count
            nq = min(max(aq / 100.0, 0.0), 1.0)
            score = (0.6 * nc + 0.4 * nq) * 100.0
            results.append({"sektor": r.get("sektor"), "company_count": cnt, "avg_data_quality": round(aq, 2), "avg_employee_count": round(self._safe_float(r.get("avg_employees")), 2), "trend_score": round(score, 2)})
        results.sort(key=lambda x: x["trend_score"], reverse=True)
        return results[: max(0, int(limit))]


def run_analysis(sector=None):
    b = MarketBrain()
    return {"sector_count": b.sector_count(), "market_size": b.market_size_estimate(sector), "trending": b.trending_sectors(), "sector_detail": b.competitive_analysis(sector) if sector else None}


if __name__ == "__main__":
    import json
    print(json.dumps(run_analysis(), ensure_ascii=False, indent=2, default=str))
