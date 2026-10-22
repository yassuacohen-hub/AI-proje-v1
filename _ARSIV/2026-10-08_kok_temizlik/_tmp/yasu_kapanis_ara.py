# -*- coding: utf-8 -*-
import pathlib
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PLANS = pathlib.Path(r"c:\HUGINN~1\HUGINN~1\plans")

AKTIF = [
    "brief_yasu_API-V1-NETWORK-REPORT-01.md",
    "brief_yasu_UI-SSR-NEXT-KUNYE-01.md",
    "brief_yasu_ALTYAPI-REPO-TEMIZLIK-01.md",
    "brief_yasu_ORCH-KODLAMA-TEMIZLIK-01.md",
    "brief_yasu_VERI-RAPIDAPI-OSINT-ISTEMCI-01.md",
]
KEYS = ["kabul", "kapan", "teslim", "kriter", "kapi", "kapı", "done",
        "definition", "bitis", "bitiş", "dogrula", "doğrula",
        "cikti", "çıktı", "kanit", "kanıt", "asama", "aşama"]

for ad in AKTIF:
    p = PLANS / ad
    print("=" * 70)
    print(ad)
    if not p.exists():
        print("  (YOK)")
        continue
    satirlar = p.read_text(encoding="utf-8", errors="replace").splitlines()
    eslesen = 0
    for i, s in enumerate(satirlar, 1):
        low = s.lower()
        if any(k in low for k in KEYS):
            print(f"  {i}: {s.strip()[:115]}")
            eslesen += 1
    if eslesen == 0:
        print("  >>> KAPANIS/TESLIM/KRITER ifadesi BULUNAMADI (bos)")
