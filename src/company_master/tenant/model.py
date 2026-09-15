# -*- coding: utf-8 -*-
"""Tenant model — Multi-tenant context."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable
from pathlib import Path
from typing import Any

TENANT_ID_RE = re.compile(r"^[a-z0-9_-]{2,32}$")


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    ad: str
    plan: str = "standart"


VARSAYILAN_TENANT = TenantContext("huginn", "Huginn Data", "kurumsal")


def tenant_coz(kaynak: dict | None) -> TenantContext:
    if kaynak is None:
        return VARSAYILAN_TENANT
    tenant_id = kaynak.get("tenant_id")
    if not tenant_id or not isinstance(tenant_id, str):
        return VARSAYILAN_TENANT
    if not TENANT_ID_RE.match(tenant_id):
        raise ValueError(f"Geçersiz tenant_id: {tenant_id!r}")
    return TenantContext(
        tenant_id=tenant_id,
        ad=kaynak.get("ad", tenant_id),
        plan=kaynak.get("plan", "standart"),
    )


def tenant_dogrula(tenant_id: str) -> str:
    if not isinstance(tenant_id, str) or not TENANT_ID_RE.match(tenant_id):
        raise ValueError(f"Geçersiz tenant_id: {tenant_id!r}")
    return tenant_id
