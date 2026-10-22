import json, sys
p = "c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/ajan-chat.jsonl"
for i, l in enumerate(open(p, encoding="utf-8-sig")):
    l = l.strip()
    if not l:
        continue
    try:
        r = json.loads(l)
    except Exception:
        continue
    d = str(r.get("durum", r.get("status", "")))
    if d.lower() in ("acik", "açık", "open", "cozum_bekleniyor", "çözüm bekleniyor"):
        print(i, r.get("ajan", r.get("agent")), r.get("task_id"), d, "|", str(r.get("sorun", r.get("mesaj", r.get("mesaj_text", ""))))[:110].replace("\n", " "))
