import json, re, os
P = "Huginn Data Insights/data/orchestrator/task_board.json"
d = json.load(open(P, encoding="utf-8"))
tasks = d["tasks"] if isinstance(d, dict) else d
kalan = [t for t in tasks if t.get("source") == "security_doc_analysis" and "KALICI" not in t.get("not", "")]
print("kalan hayalet:", len(kalan))
pats = {}
for t in kalan:
    m = re.search(r"Pattern: (.+?)(?: \||$)", t.get("not", ""))
    pat = m.group(1).strip() if m else ""
    pats[t["task_id"]] = pat
    print(f"- {t['task_id']} | {t['baslik'][:80]} | pat={pat}")
json.dump(pats, open("_tmp/hayalet_pats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("--- belgeler")
for f in ["yedekler/tasinma-rehberi-v3.md", "yedekler/güvenlik full.md", "yedekler/Altyapı alan adı pazarlama stratejimiz.docx", "_tmp/docx_metin.txt"]:
    print(f, os.path.exists(f), os.path.getsize(f) if os.path.exists(f) else "-")
