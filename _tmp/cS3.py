"""HEDEFLI REGRESYON (var olan dosyalar) + COMMIT + TESLIM."""
import json
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "SCRAPE-004-QWEN-SINIFLANDIRMA"
ADAY = ["test_kazima_qwen_classify.py", "test_yazma_kapisi.py",
        "test_odin_kacak_olcer.py", "test_gorev_at_kilit_kapisi.py"]
KUME = [f"tests/{a}" for a in ADAY if (KOK / "tests" / a).is_file()]


def p(*a):
    print(" ".join(str(x) for x in a), flush=True)


def git(*a, timeout=600):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


p(f"KUME = {KUME}")
LIVE = None
tv = (KOK / "tests" / "test_kazima_qwen_classify.py").read_text(
    encoding="utf-8", errors="replace")
for l in tv.splitlines():
    if "def test_kazima_qwen_classify_calisir" in l:
        LIVE = "tests/test_kazima_qwen_classify.py::test_kazima_qwen_classify_calisir"
p(f"canli test = {LIVE}")

args = [sys.executable, "-m", "pytest", *KUME, "-q", "--no-header",
        "-p", "no:cacheprovider", "--tb=line", "-rf"]
if LIVE:
    args += ["--deselect", LIVE]
p("")
p("=== 1) HEDEFLI REGRESYON ===")
t0 = time.time()
r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=str(KOK), timeout=600)
out = r.stdout or ""
p(f"  sure={time.time()-t0:.0f}s rc={r.returncode}")
for l in [x for x in out.strip().splitlines() if x.strip()][-4:]:
    p("  " + l[:100])
kir = [x.strip() for x in out.splitlines() if x.startswith("FAILED")]
p(f"  kirilan: {len(kir)}")
for l in kir:
    p("    " + l[:110])
kirl = "; ".join(x[:70] for x in kir) or "yok"

p("")
p("=== 2) COMMIT ===")
git("add", "--", "scripts/kazima_qwen_classify.py")
_, staged = git("diff", "--cached", "--stat")
p("  " + (staged or "(bos)").replace("\n", "\n  "))
if "kazima_qwen_classify.py" in staged and staged.count(".py") == 1:
    _, c = git("commit", "-m",
        "perf(kazima): anahtar onbellegi - SCRAPE-004 madde 5 p95<2sn\n\n"
        "keyring her sinifla_etiket() cagrisinda soruluyordu. _anahtar_bir() eklendi:\n"
        "ilk cagrida keyring/env'den okur, sonra onbellekten verir. Kullanim:\n"
        "sat 131 (_evren_bir_model_dene), sat 357 (sinifla_etiket).\n\n"
        "OLCUM (n=15, isinma haric): p95 = 22.7 ms (esik 2000 ms).\n"
        "6/6 SCRAPE-004 kabul maddesi kanitlandi: sat 107, 118/139-141/233-234,\n"
        "69, 313-315/331-332 (V3 kapisi), 358.\n\n"
        "Regresyon: degisen dosyaya ait hedefli kume (" + ", ".join(KUME) + ").\n"
        "Tam paket 5435 test (test_i18n.py tek basina 1413) ve saatlerce suruyor.\n"
        "Dislanan canli test: test_kazima_qwen_classify_calisir.\n"
        f"Kalan kirilan: {kirl}.\n\n"
        "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    p("  " + c.replace("\n", "\n  ")[:700])
else:
    p("  staged bekenmedik -> ATLANDI")

p("")
p("=== 3) TESLIM ===")
ozet = (
    "TESLIM. 6/6 KABUL MADDESI KANITLANDI + MADDE 5 DUZELTILDI. Kanit kodu "
    "c63e55a4'te commit'liydi, pano 'devam' da kalmisti. MADDE 5 GERCEKTEN "
    "KALDIYDI: keyring her sinifla_etiket() cagrisinda soruluyordu; _anahtar_bir() "
    "onbellegi eklendi (sat 131, 357). OLCUM (n=15, isinma haric): p95=22.7 ms, "
    "esik 2000 ms. MADDE 4 V3 KAPISI: kaynak=='V3' ise etiket_bos + gerekce "
    "donuyor, etiket YAZILMIYOR - ODIN K3/K4 kapisiyla celismiyor. Kanitlar: "
    "m1 sat 107, m2 sat 118/139-141/233-234, m3 sat 69, m6 sat 358. "
    "REGRESYON KAPSAMI DUZELTILDI: tam paket 5435 test (test_i18n.py tek basina "
    "1413) ve saatlerce suruyor; onceki 'regresyon yesil' iddialarim -k filtreli "
    "alt kume sanilmis. Bu teslimde hedefli kume kosuldu (" + ", ".join(KUME) +
    f"): kirilan: {kirl}. Canli test ag/anahtar bagimli, dislandi. ONERI: "
    "pytest.ini'de 'canli' isareti + varsayilan -m 'not canli'."
)
rr = subprocess.run([sys.executable, "scripts/gorev_kutusu.py", "teslim", "--ajan",
                     "yasu", "--task-id", T, "--ozet", ozet],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=str(KOK), timeout=300)
p(f"  rc={rr.returncode}")
p("  " + ((rr.stdout or "") + (rr.stderr or "")).strip()[:350].replace("\n", "\n  "))

p("")
p("=== 4) DOGRULAMA ===")
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == T), {})
p(f"  durum={g.get('durum')} teslim_gecmisi={len(g.get('teslim_gecmisi') or [])}")
_, s = git("status", "--short")
p(f"  calisma agaci: {s.strip() or '(temiz)'}")
_, c = git("log", "--oneline", "-3")
p("  " + c.replace("\n", "\n  "))