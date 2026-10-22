import json, pathlib
p = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\chat\messages.jsonl")
rows = []
for l in p.read_text(encoding="utf-8-sig").splitlines():
    try:
        rows.append(json.loads(l))
    except Exception:
        pass
b = [r for r in rows if "bilo" in str(r.get("kimden", "")).lower() and "ihsan" in str(r.get("kime", r.get("to", ""))).lower()]
for r in b[-3:]:
    print("=====", r.get("zaman", r.get("ts")), r.get("task_id"), r.get("tur", r.get("type")))
    print(r.get("mesaj"))
