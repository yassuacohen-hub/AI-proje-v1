# -*- coding: utf-8 -*-
import ast, collections, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
KOK = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")

gk = (KOK / "scripts" / "gorev_kutusu.py").read_text(encoding="utf-8").splitlines()
print("=== gorev_kutusu.py ilgili satirlar ===")
for i, s in enumerate(gk, 1):
    if any(k in s for k in ("def cmd_teslim", "def cmd_onayla", "def cmd_reddet",
                            "def _kapilar", "acik_soru", "_mesaj_kontrol",
                            "teslim_kontrol", "bulgu", "onay_kapisi", "return 1", "REDDED")):
        print(f"  {i}: {s.rstrip()[:110]}")

print("\n=== v1_network.py AST ===")
p = KOK / "src/company_master/api/routers/v1/v1_network.py"
if p.exists():
    t = ast.parse(p.read_text(encoding="utf-8"))
    fns = [n.name for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    cift = {k: v for k, v in collections.Counter(fns).items() if v > 1}
    print("  toplam fn:", len(fns), "| CIFT:", cift if cift else "YOK")
else:
    print("  v1_network.py YOK")
