# -*- coding: utf-8 -*-
import sys, io, json, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = pathlib.Path(r"c:\Huginn~1\Huginn~1")
TID = "API-V1-NETWORK-REPORT-01"

# 1) gorev_kutusu kapilari
import importlib.util
spec = importlib.util.spec_from_file_location("gk", str(R / "scripts" / "gorev_kutusu.py"))
gk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gk)

print("=== KAPI 1: chat.teslim_kontrol_et ===")
try:
    from company_master import chat
    r = chat.teslim_kontrol_et(TID)
    print("  sonuc:", r)
except Exception as e:
    print("  HATA:", e)

print("=== KAPI 2: _mesaj_kontrol_et ===")
try:
    print("  sonuc:", gk._mesaj_kontrol_et(TID))
except Exception as e:
    print("  HATA:", e)

print("=== KAPI 3: bulgu defteri ===")
bd = R / "data" / "orchestrator" / "bulgu_defteri.md"
try:
    print("  var_mi:", TID in bd.read_text(encoding="utf-8", errors="replace"))
except Exception as e:
    print("  HATA:", e)

print("=== KAPI 4: hafiza izi ===")
print("  izi:", [str(p) for p in gk._hafiza_izi(TID)])

print("=== pano durumu ===")
tb = json.loads((R / "data" / "orchestrator" / "task_board.json").read_text(encoding="utf-8"))
tasks = tb if isinstance(tb, list) else tb.get("tasks", [])
for t in tasks:
    if t.get("task_id") == TID or t.get("id") == TID:
        print("  durum:", t.get("durum"), "| sahip:", t.get("sahip"), "| not:", str(t.get("not"))[:80])
