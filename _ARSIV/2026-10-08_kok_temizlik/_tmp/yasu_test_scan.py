# -*- coding: utf-8 -*-
"""Yasu gorev durum taramasi - test sonuclari (tail'siz)."""
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = Path(r"c:\HUGINN~1\HUGINN~1")
os.chdir(BASE)


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    out = (r.stdout or "") + (r.stderr or "")
    # son 8 satir
    satirlar = [s for s in out.splitlines() if s.strip()]
    return "\n".join(satirlar[-8:])


print("=== 3. VERI-RAPIDAPI-OSINT-ISTEMCI-01 ===")
print(run("python -m pytest tests/test_rapidapi_osint.py -q"))

print("\n=== 6. ORCH-KODLAMA-TEMIZLIK-01 ===")
print(run("python scripts/kodlama_denetim.py --kapsam kod"))

print("\n=== 1b. NETWORK IMPORT/DERLEME ===")
print(run("python -c \"import ast; ast.parse(open('src/company_master/api/routers/v1/v1_network.py',encoding='utf-8').read()); print('PARSE_OK')\""))
