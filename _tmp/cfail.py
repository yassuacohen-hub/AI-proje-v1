"""Kirilan 2 testi teshis et."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
                    "-p", "no:cacheprovider", "--tb=short"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=900)
out = r.stdout or ""
sat = out.splitlines()
print(f"rc={r.returncode}")
for n, l in enumerate(sat):
    if "FAILED" in l or "assert" in l or "Error" in l or l.startswith("E "):
        print(f"  {l[:150]}")
print("\n--- son 25 satir ---")
for l in sat[-25:]:
    print("  " + l[:140])