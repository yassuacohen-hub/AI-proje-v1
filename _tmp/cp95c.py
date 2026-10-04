"""MADDE 5 DOGRU OLCUM: isinma + 3 tur, p95."""
import importlib.util
import statistics
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
M = KOK / "scripts" / "kazima_qwen_classify.py"
spec = importlib.util.spec_from_file_location("kqy3", M)
kq = importlib.util.module_from_spec(spec); spec.loader.exec_module(kq)
URL = "https://www.ostim.org.tr/kurumsal/hakkimizda"

print("=== ISINMA (keyring onbellegi doldurulur, olcume girmez) ===")
t0 = time.perf_counter()
kq.sinifla_etiket(URL)
print(f"  ilk cagri (soguk): {(time.perf_counter()-t0)*1000:.0f} ms  "
      "<- tek seferlik keyring maliyeti")

print("\n=== MADDE 5: p95 (soguk cagri haric) ===")
N = 15
hepsi = []
for label, kw in [("V1 varsayilan", {}), ("V3 kapisi", {"kaynak": "V3"}),
                  ("kaynak='' (yok)", {"kaynak": ""})]:
    ts = []
    for _ in range(N):
        t0 = time.perf_counter()
        kq.sinifla_etiket(URL, **kw)
        ts.append((time.perf_counter() - t0) * 1000)
    ts.sort()
    p95 = ts[max(0, int(len(ts) * 0.95) - 1)]
    hepsi += ts
    print(f"  {label:20s} min={ts[0]:6.1f} med={statistics.median(ts):6.1f} "
          f"p95={p95:6.1f} max={ts[-1]:6.1f} ms  {'GECTI' if p95 < 2000 else 'KALDI'}")
hepsi.sort()
genel = hepsi[max(0, int(len(hepsi) * 0.95) - 1)]
print(f"\n  TUMU BIRLESIK: n={len(hepsi)} p95={genel:.1f} ms")
print(f"  MADDE 5 (p95<2000ms): {'GECTI' if genel < 2000 else 'KALDI'}")

print("\n=== REGRESYON: ilgili testler ===")
r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
                    "-k", "qwen or kazima or classify", "-p", "no:cacheprovider"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=str(KOK), timeout=900)
print(f"  rc={r.returncode}")
for l in (r.stdout or "").strip().splitlines()[-3:]:
    print("  " + l[:90])