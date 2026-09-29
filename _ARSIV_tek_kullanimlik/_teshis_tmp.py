# -*- coding: utf-8 -*-
"""Tek seferlik teshis: tetik/pano ad tutarliligi + zincir + nobetci canliligi."""
import json
from collections import Counter
from pathlib import Path

kok = Path(__file__).resolve().parent
tri = kok / "data" / "orchestrator" / "triggers"
pano = json.loads((kok / "data" / "orchestrator" / "task_board.json").read_text(encoding="utf-8-sig"))

KANONIK = {"ihsan", "utku", "salih", "yasu"}

print("=== PANO sahip dagilimi ===")
for ad, n in Counter(t.get("sahip", "-") for t in pano).most_common():
    bayrak = "OK " if ad in KANONIK else "!! "
    print(f"{bayrak}{ad}: {n}")

print("\n=== TETIK DOSYALARI ===")
for f in sorted(tri.glob("*.jsonl")):
    kayitlar = [json.loads(s) for s in f.read_text(encoding="utf-8-sig").splitlines() if s.strip()]
    durum = Counter(k.get("durum") for k in kayitlar)
    icAd = Counter(k.get("ajan") for k in kayitlar)
    uyum = "OK " if set(icAd) <= {f.stem} else "!! "
    print(f"{uyum}{f.name}: {len(kayitlar)} kayit | durum={dict(durum)} | icerik_ajan={dict(icAd)}")

print("\n=== ZINCIR BEKLEME (askida kalanlar) ===")
pano_durum = {t.get("task_id"): t.get("durum") for t in pano}
bulundu = 0
for f in sorted(tri.glob("*.jsonl")):
    kayitlar = [json.loads(s) for s in f.read_text(encoding="utf-8-sig").splitlines() if s.strip()]
    for k in kayitlar:
        if k.get("durum") == "zincir_bekleme":
            onceki = k.get("onceki_gorev")
            od = pano_durum.get(onceki, "PANODA-YOK")
            askida = "ASKIDA" if od in ("done", "blocked", "PANODA-YOK") else "normal-bekleme"
            print(f"{f.stem}: {k.get('task_id')} <- {onceki} (onceki pano durumu={od}) => {askida}")
            bulundu += 1
if not bulundu:
    print("zincir_bekleme kaydi YOK")

print("\n=== ALARM DOSYALARI (nobetci ciktisi) ===")
for f in sorted(tri.glob("*.ALARM.json")):
    print(f"{f.name}: {f.stat().st_size} bayt")

log = kok / "data" / "orchestrator" / "trigger_log.jsonl"
if log.exists():
    satirlar = [s for s in log.read_text(encoding="utf-8-sig").splitlines() if s.strip()]
    print(f"\n=== trigger_log.jsonl: {len(satirlar)} kayit, son 3 ===")
    for s in satirlar[-3:]:
        print(s[:200])
