import sys, json
sys.path.insert(0, "c:/Huginn Data Projesi/Huginn Data Insights/src")
from company_master.orchestrator import task_board as tb

T = "MUSTERI-PANEL-TASARIM-01"
p = tb.STATE_DIR / "chat" / "messages.jsonl"
print("dosya:", p)
n = 0
for i, l in enumerate(p.read_text(encoding="utf-8-sig").splitlines()):
    if not l.strip():
        continue
    try:
        r = json.loads(l)
    except Exception:
        continue
    if r.get("task_id") != T or r.get("yanit_alindi"):
        continue
    if r.get("kimden") == "ihsan" or r.get("kime") not in ("ihsan", "hepsi"):
        continue
    n += 1
    print(i, r.get("kimden"), r.get("kime"), r.get("type"), (r.get("mesaj") or "")[:110].replace("\n", " "))
print("toplam bloklayan:", n)
