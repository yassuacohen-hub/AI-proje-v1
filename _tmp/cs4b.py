"""SCRAPE-004: 6 kabul maddesini CANLI kodda olc."""
import re
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(KOK / "src")); sys.path.insert(0, str(KOK / "scripts"))
M = KOK / "scripts" / "kazima_qwen_classify.py"
sat = M.read_text(encoding="utf-8", errors="replace").splitlines()
import importlib.util
spec = importlib.util.spec_from_file_location("kqy", M)
kq = importlib.util.module_from_spec(spec); spec.loader.exec_module(kq)

def adim(n, s, ok, kanit=""):
    print(f"  [{n}] {s:52s} {'GECTI' if ok else 'KALDI'}")
    if kanit:
        print(f"        {kanit[:100]}")

print("=== MADDE 1: find_similar ile eslesme ===")
c1 = [n for n, l in enumerate(sat, 1) if "find_similar" in l]
adim(1, "find_similar cagriliyor", bool(c1), f"satirlar {c1[:3]}")

print("\n=== MADDE 2: kaynak yoksa bos etiket + gerekce ===")
c2 = [n for n, l in enumerate(sat, 1) if "etiket_bos" in l]
gerekce = [n for n, l in enumerate(sat, 1) if "gerekce" in l.lower()]
adim(2, "etiket_bos + gerekce", bool(c2 and gerekce), f"etiket_bos@{c2[:3]} gerekce@{gerekce[:3]}")

print("\n=== MADDE 3: NACE AI'a gitmeden once maskeleniyor ===")
c3 = [n for n, l in enumerate(sat, 1)
      if re.search(r"maske|redakte|nace.*kaldir|NACE_MASKELENDI", l, re.I)]
adim(3, "maskeleme cagrisi", bool(c3), f"satirlar {c3[:5]}")
# CANLI: modele giden metinde NACE var mi?
f = next((getattr(kq, x) for x in dir(kq) if "modele" in x.lower()
          or "istedigine" in x.lower() or "prompt" in x.lower()), None)
print(f"      model metni olusturan fonksiyon: {f.__name__ if f else '(bulunamadi)'}")

print("\n=== MADDE 4: V3 musteri ciktisina etiket YAZILMAZ (KAPI) ===")
c4 = [n for n, l in enumerate(sat, 1)
      if re.search(r"V3|kaynak\s*==|hedef\s*==|musteri", l)]
adim(4, "V3 kapisi kodda", bool(c4), f"satirlar {c4[:6]}")

print("\n=== MADDE 5: p95 < 2 sn (CANLI) ===")
import inspect
cands = [x for x in dir(kq) if callable(getattr(kq, x))
         and not x.startswith("_") and getattr(kq, x).__module__ == "kqy"]
print(f"      genel fonksiyonlar: {cands}")
olcum = next((x for x in cands
              if x in ("siniflandir", "siniflandir_website", "etiketle",
                       "siniflandir_kaynak")), None)
print(f"      olcum icin: {olcum}")
if olcum:
    try:
        ts = []
        for _ in range(7):
            t0 = time.perf_counter()
            try:
                getattr(kq, olcum)("https://ornek.com", "tr")
            except TypeError:
                getattr(kq, olcum)("https://ornek.com")
            ts.append((time.perf_counter() - t0) * 1000)
        ts.sort()
        p95 = ts[max(0, int(len(ts) * 0.95) - 1)]
        print(f"      sureler(ms): {[round(x) for x in ts]}")
        adim(5, "p95 < 2000 ms", p95 < 2000, f"p95={p95:.0f}ms")
    except Exception as e:
        print(f"      OLCUM HATASI: {type(e).__name__}: {e}")
else:
    print("      olcum icin uygun fonksiyon bulunamadi")

print("\n=== MADDE 6: yeni kod __main__ altinda ===")
ana = next((n for n, l in enumerate(sat, 1) if "__main__" in l), None)
adim(6, "if __name__ == '__main__'", ana is not None, f"satir {ana}")
if ana:
    disi = [n for n, l in enumerate(sat, 1)
            if n < ana and re.match(r"^\s*(import |from |def |class )", l)]
    print(f"      __main__ disi kod: {len(disi)} satir")

print("\n=== TESLIM GECMISI ===")
import json
v = json.loads((KOK / "data" / "orchestrator" / "task_board.json").read_text(encoding="utf-8"))
gs = v if isinstance(v, list) else v["gorevler"]
g = next(x for x in gs if x["id"] == "SCRAPE-004-QWEN-SINIFLANDIRMA")
print(f"  durum={g.get('durum')} ajan={g.get('ajan')} teslim_gecmisi={g.get('teslim_gecmisi')}")