import json, os, time
R = r"c:/Huginn Data Projesi"
# 1) chat: utku'nun son mesajlari
p = R + "/Huginn Data Insights/data/orchestrator/chat/messages.jsonl"
rows = []
for l in open(p, encoding="utf-8", errors="ignore"):
    try:
        rows.append(json.loads(l))
    except Exception:
        pass
for r in [x for x in rows if "utku" in str(x.get("kimden", x.get("from", "")))][-4:]:
    print("CHAT", r.get("ts", r.get("zaman")), r.get("to", r.get("kime")), str(r.get("mesaj", ""))[:300].replace("\n", " "))
# 2) son 90 dk icinde degisen md/html dosyalari (hakem/utku ile ilgili)
now = time.time()
for base in (R, R + "/Huginn Data Insights"):
    for root, d, fs in os.walk(base):
        d[:] = [x for x in d if x not in (".git", "node_modules", "_ARSIV", ".next", "open-design", "Huginn Data Insights") or base.endswith("Insights")]
        if "node_modules" in root or ".git" in root:
            continue
        for f in fs:
            if "utku" in f.lower() and f.endswith((".md", ".txt", ".json")):
                fp = os.path.join(root, f)
                try:
                    a = (now - os.path.getmtime(fp)) / 60
                    if a < 120:
                        print("FILE", fp, os.path.getsize(fp), round(a), "dk once")
                except OSError:
                    pass
