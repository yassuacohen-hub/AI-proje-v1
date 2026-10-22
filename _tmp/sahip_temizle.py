# -*- coding: utf-8 -*-
"""UX-DENET-* kayitlarinda sahip=talimat, baslik='salih' hatasini duzeltir (idempotent)."""
import sys
sys.path.insert(0, "Huginn Data Insights/src")
from company_master.orchestrator import task_board as tb

GECERLI = {"ihsan", "utku", "salih", "yasu", "mimir", "bilo", "nur", "nisa"}
n = 0
for t in tb.gorev_listesi():
    tid = t.get("task_id", "")
    sahip = str(t.get("sahip", ""))
    if not tid.startswith("UX-DENET-") or sahip in GECERLI:
        continue
    alanlar = {"sahip": "salih", "baslik": f"UX denetimi: {tid[len('UX-DENET-'):]}"}
    if not t.get("talimat"):
        alanlar["talimat"] = sahip
    tb.gorev_guncelle(tid, **alanlar)
    n += 1
    print("duzeltildi", tid)
print("toplam", n)
assert not [t for t in tb.gorev_listesi()
            if t["task_id"].startswith("UX-DENET-") and t["sahip"] not in GECERLI]
print("OK sahip_temizle")
