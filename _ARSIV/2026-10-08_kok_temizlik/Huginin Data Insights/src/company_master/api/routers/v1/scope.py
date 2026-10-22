from __future__ import annotations

import importlib

from fastapi import Depends, HTTPException

# D-251/5: scope dict tek kaynak. Her paket → (scope_list, kredi_boolean).
PAKET_SCOPES: dict[str, dict] = {
    "free": {
        "scopes": ["read_company_vkn", "fraud_check_basic"],
        "credit_consuming": False,
        "description": "Ücretsiz katman; temel sorgu + temel fraud kontrol.",
    },
    "basic": {
        "scopes": [
            "read_company_vkn",
            "read_company_detail",
            "fraud_check_basic",
            "fraud_check_advanced",
        ],
        "credit_consuming": True,
        "description": "Ücretli paket; v1 firma sorgu ve fraud kontrolu.",
    },
    "pro": {
        "scopes": [
            "read_company_vkn",
            "read_company_detail",
            "fraud_check_basic",
            "fraud_check_advanced",
            "export_company",
        ],
        "credit_consuming": True,
        "description": "Pro paket; tüm v1 endpoint'ler + export.",
    },
    "enterprise": {
        "scopes": [
            "read_company_vkn",
            "read_company_detail",
            "fraud_check_basic",
            "fraud_check_advanced",
            "export_company",
            "admin_mask_override",
        ],
        "credit_consuming": False,
        "description": "Kurumsal; kredi yok, tüm scope + admin mask override.",
    },
}

_DEFAULT_PAKET = "basic"


def _web_app():
    return importlib.import_module("web_app")


def paket_bul(auth_key: str) -> str:
    """API key sahibinin paketini getirir. web_app.require_api_key'e bagli;
    tek kaynak (D-251/5: iki kopya olmaz)."""
    wa = _web_app()
    uid = auth_key or ""
    if not uid:
        return _DEFAULT_PAKET
    try:
        row = wa._api_key_user(str(uid))
    except Exception:
        return _DEFAULT_PAKET
    return (row or {}).get("tier") or _DEFAULT_PAKET


def scope_gerekli(requires: str | list[str] | None = None):
    """FastAPI Depends — aktif paketin `requires` scope(lar)ını kontrol eder.
    eksik → 403. enterprise hiç zaman bloklanmaz."""
    scoplist = (
        requires
        if isinstance(requires, list)
        else ([requires] if requires else [])
    )

    def _checker(api_key: str | None = None, x_api_key: str | None = None):
        wa = _web_app()
        key = x_api_key or api_key
        user = wa.require_api_key(key) if key else None
        if not user:
            raise HTTPException(status_code=401, detail="API key zorunlu")
        paket = paket_bul(user)
        allowed = PAKET_SCOPES.get(paket, {}).get("scopes", [])
        missing = [s for s in scoplist if s not in allowed]
        if missing:
            raise HTTPException(
                status_code=403,
                detail=f"Paket '{paket}' scope eksik: {missing}",
            )
        return {"paket": paket, "auth": user, "missing": missing}

    return _checker
