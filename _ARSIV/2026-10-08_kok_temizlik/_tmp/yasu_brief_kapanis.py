# -*- coding: utf-8 -*-
"""Yasu brief'lerinde kapanis kapisi — kompakt ozet tablosu."""
import pathlib
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1\plans")

def var_mi(L, kelimeler):
    low_all = "\n".join(L).lower()
    return any(k in low_all for k in kelimeler)

# Aktif teslim edilmemis gorevler (oncelikli)
AKTIF = [
    "API-V1-NETWORK-REPORT-01",
    "UI-SSR-NEXT-KUNYE-01",
    "ALTYAPI-REPO-TEMIZLIK-01",
    "ORCH-KODLAMA-TEMIZLIK-01",
    "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
    "VERI-MUSTERI-ODEME-AYAR-01",
]

briefs = sorted(BASE.glob("brief_yasu_*.md"))
rows = []
for b in briefs:
    gorev = b.stem.replace("brief_yasu_", "")
    L = b.read_bytes().decode("utf-8", errors="replace").splitlines()
    kabul = var_mi(L, ["kabul kriteri", "kabul kriterleri", "kabul kriter"])
    dod = var_mi(L, ["definition of done", "kapanis kapisi", "kapanış kapısı"])
    b14 = var_mi(L, ["b-14"])
    hub = var_mi(L, ["**hub:**"])
    teslim = var_mi(L, ["## teslim", "teslim komutu"])
    test = var_mi(L, ["test koşulu", "test kosulu", "test plan", "pytest", "vitest"])
    rows.append((gorev, kabul, dod, b14, hub, teslim, test))

print("| Gorev | KabulKrit | DoD/Kapanis | B-14 | Hub | Teslim | TestKosul |")
print("|---|:---:|:---:|:---:|:---:|:---:|:---:|")
for gorev, kabul, dod, b14, hub, teslim, test in rows:
    y = lambda x: "EVET" if x else "hayir"
    isaret = " **<<<" if gorev in AKTIF else ""
    print(f"| {gorev}{isaret} | {y(kabul)} | {y(dod)} | {y(b14)} | {y(hub)} | {y(teslim)} | {y(test)} |")

# Kritik tespit: aktif gorevlerde kapani kapisi eksik olanlar
print("\n=== AKTIF GOREV OZETI ===")
for gorev, kabul, dod, b14, hub, teslim, test in rows:
    if gorev in AKTIF:
        eksik = []
        if not (kabul or dod): eksik.append("Kabul/DoD")
        if not b14: eksik.append("B-14")
        if not (kabul or dod or b14): eksik.append("KAPANI-KAPISI-YOK")
        print(f"  {gorev}: kabul={kabul}, kapanis/dod={dod}, b14={b14} -> {'TAMAM' if not (kabul or dod or b14) or (kabul and b14) else 'EKSIK:'+','.join(eksik)}")

