# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text
from company_master.db.connection import get_engine

class IntelligenceRepository:
    def __init__(self) -> None:
        self.engine = get_engine()

    def _to_dict(self, row: Any) -> dict:
        return dict(row._mapping)

    def get_company_scores(self, company_id: str) -> dict | None:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM company_intelligence_scores WHERE company_id = :cid"),
                {"cid": uuid.UUID(company_id)}
            ).mappings().first()
            return dict(result) if result else None

    def get_top_growing_companies(self, limit: int = 10) -> list[dict]:
        with self.engine.connect() as conn:
            results = conn.execute(
                text("SELECT * FROM company_intelligence_scores ORDER BY growth_score DESC LIMIT :limit"),
                {"limit": limit}
            ).mappings().all()
            return [dict(r) for r in results]

    def get_top_investment_targets(self, limit: int = 10) -> list[dict]:
        with self.engine.connect() as conn:
            results = conn.execute(
                text("SELECT * FROM company_intelligence_scores ORDER BY investment_signal_score DESC LIMIT :limit"),
                {"limit": limit}
            ).mappings().all()
            return [dict(r) for r in results]

    def get_high_risk_companies(self, limit: int = 10) -> list[dict]:
        with self.engine.connect() as conn:
            results = conn.execute(
                text("SELECT * FROM company_intelligence_scores ORDER BY risk_score DESC LIMIT :limit"),
                {"limit": limit}
            ).mappings().all()
            return [dict(r) for r in results]

    def get_company_signals(self, company_id: str, limit: int = 50) -> list[dict]:
        with self.engine.connect() as conn:
            results = conn.execute(
                text("SELECT * FROM company_signals WHERE company_id = :cid ORDER BY detected_at DESC LIMIT :limit"),
                {"cid": uuid.UUID(company_id), "limit": limit}
            ).mappings().all()
            return [dict(r) for r in results]

    def get_company_job_postings(self, company_id: str, limit: int = 50) -> list[dict]:
        with self.engine.connect() as conn:
            results = conn.execute(
                text("SELECT * FROM job_postings WHERE company_id = :cid ORDER BY posted_at DESC LIMIT :limit"),
                {"cid": uuid.UUID(company_id), "limit": limit}
            ).mappings().all()
            return [dict(r) for r in results]

    def save_intelligence_scores(self, scores: dict) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO company_intelligence_scores (
                        company_id, growth_score, expansion_score, tech_transformation_score,
                        investment_signal_score, org_change_score, risk_score, 
                        hiring_trend, new_locations, new_departments, critical_hires, 
                        detected_signals, overall_confidence
                    )
                    VALUES (
                        :company_id, :growth_score, :expansion_score, :tech_transformation_score,
                        :investment_signal_score, :org_change_score, :risk_score, 
                        :hiring_trend, :new_locations, :new_departments, :critical_hires, 
                        :detected_signals, :overall_confidence
                    )
                    ON CONFLICT (company_id) DO UPDATE SET
                        growth_score = EXCLUDED.growth_score,
                        expansion_score = EXCLUDED.expansion_score,
                        tech_transformation_score = EXCLUDED.tech_transformation_score,
                        investment_signal_score = EXCLUDED.investment_signal_score,
                        org_change_score = EXCLUDED.org_change_score,
                        risk_score = EXCLUDED.risk_score,
                        hiring_trend = EXCLUDED.hiring_trend,
                        new_locations = EXCLUDED.new_locations,
                        new_departments = EXCLUDED.new_departments,
                        critical_hires = EXCLUDED.critical_hires,
                        detected_signals = EXCLUDED.detected_signals,
                        overall_confidence = EXCLUDED.overall_confidence,
                        updated_at = NOW()
                """),
                {
                    **scores,
                    "company_id": uuid.UUID(scores["company_id"]),
                    "new_locations": json.dumps(scores.get("new_locations", [])),
                    "new_departments": json.dumps(scores.get("new_departments", [])),
                    "critical_hires": json.dumps(scores.get("critical_hires", [])),
                    "detected_signals": json.dumps(scores.get("detected_signals", [])),
                }
            )

    def save_tech_profile(self, profile: dict) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO company_tech_profile (
                        company_id, technologies, tech_categories, modernization_signals,
                        tech_stack_maturity, innovation_index
                    )
                    VALUES (
                        :company_id, :technologies, :tech_categories, :modernization_signals,
                        :tech_stack_maturity, :innovation_index
                    )
                    ON CONFLICT (company_id) DO UPDATE SET
                        technologies = EXCLUDED.technologies,
                        tech_categories = EXCLUDED.tech_categories,
                        modernization_signals = EXCLUDED.modernization_signals,
                        tech_stack_maturity = EXCLUDED.tech_stack_maturity,
                        innovation_index = EXCLUDED.innovation_index,
                        last_updated = NOW()
                """),
                {
                    **profile,
                    "company_id": uuid.UUID(profile["company_id"]),
                    "technologies": json.dumps(profile.get("technologies", {})),
                    "tech_categories": json.dumps(profile.get("tech_categories", {})),
                    "modernization_signals": json.dumps(profile.get("modernization_signals", [])),
                }
            )

