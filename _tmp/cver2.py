"""KESIN DOGRULAMA: teslim + commit gercekten dustu mu?"""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "SCRAPE-004-QWEN-SINIFLANDIRMA"


def p(*a):
    print(" ".join(str(x) for x in a), flush=True)


def git(*a, timeout=300):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


p("=== GIT ===")
_, c = git("log", "--oneline", "-4")
p("  " + c.replace("\n", "\n  "))
_, s = git("show", "--stat", "HEAD")
p("  HEAD:\n    " + s[:350].replace("\n", "\n    "))
_, st = git("status", "--short")
p(f"  calisma agaci: {st.strip() or '(temiz)'}")
d = git("cat-file", "-e", "HEAD:scripts/kazima_qwen_classify.py")[0] == 0
p(f"  dosya HEAD'de: {d}")

p("")
p("=== PANO ===")
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == T), {})
p(f"  {T}")
p(f"  durum    : {g.get('durum')}")
p(f"  ajan     : {g.get('ajan')}")
tg = g.get("teslim_gecmisi") or []
p(f"  teslim_gecmisi : {len(tg)} kayit")
for t in (tg if isinstance(tg, list) else [tg])[-2:]:
    p("    - " + str(t)[:260])

p("")
p("=== teslim ozetinde kanitlar var mi? ===")
metin = json.dumps(g, ensure_ascii=False)
for bayrak in ["22.7", "6/6", "V3", "5435", "keyring"]:
    p(f"  {bayrak!r:10s} -> {'VAR' if bayrak in metin else 'yok'}")