# -*- coding: utf-8 -*-
import sys, ast, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")

def brief_kurallar(dosya):
    p = BASE / "plans" / dosya
    print(f"=== {dosya} ===")
    if not p.exists():
        print("  (yok)")
        return
    L = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, s in enumerate(L, 1):
        if "B-14" in s or "ZORUNLU" in s or "Teslimden" in s:
            print(f"  {i}: {s.strip()[:100]}")

def hub_kapanan():
    p = BASE / "hubs" / "PLAN_STRATEGY_HUB.md"
    print("=== PLAN_STRATEGY_HUB.md Kapanan ===")
    if not p.exists():
        print("  (yok)")
        return
    L = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, s in enumerate(L, 1):
        if "Kapanan" in s or "API-V1-NETWORK" in s or "UI-SSR-NEXT" in s:
            print(f"  {i}: {s.strip()[:100]}")

def v1_net_ast():
    p = BASE / "src" / "company_master" / "api" / "routers" / "v1" / "v1_network.py"
    print("=== v1_network.py AST ===")
    if not p.exists():
        print("  (yok)")
        return
    src = p.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            print(f"  def {node.name} (satir {node.lineno}-{node.end_lineno})")

brief_kurallar("brief_yasu_API-V1-NETWORK-REPORT-01.md")
brief_kurallar("brief_yasu_UI-SSR-NEXT-KUNYE-01.md")
hub_kapanan()
v1_net_ast()
