# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from company_master.intelligence.job_intelligence.storage.intelligence_repo import IntelligenceRepository

router = APIRouter(prefix="/api/intelligence", tags=["Job Intelligence"])

def get_repo():
    return IntelligenceRepository()

@router.get("/company/{company_id}")
async def get_intelligence(company_id: str, repo: IntelligenceRepository = Depends(get_repo)):
    try:
        data = await repo.get_company_intelligence(company_id)
        if not data:
            raise HTTPException(status_code=404, detail="Company not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-growth")
async def get_top_growth(limit: int = 20, repo: IntelligenceRepository = Depends(get_repo)):
    try:
        return await repo.get_top_growth(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-investment")
async def get_top_investment(limit: int = 20, repo: IntelligenceRepository = Depends(get_repo)):
    try:
        return await repo.get_top_investment(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-signals")
async def get_risk_signals(limit: int = 20, repo: IntelligenceRepository = Depends(get_repo)):
    try:
        return await repo.get_risk_signals(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/{company_id}")
async def get_signals(company_id: str, repo: IntelligenceRepository = Depends(get_repo)):
    try:
        data = await repo.get_signals(company_id)
        if data is None:
            raise HTTPException(status_code=404, detail="Signals not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/postings/{company_id}")
async def get_postings(company_id: str, repo: IntelligenceRepository = Depends(get_repo)):
    try:
        data = await repo.get_job_postings(company_id)
        if data is None:
            raise HTTPException(status_code=404, detail="Postings not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
