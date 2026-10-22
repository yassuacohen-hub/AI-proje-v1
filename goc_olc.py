import subprocess
import sys
from pathlib import Path

ic = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
r = subprocess.run([sys.executable, "scripts/goc_defteri.py", "--esitle"],
                   cwd=str(ic), capture_output=True, text=True,
                   encoding="utf-8", timeout=120)
print(r.stdout[-3000:])
print(r.stderr[-800:] if r.stderr else "")
print("KOD:", r.returncode)
