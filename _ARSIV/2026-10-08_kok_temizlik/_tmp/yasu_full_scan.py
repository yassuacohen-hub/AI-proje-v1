# -*- coding: utf-8 -*-
"""Yasu gorev durum taramasi - tum kanitlari tek yerde topla."""
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = Path(r"c:\HUGINN~1\HUGINN~1")
os.chdir(BASE)


def bash(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        return (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return f"[ERR] {e}"


# 1) NETWORK: cift tanim + dosya varligi + test var mi
print("=== 1. API-V1-NETWORK-REPORT-01 ===")
p = BASE / "src/company_master/api/routers/v1/v1_network.py"
print(f"  v1_network.py var: {p.exists()}")
if p.exists():
    L = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, satir in enumerate(L, 1):
        if "def _fetch_company_by_vkn" in satir or "def _get_company_vkn" in satir:
            print(f"  {i}: {satir.strip()}")
for t in ["tests/test_api_v1_network.py", "tests/test_v1_network.py"]:
    print(f"  test {t}: {(BASE / t).exists()}")

# 2) SSR frontend testi
print("\n=== 2. UI-SSR-NEXT-KUNYE-01 ===")
fdir = BASE / "frontend"
for t in ["app/firma/[vkn]/page.tsx", "app/firma/firma.test.tsx", "package.json"]:
    print(f"  {t}: {(fdir / t).exists()}")

# 3) RAPIDAPI testi tekrar dogrula
print("\n=== 3. VERI-RAPIDAPI-OSINT-ISTEMCI-01 ===")
print(bash("python -m pytest tests/test_rapidapi_osint.py -q 2>&1 | tail -5"))

# 4) MUSTERI-ODEME (review) - rapor var mi
print("\n=== 4. VERI-MUSTERI-ODEME-AYAR-01 (review) ===")
print(f"  rapor: {(BASE / 'data/orchestrator/VERI-MUSTERI-ODEME-AYAR-01_rapor_2026-10-12_yasu.md').exists()}")

# 5) ALTYAPI-REPO-TEMIZLIK - _ARSIV var mi, git status temiz mi
print("\n=== 5. ALTYAPI-REPO-TEMIZLIK-01 ===")
for d in ["_ARSIV", "_tmp", ".gitignore"]:
    print(f"  {d}: {(BASE / d).exists()}")

# 6) ORCH-KODLAMA-TEMIZLIK - kodlama_denetim kapsamda kalan
print("\n=== 6. ORCH-KODLAMA-TEMIZLIK-01 ===")
print(bash("python scripts/kodlama_denetim.py --kapsam kod 2>&1 | tail -20"))
