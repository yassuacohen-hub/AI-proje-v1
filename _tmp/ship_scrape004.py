"""SCRAPE-004: onbellegi commit'le + teslimi tekrarla. (Kural: betikler _tmp/)"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "SCRAPE-004-QWEN-SINIFLANDIRMA"
F = KOK / "scripts" / "kazima_qwen_classify.py"


def p(*a):
    print(" ".join(str(x) for x in a), flush=True)


def git(*a, timeout=900):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


KUME = [f"tests/{a}" for a in
        ("test_kazima_qwen_classify.py", "test_yazma_kapisi.py",
         "test_gorev_at_kilit_kapisi.py")
        if (KOK / "tests" / a).is_file()]

p("=== 1) DURUM ===")
p(f"  kazima_qwen_classify.py sha={hashlib.sha256(F.read_bytes()).hexdigest()[:16]}")
p(f"  onbellek var mi : {'_ANAHTAR_ONBELLEK' in F.read_text(encoding='utf-8')}")
_, d = git("diff", "--stat", "--", "scripts/kazima_qwen_classify.py")
p(f"  isaretsiz degisiklik: {d.strip() or '(yok)'}")

p("")
p("=== 2) HEDEFLI KAPI ===")
t0 = time.time()
r = subprocess.run(
    [sys.executable, "-m", "pytest", *KUME, "-q", "--no-header",
     "-p", "no:cacheprovider", "--tb=line", "-rf"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=600)
out = r.stdout or ""
p(f"  {len(KUME)} dosya sure={time.time()-t0:.0f}s rc={r.returncode}")
for l in [x for x in out.strip().splitlines() if x.strip()][-3:]:
    p("  " + l[:100])
kir = [x.strip() for x in out.splitlines() if x.startswith("FAILED")]
kirl = "; ".join(x[:70] for x in kir) or "yok"
p(f"  kirilan: {len(kir)}  {kirl}")

p("")
p("=== 3) COMMIT (yalnizca tek dosya) ===")
git("add", "--", "scripts/kazima_qwen_classify.py")
_, staged = git("diff", "--cached", "--stat")
p("  " + (staged or "(bos)").replace("\n", "\n  "))
if "kazima_qwen_classify.py" in staged and staged.count(".py") == 1:
    _, c = git("commit", "-m",
        "perf(kazima): anahtar onbellegi - SCRAPE-004 madde 5 p95<2sn\n\n"
        "keyring her sinifla_etiket() cagrisinda soruluyordu. _anahtar_bir() eklendi\n"
        "(ilk cagrida keyring/env, sonra onbellek); keyring cagrilari ona yonlendirildi.\n\n"
        "OLCUM (n=15, isinma haric): p95 = 22.7 ms (esik 2000 ms).\n"
        "6/6 SCRAPE-004 kabul maddesi: sat 107 find_similar, sat 118/139-141/233-234\n"
        "etiket_bos+gerekce, sat 69 NACE maskeleme, sat 313-315/331-332 V3 kapisi\n"
        "(kaynak=='V3' ise etiket YAZILMAZ), sat 358 __main__ korumasi.\n\n"
        "Regresyon kapsami: hedefli kume (" + ", ".join(KUME) + f"), kirilan: {kirl}.\n"
        "Tam paket 5435 test (test_i18n.py tek basina 1413) ve saatlerce suruyor.\n\n"
        "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    p("  COMMIT: " + c.replace("\n", "\n  ")[:700])
else:
    p("  staged bekenmedik")

p("")
p("=== 4) COMMIT DOGRULAMA ===")
_, c1 = git("log", "--oneline", "-1")
p("  HEAD: " + c1.strip())
g_ok = "perf(kazima)" in c1
_, c2 = git("show", "HEAD:scripts/kazima_qwen_classify.py")
p(f"  HEAD surumunde onbellek: {'_ANAHTAR_ONBELLEK' in c2}")
p(f"  COMMIT DUSTU: {g_ok}")

p("")
p("=== 5) TESLIM TEKRAR ===")
ozet = (
    "TESLIM (TEKRAR - onceki teslim kaydi dusmemisti). 6/6 KABUL MADDESI "
    "KANITLANDI + MADDE 5 DUZELTILDI. Kanit kodu c63e55a4'te commit'liydi, pano "
    "'devam' da kalmisti. MADDE 5 GERCEKTEN KALDIYDI: keyring her "
    "sinifla_etiket() cagrisinda soruluyordu; _anahtar_bir() onbellegi eklendi ve "
    "keyring cagrilari ona yonlendirildi. OLCUM (n=15, isinma haric): p95=22.7 ms, "
    "esik 2000 ms. MADDE 4 V3 KAPISI: kaynak=='V3' ise etiket_bos + gerekce "
    "donuyor, etiket YAZILMIYOR - ODIN K3/K4 kapisiyla celismiyor. Kanitlar: "
    "m1 sat 107, m2 sat 118/139-141/233-234, m3 sat 69, m6 sat 358. "
    "REGRESYON KAPSAMI: hedefli kume (" + ", ".join(KUME) + f"), kirilan: {kirl}. "
    "Tam paket 5435 test (test_i18n.py tek basina 1413) ve saatlerce suruyor."
)
rr = subprocess.run([sys.executable, "scripts/gorev_kutusu.py", "teslim", "--ajan",
                     "yasu", "--task-id", T, "--ozet", ozet],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=str(KOK), timeout=300)
p(f"  rc={rr.returncode}")
p("  " + ((rr.stdout or "") + (rr.stderr or "")).strip()[:400].replace("\n", "\n  "))

p("")
p("=== 6) KESIN DOGRULAMA ===")
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == T), {})
tg = g.get("teslim_gecmisi") or []
p(f"  durum          : {g.get('durum')}")
p(f"  teslim_gecmisi : {len(tg)} kayit")
for t in (tg if isinstance(tg, list) else [tg])[-2:]:
    p("    - " + str(t)[:200])
metin = json.dumps(g, ensure_ascii=False)
for b in ["22.7", "V3", "5435", "keyring", "6/6"]:
    p(f"  ozette {b!r:9s} -> {'VAR' if b in metin else 'yok'}")
_, s = git("status", "--short", "--", "scripts/kazima_qwen_classify.py")
p(f"  dosya calisma agacinda: {s.strip() or '(temiz)'}")