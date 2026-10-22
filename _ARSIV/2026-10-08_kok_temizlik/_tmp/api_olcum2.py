import re, pathlib, importlib.util
base = pathlib.Path("Huginn Data Insights")
print("routers:", [x.name for x in (base / "src/company_master/api/routers").iterdir()])
print("core:", [x.name for x in (base / "src/company_master/api/core").iterdir()])
print("jinja2:", importlib.util.find_spec("jinja2") is not None)
req = base / "requirements.txt"
if req.exists():
    print("req jinja/fastapi:", [l.strip() for l in req.read_text(encoding="utf-8").splitlines() if re.search(r"jinja|fastapi|starlette", l, re.I)])
# landing / ornek gorunum
for p in list(base.glob("web_dashboard/**/*.py")) + [base / "web_app.py"]:
    s = p.read_text(encoding="utf-8", errors="ignore")
    for i, l in enumerate(s.splitlines()):
        if re.search(r"landing|Örnek görünüm|Ornek gorunum|JSON-LD|ld\+json", l, re.I):
            print(p.relative_to(base), i + 1, l.strip()[:100])
# paketler tab _features
s = (base / "web_dashboard/tabs/paketler.py").read_text(encoding="utf-8").splitlines()
print("\n".join(f"{i+1} {l}" for i, l in enumerate(s[182:194])))
# static dir / dashboard index
print("static:", [str(x.relative_to(base)) for x in base.glob("*/index.html")][:5], [str(x.relative_to(base)) for x in base.glob("static*")])
# web_app.py lines 3535-3541 dashboard path
w = (base / "web_app.py").read_text(encoding="utf-8").splitlines()
print("\n".join(f"{i+1} {l}" for i, l in enumerate(w) if 3534 <= i <= 3541))
print("\n".join(f"{i+1} {l}" for i, l in enumerate(w) if 3626 <= i <= 3675))
print("\n".join(f"{i+1} {l}" for i, l in enumerate(w) if 198 <= i <= 234))
# source_registry osb
for p in base.glob("migrations/*.sql"):
    t = p.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"osb", t, re.I):
        print("osb goc:", p.name)
print("son goc:", sorted(x.name for x in base.glob("migrations/*.sql"))[-3:])
