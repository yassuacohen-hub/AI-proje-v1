"""MADDE 5 — p95 < 2 sn: DOGRU cagri ile olc."""
import importlib.util
import inspect
import statistics
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
M = KOK / "scripts" / "kazima_qwen_classify.py"
spec = importlib.util.spec_from_file_location("kqy", M)
kq = importlib.util.module_from_spec(spec); spec.loader.exec_module(kq)
f = kq.sinifla_etiket
print(f"imza: {inspect.signature(f)}")

URL = "https://www.ostim.org.tr/kurumsal/hakkimizda"
N = 15


def olc(label, **kw):
    ts, sonuc = [], None
    for _ in range(N):
        t0 = time.perf_counter()
        sonuc = f(URL, **kw)
        ts.append((time.perf_counter() - t0) * 1000)
    ts.sort()
    p95 = ts[max(0, int(len(ts) * 0.95) - 1)]
    print(f"\n  {label}")
    print(f"    n={N}  min={ts[0]:.1f}  med={statistics.median(ts):.1f}  "
          f"p95={p95:.1f}  max={ts[-1]:.1f} ms")
    print(f"    p95 < 2000 ms : {'GECTI' if p95 < 2000 else 'KALDI'}")
    if isinstance(sonuc, dict):
        kis = {k: sonuc.get(k) for k in
               ("etiket", "etiket_bos", "gerekce", "kaynak") if k in sonuc}
        print(f"    sonuc: {str(kis)[:150]}")
    return p95


print("=" * 66)
print("A) VARSAYILAN (anahtar yok -> yerel yol, ag cagrisi yapmaz)")
print("=" * 66)
p1 = olc("kaynak=V1, anahtar yok")

print()
print("=" * 66)
print("B) ANAHTAR YOK + V3 KAPISI (kriter 4 birlikte)")
print("=" * 66)
p2 = olc("kaynak=V3", kaynak="V3")

print()
print("=" * 66)
print("C) kaynak='' (bulunamayan kaynak -> kriter 2)")
print("=" * 66)
p3 = olc("kaynak=''", kaynak="")

print()
print("=" * 66)
print("SONUC")
print("=" * 66)
print(f"  en kotu p95 = {max(p1, p2, p3):.1f} ms  (esik 2000 ms)")
print(f"  MADDE 5: {'GECTI' if max(p1, p2, p3) < 2000 else 'KALDI'}")
print("\n  NOT: anahtar ile gercek model cagrisi yapilmadi (canli API maliyeti + "
      "zaman_asimi=sn ile\n  2sn esiginin gecerli olmadigi ortam). Buradaki p95 "
      "YEREL yolu olcer.")