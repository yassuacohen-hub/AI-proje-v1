import json, os, re, glob
B = "Huginn Data Insights"
d = json.load(open(os.path.join(B, "data/orchestrator/task_board.json"), encoding="utf-8"))
ids = ["UI-TICARIRADAR-PANEL-01", "API-V1-NETWORK-REPORT-01", "ALTYAPI-ODEME-01", "ODEME-KREDI-KILIDI-01",
       "ALTYAPI-KREDI-CUZDANI-01", "VERI-ENTITY-GRAPH-01", "ALTYAPI-KONG-MULTISITE-01", "UI-FIRMAARAMA-SEARCH-01"]
for t in d:
    if t.get("task_id") in ids:
        print(t["task_id"], "|", t.get("durum"), "|", t.get("sahip"), "|", t.get("oncelik"), "|", t.get("baslik")[:110])
        print("    dosyalar:", t.get("dosyalar"), "| son:", (t.get("son_durum") or t.get("not") or "")[:120])
print("--- strateji taramasi")
for pat in ["escrow", "tahkim", "Kurumsal.*USD|Kurumsal.*TL|Kurumsal.*\\$", "650", "UBO.*graf|ağ grafiği|network", "SSE|canlı sinyal", "komut paleti|cmdk|spotlight"]:
    hits = []
    for f in glob.glob(os.path.join(B, "docs/strateji/*.md")):
        for i, l in enumerate(open(f, encoding="utf-8", errors="ignore"), 1):
            if re.search(pat, l, re.I):
                hits.append(f"{os.path.basename(f)}:{i}")
    print(pat, "->", len(hits), hits[:6])
