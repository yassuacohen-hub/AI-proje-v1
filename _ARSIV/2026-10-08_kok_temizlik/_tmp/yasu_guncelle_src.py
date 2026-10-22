# -*- coding: utf-8 -*-
import sys, inspect
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

print("=== guncelle kaynak ===")
print(inspect.getsource(chat.guncelle))
