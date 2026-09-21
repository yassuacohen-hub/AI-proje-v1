#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""D-185: decision_log.jsonl'ye kayit ekle."""
import json
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "data" / "orchestrator" / "decision_log.jsonl"

ENTRY = {
    "id": "D-185",
    "tarih": "2026-09-21",
    "baslik": "DASH-UX-02a Split: v1 (Dosya) + v2 (SECTIONS) — MENUTREE Cakisma Cozumu",
    "karar_veren": "KAHIN",
    "gerekce": "D-85 karar-da seri uygulanma tanimlanmis ama DASH-UX-02a (admin_sistem.py yazma) ile ADMIN-UX-MENUTREE-01 (tabs/__init__.py duzenle) ayni SECTIONS noktasinda carpisiyordu. merge riski yuksek, parallelism kaybiyordu. Sahip onayi: v1->v2 split iyidir, paralel ile hizlanir, merge riski sifir (2026-09-21).",
    "karar": [
        "DASH-UX-02a ayrilir: v1 (dosya) + v2 (SECTIONS kaydi)",
        "v1: admin_sistem.py yazilir, tabs/__init__.py'ye DOKUNULMAZ. K1 kalibrasyonu v1'de tanimlanir. Local testler gecer. Paralel MENUTREE ile.",
        "v2: DASH-UX-02a-SECTIONS yeni gorevi. MENUTREE bitince tetiklenir. SECTIONS'a admin_sistem kaydini ekler. Full regresyon.",
        "Seri zincir: MENUTREE -> DASH-UX-02a.v2 -> DASH-UX-02b (tek __init__.py paylasmasi, merge riski 0)",
        "ADMIN-AYAR-01: pano taramasinda done (2026-09-17) bulundu -> sprint listesinden cikari."
    ],
    "blokaj_cozumu": "Klasik v1/v2 pattern: yazma (parallelizable) vs kayit (contention point, seri). Karar D-85'in scopesini genisleterek tam cakismayı ortadan kaldirdi.",
    "etkilenen_dosyalar": [
        "data/orchestrator/task_board.json",
        "data/orchestrator/SPRINT_PLANI_2026-09-21.md",
        "plans/brief_utku_DASH-UX-02a-v1.md",
        "plans/brief_utku_DASH-UX-02a-v2.md",
        "scripts/d185_board_guncelle.py",
        "AGENTS.md"
    ],
    "kaynak": [
        "data/orchestrator/D-185_DASH-UX-02a-SPLIT_MENUTREE_CAKISMA_COZUMU_2026-09-21.md",
        "Sahip tasviri v1->v2 split"
    ]
}

with open(LOG, "a", encoding="utf-8") as f:
    json.dump(ENTRY, ensure_ascii=False, fp=f)
    f.write("\n")

print("[OK] D-185 decision_log.jsonl'ye yazildi")
