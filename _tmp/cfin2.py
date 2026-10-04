"""SCRAPE-004 son: regresyon -> commit -> teslim."""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "SCRAPE-004-QWEN-SINIFLANDIRMA"


def git(*a, timeout=900):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


print("=" * 68)
print("1) TAM REGRESYON (filtresiz)")
print("=" * 68)
r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
                    "-p", "no:cacheprovider"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=900)
for l in (r.stdout or "").strip().splitlines()[-4:]:
    print("  " + l[:95])
print(f"  rc = {r.returncode}")
if r.returncode != 0:
    print("\n  !! REGRESYON - COMMIT/TESLIM ATLANDI")
    sys.exit(1)

print()
print("2) COMMIT")
print("=" * 68)
git("add", "--", "scripts/kazima_qwen_classify.py")
rc, staged = git("diff", "--cached", "--stat")
print("  " + (staged or "(bos)").replace("\n", "\n  "))
mesaj = (
    "perf(kazima): anahtar onbellegi - SCRAPE-004 madde 5 p95<2sn (D-338)\n\n"
    "keyring her sinifla_etiket() cagrisinda soruluyordu. _anahtar_bir() eklendi:\n"
    "ilk cagrida keyring/env'den okur, sonra onbellekten verir. Kullanim yerleri\n"
    "sat 131 (_evren_bir_model_dene) ve sat 357 (sinifla_etiket).\n\n"
    "OLCUM (n=45, soguk cagri haric): p95 = 22.7 ms (esik 2000 ms).\n"
    "  V1 22.7 | V3 20.9 | kaynak='' 21.5 ms. Tek seferlik soguk keyring 2327 ms.\n\n"
    "6/6 kabul maddesi kanitlandi: sat 107, 118/139-141/233-234, 69, 313-315/331-332,\n"
    "bu commit, 358. Tam regresyon yesil.\n\n"
    "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
)
if "kazima_qwen_classify.py" in staged and staged.count(".py") == 1:
    rc, c = git("commit", "-m", mesaj)
    print(f"\n  commit rc={rc}")
    print("  " + c.replace("\n", "\n  ")[:900])
else:
    print("  beklenmedik staged -> ATLANDI")

print()
print("3) TESLIM")
print("=" * 68)
ozet = (
    "6/6 KABUL MADDESI KANITLANDI + MADDE 5 DUZELTILDI. Kanit kodu c63e55a4'te "
    "commit'liydi ama pano 'devam' da kalmisti, teslim hic yapilmamisti. "
    "MADDE 5 GERCEKTEN KALDIYDI: keyring her sinifla_etiket() cagrisinda "
    "soruluyordu; _anahtar_bir() onbellegi eklendi (sat 131 ve 357 kullanim). "
    "OLCUM (n=45, isinma haric): V1 p95=22.7ms, V3 p95=20.9ms, kaynak='' "
    "p95=21.5ms, birlestirilmis p95=22.7ms; esik 2000ms -> 88 kat pay. Tek "
    "seferlik soguk keyring 2327ms. MADDE 4 V3 KAPISI: kaynak=='V3' ise "
    "etiket_bos + gerekce donuyor, etiket YAZILMIYOR - ODIN K3/K4 kapisiyla "
    "celismiyor. Diger kanitlar: madde 1 sat 107 find_similar, madde 2 sat "
    "118/139-141/233-234, madde 3 sat 69 NACE maskeleme, madde 6 sat 358 "
    "__main__. Tam regresyon yesil. DURUST NOT: ilk olcumum p95=2327ms 'KALDI' "
    "dedi; sebep kod degil olcum hatasi - tek yavas cagri ilk soguk cagriydi."
)
rr = subprocess.run(
    [sys.executable, "scripts/gorev_kutusu.py", "teslim", "--ajan", "yasu",
     "--task-id", T, "--ozet", ozet],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=300)
print(f"  rc={rr.returncode}")
print("  " + ((rr.stdout or "") + (rr.stderr or "")).strip()[:400].replace("\n", "\n  "))

print()
print("4) DOGRULAMA")
print("=" * 68)
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == T), {})
print(f"  durum={g.get('durum')} ajan={g.get('ajan')} "
      f"teslim_gecmisi={len(g.get('teslim_gecmisi') or [])}")
rc, s = git("status", "--short")
print(f"  calisma agaci: {s.strip() or '(temiz)'}")
rc, c = git("log", "--oneline", "-3")
print("  " + c.replace("\n", "\n  "))