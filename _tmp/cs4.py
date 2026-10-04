"""SCRAPE-004 hizli envanter: dosya var mi, icerigi ne, V3 kapisi kacinci madde?"""
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEDEF = [
    "scripts/kazima_qwen_classify.py",
    "src/company_master/etl/kazima_qwen_classify.py",
    "scripts/kazima_jina_fallback.py",
    "tests/test_kazima_qwen_classify.py",
]
print("=== 1) DOSYA VARLIĞI ===")
for f in HEDEF:
    p = KOK / f
    print(f"  {f:48s} {'VAR '+str(p.stat().st_size)+'b' if p.is_file() else 'YOK'}")
r = subprocess.run(["git", "log", "--oneline", "-3", "--name-only", "--format=--%h %s"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=200)
print("\n=== 2) qwen/classify geçen commitler ===")
for l in (r.stdout or "").splitlines():
    if "qwen" in l.lower() or "classify" in l.lower() or "kazima" in l.lower() or l.startswith("--"):
        print("  " + l.strip()[:90])

p = KOK / "scripts" / "kazima_qwen_classify.py"
if p.is_file():
    sat = p.read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"\n=== 3) ICERIK ({len(sat)} satir) ===")
    for n, l in enumerate(sat, 1):
        print(f"  {n:3d}: {l[:100]}")
else:
    print("\n=== 3) kod yok — yazilacak ===")
    for f in ["src/company_master/etl", "scripts"]:
        d = KOK / f
        print(f"  {f}: {len(list(d.glob('kazima*')))} kazima* dosyasi")
        for x in sorted(d.glob("kazima*")):
            print(f"      {x.name}")

print("\n=== 4) V3/etiket kapisi referanslari (tum kodda) ===")
r = subprocess.run(["grep", "-rn", "--include=*.py", "-e", "etiket_bos",
                    "-e", "musteri_id", str(KOK / "scripts"), str(KOK / "src")],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", timeout=200)
for l in [x for x in (r.stdout or "").splitlines() if ".venv" not in x][:25]:
    print("  " + l.replace(str(KOK), "")[:100])