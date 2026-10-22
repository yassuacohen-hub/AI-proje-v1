# -*- coding: utf-8 -*-
import ast, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1\src\company_master\api\routers\v1\v1_network.py"
src = open(BASE, encoding="utf-8-sig").read()
tree = ast.parse(src)
lines = src.count("\n") + 1
print(f"TOPLAM SATIR: {lines}")

# fonksiyon tanimlarini topla (cift tanim tespiti)
funcs = {}
routes = []
models = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        funcs.setdefault(node.name, []).append(node.lineno)
    if isinstance(node, ast.ClassDef):
        # pydantic model mi?
        bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
        if any("Model" in b or "Base" in b for b in bases):
            models.append((node.name, node.lineno, bases))

print("\n=== CIFT TANIMLI FONKSIYONLAR ===")
cift = {k: v for k, v in funcs.items() if len(v) > 1}
for k, v in cift.items():
    print(f"  !! {k}: satirlar {v}")
if not cift:
    print("  (cift tanim yok)")

print("\n=== ROUTE DECORATORLERI ===")
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if dec.func.attr in ("get", "post", "put", "delete"):
                    yol = dec.args[0].value if dec.args and isinstance(dec.args[0], ast.Constant) else "?"
                    dep = [a for a in dec.args[1:] if isinstance(a, ast.Call)]
                    print(f"  @router.{dec.func.attr}('{yol}') -> {node.name} (satir {node.lineno})")

print("\n=== MODELS ===")
for name, ln, bases in models:
    print(f"  {name} (satir {ln}) bases={bases}")

print("\n=== TUM FONKSIYONLAR ===")
for k, v in sorted(funcs.items(), key=lambda x: x[1][0]):
    flag = " [CIFT]" if len(v) > 1 else ""
    print(f"  {k}: {v}{flag}")
