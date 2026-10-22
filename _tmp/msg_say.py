import json, sys
p = "data/orchestrator/chat/messages.jsonl"
L = [l for l in open(p, encoding="utf-8-sig") if l.strip()]
ids, bad = [], 0
for l in L:
    try:
        ids.append(json.loads(l).get("id"))
    except Exception:
        bad += 1
print("satir", len(L), "benzersiz_id", len(set(ids)), "bozuk", bad)
