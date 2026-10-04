"""sinifla_etiket'in gercek imzasi ve cagiranlari — dogru olcum icin."""
import importlib.util
import inspect
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
M = KOK / "scripts" / "kazima_qwen_classify.py"
spec = importlib.util.spec_from_file_location("kqy", M)
kq = importlib.util.module_from_spec(spec); spec.loader.exec_module(kq)

print("=== 1) sinifla_etiket IMZASI ===")
f = getattr(kq, "sinifla_etiket")
print(f"  {inspect.signature(f)}")
print("\n  --- docstring ---")
print("  " + (inspect.getdoc(f) or "(yok)").replace("\n", "\n  "))

print("\n=== 2) parametrelerin gercek kullanimi (govde) ===")
sat = M.read_text(encoding="utf-8", errors="replace").splitlines()
b = next(i for i, l in enumerate(sat) if "def sinifla_etiket" in l)
for n in range(b, min(b + 45, len(sat))):
    print(f"  {n+1}: {sat[n][:100]}")

print("\n=== 3) VARSAYILAN DEGERLER / ENV ===")
for ad in ("EVREN_BASE", "NINEROUTER_BASE", "JINA_BASE", "EVREN_MODEL"):
    v = getattr(kq, ad, None)
    print(f"  {ad:18s} = {v!r}")

print("\n=== 4) TEST DOSYASI nasil cagiruyor? ===")
T = KOK / "tests" / "test_kazima_qwen_classify.py"
if T.is_file():
    ts = T.read_text(encoding="utf-8", errors="replace").splitlines()
    for n, l in enumerate(ts, 1):
        if "sinifla_etiket(" in l:
            print(f"  {n}: {l.strip()[:100]}")
else:
    print("  test dosyasi yok")
    for x in sorted((KOK / "tests").glob("*qwen*")):
        print(f"    {x.name}")