import sys, io, json, re, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Huginn Data Projesi\Huginn Data Insights"

# 1. task board durumlari
tb_path = os.path.join(ROOT, "data", "orchestrator", "task_board.json")
tb = json.load(io.open(tb_path, encoding="utf-8-sig"))
gorevler = tb if isinstance(tb, list) else (tb.get("gorevler") or tb.get("tasks") or [])
for g in gorevler:
    tid = str(g.get("task_id") or g.get("id") or "")
    if tid in ("API-V1-COMPANY-FRAUD-01", "API-PAKET-SCOPE-01"):
        print("BOARD:", json.dumps(g, ensure_ascii=False)[:900])

# 2. web_app.py konumu
wa_path = None
for cand in (os.path.join(ROOT, "web_app.py"), r"C:\Huginn Data Projesi\web_app.py"):
    if os.path.isfile(cand):
        wa_path = cand
        break
print("WEB_APP:", wa_path)
wa = io.open(wa_path, encoding="utf-8", errors="replace").read().splitlines()
for a, b in ((396, 408), (195, 205), (3620, 3640)):
    print(f"--- web_app.py {a}-{b} ---")
    for i in range(a - 1, min(b, len(wa))):
        print(f"{i+1}: {wa[i]}")

# 3. imzalar
for i, line in enumerate(wa):
    if re.search(r"def (normalize_company|apply_kvkk_mask|_record_api_usage|scope_gerekli|kredi_dus)\b", line):
        print(f"DEF {i+1}: {line.strip()}")

# 4. routers dizini
rd = os.path.join(ROOT, "src", "company_master", "api", "routers")
print("ROUTERS:", os.listdir(rd) if os.path.isdir(rd) else "YOK")
