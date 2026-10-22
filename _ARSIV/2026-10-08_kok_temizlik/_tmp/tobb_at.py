# -*- coding: utf-8 -*-
"""VERI-TOBB-HAVUZ-SEMA-01 atamasi: cmd.exe Unicode bozulmasini atlatir (D-86)."""
import base64
import os
import subprocess
import sys

BASLIK = "[VERI] TOBB havuz şemasını yaz → 0055-0058 + alan_sozlugu seed (4s)"
DOSYALAR = ",".join([
    "src/company_master/schema/migrations/0055_tobb_havuz_sema.sql",
    "src/company_master/schema/migrations/0056_company_persons.sql",
    "src/company_master/schema/migrations/0057_companies_tobb_kolonlari.sql",
    "src/company_master/schema/migrations/0058_adres_hukuk_gazete.sql",
    "scripts/tobb_alan_sozlugu_uret.py",
    "src/company_master/etl/tobb_alan_haritasi.py",
    "tests/test_tobb_alan_haritasi.py",
])
b64 = base64.b64encode(BASLIK.encode("utf-8")).decode("ascii")
env = dict(os.environ, HUGINN_AJAN="ihsan", PYTHONIOENCODING="utf-8")
cmd = [sys.executable, "scripts/gorev_at.py", "at",
       "--task-id", "VERI-TOBB-HAVUZ-SEMA-01", "--baslik-b64", b64,
       "--ajan", "ihsan", "--oncelik", "P0", "--dosya", DOSYALAR,
       "--talimat", "Brif: plans/brief_ihsan_VERI-TOBB-HAVUZ-SEMA-01.md; Faz A canli olcum once (D-238)",
       "--cagiran", "ihsan"]
r = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout); print(r.stderr); print("rc=", r.returncode)
