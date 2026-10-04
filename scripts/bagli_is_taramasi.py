"""Bagli is taramasi: dokunulan dosyalara ve anahtar kelimelere gore pano kaydi.

Tek kullanimlik tanilama araci (D-239 yazim kapisi: once olcer, sonra karar ver).
Salt okuma; hicbir sey yazmaz.
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PANO = os.path.join("data", "orchestrator", "task_board.json")

ANAHTAR = [
    "RAG", "KORPUS", "TSG", "EMBEDDER", "GLOBAL-INTEL",
    "FIRMA_TURU", "KVKK", "VECTOR", "TICARET_SICILI", "DINER",
]


def yukle() -> list[dict]:
    with open(PANO, encoding="utf-8") as f:
        tb = json.load(f)
    if isinstance(tb, dict):
        for alan in ("gorevler", "gorev", "tasks"):
            if alan in tb:
                liste = tb[alan]
                return liste if isinstance(liste, list) else list(liste.values())
    return tb if isinstance(tb, list) else []


def main() -> int:
    kayitlar = yukle()
    print(f"pano kaydi: {len(kayitlar)}")
    bulunan = 0
    for x in kayitlar:
        if not isinstance(x, dict):
            continue
        blob = json.dumps(x, ensure_ascii=False).upper()
        eslesme = [a for a in ANAHTAR if a in blob]
        if not eslesme:
            continue
        bulunan += 1
        print(
            f"{str(x.get('task_id', '')):32s} "
            f"{str(x.get('durum', '?')):10s} "
            f"{str(x.get('sahip', '?')):8s} "
            f"{str(x.get('oncelik', '?'))} "
            f"<-{','.join(eslesme[:4])}"
        )
    print(f"\neslesen kayit: {bulunan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
