# -*- coding: utf-8 -*-
import os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = Path(r"c:\HUGINN~1\HUGINN~1")

def var(rel):
    return (B / rel).exists()

print("=== KILITLI DOSYA VARLIK TARAMASI ===\n")

gorevler = {
    "VERI-RAPIDAPI-OSINT-ISTEMCI-01": [
        "src/company_master/engine/rapidapi_osint.py",
        "tests/test_rapidapi_osint.py",
        "docs/RAPIDAPI_OSINT_SOZLESME.md",
    ],
    "VERI-MUSTERI-ODEME-AYAR-01": [
        "src/company_master/schema/migrations/0062_odeme_musteri_ayar.sql",
        "src/company_master/schema/migrations/down/0062_odeme_musteri_ayar_down.sql",
        "web_dashboard/tabs/musteri_odeme.py",
        "web_dashboard/tabs/musteri_kredi.py",
        "tests/test_musteri_odeme.py",
    ],
    "API-V1-NETWORK-REPORT-01": [
        "src/company_master/api/routers/v1/v1_network.py",
        "tests/test_api_v1_network.py",
    ],
    "UI-SSR-NEXT-KUNYE-01": [
        "frontend/package.json",
        "frontend/next.config.mjs",
        "frontend/app/layout.tsx",
        "frontend/app/firma/[vkn]/page.tsx",
        "frontend/app/firma/firma.test.tsx",
    ],
    "ALTYAPI-REPO-TEMIZLIK-01": [
        "_ARSIV",
        "_tmp",
    ],
    "ORCH-KODLAMA-TEMIZLIK-01": [
        "scripts/kodlama_denetim.py",
    ],
}
for gid, dosyalar in gorevler.items():
    print(f"[{gid}]")
    for f in dosyalar:
        print(f"   {'VAR ' if var(f) else 'YOK '} {f}")
    print()

print("=== frontend/ dizin yapisi ===")
fe = B / "frontend"
if fe.exists():
    for p in sorted(fe.rglob("*")):
        if p.is_file() and "node_modules" not in str(p):
            print("  ", p.relative_to(B))
else:
    print("   frontend/ YOK")
