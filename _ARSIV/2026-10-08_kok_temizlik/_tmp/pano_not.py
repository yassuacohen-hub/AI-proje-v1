# -*- coding: utf-8 -*-
"""Resmi kanal: 2 blocked gorevin pano 'not' alanina kok neden + bekleyen karar yaz (D-77, D-65)."""
import json
from pathlib import Path
P = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json")
pano = json.loads(P.read_text(encoding="utf-8"))
NOT = ("2026-10-10 ihsan: Blokaj kok nedeni = nobet_modu.json yoktu, tum ajanlar 2026-10-06'dan beri kademe 1 (PLAN), "
       "gorev alamiyordu. Dosya kuruldu (utku/salih/yasu=2, ihsan=3). P0/P1 kademe 2'de 'al ETME' kuraliyla PO karari bekler: "
       "(a) utku kademe 3 ya da (b) ihsan devralir. Chat kaydi kapatildi (D-286).")
hedef = {"UI-ADMIN-PANEL-TEMEL-REFERANS-01", "DOC-BRIEF-SABLON-KIRMIZI-01"}
n = 0
for g in pano:
    if g.get("task_id") in hedef and g.get("durum") == "blocked":
        g["not"] = ((g.get("not") or "").strip() + " | " if g.get("not") else "") + NOT
        n += 1
assert n == 2, n
P.write_text(json.dumps(pano, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("not yazildi:", n)
