"""f8507a6 temizliğinin yan etkisini ölçer.

ihsan: "utku'nun kutusunda artık sadece 1 gerçek görev (RAG-KORPUS-01) kaldı."
Bu turda benim teslimim `VERI-TSG-ESLEME-CASE-01` görevi `review`'dan `plan`'a
düşmüş ve onay kuyruğunda **hiç görünmüyor**.

Soru: temizlik, *daha teslim edilmemiş* bir işi mi sildi?
"""

import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ORCH = Path("data/orchestrator")
BENIM = "VERI-TSG-ESLEME-CASE-01"

# --- 1) Pano ---
pano = json.loads((ORCH / "task_board.json").read_text(encoding="utf-8"))
gorevler = pano.get("gorevler", pano) if isinstance(pano, dict) else pano
g = next((x for x in gorevler if x.get("task_id") == BENIM), None)
print("1) PANO")
if g:
    for alan in ("durum", "bitis", "not"):
        v = str(g.get(alan, ""))
        print(f"   {alan}: {v[:150]}")
else:
    print("   PANODA YOK")

# --- 2) Onay kuyrugu ---
k = json.loads((ORCH / "onay_kuyrugu.json").read_text(encoding="utf-8"))
kayitlar = k if isinstance(k, list) else k.get("kuyruk", [])
kayit_benim = [r for r in kayitlar if r.get("task_id") == BENIM]
print(f"\n2) ONAY KUYRUĞU: toplam {len(kayitlar)} kayit, benim kayit {len(kayit_benim)}")
durumlar = {}
for r in kayitlar:
    durumlar[r.get("durum")] = durumlar.get(r.get("durum"), 0) + 1
print(f"   durum dagilimi: {durumlar}")

# --- 3) Teslim kaydi git gecmisinde mi? ---
print("\n3) GIT GECMISI (teslim kaydi dosyada mi)")
for dosya in ("onay_kuyrugu.json", "handoff.jsonl"):
    r = subprocess.run(
        ["git", "log", "--oneline", "-3", "--", f"data/orchestrator/{dosya}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(f"   {dosya}: {r.stdout.strip()[:200] or '(gecmis yok)'}")

# --- 4) commit f8507a6 onay kuyrugunu nasil degistirmis? ---
print("\n4) f8507a6 DIFF'I — onay_kuyrugu.json")
r = subprocess.run(
    ["git", "show", "f8507a6", "--stat", "--", "data/orchestrator/onay_kuyrugu.json"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)
print("   " + (r.stdout.strip() or "(bu dosya f8507a6'da DEGISMEDI)"))

r = subprocess.run(
    ["git", "show", "f8507a6", "--stat"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)
print("\n5) f8507a6 DEGISTIRILEN DOSYALAR")
print("   " + (r.stdout.strip()[:900]))
