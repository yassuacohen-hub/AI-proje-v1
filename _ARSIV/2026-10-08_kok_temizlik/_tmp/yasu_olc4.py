# -*- coding: utf-8 -*-
import json, sys, subprocess, os, ast
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"
os.chdir(BASE)

def var(rel):
    return os.path.exists(rel)

def py_compile(rel):
    if not var(rel):
        return "DOSYA-YOK"
    try:
        ast.parse(open(rel, encoding="utf-8", errors="replace").read())
        return "SYNTAX-OK"
    except SyntaxError as e:
        return f"SYNTAX-ERR satir {e.lineno}: {e.msg}"

def cift_tanim(rel, fn_list):
    """Bir dosyada fonksiyon kaç kez tanimli?"""
    if not var(rel):
        return []
    try:
        agac = ast.parse(open(rel, encoding="utf-8", errors="replace").read())
    except Exception:
        return ["PARSE-ERR"]
    sayim = {}
    for node in ast.walk(agac):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in fn_list:
            sayim[node.name] = sayim.get(node.name, 0) + 1
    return [f"{k}={v}" for k, v in sayim.items() if v > 1]

print("=" * 60)
print("1) API-V1-NETWORK-REPORT-01")
print("=" * 60)
net = "src/company_master/api/routers/v1/v1_network.py"
print(f"  {net}: {py_compile(net)}")
print(f"    cift tanim: {cift_tanim(net, ['_fetch_company_by_vkn', '_get_company_vkn']) or 'YOK'}")
print(f"  test test_api_v1_network.py var mi: {var('tests/test_api_v1_network.py')}")

print("=" * 60)
print("2) UI-SSR-NEXT-KUNYE-01")
print("=" * 60)
for f in ["frontend/package.json", "frontend/next.config.mjs",
          "frontend/app/firma/[vkn]/page.tsx", "frontend/app/firma/firma.test.tsx"]:
    print(f"  {f}: {var(f)}")

print("=" * 60)
print("3) ALTYAPI-REPO-TEMIZLIK-01")
print("=" * 60)
print(f"  _ARSIV/ klasoru var mi: {var('_ARSIV')}")
r = subprocess.run("git status --short", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
untracked = [l for l in r.stdout.splitlines() if l.startswith("??")]
print(f"  takipsiz (??) dosya sayisi: {len(untracked)}")

print("=" * 60)
print("4) ORCH-KODLAMA-TEMIZLIK-01")
print("=" * 60)
r2 = subprocess.run("python scripts/kodlama_denetim.py", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
out = r2.stdout
# ihlal sayisini say
for kat in ["utf8_bom", "mojibake", "crlf_karisik", "sondaki_bosluk", "dosya_sonu"]:
    for line in out.splitlines():
        if line.strip().startswith(kat):
            print(f"  {line.strip()}")
            break
print(f"  kodlama_denetim cikis kodu: {r2.returncode} (0=temiz)")
