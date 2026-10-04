"""NEDEN binlerce test? collection kok nedeni."""
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def p(*a):
    print(" ".join(str(x) for x in a), flush=True)


t0 = time.time()
r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q",
                    "--no-header", "-p", "no:cacheprovider"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=900)
out = r.stdout or ""
sat = [l for l in out.splitlines() if "::" in l]
p(f"collection suresi={time.time()-t0:.0f}s rc={r.returncode}")
p(f"toplanan test : {len(sat)}")

dosya = Counter(l.split("::")[0] for l in sat)
p(f"\n-- DOSYA BAZINDA (ilk 15) --")
for f, n in dosya.most_common(15):
    p(f"  {n:6d}  {f}")

p("\n-- EN COK TESTE SAHIP SINIF --")
sinif = Counter(l.split("::")[1] if l.count("::") > 1 else "?" for l in sat)
for c, n in sinif.most_common(10):
    p(f"  {n:6d}  {c}")

p("\n-- pytest.ini / pyproject ayarlari --")
for f in ("pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini", "conftest.py"):
    q = KOK / f
    if q.is_file():
        p(f"  --- {f} ---")
        t = q.read_text(encoding="utf-8", errors="replace")
        for l in t.splitlines()[:40]:
            if l.strip() and not l.strip().startswith("#"):
                p("    " + l[:95])