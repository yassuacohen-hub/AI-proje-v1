"""Kaybolan TSG kodunu ve canli DB durumunu olcer (PowerShell tirnak tuzaklarindan kacinmak icin)."""

import glob
import os
import sqlite3
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=== 1) stash@{0} icinde benim kodum ===")
r = subprocess.run(["git", "stash", "show", "-p", "stash@{0}"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
bulunan = [ln for ln in r.stdout.splitlines()
           if any(k in ln for k in ("olay_esle", "ILAN_TURU_ESLEME", "ilan_turu_normalize_et"))]
if bulunan:
    for ln in bulunan[:8]:
        print("   " + ln.strip()[:110])
else:
    print("   YOK (onceki eslesme dosya-adindan geldi)")

print("\n=== 2) stash@{0} dosya listesi ===")
r = subprocess.run(["git", "stash", "show", "--name-only", "stash@{0}"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
dosyalar = [d for d in r.stdout.splitlines() if d.strip()]
print(f"   toplam {len(dosyalar)} dosya; ilk 12:")
for d in dosyalar[:12]:
    print("     " + d)

print("\n=== 3) tum stash'lerde kanit_sicili dosyasi ===")
for i in range(8):
    r = subprocess.run(["git", "stash", "show", "-p", f"stash@{{{i}}}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if "olay_esle" in r.stdout or "ILAN_TURU_ESLEME" in r.stdout:
        print(f"   stash@{{{i}}}: *** KOD ICERIYOR ***")

print("\n=== 4) canli DB ===")
adaylar = []
for kalip in ("data/*.db", "data/**/*.db", "*.db", "**/huginn.db"):
    adaylar.extend(glob.glob(kalip, recursive=True))
gorulen = set()
for d in adaylar:
    if d in gorulen:
        continue
    gorulen.add(d)
    try:
        if os.path.getsize(d) < 50_000:
            continue
        c = sqlite3.connect(d)
        var = c.execute(
            "select name from sqlite_master where type='table' and name='company_events'"
        ).fetchone()
        if not var:
            continue
        toplam = c.execute("select count(*) from company_events").fetchone()[0]
        tsg = c.execute(
            "select count(*) from company_events where event_source='TSG'"
        ).fetchone()[0]
        print(f"   {d}: company_events={toplam}, TSG={tsg}")
        c.close()
    except Exception as e:
        print(f"   {d}: {type(e).__name__}")
