# -*- coding: utf-8 -*-
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"
r = subprocess.run(
    [sys.executable, "scripts/gorev_kutusu.py", "teslim",
     "--task-id", "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
     "--ajan", "yasu",
     "--ozet", "Faz A sozlesme (docs/RAPIDAPI_OSINT_SOZLESME.md) + Faz B istemci (src/company_master/engine/rapidapi_osint.py: env, timeout, GUNLUK_TAVAN=50 'varsayim, dogrulanmadi' isaretli + env override, hata siniflari) + Faz C 9/9 mock test (tests/test_rapidapi_osint.py). Hub B-14 hafiza izi + bulgu defteri kaydi + rapor tamam. 2 acik chat kaydi (kademe-1 yasagi, GUNLUK_TAVAN varsayimi) gerekceli kapatildi.",
     "--cikti", "docs/RAPIDAPI_OSINT_SOZLESME.md,src/company_master/engine/rapidapi_osint.py,tests/test_rapidapi_osint.py,data/orchestrator/VERI-RAPIDAPI-OSINT-ISTEMCI-01_rapor_2026-10-12_yasu.md"],
    cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("STDOUT:")
print(r.stdout)
print("STDERR:")
print(r.stderr)
print("RC:", r.returncode)
