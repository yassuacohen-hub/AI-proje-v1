import sys, json
sys.path.insert(0, "c:/Huginn Data Projesi/Huginn Data Insights/src")
from company_master.orchestrator import task_board as tb

T = "MUSTERI-PANEL-TASARIM-01"
p = tb.STATE_DIR / "chat" / "messages.jsonl"
satirlar = p.read_text(encoding="utf-8-sig").split("\n")
n = 0
for i, l in enumerate(satirlar):
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
    if r.get("type") == "soru" and "Faz B-0 i18n" not in (r.get("mesaj") or ""):
        continue  # yalniz cevaplanan soru kapanir
    r["yanit_alindi"] = True
    satirlar[i] = json.dumps(r, ensure_ascii=False)
    n += 1
p.write_text("\n".join(satirlar), encoding="utf-8", newline="\n")
print("isaretlendi:", n)
