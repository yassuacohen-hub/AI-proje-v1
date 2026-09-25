#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gunluk Senkronizasyon Tetikleme (2026-09-25)
Tetik saatleri: 09:00, 14:00, 19:00 Istanbul (UTC+3)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any

# Paths
TASK_BOARD_PATH = Path(__file__).parent.parent / "data" / "orchestrator" / "task_board.json"
SYNC_LOG_PATH = Path(__file__).parent.parent / "data" / "orchestrator" / "sync_gunluk.log"


def get_istanbul_time() -> datetime:
    """Istanbul saati (UTC+3) al."""
    utc_now = datetime.now(timezone.utc)
    istanbul_tz = timezone(timedelta(hours=3))
    return utc_now.astimezone(istanbul_tz)


def load_task_board() -> list[dict[str, Any]]:
    """task_board.json oku."""
    if not TASK_BOARD_PATH.exists():
        raise FileNotFoundError(f"task_board.json bulunamadi: {TASK_BOARD_PATH}")
    with open(TASK_BOARD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_tasks(board: list[dict[str, Any]]) -> dict[str, Any]:
    """Gorev durumunu analiz et."""
    todo = [t for t in board if t["durum"] == "todo"]
    in_progress = [t for t in board if t["durum"] == "in_progress"]
    aktif = [t for t in board if t["durum"] == "aktif"]
    review = [t for t in board if t["durum"] == "review"]
    bekliyor = [t for t in board if t["durum"] == "bekliyor"]
    done = [t for t in board if t["durum"] == "done"]
    tamamlandi = [t for t in board if t["durum"] == "tamamlandi"]
    iptal = [t for t in board if t["durum"] == "iptal"]

    p0_tasks = [t for t in board if t["oncelik"] == "P0"]
    p1_tasks = [t for t in board if t["oncelik"] == "P1"]

    return {
        "toplam": len(board),
        "todo": len(todo),
        "in_progress": len(in_progress),
        "aktif": len(aktif),
        "review": len(review),
        "bekliyor": len(bekliyor),
        "done": len(done),
        "tamamlandi": len(tamamlandi),
        "iptal": len(iptal),
        "p0_count": len(p0_tasks),
        "p1_count": len(p1_tasks),
        "todo_tasks": todo,
        "p0_tasks": p0_tasks,
        "p1_tasks": p1_tasks,
        "blocked_or_waiting": review + bekliyor,
    }


def log_sync(message: str, level: str = "INFO") -> None:
    """Senkronizasyon loguna yaz."""
    ts = get_istanbul_time().isoformat()
    log_entry = f"[{ts}] [{level}] {message}\n"

    with open(SYNC_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(log_entry.strip())


def generate_sync_report(analysis: dict[str, Any]) -> str:
    """Gunluk senkronizasyon raporu olustur."""
    now = get_istanbul_time()
    report = f"""# Gunluk Senkronizasyon Raporu
**Tarih:** {now.strftime('%Y-%m-%d')}
**Saat:** {now.strftime('%H:%M:%S')} Istanbul

## Gorev Durumu Ozeti

| Durum | Sayi |
|-------|------|
| TODO | {analysis['todo']} |
| In Progress | {analysis['in_progress']} |
| Aktif | {analysis['aktif']} |
| Review | {analysis['review']} |
| Bekliyor | {analysis['bekliyor']} |
| Done | {analysis['done']} |
| Tamamlandi | {analysis['tamamlandi']} |
| Iptal | {analysis['iptal']} |
| **Toplam** | **{analysis['toplam']}** |

## Oncelik Durumu

- **P0:** {analysis['p0_count']} gorev
- **P1:** {analysis['p1_count']} gorev

## Bloke/Bekleyen Gorevler

"""
    for task in analysis["blocked_or_waiting"]:
        report += f"- **{task['task_id']}** ({task['durum']}) - {task['baslik']}\n"

    if not analysis["blocked_or_waiting"]:
        report += "- Bloklu gorev yok [OK]\n"

    # Tetikleme listesi
    report += "\n## Tetikle (TODO > IN PROGRESS)\n\n"
    p0_p1_todos = [t for t in analysis["todo_tasks"] if t["oncelik"] in ["P0", "P1"]][:3]

    if p0_p1_todos:
        for task in p0_p1_todos:
            report += f"- [ ] **{task['task_id']}** (@{task['sahip']}) - {task['baslik']}\n"
    else:
        report += "- Tetiklenecek P0/P1 yok\n"

    return report


def main():
    """Ana senkronizasyon fonksiyonu."""
    try:
        istanbul_time = get_istanbul_time()
        hour = istanbul_time.hour

        log_sync(f"Senkronizasyon basladi (saat: {hour}:00 Istanbul)")

        # task_board.json oku
        board = load_task_board()
        log_sync(f"task_board.json okundu: {len(board)} gorev")

        # Gorevleri analiz et
        analysis = analyze_tasks(board)
        log_sync(
            f"Durum: {analysis['todo']} TODO, {analysis['in_progress']} IN PROGRESS, "
            f"{analysis['done']} DONE, {analysis['review']} REVIEW"
        )

        # Rapor olustur
        report = generate_sync_report(analysis)

        # Raporun kaydedilecegi dosya
        report_path = TASK_BOARD_PATH.parent / f"sync_rapor_{istanbul_time.strftime('%Y-%m-%d_%H-%M')}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        log_sync(f"Rapor kaydedildi: {report_path}")

        # Tetik onerileri
        if hour == 6:  # Sabah 09:00 (UTC 06:00)
            log_sync("SABAH SYNC: P0/P1 govrevleri tetikleyin", "TRIGGER")
            for task in analysis["p0_tasks"][:2]:
                log_sync(f"  - {task['task_id']} (@{task['sahip']})", "TRIGGER")

        elif hour == 11:  # Ögleden sonra 14:00 (UTC 11:00)
            log_sync("OGLEDEN SONRA: Midway progress kontrol", "TRIGGER")
            if analysis["in_progress"] > 0:
                log_sync(f"  - {analysis['in_progress']} gorev devam ediyor", "INFO")

        elif hour == 16:  # Aksam 19:00 (UTC 16:00)
            log_sync("AKSAM: Gunluk kapanisi kontrol", "TRIGGER")
            if analysis["done"] > 0:
                log_sync(f"  - {analysis['done']} gorev tamamlandi", "INFO")

        log_sync("Senkronizasyon tamamlandi [OK]")
        return 0

    except Exception as e:
        log_sync(f"Hata: {str(e)}", "ERROR")
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
