#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Görev atama otomasyonu: brif var → tetik gönder → pano güncelle (hepsi bir komut).

Kullanım:
  python scripts/gorev_atama_otomatis.py --task-id DASH-UX-02a --ajan utku

Kontrol:
  1. Brif dosyası var mı? (plans/brief_{ajan}_{task_id}.md)
  2. Panodan görev oku (task_board.json)
  3. Tetik gönder (trigger.tetik_ekle)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Yol düzelt
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from src.company_master.orchestrator import trigger


def brif_bul(task_id: str, ajan: str) -> Path | None:
    """Brif dosyasını bul. Uzlaşma: plans/brief_{ajan}_{task_id}.md"""
    plans_dir = root / "plans"
    brif = plans_dir / f"brief_{ajan}_{task_id}.md"
    return brif if brif.exists() else None


def gorev_oku(task_id: str) -> dict | None:
    """task_board.json'dan görev oku (büyük/küçük harf duyarsız eşleşme)."""
    board_file = root / "data" / "orchestrator" / "task_board.json"
    if not board_file.exists():
        return None

    board = json.loads(board_file.read_text(encoding="utf-8"))
    hedef = task_id.lower()
    for t in board:
        if str(t.get("task_id", "")).lower() == hedef or str(t.get("id", "")).lower() == hedef:
            return t
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--task-id", required=True, help="Görev ID'si (örn. DASH-UX-02a)")
    parser.add_argument("--ajan", required=True, help="Ajan adı (örn. utku)")
    parser.add_argument("--talimat", default="", help="Özel talimat (brif varsa yok sayılır)")
    
    args = parser.parse_args()
    ajan = args.ajan.lower()

    # 1. Görev var mı? (büyük/küçük harf duyarsız ara, panodaki gerçek yazımı kullan)
    gorev = gorev_oku(args.task_id)
    if not gorev:
        print(f"[ERROR] Gorev bulunamadi: {args.task_id}")
        return 1
    task_id = gorev.get("task_id") or gorev.get("id")
    
    # 2. Brif var mı?
    brif = brif_bul(task_id, ajan)
    if not brif:
        print(f"[ERROR] Brif bulunamadi: {brif}")
        print(f"        Beklenen: plans/brief_{ajan}_{task_id}.md")
        return 1
    
    # 3. Talimat belirle
    talimat = args.talimat.strip()
    if not talimat:
        # Brif'ten ilk satırı al (başlık)
        brif_text = brif.read_text(encoding="utf-8")
        ilk_satir = brif_text.split("\n")[0]
        talimat = ilk_satir.replace("#", "").strip()
        if not talimat:
            talimat = f"Brif: {brif.relative_to(root)}"
    
    # 4. Tetik gönder
    try:
        sonuc = trigger.tetik_ekle(task_id, ajan, talimat)
        print(f"[OK] Tetik gonderildi: {task_id} -> {ajan}")
        print(f"    Talimat: {talimat[:60]}...")
        print(f"    Brif: {brif.relative_to(root)}")
        return 0
    except Exception as e:
        print(f"[ERROR] Tetik gonderilemedi: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
