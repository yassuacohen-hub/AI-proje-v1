"""D-68 tetik <-> pano tutarlilik denetimi (utku icin tek kullanimlik olcum).

Postada gorunen gorevlerin pano durumunu tek tek yazar. Tetik `bekliyor`
demirken pano `iptal` / `done` / `review` ise kayit BAYAT tetiktir.

Salt okuma; hicbir sey yazmaz.
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AJAN = "utku"
KOK = os.path.join("data", "orchestrator")
PANO = os.path.join(KOK, "task_board.json")
TETIK = os.path.join(KOK, "triggers", f"{AJAN}.jsonl")

#: Tetigin bekleyebilecegi durumlar. D-68: pano `aktif`/`review` ise tetik
#: `plan`'a cekilir; `iptal`/`done`/`archive` ise tetik HIC olmamalidir.
KAPALI = {"iptal", "done", "archive", "inactive", "iptal_stale"}


def pano_yukle() -> dict[str, dict]:
    with open(PANO, encoding="utf-8") as f:
        tb = json.load(f)
    if isinstance(tb, dict):
        for alan in ("gorevler", "gorev", "tasks"):
            if alan in tb:
                liste = tb[alan]
                break
        else:
            liste = []
    else:
        liste = tb
    if isinstance(liste, dict):
        liste = list(liste.values())
    return {
        str(x.get("task_id")): x
        for x in liste
        if isinstance(x, dict) and x.get("task_id")
    }


def main() -> int:
    pano = pano_yukle()
    bekleyen: list[str] = []
    with open(TETIK, encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            try:
                kayit = json.loads(satir)
            except json.JSONDecodeError:
                continue
            if kayit.get("durum") == "bekliyor":
                bekleyen.append(str(kayit.get("task_id")))

    print(f"pano kaydi     : {len(pano)}")
    print(f"bekleyen tetik : {len(bekleyen)}")
    print()
    bayat = 0
    for tid in bekleyen:
        gorev = pano.get(tid)
        if gorev is None:
            print(f"  [ORPHAN] {tid:34s} panoda YOK (arşive bak D-231)")
            bayat += 1
            continue
        durum = str(gorev.get("durum", "?"))
        bayrak = "BAYAT" if durum in KAPALI else "OK   "
        if durum in KAPALI:
            bayat += 1
        print(f"  [{bayrak}] {tid:34s} pano={durum:10s} sahip={gorev.get('sahip', '?')}")
    print(f"\nbayat tetik: {bayat} / {len(bekleyen)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
