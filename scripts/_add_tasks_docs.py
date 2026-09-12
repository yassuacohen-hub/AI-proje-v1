#!/usr/bin/env python3
"""DOC-02, DASH-04, DASH-05 görevlerini panoya ekler."""
import json, sys
from pathlib import Path
from datetime import datetime

TASK_BOARD = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json")
TODO_MD = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\AI proje v1/V10/TODO.md")

def load_board():
    if TASK_BOARD.exists():
        data = json.loads(TASK_BOARD.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            return {"tasks": data}
    return {"tasks": []}

def save_board(board):
    TASK_BOARD.write_text(json.dumps(board["tasks"], indent=2, ensure_ascii=False), encoding="utf-8")

def add_task(board, task):
    board["tasks"].append({
        "task_id": task["task_id"],
        "title": task["title"],
        "owner": task["owner"],
        "mod": task["mod"],
        "priority": task.get("priority", "P2"),
        "status": "plan",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "not": task.get("not", ""),
        "dependencies": task.get("dependencies", [])
    })
    return board

def append_todo(task):
    line = f"- [ ] {task['task_id']} ({task['priority']}): {task['title']} — sahibi: {task['owner']} ({task['mod']})"
    if TODO_MD.exists():
        content = TODO_MD.read_text(encoding="utf-8")
        if line not in content:
            TODO_MD.write_text(content + "\n" + line + "\n", encoding="utf-8")
    else:
        TODO_MD.write_text("# TODO\n\n" + line + "\n", encoding="utf-8")

tasks = [
    {"task_id": "DOC-02", "title": "Decision Log mekanizmasini kur", "owner": "mimari", "mod": "architect", "priority": "P1", "not": "data/orchestrator/decision_log.jsonl", "dependencies": []},
    {"task_id": "DASH-04", "title": "Hybrid Admin Panel - API client + DB fallback", "owner": "mimar", "mod": "architect", "priority": "P1", "not": "api_client.py, db_reader.py, .streamlit/config.toml", "dependencies": ["DOC-02"]},
    {"task_id": "DASH-05", "title": "Admin Panel Karar Defteri sekmesi", "owner": "mimar", "mod": "architect", "priority": "P1", "not": "tabs/admin_panel.py icinde karar tab'i", "dependencies": ["DOC-02", "DASH-04"]}
]

if __name__ == "__main__":
    board = load_board()
    for t in tasks:
        board = add_task(board, t)
        append_todo(t)
    save_board(board)
    print("Görevler eklendi:")
    for t in tasks:
        print(f"  {t['task_id']}: {t['title']}")
    print(f"\nToplam görev: {len(board['tasks'])}")
