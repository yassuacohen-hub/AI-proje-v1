#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gorev_kutusu.py — Görev yönetim aracı (tetik, teslim, nobet)

Kullanım:
    python scripts/gorev_kutusu.py bak --ajan <isim>
    python scripts/gorev_kutusu.py teslim --ajan <isim> --task-id <ID> --ozet <mesaj>
    python scripts/gorev_kutusu.py nobet --ajan <isim>
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Root paths
ROOT = Path(__file__).parent.parent
TASK_BOARD_PATH = ROOT / "Huginn Data Insights" / "data" / "orchestrator" / "task_board.json"
TRIGGER_PATH = ROOT / "Huginn Data Insights" / "data" / "orchestrator" / "triggers"


def load_task_board() -> List[Dict[str, Any]]:
    """Görev panosunu yükler."""
    if not TASK_BOARD_PATH.exists():
        return []
    with open(TASK_BOARD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_task_board(board: List[Dict[str, Any]]) -> None:
    """Görev pano dosyasını kaydeder."""
    with open(TASK_BOARD_PATH, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)


def find_task(board: List[Dict[str, Any]], task_id: str) -> Optional[int]:
    """Görev ID'sine göre indeksi döndürür."""
    for i, task in enumerate(board):
        if task.get("task_id") == task_id or task.get("id") == task_id:
            return i
    return None


def task_status(board: List[Dict[str, Any]], ajan: str) -> List[Dict[str, Any]]:
    """Belirli ajanın bekleyen görevlerini döndürür."""
    return [
        t for t in board
        if t.get("sahip") == ajan.lower() and t.get("durum") in ("plan", "beklemede", "aktif")
    ]


def mark_done(board: List[Dict[str, Any]], task_id: str, ajan: str, ozet: str) -> bool:
    """Görevi 'done' durumuna işaret eder."""
    idx = find_task(board, task_id)
    if idx is None:
        print(f"Görev bulunamadı: {task_id}")
        return False

    board[idx]["durum"] = "done"
    board[idx]["bitis"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    board[idx]["son_durum"] = f"Teslim: {ajan} — {ozet}"
    save_task_board(board)
    return True


def take_task(board: List[Dict[str, Any]], task_id: str) -> bool:
    """Görevi 'aktif' durumuna alır."""
    idx = find_task(board, task_id)
    if idx is None:
        print(f"Görev bulunamadı: {task_id}")
        return False

    board[idx]["durum"] = "aktif"
    board[idx]["baslangic"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    save_task_board(board)
    return True


def go_to_nobet(ajan: str) -> None:
    """Ajani nobete ceker (servis durumunu aktif hale getirir)."""
    print(f"[OK] {ajan} nobeye gecti. Gorev devretme bekleniyor.")
    # Not: Gercek sistemde burada gorev dagitma mekanizmasi calistirilir


def main():
    parser = argparse.ArgumentParser(description="Görev Yönetim Aracı")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # bak komutu
    bak_parser = subparsers.add_parser("bak", help="Görev panosunu göster")
    bak_parser.add_argument("--ajan", required=True, help="Ajan ismi")

    # teslim komutu
    teslim_parser = subparsers.add_parser("teslim", help="Görevi teslim et")
    teslim_parser.add_argument("--ajan", required=True, help="Ajan ismi")
    teslim_parser.add_argument("--task-id", required=True, help="Görev ID")
    teslim_parser.add_argument("--ozet", required=True, help="Teslim özeti")

    # nobet komutu
    nobet_parser = subparsers.add_parser("nobet", help="Nöbete geç")
    nobet_parser.add_argument("--ajan", required=True, help="Ajan ismi")

    args = parser.parse_args()

    if args.command == "bak":
        board = load_task_board()
        tasks = task_status(board, args.ajan)
        print(f"[{args.ajan}] bekleyen gorevler:")
        for t in tasks:
            print(f"  - {t.get('task_id')}: {t.get('baslik', 'N/A')[:60]}... ({t.get('oncelik')})")

    elif args.command == "teslim":
        board = load_task_board()
        success = mark_done(board, args.task_id, args.ajan, args.ozet)
        if success:
            print(f"[OK] Gorev teslim edildi: {args.task_id}")
        sys.exit(0 if success else 1)

    elif args.command == "nobet":
        go_to_nobet(args.ajan)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()