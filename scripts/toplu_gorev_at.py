# -*- coding: utf-8 -*-
"""Toplu gorev atama: JSON listesini gorev_at.py at'e --baslik-b64 ile gecirir.

Kullanim:
    python scripts/toplu_gorev_at.py data/orchestrator/devir_2026-10-03.json [--kuru]

JSON: [{"task_id","baslik","ajan","oncelik","talimat","dosya"(ops)}, ...]
cmd.exe Turkce karakteri bozar; baslik burada utf-8 base64'e cevrilir (D-57 kalibi korunur).
ponytail: sirali subprocess; 6-10 gorev icin yeter, paralel gerekmez.
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
CAGIRAN = "ihsan"


def komut(g: dict) -> list[str]:
    b64 = base64.b64encode(g["baslik"].encode("utf-8")).decode("ascii")
    cmd = [sys.executable, str(KOK / "scripts" / "gorev_at.py"), "at",
           "--task-id", g["task_id"], "--baslik-b64", b64, "--ajan", g["ajan"],
           "--oncelik", g.get("oncelik", "P2"), "--cagiran", CAGIRAN]
    if g.get("talimat"):
        cmd += ["--talimat", g["talimat"]]
    if g.get("dosya"):
        cmd += ["--dosya", g["dosya"]]
    return cmd


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    kuru = "--kuru" in argv
    gorevler = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    hata = 0
    for g in gorevler:
        cmd = komut(g)
        if kuru:
            print("KURU", g["task_id"], g["ajan"])
            continue
        rc = subprocess.run(cmd, cwd=KOK).returncode
        print(f"{g['task_id']}: rc={rc}")
        hata += rc != 0
    return 1 if hata else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
