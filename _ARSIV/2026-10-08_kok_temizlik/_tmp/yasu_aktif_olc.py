# -*- coding: utf-8 -*-
"""4 aktif gorevin fiilen teslime hazirlik durumunu olc."""
import os, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KOK = Path(r"c:\HUGINN~1\HUGINN~1")
os.chdir(KOK)
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")

def sh(cmd):
    r = subprocess.run(cmd, shell=True, cwd=KOK, env=ENV,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (r.stdout or "") + (r.stderr or "")

# ---- API-V1-NETWORK-REPORT-01 ----
print("========== API-V1-NETWORK-REPORT-01 ==========")
print("v1_network.py py_compile:", "OK" if sh('python -m py_compile src/company_master/api/routers/v1_network.py 2>&1').strip()=="" else "FAIL")
out = sh('findstr /n /c:"def _fetch_company_by_vkn" /c:"def _get_company_vkn" src\\company_master\\api\\routers\\v1_network.py')
print("cift tanim kontrol:\n", out.strip() or "(bulunamadi)")
print("test dosyasi:", "VAR" if (KOK/"tests/test_api_v1_network.py").exists() else "YOK")
# deps durumu
print("--- test_paket_scope (dep utku) ---")
print(sh('python -m pytest tests/test_paket_scope.py -q 2>&1').strip().splitlines()[-1] if sh('python -m pytest tests/test_paket_scope.py -q 2>&1').strip() else "(yok)")

# ---- UI-SSR-NEXT-KUNYE-01 ----
print("\n========== UI-SSR-NEXT-KUNYE-01 ==========")
for f in ["frontend/package.json","frontend/next.config.mjs","frontend/app/layout.tsx",
          "frontend/app/firma/[vkn]/page.tsx","frontend/app/firma/firma.test.tsx"]:
    p = KOK/f
    print(f"  {f}:", "VAR" if p.exists() else "YOK")
print("--- frontend vitest ---")
print(sh('cd frontend && npx vitest run app/firma 2>&1').strip()[-400:])

# ---- ORCH-KODLAMA-TEMIZLIK-01 ----
print("\n========== ORCH-KODLAMA-TEMIZLIK-01 ==========")
print("--- kodlama_denetim.py (tam repo, sadece sayilar) ---")
full = sh('python scripts/kodlama_denetim.py --tam-repo 2>&1')
for line in full.splitlines():
    if any(k in line for k in ("utf8_bom","mojibake","crlf_karisik","sondaki_bosluk","dosya_sonu","tab_girinti","utf16","nul","sozdizimi","ALLOWLIST")):
        print("  ", line.strip()[:90])

# ---- ALTYAPI-REPO-TEMIZLIK-01 ----
print("\n========== ALTYAPI-REPO-TEMIZLIK-01 ==========")
st = sh('git status --short 2>&1')
untracked = [l for l in st.splitlines() if l.startswith("??")]
print(f"  takipsiz (??) dosya sayisi: {len(untracked)}")
print(f"  _ARSIV var mi:", "VAR" if (KOK/"_ARSIV").exists() else "YOK")
print(f"  _ARSIV_tek_kullanimlik var mi:", "VAR" if (KOK/"_ARSIV_tek_kullanimlik").exists() else "YOK")
print("\n=== BITTI ===")
