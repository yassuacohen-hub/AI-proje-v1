#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Customer Brain Modulu - Musteri Segmentasyonu, LTV, Churn, Lead Scoring."""

from __future__ import annotations
import logging
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine

from company_master.db.connection import get_engine, get_session

logger = logging.getLogger(__name__)

_SECTOR_TABLE = {
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


def _sector_coef(sektor):
    return _SECTOR_TABLE.get(sektor, _SECTOR_TABLE["default"])


class CustomerBrain:
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
            logger.exception("CustomerBrain sorgusu basarisiz")
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

    def _get_company_row(self, comp):
        if isinstance(comp, str):
            params = {"company_id": comp}
            cond = "company_id = :company_id"
        elif isinstance(comp, dict):
            if comp.get("company_id"):
                params = {"company_id": comp["company_id"]}
                cond = "company_id = :company_id"
            elif comp.get("tax_number"):
                params = {"tax_number": comp["tax_number"]}
                cond = "tax_number = :tax_number"
            else:
                raise ValueError("comp dict en az company_id veya tax_number icermeli.")
        else:
            raise TypeError("comp str veya dict olmali.")
        sql = ("SELECT company_id, legal_name, tax_number, status, status_confidence, employee_count, is_ankara, is_osb_member, data_quality_score, entity_confidence, last_verified_at, created_at, updated_at FROM companies WHERE " + cond + " LIMIT 1")
        rows = self._fetch_all(sql, params)
        return rows[0] if rows else None

    def quality_score(self, comp):
        row = self._get_company_row(comp)
        if not row:
            return {"score": 0, "components": {}, "found": False, "caveat": "Sirket bulunamadi."}
        dq = self._safe_float(row.get("data_quality_score"))
        ec = self._safe_float(row.get("entity_confidence"))
        status = row.get("status")
        is_ankara = bool(row.get("is_ankara"))
        is_osb = bool(row.get("is_osb_member"))
        emp = self._safe_int(row.get("employee_count"), -1)
        last_v = row.get("last_verified_at")
        completeness = 0.0
        if dq > 0: completeness += 25.0
        if ec > 0: completeness += 20.0
        if status and status != "unknown": completeness += 15.0
        if emp >= 0: completeness += 15.0
        if is_ankara or is_osb: completeness += 10.0
        if last_v: completeness += 15.0
        recency = 0.0
        if last_v:
            try:
                lv = last_v
                if isinstance(lv, str):
                    lv = datetime.fromisoformat(lv.replace("Z", "+00:00"))
                if lv.tzinfo is None:
                    lv = lv.replace(tzinfo=timezone.utc)
                delta_days = (datetime.now(timezone.utc) - lv).days
                if delta_days <= 30: recency = 30.0
                elif delta_days <= 90: recency = 20.0
                elif delta_days <= 180: recency = 10.0
            except Exception:
                recency = 0.0
        raw = dq * 0.40 + ec * 0.25 + completeness * 0.20 + recency * 0.15
        score = int(round(max(0.0, min(100.0, raw))))
        return {"company_id": row.get("company_id"), "legal_name": row.get("legal_name"), "score": score, "components": {"data_quality_score": dq, "entity_confidence": ec, "field_completeness": completeness, "recency": recency}, "found": True, "caveat": "Skor bilesiktir."}

    def segment_companies(self):
        sql = ("SELECT c.company_id, c.legal_name, COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) AS sektor, COALESCE(c.employee_count, 0)::int AS employee_count, COALESCE(c.data_quality_score, 0)::float AS dq, COALESCE(c.status, CHR(39)unknownCHR(39)) AS status, COALESCE(c.is_ankara, FALSE) AS is_ankara, COALESCE(c.is_osb_member, FALSE) AS is_osb_member FROM companies c JOIN source_records sr ON c.source_record_id = sr.source_record_id")
        rows = self._fetch_all(sql, None)
        buckets = {"ENTERPRISE": [], "GROWTH": [], "SME": [], "UNVERIFIED": [], "INACTIVE": []}
        for r in rows:
            dq = self._safe_float(r.get("dq"))
            emp = self._safe_int(r.get("employee_count"))
            st = (r.get("status") or "unknown").lower()
            item = {"company_id": r.get("company_id"), "legal_name": r.get("legal_name"), "sektor": r.get("sektor"), "employee_count": emp, "data_quality": dq, "status": st}
            if st == "inactive":
                buckets["INACTIVE"].append(item)
            elif dq < 30 or st == "unknown":
                buckets["UNVERIFIED"].append(item)
            elif emp >= 50 and dq >= 70:
                buckets["ENTERPRISE"].append(item)
            elif emp >= 10:
                buckets["GROWTH"].append(item)
            else:
                buckets["SME"].append(item)
        result = []
        for seg, items in buckets.items():
            result.append({"segment": seg, "count": len(items), "share_pct": round((len(items) / max(1, len(rows))) * 100.0, 2), "avg_employee_count": round(sum(self._safe_int(i["employee_count"]) for i in items) / max(1, len(items)), 2), "avg_data_quality": round(sum(self._safe_float(i["data_quality"]) for i in items) / max(1, len(items)), 2)})
        return {"total_companies": len(rows), "segments": result, "buckets_detail": buckets}

    def lifetime_value_estimate(self, comp):
        row = self._get_company_row(comp)
        if not row:
            return {"found": False, "ltv_tl": 0.0, "caveat": "Sirket bulunamadi."}
        emp = self._safe_int(row.get("employee_count"))
        dq = self._safe_float(row.get("data_quality_score"))
        params = {"cid": row.get("company_id")}
        sektor_rows = self._fetch_all("SELECT COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) AS sektor FROM companies c JOIN source_records sr ON c.source_record_id = sr.source_record_id WHERE c.company_id = :cid LIMIT 1", params)
        sektor = (sektor_rows[0].get("sektor") if sektor_rows else "Bilinmiyor")
        coef = _sector_coef(sektor)
        base = emp * coef
        size_bonus = 0.0 if emp <= 0 else min(0.5, math.log10(max(emp, 1)) * 0.2)
        quality_mult = max(0.3, dq / 100.0)
        ltv = base * (1.0 + size_bonus) * quality_mult
        return {"found": True, "company_id": row.get("company_id"), "legal_name": row.get("legal_name"), "sektor": sektor, "employee_count": emp, "data_quality_score": dq, "ltv_tl": round(ltv, 2), "method": "employee_count * sector_coef * quality_multiplier", "caveat": "Tahmini."}

    def churn_risk(self, comp):
        row = self._get_company_row(comp)
        if not row:
            return {"found": False, "risk": "UNKNOWN", "caveat": "Sirket bulunamadi."}
        dq = self._safe_float(row.get("data_quality_score"))
        st = (row.get("status") or "unknown").lower()
        last_v = row.get("last_verified_at")
        days_since = None
        if last_v:
            try:
                lv = last_v
                if isinstance(lv, str):
                    lv = datetime.fromisoformat(lv.replace("Z", "+00:00"))
                if lv.tzinfo is None:
                    lv = lv.replace(tzinfo=timezone.utc)
                days_since = (datetime.now(timezone.utc) - lv).days
            except Exception:
                days_since = None
        reasons = []
        if dq < 30: reasons.append("dusuk_veri_kalitesi")
        if st == "inactive": reasons.append("status_inactive")
        if days_since is None or days_since > 180: reasons.append("stale_verification")
        if st == "unknown": reasons.append("status_unknown")
        if dq < 30 or st == "inactive" or (days_since is not None and days_since > 180):
            risk = "HIGH"
        elif dq < 60 or st == "unknown" or (days_since is not None and days_since > 90):
            risk = "MEDIUM"
        else:
            risk = "LOW"
        return {"found": True, "company_id": row.get("company_id"), "legal_name": row.get("legal_name"), "risk": risk, "reasons": reasons, "data_quality_score": dq, "status": st, "days_since_verified": days_since, "caveat": "Kural tabanli."}

    def priority_leads(self, top_n=50):
        sql = ("SELECT c.company_id, c.legal_name, COALESCE(NULLIF(TRIM(sr.raw_payload->>CHR(39)sektorCHR(39)), CHR(39)CHR(39)), CHR(39)BilinmiyorCHR(39)) AS sektor, COALESCE(c.employee_count, 0)::int AS employee_count, COALESCE(c.data_quality_score, 0)::float AS dq, COALESCE(c.entity_confidence, 0)::float AS ec, COALESCE(c.status, CHR(39)unknownCHR(39)) AS status, c.last_verified_at FROM companies c JOIN source_records sr ON c.source_record_id = sr.source_record_id ORDER BY COALESCE(c.data_quality_score, 0) DESC LIMIT 500")
        rows = self._fetch_all(sql, None)
        if not rows:
            return []
        max_emp = max(self._safe_int(r.get("employee_count")) for r in rows) or 1
        now = datetime.now(timezone.utc)
        scored = []
        for r in rows:
            dq = self._safe_float(r.get("dq"))
            ec = self._safe_float(r.get("ec"))
            emp = self._safe_int(r.get("employee_count"))
            st = (r.get("status") or "unknown").lower()
            lv = r.get("last_verified_at")
            days_since = None
            if lv:
                try:
                    if isinstance(lv, str):
                        lv_dt = datetime.fromisoformat(lv.replace("Z", "+00:00"))
                    else:
                        lv_dt = lv
                    if lv_dt.tzinfo is None:
                        lv_dt = lv_dt.replace(tzinfo=timezone.utc)
                    days_since = (now - lv_dt).days
                except Exception:
                    days_since = None
            size_score = emp / max_emp
            activity = 1.0 if st == "active" else (0.5 if st == "unknown" else 0.0)
            if days_since is None:
                recency = 0.0
            elif days_since <= 30:
                recency = 1.0
            elif days_since <= 90:
                recency = 0.7
            elif days_since <= 180:
                recency = 0.3
            else:
                recency = 0.0
            score = 0.4 * (dq / 100.0) + 0.3 * size_score + 0.2 * activity + 0.1 * recency
            scored.append({"company_id": r.get("company_id"), "legal_name": r.get("legal_name"), "sektor": r.get("sektor"), "employee_count": emp, "data_quality_score": dq, "entity_confidence": ec, "status": st, "days_since_verified": days_since, "priority_score": round(score * 100.0, 2)})
        scored.sort(key=lambda x: x["priority_score"], reverse=True)
        return scored[: max(0, int(top_n))]


def run_analysis(top_n=50):
    b = CustomerBrain()
    return {"segments": b.segment_companies(), "priority_leads": b.priority_leads(top_n=top_n)}


if __name__ == "__main__":
    import json
    print(json.dumps(run_analysis(top_n=10), ensure_ascii=False, indent=2, default=str))
