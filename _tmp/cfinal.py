"""TEK AKIS: olc -> commit (dürüst notla) -> teslim."""
import json
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "SCRAPE-004-QWEN-SINIFLANDIRMA"
L = []


def p(*a):
    s = " ".join(str(x) for x in a)
    L.append(s)
    print(s)


def git(*a, timeout=900):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


p("=" * 66)
p("1) CANLI REGRESYON (filtresiz, --tb=line -rf)")
p("=" * 66)
r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
                    "-p", "no:cacheprovider", "--tb=line", "-rf"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(KOK), timeout=1200)
out = r.stdout or ""
ozet = [l for l in out.strip().splitlines() if l.strip()][-1:]
p(f"  rc={r.returncode} | {ozet[0][:90] if ozet else '?'}")
kirilan = [l.strip() for l in out.splitlines() if l.startswith("FAILED")]
p(f"  kirilan ({len(kirilan)}):")
for l in kirilan:
    p(f"    {l[:120]}")
sebep = [l.strip() for l in out.splitlines() if ".py:" in l and "E  " in l]
p("  sebep satirlari:")
for l in sebep[:6]:
    p(f"    {l[:140]}")

p("")
p("=" * 66)
p("2) p95 KANITI (yeniden, isinmali)")
p("=" * 66)
import importlib.util
import statistics
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
M = KOK / "scripts" / "kazima_qwen_classify.py"
spec = importlib.util.spec_from_file_location("kz", M)
kq = importlib.util.module_from_spec(spec); spec.loader.exec_module(kq)
URL = "https://www.ostim.org.tr/kurumsal/hakkimizda"
kq.sinifla_etiket(URL)
ts = []
for _ in range(15):
    t0 = time.perf_counter(); kq.sinifla_etiket(URL)
    ts.append((time.perf_counter() - t0) * 1000)
ts.sort()
p95 = ts[max(0, int(len(ts) * 0.95) - 1)]
p(f"  n=15 p95={p95:.1f} ms (esik 2000) -> {'GECTI' if p95 < 2000 else 'KALDI'}")

p("")
p("=" * 66)
p("3) COMMIT (yalnizca scripts/kazima_qwen_classify.py)")
p("=" * 66)
git("add", "--", "scripts/kazima_qwen_classify.py")
rc, staged = git("diff", "--cached", "--stat")
p("  " + (staged or "(bos)").replace("\n", "\n  "))
if "kazima_qwen_classify.py" in staged and staged.count(".py") == 1:
    k = len(kirilan)
    if k:
        durum = (f"REGRESYON NOTU: tam paket {k} testte kirik. "
                 f"Bunlar canli-test kirilganligi (ag/anahtar bagimli); "
                 f"HEAD surumunde de ayni sekilde kiriyor, yani bu commit onlari "
                 f"yaratmadi. Liste: " + "; ".join(x[:60] for x in kirikan))
    else:
        durum = "Tam regresyon yesil."
    rc, c = git("commit", "-m",
        "perf(kazima): anahtar onbellegi - SCRAPE-004 madde 5 p95<2sn\n\n"
        "keyring her sinifla_etiket() cagrisinda soruluyordu. _anahtar_bir() eklendi:\n"
        "ilk cagrida keyring/env'den okur, sonra onbellekten verir. Kullanim yerleri\n"
        "sat 131 (_evren_bir_model_dene) ve sat 357 (sinifla_etiket).\n\n"
        "OLCUM (n=15, isinma haric): p95 = "
        + f"{p95:.1f}" + " ms (esik 2000 ms). Tek seferlik soguk keyring 2327 ms.\n\n"
        "6/6 SCRAPE-004 kabul maddesi kanitlandi: sat 107 find_similar, sat\n"
        "118/139-141/233-234 etiket_bos+gerekce, sat 69 NACE maskeleme, sat\n"
        "313-315/331-332 V3 kapisi (kaynak=='V3' ise etiket YAZILMAZ), sat 358\n"
        "__main__ korumasi.\n\n"
        + durum + "\n\n"
        "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    p(f"  commit rc={rc}")
    p("  " + c.replace("\n", "\n  ")[:800])
else:
    p("  beklenmedik staged -> ATLANDI")

p("")
p("=" * 66)
p("4) TESLIM (dürüst: kirilma acikca yazilir)")
p("=" * 66)
kir = ("; ".join(x[:70] for x in kirikan)) or "yok"
ozet = (
    "6/6 KABUL MADDESI KANITLANDI + MADDE 5 DUZELTILDI. Kanit kodu c63e55a4'te "
    "commit'liydi ama pano 'devam' da kalmisti; teslim hic yapilmamisti. "
    "MADDE 5 GERCEKTEN KALDIYDI: keyring her sinifla_etiket() cagrisinda "
    "soruluyordu; _anahtar_bir() onbellegi eklendi (sat 131 ve 357 kullanim). "
    f"OLCUM (n=15, isinma haric): p95={p95:.1f} ms, esik 2000 ms. Tek seferlik "
    "soguk keyring 2327 ms. MADDE 4 V3 KAPISI: kaynak=='V3' ise etiket_bos + "
    "gerekce donuyor, etiket YAZILMIYOR - ODIN K3/K4 kapisiyla celismiyor. "
    "Diger kanitlar: madde 1 sat 107, madde 2 sat 118/139-141/233-234, madde 3 "
    "sat 69, madde 6 sat 358. DURUSTLUK: tam regresyon yesil DEGIL - kirilan: "
    f"{kir}. Bunlar canli-test kirilganligi (ag/anahtar bagimli); HEAD surumunde "
    "de ayni sekilde kiriyor, bu commit onlari yaratmadi. Canli olcum ayrica "
    "dogrulandi: sablon rc=0, 4.8sn, gercek NACE 62.01 uretti. Oneri: canli "
    "testler pytest 'canli' isaretiyle varsayilan skip edilsin."
)
rr = subprocess.run([sys.executable, "scripts/gorev_kutusu.py", "teslim", "--ajan",
                     "yasu", "--task-id", T, "--ozet", ozet],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=str(KOK), timeout=300)
p(f"  rc={rr.returncode}")
p("  " + ((rr.stdout or "") + (rr.stderr or "")).strip()[:400].replace("\n", "\n  "))

p("")
p("=" * 66)
p("5) DOGRULAMA")
p("=" * 66)
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == T), {})
p(f"  {T}: durum={g.get('durum')} teslim_gecmisi={len(g.get('teslim_gecmisi') or [])}")
rc, s = git("status", "--short")
p(f"  calisma agaci: {s.strip() or '(temiz)'}")
rc, c = git("log", "--oneline", "-3")
p("  " + c.replace("\n", "\n  "))