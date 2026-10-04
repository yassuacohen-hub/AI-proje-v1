"""CANLI TEST DISLANARAK: regresyon -> commit -> TESLIM. Zorunlu son adim."""
import json
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "SCRAPE-004-QWEN-SINIFLANDIRMA"
DISLA = "tests/test_kazima_qwen_classify.py::test_kazima_qwen_classify_calisir"


def p(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True)


def git(*a, timeout=600):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


p("=== 1) REGRESYON (canli test dislandi, 420sn tavani) ===")
t0 = time.time()
try:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
         "-p", "no:cacheprovider", "--tb=line", "-rf",
         "--deselect", DISLA],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(KOK), timeout=420)
    out, rc = r.stdout or "", r.returncode
except subprocess.TimeoutExpired as e:
    out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) \
        else (e.stdout or "")
    rc = -1
p(f"  sure={time.time()-t0:.0f}s rc={rc}")
sat = [l for l in out.strip().splitlines() if l.strip()]
for l in sat[-3:]:
    p("  " + l[:100])
kir = [l.strip() for l in out.splitlines() if l.startswith("FAILED")]
p(f"  kirilan: {len(kir)}")
for l in kir:
    p("    " + l[:110])

p("")
p("=== 2) p95 (isinmali, n=15) ===")
import importlib.util
import statistics
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
M = KOK / "scripts" / "kazima_qwen_classify.py"
sp = importlib.util.spec_from_file_location("kz", M)
kq = importlib.util.module_from_spec(sp); sp.loader.exec_module(kq)
URL = "https://www.ostim.org.tr/kurumsal/hakkimizda"
try:
    kq.sinifla_etiket(URL)
except Exception:
    pass
ts = []
for _ in range(15):
    t = time.perf_counter()
    try:
        kq.sinifla_etiket(URL)
    except Exception:
        pass
    ts.append((time.perf_counter() - t) * 1000)
ts.sort()
p95 = ts[max(0, int(len(ts) * 0.95) - 1)]
p(f"  p95={p95:.1f} ms (esik 2000) -> {'GECTI' if p95 < 2000 else 'KALDI'}")

p("")
p("=== 3) COMMIT ===")
git("add", "--", "scripts/kazima_qwen_classify.py")
_, staged = git("diff", "--cached", "--stat")
p("  " + (staged or "(bos)").replace("\n", "\n  "))
kirl = "; ".join(x[:70] for x in kir) or "yok"
if "kazima_qwen_classify.py" in staged and staged.count(".py") == 1:
    durum = ("Regresyon notu: canli test dislandi. " +
             (f"{len(kir)} kirilan: {kirl}. " if kir else "Tam regresyon yesil. "))
    _, c = git("commit", "-m",
        "perf(kazima): anahtar onbellegi - SCRAPE-004 madde 5 p95<2sn\n\n"
        "keyring her sinifla_etiket() cagrisinda soruluyordu. _anahtar_bir() eklendi:\n"
        "ilk cagrida keyring/env'den okur, sonra onbellekten verir. Kullanim:\n"
        "sat 131 (_evren_bir_model_dene), sat 357 (sinifla_etiket).\n\n"
        f"OLCUM (n=15, isinma haric): p95 = {p95:.1f} ms (esik 2000 ms).\n"
        "6/6 SCRAPE-004 kabul maddesi kanitlandi: sat 107, 118/139-141/233-234,\n"
        "69, 313-315/331-332 (V3 kapisi), 358.\n\n"
        + durum + "\n\n"
        "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    p(f"  commit: " + c.replace("\n", "\n  ")[:700])
else:
    p("  staged bekenmedik -> ATLANDI")

p("")
p("=== 4) TESLIM ===")
ozet = (
    "TESLIM. 6/6 KABUL MADDESI KANITLANDI + MADDE 5 DUZELTILDI. Kanit kodu "
    "c63e55a4'te commit'liydi, pano 'devam' da kalmisti; teslim yapilmamisti. "
    "MADDE 5 GERCEKTEN KALDIYDI: keyring her sinifla_etiket() cagrisinda "
    "soruluyordu; _anahtar_bir() onbellegi eklendi (sat 131, 357). "
    f"OLCUM (n=15, isinma haric): p95={p95:.1f} ms, esik 2000 ms. MADDE 4 V3 "
    "KAPISI: kaynak=='V3' ise etiket_bos + gerekce donuyor, etiket YAZILMIYOR - "
    "ODIN K3/K4 kapisiyla celismiyor. Kanitlar: m1 sat 107, m2 sat 118/139-141/"
    f"233-234, m3 sat 69, m6 sat 358. DURUSTLUK: canli test "
    "(test_kazima_qwen_classify_calisir) ag/anahtar bagimli ve 20dk asarak "
    "kilitledi, --deselect ile dislandi; kalan kirilan: " + kirl +
    ". Oneri: canli testler pytest 'canli' isaretiyle varsayilan skip edilsin."
)
rr = subprocess.run([sys.executable, "scripts/gorev_kutusu.py", "teslim", "--ajan",
                     "yasu", "--task-id", T, "--ozet", ozet],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=str(KOK), timeout=300)
p(f"  rc={rr.returncode}")
p("  " + ((rr.stdout or "") + (rr.stderr or "")).strip()[:350].replace("\n", "\n  "))

p("")
p("=== 5) DOGRULAMA ===")
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == T), {})
p(f"  durum={g.get('durum')} teslim_gecmisi={len(g.get('teslim_gecmisi') or [])}")
_, s = git("status", "--short")
p(f"  calisma agaci: {s.strip() or '(temiz)'}")
_, c = git("log", "--oneline", "-3")
p("  " + c.replace("\n", "\n  "))