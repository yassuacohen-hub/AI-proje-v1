# -*- coding: utf-8 -*-
import sys, ast, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")
p = BASE / "src" / "company_master" / "api" / "routers" / "v1" / "v1_network.py"
src = p.read_text(encoding="utf-8", errors="replace")
tree = ast.parse(src)

print("=== UST DÜZEY FONKSİYONLAR + DECORATOR + OLU KOD ===")
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        decos = [ast.dump(d) for d in node.decorator_list]
        deco_isim = []
        for d in node.decorator_list:
            if isinstance(d, ast.Call):
                f = d.func
                # router.post("...") -> attr=post, args[0]=path
                if isinstance(f, ast.Attribute):
                    if d.args and isinstance(d.args[0], ast.Constant):
                        deco_isim.append(f"{f.attr}({d.args[0].value!r})")
                    else:
                        deco_isim.append(f.attr)
            elif isinstance(d, ast.Attribute):
                deco_isim.append(d.attr)
            elif isinstance(d, ast.Name):
                deco_isim.append(d.id)
        print(f"\n  def {node.name} [{node.lineno}-{node.end_lineno}] deco={deco_isim}")
        # olü kod: return'dan sonra statement var mı (fonksiyon gövdesinde)
        govde = node.body
        oluler = []
        for i, stmt in enumerate(govde):
            if isinstance(stmt, ast.Return) and i < len(govde) - 1:
                oluler = govde[i+1:]
                break
        if oluler:
            print(f"    !! OLU KOD: return sonrasi {len(oluler)} statement (satir {oluler[0].lineno}-{oluler[-1].end_lineno})")
            for o in oluler:
                print(f"       - {type(o).__name__} @ {o.lineno}: {ast.dump(o)[:80]}")
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name):
                print(f"  ASSIGN {t.id} @ {node.lineno}")
    elif isinstance(node, ast.ImportFrom):
        pass

print("\n=== IMPORTLAR ===")
for node in tree.body:
    if isinstance(node, ast.Import):
        for a in node.names:
            print(f"  import {a.name}")
    elif isinstance(node, ast.ImportFrom):
        print(f"  from {node.module} import {[a.name for a in node.names]}")
