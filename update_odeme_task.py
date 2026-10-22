# -*- coding: utf-8 -*-
"""Update task status - mark ALTYAPI-ODEME-01 as done."""

import json
from pathlib import Path

TASK_BOARD = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json")

if TASK_BOARD.exists():
    with open(TASK_BOARD, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Mark ALTYAPI-ODEME-01 as done
    for item in data:
        if item.get("task_id") == "ALTYAPI-ODEME-01" or item.get("id") == "ALTYAPI-ODEME-01":
            item["durum"] = "done"
            break
    
    with open(TASK_BOARD, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Task board updated: ALTYAPI-ODEME-01 marked as done")
else:
    print("Task board not found")