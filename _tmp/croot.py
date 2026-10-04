"""Iki kirilmanin KOK NEDENI: sablonun canli testi."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
O = KOK / "data" / "orchestrator"


def sh(*a, timeout=600):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "").strip())


print("=" * 68)
print("1) test'in ne yaptigi")
print("=" * 68)
T = KOK / "tests" / "test_kazima_qwen_classify.py"
ts = T.read_text(encoding="utf-8", errors="replace").splitlines()
for n, l in enumerate(ts, 1):
    if "canli" in l.lower() or "def test" in l or "slow" in l or "skipif" in l \
            or "environ" in l:
        print(f"  {n:3d}: {l.strip()[:100]}")

print()
print("=" * 68)
print("2) CANLI: sablonun kendisi saglam mi? (1 kez, ~15sn)")
print("=" * 68)
t0 = time.time()
rc, c = sh("scripts/kazima_qwen_classify.py",
           "--url", "https://www.ostim.org.tr/kurumsal/hakkimizda")
dt = time.time() - t0
print(f"  rc={rc}  sure={dt:.1f}s")
print("  " + c.strip()[:700].replace("\n", "\n  "))

print()
print("=" * 68)
print("3) Neden test kiriliyor? — testin cagirdigi yol")
print("=" * 68)
spec = importlib.util.spec_from_file_location(
    "kqx", KOK / "scripts" / "kazima_qwen_classify.py")
kq = importlib.util.module_from_spec(spec); spec.loader.exec_module(kq)
import inspect
print(f"  sinifla_etiket: {inspect.signature(kq.sinifla_etiket)}")
print(f"  jina_uygula   : {inspect.signature(kq.jina_uygula)}")
print(f"  env'ler: {[(k, osv) for k, osv in kq.NO_SECRETS.items() if k.startswith(('EVREN','9ROUTER','SINIF'))]}"
      if hasattr(kq, "NO_SECRETS") else "")

print()
print("=" * 68)
print("4) MANDAL: test neden 'copied' gormedi?")
print("=" * 68)
spec2 = importlib.util.spec_from_file_location(
    "yz", KOK / "tests" / "test_yazma_kapisi.py")
yz = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(yz)
print(f"  TAVAN_KOPYA={yz.TAVAN_KOPYA} KOPYA_ESIK={yz.KOPYA_ESIK}")
print(f"  _kopyalayanlar(): {yz._kopyalayanlar()}")
T2 = KOK / "tests" / "test_yazma_kapisi.py"
ts2 = T2.read_text(encoding="utf-8", errors="replace").splitlines()
for n, l in enumerate(ts2, 1):
    if "sabotaj" in l:
        for m in range(n - 1, min(n + 34, len(ts2))):
            print(f"  {m+1}: {ts2[m][:100]}")
        break