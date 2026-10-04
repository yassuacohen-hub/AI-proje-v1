"""Pre-commit kanca teşhisi: neden takiliyor?"""
import os
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HOOK = Path(".git") / "hooks" / "pre-commit"


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=== 1) KANCA VAR MI? ===")
print(f"  yol            : {(KOK / HOOK)}")
print(f"  is_file        : {(KOK / HOOK).is_file()}")
print(f"  executable     : {os.access(KOK / HOOK, os.X_OK) if (KOK / HOOK).is_file() else '-'}")
if (KOK / HOOK).is_file():
    t = (KOK / HOOK).read_text(encoding="utf-8", errors="replace")
    print(f"  boyut          : {len(t)} karakter")
    print("\n  --- ICERIK ---")
    for n, l in enumerate(t.splitlines(), 1):
        print(f"   {n:3d}: {l[:105]}")

print()
print("=== 2) core.hooksPath ayarli mi? ===")
rc, c = git("config", "--get", "core.hooksPath")
print(f"  core.hooksPath = {c or '(ayarli degil -> .git/hooks)'}")
rc, c = git("config", "--list", "--local")
print(f"  yerel ayar sayisi = {len(c.splitlines())}")

print()
print("=== 3) KANCANIN CALISTIRDIGI SCRIPTLER ===")
if (KOK / HOOK).is_file():
    t = (KOK / HOOK).read_text(encoding="utf-8", errors="replace")
    import re
    for m in sorted(set(re.findall(r"[\w./-]+\.(?:py|sh|ps1)", t))):
        p = KOK / m if (KOK / m).is_file() else None
        print(f"  {m:50s} {'VAR' if p else 'YOK!!'}")
    for m in sorted(set(re.findall(r"python[^\n|]{0,80}", t)))[:12]:
        print(f"  cmd: {m.strip()[:100]}")

print()
print("=== 4) ZAMAN OLÇUMU — kancanin parcasi nedir? ===")
for adim, args, sn in [
    ("pytest tests/ (tam)", [sys.executable, "-m", "pytest", "tests/", "-q",
                             "--no-header", "-p", "no:cacheprovider"], 900),
]:
    t0 = time.time()
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(KOK), timeout=sn)
    dt = time.time() - t0
    out = (r.stdout or "").strip().splitlines()
    print(f"  {adim}: {dt:.1f}s rc={r.returncode}")
    for l in out[-3:]:
        print("      " + l[:90])