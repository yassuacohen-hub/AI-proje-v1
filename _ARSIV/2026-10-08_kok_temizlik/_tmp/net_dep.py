import json, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = pathlib.Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
d = json.load(open(R / "data/orchestrator/task_board.json", encoding="utf-8"))
out = []
for g in d:
    if isinstance(g, dict) and g.get("task_id") in ("API-PAKET-SCOPE-01","API-V1-COMPANY-FRAUD-01","VERI-ENTITY-GRAPH-01"):
        out.append(f"{g.get('task_id'):28} | durum={g.get('durum')} | atanan={g.get('atanan')}")
out.append("scope.py " + ("VAR" if (R/"src/company_master/api/scope.py").exists() else "YOK"))
out.append("v1_network.py " + ("VAR" if (R/"src/company_master/api/routers/v1_network.py").exists() else "YOK"))
pathlib.Path(r"c:\Huginn Data Projesi\_tmp\net_dep.txt").write_text("\n".join(out), encoding="utf-8")
