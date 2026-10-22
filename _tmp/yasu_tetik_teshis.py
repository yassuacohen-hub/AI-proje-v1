# -*- coding: utf-8 -*-
"""yasu bekliyor tetik gorunmezlik teshisi."""
import sys
from pathlib import Path

KOK = Path(r"c:/Huginn Data Projesi/Huginn Data Insights")
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "src"))
sys.path.insert(0, str(KOK / "scripts"))
from company_master.orchestrator import trigger, task_board as tb  # noqa: E402

ham = trigger._tetikleri_oku("yasu")
print("ham tetik:", len(ham))
for k in ham:
    tid = k.get("task_id")
    g = tb.gorev_getir(tid) if hasattr(tb, "gorev_getir") else None
    print(tid, k.get("durum"), "| pano:", (g or {}).get("durum"), "| sahip:", (g or {}).get("sahip"))
print("KAPALI:", tb.KAPALI_DURUMLAR)
print("bekleyen:", [k["task_id"] for k in trigger.bekleyen_tetikler("yasu")])
