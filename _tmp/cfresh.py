"""GERCEK kirilanlar - sifirdan, temiz."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
                    "-p", "no:cacheprovider", "--tb=line", "-rf"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=1200)
out = r.stdout or ""
print(f"rc={r.returncode}\n")
print("--- OZET ---")
for l in out.strip().splitlines()[-6:]:
    print("  " + l[:110])
print("\n--- FAILED SATIRLARI ---")
for l in out.splitlines():
    if l.startswith("FAILED") or l.startswith("ERROR"):
        print("  " + l.strip()[:130])
print("\n--- HATA SATIRLARI (tb=line) ---")
for l in out.splitlines():
    if "/Huginn" in l and (".py:" in l) and ("Error" in l or "assert" in l or "E  " in l):
        print("  " + l.strip()[:150])