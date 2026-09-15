# -*- coding: utf-8 -*-
"""TEN-01 tenant tests."""
from __future__ import annotations

import pytest
from company_master.tenant.model import (
    TenantContext,
    VARSAYILAN_TENANT,
    tenant_coz,
    tenant_dogrula,
)


def test_varsayilan_tenant():
    assert VARSAYILAN_TENANT.tenant_id == "huginn"
    assert VARSAYILAN_TENANT.ad == "Huginn Data"
    assert VARSAYILAN_TENANT.plan == "kurumsal"


def test_frozen():
    ctx = TenantContext("abc", "Test")
    with pytest.raises(Exception):
        ctx.tenant_id = "xxx"


def test_coz_none_returns_default():
    assert tenant_coz(None) == VARSAYILAN_TENANT


def test_coz_valid():
    result = tenant_coz({"tenant_id": "myco", "ad": "My Company", "plan": "pro"})
    assert result.tenant_id == "myco"
    assert result.ad == "My Company"
    assert result.plan == "pro"


def test_coz_empty_returns_default():
    assert tenant_coz({}) == VARSAYILAN_TENANT
    assert tenant_coz({"tenant_id": ""}) == VARSAYILAN_TENANT
    assert tenant_coz({"tenant_id": None}) == VARSAYILAN_TENANT


def test_coz_invalid_id():
    with pytest.raises(ValueError):
        tenant_coz({"tenant_id": "AB"})


def test_dogrula_valid():
    assert tenant_dogrula("huginn") == "huginn"


def test_dogrula_invalid():
    with pytest.raises(ValueError):
        tenant_dogrula("invalid id!")
