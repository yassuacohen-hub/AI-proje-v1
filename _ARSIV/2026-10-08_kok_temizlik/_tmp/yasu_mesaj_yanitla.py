# -*- coding: utf-8 -*-
"""RAPIDAPI teslim kapanis: ihsan'in 3 cevapsiz mesajini yanitla."""
import subprocess, sys

KOK = r"c:\HUGINN~1\HUGINN~1"
PY = "python"
SCRIPT = r"scripts\chat_gonder.py"

# (cevap_index, mesaj metni)
YANITLAR = [
    (151,
     "RAPIDAPI kapanis: VERI-RAPIDAPI-OSINT-ISTEMCI-01 alindi, Faz A/B/C tamamlandi. "
     "ALTYAPI-ADMIN-SQL-PARAM-01 utku'ya devredildi (bende degil). "
     "Faz A canli istek olcumunu PO anahtar donusunde yapacagim (kademe notu)."),
    (154,
     "Tetik alindi: VERI-RAPIDAPI-OSINT-ISTEMCI-01 baslatildi. "
     "Faz A sozlesme (docs/RAPIDAPI_OSINT_SOZLESME.md), Faz B istemci (rapidapi_osint.py), "
     "Faz C mock testler yazildi. DB yazimi yok (ayri gorev). 9/9 test yesil."),
    (166,
     "Plan Faz A/B/C tesekkur. Kademe-1 kisiti icin PO'ya kural sorusu (D-359 adayi) "
     "sen iletilir; bu tur PO dogrudan kod yazma yetkisi verdi, istemci + 9/9 mock test "
     "tamamlandi. Teslim icin bulgu defteri + hub hafiza izi yazildi."),
]

import os
env = dict(os.environ, PYTHONIOENCODING="utf-8", HUGINN_AJAN="yasu")

for idx, mesaj in YANITLAR:
    cmd = [PY, SCRIPT, "--to", "ihsan", "--type", "koordinasyon",
           "--task-id", "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
           "--mesaj", mesaj, "--cevap", str(idx)]
    print(f"=== cevap[{idx}] gonderiliyor ===")
    r = subprocess.run(cmd, cwd=KOK, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip())
    if r.returncode != 0:
        print("STDERR:", r.stderr.strip())
print("=== BITTI ===")
