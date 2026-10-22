# -*- coding: utf-8 -*-
import ast
import sys
import pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")
DOSYA = BASE / "src/company_master/api/routers/v1/v1_network.py"
src = DOSYA.read_text(encoding="utf-8")
L = src.splitlines()
agac = ast.parse(src)

# 1) Fonksiyon govdelerini metin olarak cikar (birebir karsilastirma)
def fn_kaynak(lb, eb):
    return "\n".join(L[lb - 1:eb])

funcs = [n for n in agac.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
by_name = {}
for f in funcs:
    by_name.setdefault(f.name, []).append((f.lineno, f.end_lineno))

print("=== CIFT TANIM KARSILASTIRMA ===")
for ad in ("_fetch_company_by_vkn", "_get_company_vkn"):
    tanimlar = by_name.get(ad, [])
    if len(tanimlar) == 2:
        (l1, e1), (l2, e2) = tanimlar
        k1 = fn_kaynak(l1, e1)
        k2 = fn_kaynak(l2, e2)
        ayni = (k1 == k2)
        print(f"\n{ad}: 1.tanim [{l1}-{e1}] vs 2.tanim [{l2}-{e2}] -> BITEBIT AYNI: {ayni}")
        if not ayni:
            print("  --- 1.tanim ---")
            print(k1)
            print("  --- 2.tanim ---")
            print(k2)

# 2) get_full_report icindeki gercek return'u bul (return sonrasi oluden once)
print("\n=== get_full_report return noktalari ===")
for f in funcs:
    if f.name == "get_full_report":
        for i, node in enumerate(ast.walk(f)):
            if isinstance(node, ast.Return):
                print(f"  return @ satir {node.lineno} (ust-duzey statement mi: {any(node is s for s in f.body)})")
        # govdenin ust-duzey statementlarini listele
        print(f"  --- get_full_report ust-duzey govde ({f.lineno}-{f.end_lineno}) ---")
        for s in f.body:
            print(f"    {type(s).__name__} @ {s.lineno}-{s.end_lineno}")
