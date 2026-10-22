# -*- coding: utf-8 -*-
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Bulgu ekle
cmd = [
    "python", "scripts/bulgu_defteri.py", "ekle",
    "--task-id", "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
    "--rol", "yasu",
    "--ozet", "Faz A/B/C tamam: rapidapi_osint.py (env KEY/HOST, timeout, GUNLUK_TAVAN=50 varsayim olarak isaretli, hata siniflari) + docs/RAPIDAPI_OSINT_SOZLESME.md + 9/9 test PASSED",
    "--karar", "D-306 devami: env'den anahtar okuma + timeout + gunluk tavan + hata siniflari, DB yazimi YOK",
    "--renk", "tamam"
]
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("BULGU EKLEME SONUC:")
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
