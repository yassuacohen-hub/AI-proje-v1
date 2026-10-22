import os, re
B = "Huginn Data Insights"
def grep(path, pat, lim=12):
    p = os.path.join(B, path)
    if not os.path.exists(p):
        print("YOK:", path); return
    for i, l in enumerate(open(p, encoding="utf-8", errors="ignore"), 1):
        if re.search(pat, l):
            print(f"{path}:{i} | {l.rstrip()[:150]}"); lim -= 1
            if lim == 0: break
grep("src/company_master/api/routers/v1/network_router.py", r"@router|nodes|edges|kredi|derinlik")
print("--- sse")
grep("web_app.py", r"yield|signal|sinyal|sleep", 8)
print("--- cmdk")
grep("frontend/src/components/base_ui.tsx", r"cmdk|Command", 6)
print("--- panel brief")
grep("plans/brief_utku_UI-TICARIRADAR-PANEL-01.md", r"^## |SSE|Tremor|recharts|graf|network", 14)
