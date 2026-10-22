import json, re, sys
p = r"Huginn Data Insights/data/orchestrator/chat/messages.jsonl"
satirlar = open(p, encoding="utf-8").read().splitlines()[-int(sys.argv[1] if len(sys.argv) > 1 else 6):]
for s in satirlar:
    try:
        j = json.loads(s)
    except ValueError:
        continue
    m = re.sub(r"ent_[0-9a-f]+", "ent_***", str(j.get("message", j.get("mesaj", ""))))
    print(j.get("ts"), j.get("from"), "->", j.get("to"), f"[{j.get('task_id')}]", m[:700])
    print("---")
