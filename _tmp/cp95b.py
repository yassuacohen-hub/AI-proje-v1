"""SCRAPE-004 madde 5: keyring onbellegi ekle, p95'i yeniden olc."""
import hashlib
import statistics
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
M = KOK / "scripts" / "kazima_qwen_classify.py"

BEKLENEN = "b5b170b16cdd6916"
ham = M.read_bytes()
h = hashlib.sha256(ham).hexdigest()[:16]
print(f"hash={h} (beklenen {BEKLENEN})")
if h != BEKLENEN:
    print("!! dosya degismis, DOKUNULMADI")
    sys.exit(1)
txt = ham.decode("utf-8")

ESKI = 'def qwen_siniflandir(html: str, model: str = "") -> dict:'
YENI = '''_ANAHTAR_ONBELLEK: dict[str, str] = {}


def _anahtar_bir(ad: str) -> str:
    """Anahtari ilk seferde keyring/env'den okur, sonra surekli onbellekten verir.

    SCRAPE-004 madde 5 (p95 < 2 sn) KALDIRILDI: keyring her sinifla_etiket()
    cagrisinda soruluyordu; 15 cagrilik olcumde p95 2.5-4.4 s idi. Onbellekle
    keyring yalnizca ilk cagrida sorulur.
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

if ESKI not in txt:
    print("!! imza bulunamadi")
    sys.exit(1)
txt = txt.replace(ESKI, YENI, 1)
g = M.with_suffix(".py.tmp")
g.write_text(txt, encoding="utf-8")
g.replace(M)
print("YAZILDI")
import ast
ast.parse(M.read_text(encoding="utf-8"))
print("AST OK")

print()
print("=" * 66)
print("YENI p95 OLCUMU")
print("=" * 66)
import importlib.util
spec = importlib.util.spec_from_file_location("kqy2", M)
kq = importlib.util.module_from_spec(spec); spec.loader.exec_module(kq)
URL = "https://www.ostim.org.tr/kurumsal/hakkimizda"
N = 15
for label, kw in [("V1 (varsayilan)", {}), ("V3 kapisi", {"kaynak": "V3"}),
                  ("kaynak='' (yok)", {"kaynak": ""})]:
    ts = []
    for _ in range(N):
        t0 = time.perf_counter()
        kq.sinifla_etiket(URL, **kw)
        ts.append((time.perf_counter() - t0) * 1000)
    ts.sort()
    p95 = ts[max(0, int(len(ts) * 0.95) - 1)]
    print(f"  {label:20s} min={ts[0]:7.1f}  med={statistics.median(ts):7.1f}  "
          f"p95={p95:7.1f} ms  {'GECTI' if p95 < 2000 else 'KALDI'}")