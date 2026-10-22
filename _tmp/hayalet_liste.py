import json, os
B = "Huginn Data Insights"
p = os.path.join(B, "data/orchestrator/task_board.json")
d = json.load(open(p, encoding="utf-8"))
tasks = d if isinstance(d, list) else d.get("tasks", d.get("gorevler", []))
for t in tasks:
    s = json.dumps(t, ensure_ascii=False)
    if "security_doc_analysis" in s or t.get("id", "").endswith(("-010", "-011")) or "hayalet" in (t.get("not") or "").lower() and t.get("durum") == "archive" and "2026-10" in s:
        dos = t.get("dosyalar") or []
        var = [f for f in dos if os.path.exists(os.path.join(B, f))]
        print(t.get("id"), "|", t.get("durum"), "|", t.get("atanan") or t.get("assignee"), "|", t.get("oncelik"))
        print("   baslik:", t.get("baslik"))
        print("   dosyalar:", dos, "-> var:", var)
        print("   brif:", t.get("brif") or t.get("brief"), "| not:", (t.get("not") or "")[:200])
