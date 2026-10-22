# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"

# 1) kapat fonksiyonunun imzasini ve govdesini goster
import inspect
print("=== kapat imza ===")
try:
    print(inspect.signature(chat.kapat))
except Exception as e:
    print("  HATA:", e)
print("=== kapat kaynak (ilk 60 satir) ===")
try:
    src = inspect.getsource(chat.kapat)
    for i, l in enumerate(src.splitlines()[:60], 1):
        print(f"{i:3} {l}")
except Exception as e:
    print("  HATA:", e)

# 2) tum kayitlari oku, acik olanlarin gercek index'ini bul
print()
print("=== kayit listesi (durum + index) ===")
kayitlar = chat.oku(tid) if hasattr(chat, "oku") else None
if kayitlar is None:
    # muhtemel farkli ad: liste donduren bir fonksiyon ara
    aday = [a for a in dir(chat) if not a.startswith("__") and callable(getattr(chat, a))]
    print("  chat fonksiyonlari:", aday)
