# -*- coding: utf-8 -*-
"""TEN-01 tenant bekci — AST scan test."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest


def _find_tenant_module():
    for p in sys.path:
        mod_path = Path(p) / "company_master" / "tenant"
        if mod_path.exists():
            return mod_path
    return None


def test_tenant_no_streamlit_auth_import():
    mod_path = _find_tenant_module()
    assert mod_path is not None, "tenant module bulunamadi"

    for py_file in list(mod_path.rglob("*.py")):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("streamlit"), \
                        f"{py_file}: streamlit import yasak: {alias.name}"
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "streamlit" not in node.module, \
                        f"{py_file}: streamlit import yasak: {node.module}"
                for alias in (node.names or []):
                    assert "streamlit" not in alias.name, \
                        f"{py_file}: streamlit import yasak: {alias.name}"
            if isinstance(node, ast.Attribute):
                assert node.attr != "streamlit", \
                    f"{py_file}: streamlit attribute yasak"


def test_tenant_frozen_context():
    mod_path = _find_tenant_module()
    assert mod_path is not None
    model_py = mod_path / "model.py"
    assert model_py.exists(), "model.py bulunamadi"
    source = model_py.read_text(encoding="utf-8")
    assert "frozen=True" in source, "TenantContext frozen=True olmali"
