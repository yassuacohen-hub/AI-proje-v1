"""SCRAPE-004 ve review'daki 3 gorevin detayi: ne kaldi?"""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"

v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])

HEDEF = ["SCRAPE-004-QWEN-SINIFLANDIRMA", "ALTYAPI-9ROUTER-ANAHTAR-01",
         "VERI-PAKET-FIYAT-SENKRON-01", "ALTYAPI-GOREV-AT-KAPI-01",
         "ALTYAPI-MIMIR-BAGLAM-01"]

for g in gs:
    if g.get("id") in HEDEF:
        print("=" * 70)
        print(f"{g.get('id')}  [{g.get('durum')}]  ajan={g.get('ajan')}")
        print("=" * 70)
        for alan in ("baslik", "onem", "aciklama", "not", "ozet"):
            val = g.get(alan)
            if val:
                print(f"  {alan}: {str(val)[:400]}")
        gec = g.get("teslim_gecmisi")
        if gec:
            print(f"  teslim_gecmisi ({len(gec)}):")
            for t in (gec if isinstance(gec, list) else [gec]):
                print(f"     - {str(t)[:220]}")
        print()

print("=" * 70)
print("SCRAPE-004 ile ilgili dosyalar git'te ne durumda?")
print("=" * 70)
for f in ["scripts/kazima_qwen_classify.py", "tests/test_kazima_qwen_classify.py",
          "scripts/kazima_jina_fallback.py"]:
    p = KOK / f
    r = subprocess.run(["git", "log", "--oneline", "-2", "--", f],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(KOK), timeout=180)
    print(f"  {f}")
    print(f"    diskte: {p.is_file()}")
    print(f"    commit: {(r.stdout or '').strip() or '(hic)'}")
    r2 = subprocess.run(["git", "status", "--short", "--", f],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", cwd=str(KOK), timeout=180)
    if r2.stdout.strip():
        print(f"    calisma agacinda: {r2.stdout.strip()}")