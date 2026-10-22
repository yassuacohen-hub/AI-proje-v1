# -*- coding: utf-8 -*-
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"
TASK = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
OZET = ("Faz A (docs/RAPIDAPI_OSINT_SOZLESME.md) + Faz B (engine/rapidapi_osint.py: "
        "env host/token, timeout, günlük tavan=50 varsayım olarak işaretli, hata sınıfları) + "
        "Faz C (test_rapidapi_osint.py mock: 9/9 PASSED). "
        "Teslim öncesi 3 sistem kapısı geçildi: chat engel=False, mesaj=[], bulgu_defteri kayıtlı.")
CIKTI = ("docs/RAPIDAPI_OSINT_SOZLESME.md,src/company_master/engine/rapidapi_osint.py,"
         "tests/test_rapidapi_osint.py")
cmd = [sys.executable, BASE + r"\scripts\gorev_kutusu.py", "teslim",
       "--task-id", TASK, "--ajan", "yasu", "--ozet", OZET, "--cikti", CIKTI]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=BASE)
print("RETURN CODE:", r.returncode)
print("--- STDOUT ---")
print(r.stdout)
print("--- STDERR ---")
print(r.stderr)
