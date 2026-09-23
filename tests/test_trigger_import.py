# -*- coding: utf-8 -*-
"""ALTYAPI-IMPORT-TEKLES-01: trigger.py import yolu iki baglamda da calismali.

Baglam 1: repo kokunden `from src.company_master.orchestrator import trigger`
          (scripts'lerin kullandigi yol).
Baglam 2: `sys.path=src` ile `from company_master.orchestrator import trigger`
          (paket-ic yolu).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]


def _py(kod: str, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-c", kod],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=cwd,
    )


def test_kok_baglaminda_import_calisir():
    """scripts/ bolumundeki klasik yol: kok sys.path'te, src. oneki ile."""
    r = _py("from src.company_master.orchestrator import trigger; print('OK')", str(KOK))
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_paket_baglaminda_import_calisir():
    """sys.path=src ile kok-mutlak import KIRILMAZ (gorili import duzeltmesi)."""
    r = _py(
        "import sys; sys.path.insert(0, 'src'); "
        "from company_master.orchestrator import trigger; print('OK')",
        str(KOK),
    )
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_uzaktan_cagirma_baglaminda_import_calisir():
    """trigger.py kok-mutlak import icermedigi icin farkli cwd'den de import
    edilebilmeli (kok neden: pano_denetim ithalat uyarisi)."""
    src_yolu = str(KOK / "src")
    kod = (
        "import sys; sys.path.insert(0, r'" + src_yolu + "'); "
        "from company_master.orchestrator import trigger; print('OK')"
    )
    r = _py(kod, str(KOK / "scripts"))
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_gorev_kutusu_scripts_baglaminda_calisir():
    """Kritik cagiran: gorev_kutusu.py'ye --help ile dokunmadan calisir mi."""
    r = subprocess.run(
        [sys.executable, "-X", "utf8", "scripts/gorev_kutusu.py", "--help"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(KOK),
    )
    assert r.returncode == 0, r.stderr
    assert "al" in r.stdout
