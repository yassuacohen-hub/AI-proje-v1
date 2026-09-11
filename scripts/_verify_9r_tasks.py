#!/usr/bin/env python3
"""9R-02/03/04 gorev + kilit durumu dogrulama (pano, file_locks, AGENT_SYNC)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "data/orchestrator/task_board.json"
LOCKS = ROOT / "data/orchestrator/file_locks.json"

board = json.loads(BOARD.read_text(encoding="utf-8"))
locks = json.loads(LOCKS.read_text(encoding="utf-8"))

print("=== Pano: 9R gorevleri ===")
for t in board:
    if t["task_id"].startswith("9R"):
        print(f"{t['task_id']} | {t['durum']} | {t['sahip']} | {t['baslik'][:70]}")

print("\n=== file_locks: 9R dosyalari ===")
hedef = {
    "src/company_master/vector/",
    "src/company_master/entity_resolution/matcher.py",
    "scripts/index_companies.py",
    "requirements-app.txt",
    "tests/vector/",
    "src/company_master/intelligence/job_intelligence/pipeline/analyzer.py",
    "src/company_master/gateway/ninerouter_client.py",
}
for f in sorted(hedef):
    lock = locks.get(f)
    print(f"{'KILITLI' if lock else 'BOS    '} | {f}" + (f" | {lock['sahip']}/{lock['task_id']}" if lock else ""))

aktif = [t["task_id"] for t in board if t["durum"] == "aktif"]
print("\n=== Aktif gorevler ===")
print(", ".join(aktif))