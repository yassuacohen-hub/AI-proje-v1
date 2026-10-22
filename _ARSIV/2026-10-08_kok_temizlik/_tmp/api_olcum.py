import re, pathlib, sys
base = pathlib.Path("Huginn Data Insights")
for p in ["web_app.py", "src/company_master/api/routers/normalize.py",
          "src/company_master/auth/session.py", "src/company_master/kredi.py",
          "src/company_master/api/core/__init__.py", "src/company_master/api/__init__.py"]:
    f = base / p
    if not f.exists():
        print("YOK", p); continue
    s = f.read_text(encoding="utf-8").splitlines()
    print("==", p, len(s))
    for i, l in enumerate(s):
        if re.search(r"@(app|router)\.(get|post|put|delete)|APIRouter\(|include_router|^def |^class |require_api_key|KrediYetersiz|Jinja2Templates|HTMLResponse|templates", l):
            print(i + 1, l[:110])
print("templates dirs:", [str(x) for x in base.rglob("templates") if x.is_dir() and "node_modules" not in str(x) and ".venv" not in str(x)][:10])
print("tabs:", [x.name for x in (base / "web_dashboard/tabs").glob("*.py")])
