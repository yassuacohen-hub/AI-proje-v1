# -*- coding: utf-8 -*-
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OZET = ("Faz A sozlesme + Faz B istemci (env KEY/HOST, timeout 60s, gunluk tavan 50, "
        "RapidApiHata/KotaAsildi, verimlilik logu) + Faz C 9/9 mock test yesil. "
        "DB yazimi yok (ayri gorev, brif kapsami disi).")
KARAR = "kapandi: pytest 9/9 + py_compile OK + kodlama_denetim kapsamda 0 ihlal"

def calistir(args, etiket):
    print(f"\n===== {etiket} =====")
    r = subprocess.run([sys.executable] + args, cwd=r"c:\HUGINN~1\HUGINN~1")
    print(f"[cikis kodu={r.returncode}]")
    return r.returncode

# 1) Bulgu defterine ekle (D-318 kapisi)
calistir(["scripts/bulgu_defteri.py", "ekle",
          "--task-id", "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
          "--rol", "yasu",
          "--ozet", OZET,
          "--karar", KARAR,
          "--renk", "tamam"], "BULGU DEFTERI EKLE")

# 2) Teslim et (review)
TESLIM_OZET = ("Faz A (docs/RAPIDAPI_OSINT_SOZLESME.md), Faz B (rapidapi_osint.py istemci: "
               "env KEY/HOST, timeout 60s, gunluk tavan 50, RapidApiHata/KotaAsildi, verimlilik "
               "logu, ham veri yazimi), Faz C (9/9 mock test yesil). DB yazimi yok (ayri gorev). "
               "py_compile OK, kodlama_denetim kapsamda 0 ihlal. "
               "Rapor: data/orchestrator/VERI-RAPIDAPI-OSINT-ISTEMCI-01_rapor_2026-10-12_yasu.md")
CIKTI = ("src/company_master/engine/rapidapi_osint.py,tests/test_rapidapi_osint.py,"
         "docs/RAPIDAPI_OSINT_SOZLESME.md,"
         "data/orchestrator/VERI-RAPIDAPI-OSINT-ISTEMCI-01_rapor_2026-10-12_yasu.md")
calistir(["scripts/gorev_kutusu.py", "teslim",
          "--ajan", "yasu",
          "--task-id", "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
          "--ozet", TESLIM_OZET,
          "--cikti", CIKTI], "TESLIM ET")
