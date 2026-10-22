# -*- coding: utf-8 -*-
import sys, json, subprocess, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")
sys.path.insert(0, str(ROOT))

print("=== 1) v1_network.py DURUM ===")
vf = ROOT / "src/company_master/api/routers/v1/v1_network.py"
if vf.exists():
    src = vf.read_text(encoding="utf-8", errors="replace")
    lines = src.splitlines()
    print(f"  satir: {len(lines)}")
    # cift tanim kontrol
    import re
    defs = re.findall(r"^def\s+(\w+)", src, re.M)
    from collections import Counter
    dup = [k for k,v in Counter(defs).items() if v > 1]
    print(f"  fonksiyonlar: {len(defs)} | cift tanim: {dup if dup else 'YOK'}")
    print(f"  EOF(\\n): {src.endswith(chr(10))}")
    r = subprocess.run([sys.executable, "-m", "py_compile", str(vf)], capture_output=True, text=True)
    print(f"  compile: {'OK' if r.returncode==0 else 'HATA: '+r.stderr[:200]}")

print("\n=== 2) tests/test_api_v1_network.py VAR MI ===")
tf = ROOT / "tests/test_api_v1_network.py"
print(f"  {'VAR' if tf.exists() else 'YOK'} -> {tf}")

print("\n=== 3) TASK BOARD: aktif/review yasu gorevleri ===")
tb = json.loads((ROOT / "data/orchestrator/task_board.json").read_text(encoding="utf-8"))
tasks = tb if isinstance(tb, list) else tb.get("tasks", [])
for t in tasks:
    if t.get("sahip") == "yasu" and t.get("durum") in ("aktif", "review"):
        print(f"  [{t['durum']:6}] {t['id']}")

print("\n=== 4) PLAN_STRATEGY_HUB Kapanan bolumu ===")
hub = ROOT / "hubs/PLAN_STRATEGY_HUB.md"
if hub.exists():
    h = hub.read_text(encoding="utf-8", errors="replace")
    print(f"  'Kapanan' var: {'Kapanan' in h} | 'API-V1-NETWORK' gec: {'API-V1-NETWORK' in h}")

print("\n=== 5) web_app.py include_router v1_network ===")
wa = ROOT / "web_app.py"
if wa.exists():
    w = wa.read_text(encoding="utf-8", errors="replace")
    print(f"  include_router network: {'network' in w and 'include_router' in w}")
    for ln in w.splitlines():
        if "network" in ln.lower() and "router" in ln.lower():
            print(f"    > {ln.strip()[:90]}")
