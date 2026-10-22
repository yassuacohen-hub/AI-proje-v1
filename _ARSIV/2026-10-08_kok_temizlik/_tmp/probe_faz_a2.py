import sys, io, os, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Huginn Data Projesi\Huginn Data Insights"

# 1. v1_router import kaynagi
wa_path = os.path.join(ROOT, "web_app.py")
wa = io.open(wa_path, encoding="utf-8", errors="replace").read().splitlines()
for i, line in enumerate(wa):
    if "v1_router" in line or "job_intelligence_router" in line and "import" in line:
        print(f"WA {i+1}: {line.strip()}")

# 2. routers/v1 neydir
rv = os.path.join(ROOT, "src", "company_master", "api", "routers", "v1")
print("v1 tipi:", "DIR" if os.path.isdir(rv) else ("FILE" if os.path.isfile(rv) else "YOK"))
if os.path.isdir(rv):
    print("v1 icerik:", os.listdir(rv))
elif os.path.isfile(rv):
    print("v1.py boyut:", os.path.getsize(rv))

# 3. normalize_company / apply_kvkk_mask / kredi_dus / scope_gerekli tanimlari
patt = re.compile(r"def (normalize_company|apply_kvkk_mask|kredi_dus|scope_gerekli)\b")
for base in ("src", "web_app.py"):
    if os.path.isfile(os.path.join(ROOT, base)):
        files = [os.path.join(ROOT, base)]
    else:
        files = []
        for dp, dn, fn in os.walk(os.path.join(ROOT, base)):
            if "__pycache__" in dp or ".venv" in dp:
                continue
            for f in fn:
                if f.endswith(".py"):
                    files.append(os.path.join(dp, f))
    for fp in files:
        try:
            txt = io.open(fp, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        for i, line in enumerate(txt):
            if patt.search(line):
                rel = os.path.relpath(fp, ROOT)
                print(f"DEF {rel}:{i+1}: {line.strip()}")

# 4. api paketi yapisi
api_dir = os.path.join(ROOT, "src", "company_master", "api")
for dp, dn, fn in os.walk(api_dir):
    if "__pycache__" in dp:
        continue
    rel = os.path.relpath(dp, ROOT)
    print("DIR:", rel, "| py:", sorted(f for f in fn if f.endswith(".py")))
