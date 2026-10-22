# -*- coding: utf-8 -*-
import os, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KOK = Path(r"c:\HUGINN~1\HUGINN~1")
os.chdir(KOK)
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")

# API-V1-NETWORK cift tanim
src = (KOK/"src/company_master/api/routers/v1/v1_network.py").read_text(encoding="utf-8", errors="replace")
import re
print("=== API-V1-NETWORK-REPORT-01 ===")
print("  _fetch_company_by_vkn tanim sayisi:", len(re.findall(r"def _fetch_company_by_vkn", src)))
print("  _get_company_vkn tanim sayisi:", len(re.findall(r"def _get_company_vkn", src)))
print("  test dosyasi:", "VAR" if (KOK/"tests/test_api_v1_network.py").exists() else "YOK")
print("  py_compile:", end=" ")
r = subprocess.run([sys.executable,"-m","py_compile","src/company_master/api/routers/v1/v1_network.py"], cwd=KOK, capture_output=True, text=True)
print("OK" if r.returncode==0 else "FAIL "+r.stderr[-200:])

# git takipsiz sayisi
st = subprocess.run(["git","status","--short"], cwd=KOK, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
untracked = [l for l in st.splitlines() if l.startswith("??")]
print("\n=== ALTYAPI-REPO-TEMIZLIK-01 ===")
print("  takipsiz (??) dosya sayisi:", len(untracked))
print("  _ARSIV:", "VAR" if (KOK/"_ARSIV").exists() else "YOK")
print("  _ARSIV_tek_kullanimlik:", "VAR" if (KOK/"_ARSIV_tek_kullanimlik").exists() else "YOK")

# ORCH kodlama: sadece kod dizinleri (kapsam git) kendi dosyalari
print("\n=== ORCH-KODLAMA-TEMIZLIK-01 (kapsam=kod, ozet sayilar) ===")
r = subprocess.run([sys.executable,"scripts/kodlama_denetim.py"], cwd=KOK, capture_output=True, text=True, encoding="utf-8", errors="replace")
out = r.stdout + r.stderr
for line in out.splitlines():
    ls = line.strip()
    if ls.endswith("):") or "ALLOWLIST DISI" in ls or "ihlal yok" in ls:
        print("  ", ls[:90])
print("\n=== BITTI ===")
