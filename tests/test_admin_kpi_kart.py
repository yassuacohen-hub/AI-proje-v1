# -*- coding: utf-8 -*-
"""ADMIN-KPI-KART-01: Her sekmede st.metricavigasyon call kalmadığını doğrula."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest


_FILE_KATEGORI = {
    "admin_cost": "maliyet",
    "admin_quality": "kalite",
    "admin_performance": "sistem",
    "admin_api_analytics": "sistem",
    "admin_dlq": "uyari",
    "admin_audit": "guvenlik",
}

_ST_METRIC = re.compile(r"\bst\.metric\(")
_KPI_KARTI_CALL = re.compile(r"\bkpi_karti\(")
_CHARTS_IMPORT = re.compile(r"from web_dashboard\.charts import")
_KPI_IMPORT = re.compile(r"\bkpi_karti\b")


def _yorumsuz(kod: str) -> str:
    satirlar = []
    for satir in kod.split("\n"):
        satir = re.sub(r'#.*$', '', satir)
        satirlar.append(satir)
    return "\n".join(satirlar)


def _dosya_kaynak(modul_adi: str) -> str:
    path = (
        Path(__file__).resolve().parent.parent
        / "web_dashboard/tabs" / f"{modul_adi}.py"
    )
    return path.read_text(encoding="utf-8-sig")


@pytest.mark.parametrize("modul", list(_FILE_KATEGORI.keys()))
def test_st_metric_yok(modul: str) -> None:
    kod = _yorumsuz(_dosya_kaynak(modul))
    assert not _ST_METRIC.search(kod), f"{modul}.py hâlâ st.metric kullanıyor"


@pytest.mark.parametrize("modul", list(_FILE_KATEGORI.keys()))
def test_kpi_karti_cagiriliyor(modul: str) -> None:
    kod = _yorumsuz(_dosya_kaynak(modul))
    assert _KPI_KARTI_CALL.search(kod), f"{modul}.py kpi_karti çağırmıyor"


@pytest.mark.parametrize("modul", list(_FILE_KATEGORI.keys()))
def test_kpi_karti_import_edilmis(modul: str) -> None:
    kod = _dosya_kaynak(modul)
    assert _CHARTS_IMPORT.search(kod) and _KPI_IMPORT.search(kod), (
        f"{modul}.py kpi_karti import etmiyor"
    )


@pytest.mark.parametrize("modul", list(_FILE_KATEGORI.keys()))
def test_kategori_parametresi(modul: str) -> None:
    """AST ile kpi_karti-call kategori kwarg kontrolü."""
    kod = _dosya_kaynak(modul)
    tree = ast.parse(kod)
    kpi_calls = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "kpi_karti"
        ):
            kpi_calls.append(node)
    assert kpi_calls, f"{modul}.py kpi_karti call yok"
    for call in kpi_calls:
        kwarg_names = [
            kw.arg for kw in call.keywords if isinstance(kw, ast.keyword)
        ]
        assert "kategori" in kwarg_names, (
            f"{modul}.py kpi_karti call kategori eksik: "
            f"{ast.dump(call, indent=2)[:200]}"
        )

