from __future__ import annotations

from datetime import datetime, timezone

import importlib

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .scope import PAKET_SCOPES, paket_bul
from ..paket_scope import PAKET_SCOPES as _PS


def _wa():
    return importlib.import_module("web_app")


router = APIRouter(prefix="/fraud-check", tags=["v1_fraud"])


class FraudRequest(BaseModel):
    vkn: str = Field(..., min_length=10, max_length=11, description="VKN/TCKN")
    reason: str | None = Field(
        None, max_length=500, description="Fraud kontrol nedeni / aciklama"
    )


class FraudResponse(BaseModel):
    vkn: str
    legal_name: str | None
    fraud_risk_score: float | None
    recommendation_tier: str | None
    is_fraud_risk: bool
    reason: str | None
    checked_at: str
    credit_balance: int | None


@router.post("", response_model=FraudResponse, response_model_exclude_none=True)
def fraud_check(payload: FraudRequest, request: Request):
    """POST /api/v1/fraud-check — VKN uzerinden fraud risk puani (1 kredi / analiz).
    D-206: paketine gore kontor; enterprise serbest."""
    wa = _wa()
    user = wa.require_api_key(request)
    tier = paket_bul(user)
    remaining = wa._charge_module_credit(str(user), tier, "analiz")
    if remaining == 0:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "credit_exhausted",
                "credit_balance": 0,
                "credit_pack": "750 TRY / 50 kredi (credit pack ile devam edebilirsiniz)",
            },
        )

    with wa.get_engine().connect() as conn:
        row = (
            conn.execute(
                wa.text(
                    """
                    SELECT c.tax_number, c.legal_name, c.trade_name,
                           r.fraud_risk_score, r.recommendation_tier, r.calculated_at
                    FROM companies c
                    LEFT JOIN company_risk_scores r ON r.company_id = c.company_id
                    WHERE c.tax_number = :vkn
                    """
                ),
                {"vkn": payload.vkn},
            )
            .mappings()
            .first()
        )
    if not row:
        return FraudResponse(
            vkn=payload.vkn,
            legal_name=None,
            fraud_risk_score=None,
            is_fraud_risk=False,
            checked_at=datetime.now(timezone.utc).isoformat(),
            credit_balance=remaining,
        )

    score = float(row["fraud_risk_score"]) if row["fraud_risk_score"] is not None else None
    tier_val = row["recommendation_tier"]
    is_fraud = score is not None and score >= 0.65
    legal_name = wa.normalize_company({"legal_name": row["legal_name"]})["legal_name"]

    return FraudResponse(
        vkn=row["tax_number"],
        legal_name=legal_name,
        fraud_risk_score=score,
        recommendation_tier=tier_val,
        is_fraud_risk=is_fraud,
        reason=payload.reason,
        checked_at=(
            row["calculated_at"].isoformat()
            if row["calculated_at"]
            else datetime.now(timezone.utc).isoformat()
        ),
        credit_balance=remaining,
    )
