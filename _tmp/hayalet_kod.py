import json, glob, os, re
B = "Huginn Data Insights"
# brif iceriği: hepsi placeholder mı?
for p in glob.glob(os.path.join(B, "plans", "brief_utku_*-0[0-1][0-9].md")):
    s = open(p, encoding="utf-8").read()
    print(os.path.basename(p), "| placeholder:", "D-66 ihlali" in s, "| satir:", s.count("\n"))
# frontend bagimliliklari
pk = json.load(open(os.path.join(B, "frontend/package.json"), encoding="utf-8"))
deps = {**pk.get("dependencies", {}), **pk.get("devDependencies", {})}
for k in ["next", "@tremor/react", "cmdk", "reactflow", "@xyflow/react", "shadcn", "@radix-ui/react-dialog", "recharts"]:
    print("dep", k, "=", deps.get(k))
# kod icinde SSE / escrow / webhook sinyal / enterprise
for pat, roots in [("EventSource|text/event-stream", ["web_app.py", "web_dashboard", "frontend/src", "frontend/app"]),
                   ("escrow|tahkim", ["web_app.py", "src", "web_dashboard"]),
                   ("sinyal.*kredi|signal.*credit", ["web_app.py", "src", "web_dashboard"]),
                   ("enterprise", ["web_dashboard/tabs/paketler.py", "src"])]:
    hits = set()
    for r in roots:
        rp = os.path.join(B, r)
        files = [rp] if os.path.isfile(rp) else [os.path.join(d, f) for d, _, fs in os.walk(rp) for f in fs if f.endswith((".py", ".ts", ".tsx")) and "node_modules" not in d]
        for f in files:
            try:
                if re.search(pat, open(f, encoding="utf-8", errors="ignore").read(), re.I):
                    hits.add(os.path.relpath(f, B))
            except OSError:
                pass
    print("PAT", pat, "->", len(hits), sorted(hits)[:8])
