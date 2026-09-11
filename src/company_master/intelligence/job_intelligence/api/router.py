# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from company_master.intelligence.job_intelligence.storage.intelligence_repo import (
    IntelligenceRepository,
)

router = APIRouter(prefix="/api/intelligence", tags=["Job Intelligence"])


def get_repo() -> IntelligenceRepository:
    return IntelligenceRepository()


@router.get("/company/{company_id}")
def get_company_intelligence(
    company_id: str, repo: IntelligenceRepository = Depends(get_repo)
):
    data = repo.get_company_scores(company_id)
    if not data:
        raise HTTPException(status_code=404, detail="Company not found")
    return data


@router.get("/top-growth")
def get_top_growth(limit: int = 20, repo: IntelligenceRepository = Depends(get_repo)):
    return repo.get_top_growing_companies(limit)


@router.get("/top-investment")
def get_top_investment(
    limit: int = 20, repo: IntelligenceRepository = Depends(get_repo)
):
    return repo.get_top_investment_targets(limit)


@router.get("/risk-signals")
def get_risk_signals(limit: int = 20, repo: IntelligenceRepository = Depends(get_repo)):
    return repo.get_high_risk_companies(limit)


@router.get("/signals/{company_id}")
def get_signals(company_id: str, repo: IntelligenceRepository = Depends(get_repo)):
    data = repo.get_company_signals(company_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Signals not found")
    return {"company_id": company_id, "signals": data}


@router.get("/postings/{company_id}")
def get_postings(company_id: str, repo: IntelligenceRepository = Depends(get_repo)):
    data = repo.get_company_job_postings(company_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Postings not found")
    return {"company_id": company_id, "postings": data}
