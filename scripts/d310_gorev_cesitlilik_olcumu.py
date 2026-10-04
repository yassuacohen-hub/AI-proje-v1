"""ihsan'ın chat mesajı ile pano arasındaki çelişkiyi ölçer.

ihsan bana 3 zincirli Odin görevi verdi (chat #1). D-317 ölçümü aynı 3 görevin
2'sinin panoda `iptal`, 1'inin `done` olduğunu söylüyor. Hangisi doğru?
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ORCH = Path("data/orchestrator")
pano = json.loads((ORCH / "task_board.json").read_text(encoding="utf-8"))
gorevler = pano.get("gorevler", pano) if isinstance(pano, dict) else pano
by_id = {g.get("task_id"): g for g in gorevler}

IDLER = [
    "ALTYAPI-EVREN-PRIVATE-DOGRULAMA",
    "VERI-ODIN-EGITIM-VERISI-HAZIRLA",
    "ALTYAPI-ODIN-EGITIM-PIPELINE",
    "VERI-TSG-ESLEME-CASE-01",
]

print("PANODAKI DURUM (SSOT: task_board.json)")
for tid in IDLER:
    g = by_id.get(tid)
    if not g:
        print(f"  {tid:42} -> PANODA YOK")
        continue
    print(
        f"  {tid:42} durum={g.get('durum'):9} "
        f"sahip={str(g.get('sahip')):7} oncelik={g.get('oncelik')}"
    )

# --- utku kuyruğunda bu görevler tetikli mi? ---
print("\nUTKU KUYRUĞU")
kuyruk = ORCH / "triggers" / "utku.jsonl"
if kuyruk.exists():
    tetikler = [json.loads(l) for l in kuyruk.read_text(encoding="utf-8").splitlines() if l.strip()]
    for t in tetikler:
        if t.get("gorev_id") in IDLER or t.get("task_id") in IDLER:
            print(
                f"  {t.get('gorev_id') or t.get('task_id'):42} "
                f"durum={t.get('durum')} tarih={t.get('tarih')}"
            )
else:
    print("  kuyruk dosyasi yok")

# --- teslim / onay durumu ---
print("\nONAY KUYRUĞU")
k = json.loads((ORCH / "onay_kuyrugu.json").read_text(encoding="utf-8"))
kayitlar = k if isinstance(k, list) else k.get("kuyruk", [])
for r in kayitlar:
    if r.get("task_id") in IDLER:
        print(f"  {r.get('task_id'):42} durum={r.get('durum')} ajan={r.get('ajan')}")
