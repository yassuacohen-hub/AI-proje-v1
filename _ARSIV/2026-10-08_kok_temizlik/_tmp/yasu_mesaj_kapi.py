# -*- coding: utf-8 -*-
import sys, importlib.util, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
spec = importlib.util.spec_from_file_location("gk", str(R / "scripts" / "gorev_kutusu.py"))
gk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gk)

TID = "API-V1-NETWORK-REPORT-01"
print("=== _mesaj_kontrol_et(TID, yasu) ===")
try:
    print(gk._mesaj_kontrol_et(TID, "yasu"))
except Exception as e:
    print("HATA:", type(e).__name__, e)

print("=== chat.teslim_kontrol_et ===")
try:
    from company_master import chat
    print(chat.teslim_kontrol_et(TID))
except Exception as e:
    print("HATA:", e)
