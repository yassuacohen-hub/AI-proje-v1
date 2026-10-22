import json
p = "c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/ajan-chat.jsonl"
n = 0
for l in open(p, encoding="utf-8-sig"):
    l = l.strip()
    if not l:
        continue
    try:
        r = json.loads(l)
    except Exception:
        continue
    if r.get("task_id") != "MUSTERI-PANEL-TASARIM-01":
        continue
    if r.get("durum") == "acik":
        print(n, r.get("kimden"), "->", r.get("ajan"), "|", str(r.get("sorun"))[:70].replace("\n", " "))
    n += 1
print("toplam kayit", n)
