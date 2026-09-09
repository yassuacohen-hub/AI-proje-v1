#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Harici ajan sonuç toplama scripti.

Her ajanin output/ dizinindeki ciktilari okur,
AGENT_SYNC.md'ye ekler, task_board.json'u gunceller.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_DIR = ROOT / "workspace" / "external"
STATE_DIR = ROOT / "data" / "orchestrator"
TASK_BOARD = STATE_DIR / "task_board.json"
AGENT_SYNC = ROOT / "AGENT_SYNC.md"
ERROR_LEDGER = STATE_DIR / "error_ledger.json"

AJANLAR = ["harici_ajan", "copilot", "claude_code", "cursor_grok"]


def _read_json(path: Path):
    if not path.exists():
        return {} if path.name.endswith(".json") else []
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _output_files(ajan_id: str) -> list[Path]:
    out = EXTERNAL_DIR / ajan_id / "output"
    if not out.exists():
        return []
    return sorted(out.rglob("*"))


def _board_guncelle(task_id: str, durum: str, not_: str = "") -> None:
    board = _read_json(TASK_BOARD)
    if not isinstance(board, list):
        board = []
    for t in board:
        if t.get("task_id") == task_id:
            t["durum"] = durum
            if not_:
                t["not"] = not_
            if durum in ("done", "blocked"):
                t["bitis"] = datetime.now().isoformat(timespec="seconds")
            _write_json(TASK_BOARD, board)
            return


def _error_ledger_guncelle(ajan_id: str, gorev_id: str, hata: str) -> None:
    ledger = _read_json(ERROR_LEDGER)
    if not isinstance(ledger, list):
        ledger = []
    ledger.append({
        "tarih": datetime.now().isoformat(timespec="seconds"),
        "ajan": ajan_id,
        "gorev_id": gorev_id,
        "hata": hata,
    })
    _write_json(ERROR_LEDGER, ledger)


def topla() -> None:
    for ajan_id in AJANLAR:
        files = _output_files(ajan_id)
        if not files:
            continue

        for f in files:
            if f.is_file():
                print(f"[{ajan_id}] {f.relative_to(EXTERNAL_DIR / ajan_id)}")

        _board_guncelle(
            task_id=ajan_id,
            durum="done",
            not_=f"{len(files)} dosya output/ altinda uretildi",
        )
        print(f"[{ajan_id}] task_board guncellendi: done")


if __name__ == "__main__":
    topla()
