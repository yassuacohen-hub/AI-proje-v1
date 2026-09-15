#!/usr/bin/env python3
"""Print active tasks and assignments from the task board."""
import json
import sys
from collections import Counter

sys.path.insert(0, ".")

with open("data/orchestrator/task_board.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Toplam görev: {len(data)}")
print()

aktif = [t for t in data if t.get("durum") in ("plan', 'active", "in_progress")]