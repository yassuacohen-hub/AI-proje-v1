# -*- coding: utf-8 -*-
"""ALTYAPI-TETIK-ARSIV-01: kanonik olmayan tetik dosyalarini tasi (sil yok)."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "src")
from company_master.orchestrator.trigger import AJANLAR  # noqa: E402

TR = Path("data/orchestrator/triggers")
ARSIV = TR / "_arsiv_2026-09-23"
TASINMAYACAK_DURUMLAR = ("bekliyor", "alindi")

def tarama() -> tuple[list, list, list]:
    ARSIV.mkdir(exist_ok=True)
    tasinan, beklemede, bos = [], [], []
    for f in sorted(TR.glob("*.jsonl")):
        if f.stem in AJANLAR:
            continue
        acik = []
        for i, line in enumerate(
            f.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1
        ):
            line = line.strip()
            if not line:
                continue
            try:
                k = json.loads(line)
            except json.JSONDecodeError:
                acik.append((i, "?", "BOZUK_JSON"))
                continue
            if k.get("durum") in TASINMAYACAK_DURUMLAR:
                acik.append((i, k.get("task_id"), k.get("durum")))
        if acik:
            beklemede.append((f.name, acik))
        elif f.stat().st_size == 0:
            bos.append(f.name)
            shutil.move(str(f), ARSIV / f.name)
        else:
            tasinan.append(f.name)
            shutil.move(str(f), ARSIV / f.name)
    return tasinan, beklemede, bos

if __name__ == "__main__":
    tasinan, beklemede, bos = tarama()
    print("TASINAN:", tasinan)
    print("BOŞ (taşındı):", bos)
    print("AÇIK KAYITLI (taşınmadı):", beklemede)
