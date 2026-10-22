# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"c:\HUGINN~1\HUGINN~1\src")
BASE = Path(r"c:\HUGINN~1\HUGINN~1")
TASK = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"

# --- KAPI 1 + 2: chat.teslim_kontrol_et ---
try:
    from company_master import chat
    sonuc = chat.teslim_kontrol_et(TASK)
    print(f"[KAPI 1] chat.teslim_kontrol_et tipi = {type(sonuc).__name__}")
    if isinstance(sonuc, dict):
        print(f"   engel = {sonuc.get('engel')}")
        nedenler = sonuc.get('nedenler') or []
        print(f"   neden sayisi = {len(nedenler)}")
        for n in nedenler:
            print(f"   - {n}")
    else:
        print(f"   ham: {sonuc}")
except Exception as e:
    print(f"[KAPI 1] HATA: {e}")

# --- KAPI 3: bulgu defteri ---
try:
    import subprocess
    r = subprocess.run(
        [sys.executable, str(BASE / "scripts" / "bulgu_defteri.py"), "ekle", "--task-id", TASK],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(BASE))
    # ekle --dry yok; sadece varlik grep
except Exception as e:
    pass

# bulgu defterinde bu task var mi (grep)
defter = BASE / "data" / "orchestrator" / "bulgu_defteri.md"
if defter.exists():
    icerik = defter.read_text(encoding="utf-8", errors="replace")
    print(f"[KAPI 3] bulgu_defteri.md -> {TASK} gecıyor mu: {TASK in icerik}")
else:
    print("[KAPI 3] bulgu_defteri.md YOK")

# --- _mesaj_kontrol_et (gorev_kutusu icinde) ---
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("gk", BASE / "scripts" / "gorev_kutusu.py")
    gk = importlib.util.module_from_spec(spec)
    sys.argv = ["gk"]
    spec.loader.exec_module(gk)
    if hasattr(gk, "_mesaj_kontrol_et"):
        import inspect
        sig = inspect.signature(gk._mesaj_kontrol_et)
        if "ajan" in sig.parameters:
            sonuc = gk._mesaj_kontrol_et(TASK, "yasu")
        else:
            sonuc = gk._mesaj_kontrol_et(TASK)
        print(f"[KAPI 2] _mesaj_kontrol_et -> {type(sonuc).__name__}: {sonuc}")
    else:
        print("[KAPI 2] _mesaj_kontrol_et fonksiyonu yok (imza degismis)")
except Exception as e:
    print(f"[KAPI 2] HATA: {e}")
