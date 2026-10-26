#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gorev_kutusu.py — Görev yönetim aracı (watchdog tetik + manuel komutlar)

Kullanım (watchdog tetik):
    python scripts/gorev_kutusu.py move_plan_tasks --from-agent <ajan> --to-agent <ajan> [--task-id <ID>]
    python scripts/gorev_kutusu.py redistribute_yasu --to-group <CORE|BACKUP>
    python scripts/gorev_kutusu.py resolve_blocked --task-id <ID>

Kullanım (manuel):
    python scripts/gorev_kutusu.py bak --ajan <isim>
    python scripts/gorev_kutusu.py teslim --ajan <isim> --task-id <ID> --ozet <mesaj>
    python scripts/gorev_kutusu.py nobet --ajan <isim>
    python scripts/gorev_kutusu.py devret --task-id <ID> --yeni-ajan <ajan>
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Root paths
ROOT = Path(__file__).parent.parent
TASK_BOARD_PATH = ROOT / "Huginn Data Insights" / "data" / "orchestrator" / "task_board.json"
TRIGGER_PATH = ROOT / "Huginn Data Insights" / "data" / "orchestrator" / "triggers"

# nisa: PO 25.10 emri - hasta (yasu gibi), bir sure gorev alamaz. salih tek yedek.
CAPACITIES = {'ihsan': 2, 'utku': 3, 'bilo': 2, 'nur': 2, 'salih': 5, 'nisa': 0, 'yasu': 0, 'mimir': 0}


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
        if t.get("sahip") == ajan.lower() and t.get("durum") in ("plan", "beklemede", "aktif", "bekliyor")
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


def move_task(board: List[Dict[str, Any]], task_id: str, yeni_ajan: str) -> bool:
    """Görevi başka bir ajana devreder."""
    idx = find_task(board, task_id)
    if idx is None:
        print(f"Gorev bulunamadi: {task_id}")
        return False

    eski_ajan = board[idx].get("sahip", "bilinmiyor")
    board[idx]["sahip"] = yeni_ajan.lower()
    board[idx]["son_durum"] = f"Devretildi: {eski_ajan} -> {yeni_ajan} ({datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')})"
    save_task_board(board)
    print(f"[OK] Gorev devredildi: {task_id} ({eski_ajan} -> {yeni_ajan})")
    return True


def move_plan_tasks(from_agent: str, to_agent: str, task_id: Optional[str] = None) -> int:
    """Aşırı yüklü ajandan plan görevlerini hedef ajana taşır."""
    board = load_task_board()
    moved = 0
    
    for t in board:
        if t.get("sahip") == from_agent.lower() and t.get("durum") == "plan":
            if task_id and t.get("task_id") != task_id:
                continue
            # Kapasite kontrolü
            to_load = sum(1 for x in board if x.get("sahip") == to_agent.lower() and x.get("durum") in ("plan", "aktif", "bekliyor", "in_progress"))
            to_cap = CAPACITIES.get(to_agent.lower(), 0)
            if to_cap > 0 and to_load >= to_cap:
                print(f"[UYARI] {to_agent} kapasitesi dolu ({to_load}/{to_cap}), atlanıyor: {t.get('task_id')}")
                continue
            
            move_task(board, t.get("task_id"), to_agent)
            moved += 1
            
            if task_id:
                break
    
    return moved


def redistribute_yasu(to_group: str = "CORE") -> int:
    """Yasu'daki görevleri hedef gruba dağıtır."""
    board = load_task_board()
    yasu_tasks = [t for t in board if t.get("sahip") == "yasu" and t.get("durum") in ("plan", "beklemede", "aktif", "bekliyor")]
    
    if not yasu_tasks:
        print("[BİLGİ] Yasu'da dağıtılacak görev yok")
        return 0
    
    # Hedef grup ajanları
    groups = {
        "CORE": ["ihsan", "utku", "bilo", "nur"],
        "BACKUP": ["salih", "nisa"],
    }
    target_agents = groups.get(to_group.upper(), [])
    
    moved = 0
    for task in yasu_tasks:
        # En az yüklü uygun ajanı bul
        best_agent = None
        best_load = float('inf')
        for agent in target_agents:
            load = sum(1 for x in board if x.get("sahip") == agent and x.get("durum") in ("plan", "aktif", "bekliyor", "in_progress"))
            cap = CAPACITIES.get(agent, 0)
            if cap > 0 and load < cap and load < best_load:
                best_load = load
                best_agent = agent
        
        if best_agent:
            move_task(board, task.get("task_id"), best_agent)
            moved += 1
        else:
            print(f"[UYARI] {to_group} grubunda kapasite yok, atlanıyor: {task.get('task_id')}")
    
    return moved


def resolve_blocked(task_id: str) -> bool:
    """Bloklu görevi çözmeye çalışır (bağımlılık kontrolü)."""
    board = load_task_board()
    idx = find_task(board, task_id)
    if idx is None:
        print(f"Görev bulunamadı: {task_id}")
        return False
    
    task = board[idx]
    deps = task.get("dependencies", [])
    done_ids = set(t.get("task_id", "") for t in board if t.get("durum") in ("done", "archive", "tamamlandı"))
    blocked_deps = [d for d in deps if d not in done_ids]
    
    if not blocked_deps:
        print(f"[OK] {task_id} bloklu değil, bağımlılıklar tamam")
        return True
    
    print(f"[BİLGİ] {task_id} hala bloklu, bekleyen bağımlılıklar: {blocked_deps}")
    return False


def go_to_nobet(ajan: str) -> None:
    """Ajani nobete ceker (servis durumunu aktif hale getirir)."""
    print(f"[OK] {ajan} nobeye gecti. Gorev devretme bekleniyor.")


def main():
    parser = argparse.ArgumentParser(description="Görev Yönetim Aracı (Watchdog + Manuel)")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # --- Watchdog tetik komutları ---
    move_plan_parser = subparsers.add_parser("move_plan_tasks", help="Plan görevlerini taşı (watchdog)")
    move_plan_parser.add_argument("--from-agent", required=True, help="Kaynak ajan")
    move_plan_parser.add_argument("--to-agent", required=True, help="Hedef ajan")
    move_plan_parser.add_argument("--task-id", help="Belirli görev ID (opsiyonel)")

    redistribute_parser = subparsers.add_parser("redistribute_yasu", help="Yasu görevlerini dağıt (watchdog)")
    redistribute_parser.add_argument("--to-group", choices=["CORE", "BACKUP"], default="CORE", help="Hedef grup")

    resolve_parser = subparsers.add_parser("resolve_blocked", help="Bloklu görevi çöz (watchdog)")
    resolve_parser.add_argument("--task-id", required=True, help="Görev ID")

    # --- Manuel komutlar ---
    bak_parser = subparsers.add_parser("bak", help="Görev panosunu göster")
    bak_parser.add_argument("--ajan", required=True, help="Ajan ismi")

    teslim_parser = subparsers.add_parser("teslim", help="Görevi teslim et")
    teslim_parser.add_argument("--ajan", required=True, help="Ajan ismi")
    teslim_parser.add_argument("--task-id", required=True, help="Görev ID")
    teslim_parser.add_argument("--ozet", required=True, help="Teslim özeti")

    nobet_parser = subparsers.add_parser("nobet", help="Nöbete geç")
    nobet_parser.add_argument("--ajan", required=True, help="Ajan ismi")

    devret_parser = subparsers.add_parser("devret", help="Görevi başka ajana devret (ihsan onayıyla)")
    devret_parser.add_argument("--task-id", required=True, help="Görev ID")
    devret_parser.add_argument("--yeni-ajan", required=True, help="Yeni ajan ismi")

    # Watchdog positional argüman desteği (eski çağrı stili: action [task_id])
    parser.add_argument("positional_action", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("positional_task_id", nargs="?", help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Watchdog eski çağrı stili: python gorev_kutusu.py move_plan_tasks [task_id]
    # Bu durumda subcommand parse edilmez, positional_action dolu gelir
    if args.positional_action and not args.command:
        action = args.positional_action
        task_id = args.positional_task_id
        
        if action == "move_plan_tasks":
            # Watchdog'dan gelen basit çağrı: en aşırı yüklü ajandan en az yüklüye taşı
            board = load_task_board()
            # Ajan yüklerini hesapla
            agent_loads = {}
            for t in board:
                if t.get("durum") in ("plan", "aktif", "bekliyor", "in_progress"):
                    agent = t.get("sahip", "unknown")
                    agent_loads[agent] = agent_loads.get(agent, 0) + 1
            
            # En aşırı yüklü (kapasite oranı en yüksek)
            overloaded = None
            max_ratio = 0
            for agent, load in agent_loads.items():
                cap = CAPACITIES.get(agent, 0)
                if cap > 0:
                    ratio = load / cap
                    if ratio > max_ratio and ratio > 1.0:
                        max_ratio = ratio
                        overloaded = agent
            
            # En az yüklü (kapasite oranı en düşük, 0 hariç)
            underloaded = None
            min_ratio = float('inf')
            for agent, cap in CAPACITIES.items():
                if cap > 0:
                    load = agent_loads.get(agent, 0)
                    ratio = load / cap
                    if ratio < min_ratio:
                        min_ratio = ratio
                        underloaded = agent
            
            if overloaded and underloaded and overloaded != underloaded:
                moved = move_plan_tasks(overloaded, underloaded, task_id)
                print(f"[OK] {moved} plan görevi taşındı ({overloaded} → {underloaded})")
                sys.exit(0 if moved > 0 else 1)
            else:
                print("[BİLGİ] Taşınacak uygun ajan çifti yok")
                sys.exit(0)
        
        elif action == "redistribute_yasu":
            moved = redistribute_yasu("CORE")
            print(f"[OK] {moved} yasu görevi CORE grubuna dağıtıldı")
            sys.exit(0 if moved > 0 else 1)
        
        elif action == "resolve_blocked":
            if task_id:
                success = resolve_blocked(task_id)
                sys.exit(0 if success else 1)
            else:
                print("[HATA] resolve_blocked için task_id gerekli")
                sys.exit(1)
        
        else:
            print(f"[HATA] Bilinmeyen watchdog aksiyonu: {action}")
            sys.exit(1)

    # Normal subcommand işleme
    if args.command == "move_plan_tasks":
        moved = move_plan_tasks(args.from_agent, args.to_agent, args.task_id)
        print(f"[OK] {moved} plan görevi taşındı ({args.from_agent} → {args.to_agent})")
        sys.exit(0 if moved > 0 else 1)

    elif args.command == "redistribute_yasu":
        moved = redistribute_yasu(args.to_group)
        print(f"[OK] {moved} yasu görevi {args.to_group} grubuna dağıtıldı")
        sys.exit(0 if moved > 0 else 1)

    elif args.command == "resolve_blocked":
        success = resolve_blocked(args.task_id)
        sys.exit(0 if success else 1)

    # Manuel komutlar
    elif args.command == "bak":
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

    elif args.command == "devret":
        board = load_task_board()
        success = move_task(board, args.task_id, args.yeni_ajan)
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()