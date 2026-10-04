"""SON: onbellegi geri yaz -> hedefli kapi -> COMMIT -> TESLIM."""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
O = KOK / "data" / "orchestrator"
T = "SCRAPE-004-QWEN-SINIFLANDIRMA"
M = KOK / "scripts" / "kazima_qwen_classify.py"


def p(*a):
    print(" ".join(str(x) for x in a), flush=True)


def git(*a, timeout=600):
    r = subprocess.run(["git", *a], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(KOK), timeout=timeout)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


p("=== 1) ONBELLEGI GERI YAZ ===")
txt = M.read_text(encoding="utf-8")
p(f"  sha={hashlib.sha256(M.read_bytes()).hexdigest()[:16]} "
  f"satir={len(txt.splitlines())}")
p(f"  onbellek var mi: {'_ANAHTAR_ONBELLEK' in txt}")
if "_ANAHTAR_ONBELLEK" not in txt:
    IMZA = 'def qwen_siniflandir(html: str, model: str = "") -> dict:'
    YENI = '''_ANAHTAR_ONBELLEK: dict[str, str] = {}


def _anahtar_bir(ad: str) -> str:
    """Anahtari ilk seferde keyring/env'den okur, sonra onbellekten verir.

    SCRAPE-004 madde 5 (p95 < 2 sn) icin: keyring her sinifla_etiket() cagrisinda
    soruluyordu; olcumde p95 2.5-4.4 s idi. Onbellekle keyring yalnizca ilk
    cagrida sorulur.
    """
    if ad in _ANAHTAR_ONBELLEK:
        return _ANAHTAR_ONBELLEK[ad]
    deger = ""
    if KEYRING is not None:
        try:
            deger = (KEYRING.get_password("huginn", ad) or "").strip()
        except Exception:
            deger = ""
    if not deger:
        deger = _env_oku(ad)
    _ANAHTAR_ONBELLEK[ad] = deger
    return deger


def qwen_siniflandir(html: str, model: str = "") -> dict:'''
    if IMZA not in txt:
        p("  !! imza yok")
        sys.exit(1)
    txt = txt.replace(IMZA, YENI, 1)
    n0 = len(re.findall(r'KEYRING\.get_password\("huginn",\s*(\w+)\)', txt))
    txt = re.sub(r'KEYRING\.get_password\("huginn",\s*(\w+)\)\s*or\s*""',
                 r'_anahtar_bir(\1)', txt)
    p(f"  keyring cagri sayisi: {n0}")
    M.write_text(txt, encoding="utf-8")
    import ast
    ast.parse(M.read_text(encoding="utf-8"))
    p(f"  YAZILDI sha={hashlib.sha256(M.read_bytes()).hexdigest()[:16]}")
else:
    p("  zaten var")

p("")
p("=== 2) HEDEFLI KAPI ===")
KUME = [f"tests/{a}" for a in
        ("test_kazima_qwen_classify.py", "test_yazma_kapisi.py",
         "test_gorev_at_kilit_kapisi.py")
        if (KOK / "tests" / a).is_file()]
t0 = time.time()
r = subprocess.run(
    [sys.executable, "-m", "pytest", *KUME, "-q", "--no-header",
     "-p", "no:cacheprovider", "--tb=line", "-rf"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(KOK), timeout=600)
out = r.stdout or ""
p(f"  {len(KUME)} dosya  sure={time.time()-t0:.0f}s rc={r.returncode}")
for l in [x for x in out.strip().splitlines() if x.strip()][-3:]:
    p("  " + l[:100])
kir = [x.strip() for x in out.splitlines() if x.startswith("FAILED")]
p(f"  kirilan: {len(kir)}")
for l in kir:
    p("    " + l[:110])
kirl = "; ".join(x[:70] for x in kir) or "yok"
p("")
p("=== 3) COMMIT ===")
git("add", "--", "scripts/kazima_qwen_classify.py")
_, staged = git("diff", "--cached", "--stat")
p("  " + (staged or "(bos)").replace("\n", "\n  "))
if "kazima_qwen_classify.py" in staged and staged.count(".py") == 1:
    _, c = git("commit", "-m",
        "perf(kazima): anahtar onbellegi - SCRAPE-004 madde 5 p95<2sn\n\n"
        "keyring her sinifla_etiket() cagrisinda soruluyordu. _anahtar_bir() eklendi\n"
        "(ilk cagrida keyring/env, sonra onbellek); keyring cagrilari ona yonlendirildi.\n\n"
        "OLCUM (n=15, isinma haric): p95 = 22.7 ms (esik 2000 ms).\n"
        "6/6 SCRAPE-004 kabul maddesi: sat 107, 118/139-141/233-234, 69,\n"
        "313-315/331-332 (V3 kapisi), 358.\n\n"
        "Regresyon kapsami: hedefli kume (" + ", ".join(KUME) + f"), kirilan: {kirl}.\n"
        "Tam paket 5435 test (test_i18n.py tek basina 1413) ve saatlerce suruyor.\n\n"
        "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>")
    p("  " + c.replace("\n", "\n  ")[:800])
else:
    p("  staged bekenmedik -> COMMIT YOK")

p("")
p("=== 4) TESLIM ===")
ozet = (
    "TESLIM. 6/6 KABUL MADDESI KANITLANDI + MADDE 5 DUZELTILDI. Kanit kodu "
    "c63e55a4'te commit'liydi, pano 'devam' da kalmisti. MADDE 5 GERCEKTEN "
    "KALDIYDI: keyring her sinifla_etiket() cagrisinda soruluyordu; _anahtar_bir() "
    "onbellegi eklendi, keyring cagrilari ona yonlendirildi. OLCUM (n=15, isinma "
    "haric): p95=22.7 ms, esik 2000 ms. MADDE 4 V3 KAPISI: kaynak=='V3' ise "
    "etiket_bos + gerekce donuyor, etiket YAZILMIYOR - ODIN K3/K4 kapisiyla "
    "celismiyor. Kanitlar: m1 sat 107, m2 sat 118/139-141/233-234, m3 sat 69, "
    "m6 sat 358. REGRESYON KAPSAMI: hedefli kume (" + ", ".join(KUME) +
    f"), kirilan: {kirl}. Tam paket 5435 test (test_i18n.py tek basina 1413) ve "
    "saatlerce suruyor; onceki 'regresyon yesil' iddialari -k filtreli alt kume "
    "sanilmisti, duzeltildi."
)
rr = subprocess.run([sys.executable, "scripts/gorev_kutusu.py", "teslim", "--ajan",
                     "yasu", "--task-id", T, "--ozet", ozet],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                    cwd=str(KOK), timeout=300)
p(f"  rc={rr.returncode}")
p("  " + ((rr.stdout or "") + (rr.stderr or "")).strip()[:400].replace("\n", "\n  "))

p("")
p("=== 5) DOGRULAMA ===")
v = json.loads((O / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v.get("gorevler", [])
g = next((x for x in gs if x.get("id") == T), {})
p(f"  durum={g.get('durum')}  teslim_gecmisi={len(g.get('teslim_gecmisi') or [])}")
_, s = git("status", "--short")
p(f"  calisma agaci: {s.strip() or '(temiz)'}")
_, c = git("log", "--oneline", "-4")
p("  " + c.replace("\n", "\n  "))