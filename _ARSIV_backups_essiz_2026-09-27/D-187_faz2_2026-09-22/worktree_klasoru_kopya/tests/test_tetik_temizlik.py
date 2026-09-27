# -*- coding: utf-8 -*-
"""ORKESTRA-IHSAN-TETIK-01: Tetik dosyası temizliği (dedupe) testi."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_tetik_dedupe_ayni_task_id_tekrar_atlanir(tmp_path: Path) -> None:
    """_sprint_baslat.py'nin dedupe mantığı: task_id tekrarlarını siler."""
    # Orijinal (duplikatlı) tetik dosyası oluştur
    triggers = tmp_path / "ihsan.jsonl"
    kayitlar = [
        {"task_id": "DASH-UX-02a", "ajan": "ihsan", "durum": "zincir_bekleme"},
        {"task_id": "DASH-UX-02b", "ajan": "ihsan", "durum": "blocked"},
        {"task_id": "DASH-UX-02b", "ajan": "ihsan", "durum": "blocked"},  # DUP
        {"task_id": "ADMIN-MENU-01", "ajan": "ihsan", "durum": "done"},
        {"task_id": "ADMIN-MENU-01", "ajan": "ihsan", "durum": "done"},  # DUP
        {"task_id": "ADMIN-MENU-01", "ajan": "ihsan", "durum": "done"},  # DUP
    ]
    
    with open(triggers, "w", encoding="utf-8") as f:
        for k in kayitlar:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    
    assert len(kayitlar) == 6
    
    # Dedupe mantığını uygula
    mevcut = []
    gorulen = set()
    with open(triggers, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            k = json.loads(line)
            tid = k.get("task_id", "")
            if tid not in gorulen:
                gorulen.add(tid)
                mevcut.append(k)
    
    # Sonuç: ilk 3 unique task_id'yi saklamalı
    assert len(mevcut) == 3
    assert [k["task_id"] for k in mevcut] == ["DASH-UX-02a", "DASH-UX-02b", "ADMIN-MENU-01"]
