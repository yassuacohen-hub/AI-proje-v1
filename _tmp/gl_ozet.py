import json
from pathlib import Path

r = json.loads(Path("_tmp/gl_rapor.json").read_text(encoding="utf-8"))
gercek = [x for x in r if x["Commit"].startswith("772a2937")]
yanlis = [x["Fingerprint"] for x in r if not x["Commit"].startswith("772a2937")]
p = Path("Huginn Data Insights/.gitleaksignore")
bas = [l for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("#")]
p.write_text("\n".join(bas + yanlis) + "\n", encoding="utf-8")
print("gercek:", len(gercek), "yanlis alarm susturuldu:", len(yanlis))
