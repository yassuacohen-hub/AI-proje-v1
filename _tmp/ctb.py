"""2 kirilmanin TAM nedeni (traceback)."""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

r = subprocess.run(
    [sys.executable, "-m", "pytest",
     "tests/test_yazma_kapisi.py::test_yazma_kapisi_sabotaj_mandal_kirmaz",
     "tests/test_kazima_qwen_classify.py", "-q", "--no-header",
     "-p", "no:cacheprovider", "--tb=short", "-rf"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=900)
print(f"rc={r.returncode}")
print((r.stdout or "")[-4000:])