#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Telegram periyodik durum mesaji.

task_board.json + data/kpi_raporu.md'yi okuyup belirli aralikla
Telegram'a durum ozeti gonderir.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.utils.telegram_bot import send_message

TASK_BOARD = ROOT / "data" / "orchestrator" / "task_board.json"
KPI_RAPORU = ROOT / "data" / "kpi_raporu.md"
INTERVAL = 30 * 60  # 30 dakika


def _read_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def board_ozet() -> str:
    board = _read_json(TASK_BOARD)
    if not isinstance(board, list):
        return ""
    aktif = [t for t in board if t.get("durum") not in ("done",)]
    tamamlanan = [t for t in board if t.get("durum") == "done"]
    lines = [
        "📋 <b>Gorev Panosu</b>",
        f"• Aktif: <b>{len(aktif)}</b>",
        f"• Tamamlanan: <b>{len(tamamlanan)}</b>",
    ]
    for t in aktif[:8]:
        lines.append(f"• {t['task_id']}: {t['baslik'][:40]} ({t['durum']})")
    return "\n".join(lines)


def kpi_ozet() -> str:
    if not KPI_RAPORU.exists():
        return "📊 KPI raporu bulunamadi."
    text = KPI_RAPORU.read_text(encoding="utf-8")
    lines = ["📊 <b>Veri Kalitesi KPI</b>"]
    for line in text.splitlines()[1:20]:
        if line.strip():
            lines.append(line.strip())
    return "\n".join(lines[:15])


def mesaj_olustur() -> str:
    return f"{board_ozet()}\n\n{kpi_ozet()}"


def main() -> int:
    print("Periyodik mesaj baslatildi. Ctrl+C ile durdur.")
    while True:
        try:
            send_message(mesaj_olustur())
        except Exception as exc:
            print(f"Mesaj gonderim hatasi: {exc}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Durduruldu.")
        sys.exit(0)
