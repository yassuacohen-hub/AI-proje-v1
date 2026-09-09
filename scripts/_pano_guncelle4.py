# -*- coding: utf-8 -*-
"""P0-3 kalite skoru hedefi basarili."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.orchestrator import task_board as tb  # noqa: E402

tb.gorev_guncelle("P0-3", durum="done", **{
    "not": ("Kalite skoru 56.54/100 (hedef 50+ BASARILI). "
            "Dagilim: 80-100: 727, 60-79: 4854, 40-59: 1025, 20-39: 2241, 0-19: 160. "
            "Alanlar: telefon %92.3, email %48.4, web %56.2, NACE %100, VKN %0.4. "
            "VKN tek eksik alan — MERSIS API (P2-1) ile cozulebilir.")
})
tb.handoff_yaz("P0-3", "Kalite skoru 56.54/100 — hedef 50+ basarili",
               "VKN %0.4 tek eksik alan; MERSIS API (P2-1) hedefi")

tb.agent_sync_yaz()
print("P0-3 kapatildi")