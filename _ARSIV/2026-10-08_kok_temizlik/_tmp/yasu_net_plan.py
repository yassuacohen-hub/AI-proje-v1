# -*- coding: utf-8 -*-
"""YASU: API-V1-NETWORK-REPORT-01 bitirme plani icin canli olcum."""
import ast
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = Path(r"c:\HUGINN~1\HUGINN~1")

# 1) AKTIF GOREVLER
print("=== AKTIF / REVIEW GOREVLER ===")
tb = BASE / "data" / "orchestrator" / "task_board.json"
if tb.exists():
    data = json.loads(tb.read_text(encoding="utf-8"))
    tasks = data if isinstance(data, list) else data.get("tasks", data.get("gorevler", []))
    for t in tasks:
        if isinstance(t, dict) and t.get("sahip") == "yasu" and t.get("durum") not in ("done", "archive", "iptal"):
            print(f"- {t.get('task_id')} | {t.get('durum')} | {t.get('oncelik')}")
            print(f"    brief: {t.get('brief')}")
            print(f"    dosyalar: {t.get('dosyalar')}")
            dep = t.get("dependencies") or t.get("dependson")
            print(f"    deps: {dep}")
            tal = (t.get("talimat") or "")[:110]
            print(f"    talimat: {tal}")

# 2) V1_NETWORK.PY AST ANALIZI
print("\n=== V1_NETWORK.PY ===")
net = BASE / "src" / "company_master" / "api" / "routers" / "v1" / "v1_network.py"
if net.exists():
    src = net.read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = Counter()
    routes = []
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn[node.name] += 1
        if isinstance(node, ast.Import):
            imports += [a.name for a in node.names]
        if isinstance(node, ast.ImportFrom):
            names = ", ".join(a.name for a in node.names[:5])
            imports.append(f"from {node.module} import {names}")
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in node.decorator_list:
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in ("get", "post", "put", "delete", "patch"):
                    arg = ast.literal_eval(d.args[0]) if d.args and isinstance(d.args[0], ast.Constant) else "?"
                    routes.append(f"{d.func.attr.upper()} {arg} -> {node.name}")
    cift = {k: v for k, v in fn.items() if v > 1}
    print(f"satir: {len(src.splitlines())}")
    print(f"CIFT TANIMLI: {cift if cift else 'YOK'}")
    print(f"ROUTE ({len(routes)}):")
    for r in routes:
        print(f"    {r}")
    print("IMPORTLAR:")
    for i in imports:
        print(f"    {i}")
else:
    print("DOSYA YOK!")

# 3) BRIEF KAPANIS DURUMU
print("\n=== BRIEF KAPANIS KAPISI ===")
for bf in sorted((BASE / "plans").glob("brief_yasu_*.md")):
    txt = bf.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()
    kabul = [i + 1 for i, l in enumerate(lines) if "Kabul kriteri" in l]
    teslim = [i + 1 for i, l in enumerate(lines) if l.startswith("## Teslim")]
    hub = [i + 1 for i, l in enumerate(lines) if "B-14" in l or "Kapanan i" in l]
    print(f"- {bf.name}: kabul={kabul} teslim={teslim} hub_b14={hub}")

# 4) HUB DOSYALARI
print("\n=== HUBS ===")
hubs = BASE / "hubs"
if hubs.exists():
    for h in sorted(hubs.glob("*.md")):
        print(f"- {h.name}")
else:
    print("hubs/ yok")
