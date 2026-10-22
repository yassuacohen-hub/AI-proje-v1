import sys, json, collections
sys.path.insert(0, "c:/Huginn Data Projesi/Huginn Data Insights/src")
from company_master.orchestrator import task_board as tb

T = "MUSTERI-PANEL-TASARIM-01"
p = tb.STATE_DIR / "chat" / "messages.jsonl"
tur = collections.Counter()
out = []
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
    m = r.get("mesaj") or ""
    dold = m.startswith("ORTAK TASARIM 4.1 utku DOLDU")
    tur[(r.get("kimden"), r.get("type"), dold)] += 1
    if not dold:
        out.append(f"#### satir={i} kimden={r.get('kimden')} tur={r.get('type')} tarih={r.get('tarih')}\n{m}\n")
out.append(str(dict(tur)))
open("c:/Huginn Data Projesi/_tmp/msg_bak2.out.md", "w", encoding="utf-8").write("\n".join(out))
print("ok", len(out))
