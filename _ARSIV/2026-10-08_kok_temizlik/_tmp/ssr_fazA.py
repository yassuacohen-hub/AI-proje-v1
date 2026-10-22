import json, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
d = json.load(open(R / "data/orchestrator/task_board.json", encoding="utf-8"))
out = []
for g in d:
    if isinstance(g, dict) and g.get("task_id") in ("API-V1-COMPANY-FRAUD-01","API-PAKET-SCOPE-01","API-V1-NETWORK-REPORT-01"):
        out.append(f"{g.get('task_id'):28} | durum={g.get('durum')}")
# web_app.py halka acik /firma/ rotasi var mi
wapp = R / "web_app.py"
if wapp.exists():
    t = wapp.read_text(encoding="utf-8", errors="replace")
    out.append("web_app.py /firma/ rotasi: " + ("VAR" if "/firma/" in t or "@app.get(\"/firma" in t else "YOK"))
    out.append("web_app.py include_router sayisi: " + str(t.count("include_router")))
# api routers
routers = R / "src/company_master/api/routers"
out.append("routers py: " + str([p.name for p in routers.glob("*.py")] if routers.exists() else "YOK"))
pathlib.Path(r"c:\Huginn Data Projesi\_tmp\ssr_fazA.txt").write_text("\n".join(out), encoding="utf-8")
