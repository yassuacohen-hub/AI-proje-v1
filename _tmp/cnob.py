"""YASU'YA ATANMIS IS VAR MI — butun kanallar (nobet=0 is var)."""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"


def sh(*a, timeout=600):
    r = subprocess.run([sys.executable, *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "").strip())


print("=" * 68)
print("1) NOBET — tek yoklama (cikis kodu 0 = IS VAR, D-335)")
print("=" * 68)
rc, c = sh("scripts/gorev_kutusu.py", "nobet", "--ajan", "yasu")
print(f"  rc = {rc}   {'*** IS VAR ***' if rc == 0 else '(is yok)'}")
print("  " + c.strip()[:1500].replace("\n", "\n  "))

print()
print("=" * 68)
print("2) POSTA KUTUSU — bak --ajan yasu")
print("=" * 68)
rc, c = sh("scripts/gorev_kutusu.py", "bak", "--ajan", "yasu")
print(f"  rc = {rc}")
print("  " + c.strip()[:1800].replace("\n", "\n  "))

print()
print("=" * 68)
print("3) ONAY BEKLEYEN (benden teslim bekleyenler)")
print("=" * 68)
rc, c = sh("scripts/gorev_kutusu.py", "onay-bekleyen")
print(f"  rc = {rc}")
print("  " + c.strip()[:900].replace("\n", "\n  "))

print()
print("=" * 68)
print("4) PANODA ajan=yasu OLAN HER GOREV (her durum)")
print("=" * 68)
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
benim = [g for g in gs if g.get("ajan") == "yasu"]
print(f"  toplam {len(benim)}")
for g in benim:
    print(f"    [{g.get('durum'):9s}] {g.get('id'):<34s} onem={g.get('onem')}")

print()
print("=" * 68)
print("5) TRIGGER KUYRUGU + ZINCIR (bekleyen tetikler)")
print("=" * 68)
try:
    sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
    from company_master.orchestrator import trigger
    bek = trigger.bekleyen_tetikler("yasu")
    print(f"  bekleyen tetrikler: {len(bek)}")
    for k in bek:
        print(f"    {k}")
    zinc = trigger.zincir_kalan("yasu")
    print(f"  zincir kalan: {len(zinc)}")
    for k in zinc:
        print(f"    {k}")
except Exception as e:
    print(f"  HATA: {type(e).__name__}: {e}")

print()
print("=" * 68)
print("6) SON COMMITLER — ihsan yeni dosya/gorev eklemis mi?")
print("=" * 68)
r = subprocess.run(["git", "log", "--oneline", "-6"], capture_output=True,
                   text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=300)
print("  " + (r.stdout or "").strip().replace("\n", "\n  "))
r = subprocess.run(["git", "log", "-3", "--name-only", "--format=%h %s"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=str(KOK), timeout=300)
print("\n  son 3 commitin dosyalari:")
for l in (r.stdout or "").splitlines():
    if l.strip():
        print("   ", l[:95])