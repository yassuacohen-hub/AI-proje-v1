# -*- coding: utf-8 -*-
"""Utku için gece zinciri: 5 task sıra, blokaj yok, bağımsız işler.

Gece zinciri: Sürdürülebilir, hatasız, ardışık iş akışı.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
PANO = KOK / "data" / "orchestrator" / "task_board.json"

ZINCIR_GOREVLER = [
    # Admin panel işleri — test çerçevesi & güvenlik — blokaj yok
    "TEST-AYARLAR-KAPSAM-01",       # Kullanıcı Ayarları test iskeleti yaz
    "TEST-MERVE-KAPSAM-01",         # Ayarlar test kapsamını denetle (salih → utku tarafından bağlantı kurulacak)
    "ORKESTRA-BASLIK-GERIYE-01",    # Task başlıklarını D-57 kalibına taşı
    "SEC-BANDIT-01",                # Bandit statik güvenlik taraması (ertelendi ama temel)
    "DASH-UX-02a-SECTIONS",         # DASH-UX-02a sekmesi __init__.py kaydı (tekil, bağımsız)
]


def main() -> None:
    pano = json.loads(PANO.read_text(encoding="utf-8"))
    gonc = {}

    for task_id in ZINCIR_GOREVLER:
        g = next((x for x in pano if x["task_id"] == task_id), None)
        if g:
            gonc[task_id] = {
                "title": g.get("baslik", ""),
                "owner": g.get("sahip", "-"),
                "status": g.get("durum", ""),
                "priority": g.get("oncelik", "?"),
            }
        else:
            gonc[task_id] = {"title": "(BULUNAMADI)", "error": "not_found"}

    rapor = f"# Utku Gece Zinciri — {datetime.now().isoformat()}\n\n"
    rapor += "5 ardışık görev (blokaj yok, oto-tetiklenecek):\n\n"
    for i, task_id in enumerate(ZINCIR_GOREVLER, 1):
        info = gonc[task_id]
        rapor += f"**{i}. {task_id}** [{info.get('priority')}]\n"
        rapor += f"   Sahibi: {info.get('owner')}\n"
        rapor += f"   Durum: {info.get('status')}\n"
        rapor += f"   Konu: {info.get('title')}\n\n"

    rapor_dosya = KOK / "data" / "orchestrator" / f"GECE-ZINCIRI-UTKU_2026-09-22T04-30.md"
    rapor_dosya.write_text(rapor, encoding="utf-8")
    print(f"Zincir hazır: {rapor_dosya}")


if __name__ == "__main__":
    main()
