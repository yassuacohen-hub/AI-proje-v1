# -*- coding: utf-8 -*-
"""Pano alan duzeltmesi: teslim edilen gorevlerde `cikti` yolu kacmis oluyor.

`gorev_at.py guncelle` `--cikti` bilmez; `gorev_kutusu.py teslim` ise gorev
`done`/`review` olduktan sonra tekrar calistirilirsa reddediyor. Bu yuzden
kayitli ama BOS `cikti` alanlari geriye donuk (backfill) ile doldurulur.

Guvenlik: YALNIZCA bos `cikti` alanina dokunur; hicbir baska alan degismez.
"""
from __future__ import annotations

import json
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
PANO = KOK / "data" / "orchestrator" / "task_board.json"

#: gorev_id -> kanitli cikti yolu (yol raporun kendisinde belgeli)
BACKFILL = {
    "TSG-PILOT-20": "plans/rapor_yasu_TSG-PILOT-20.md",
    "VERI-TOBB2B-KESISIM-01": "data/pilots/VERI-TOBB2B-KESISIM-01/ozet.json",
}


def main() -> None:
    veri = json.loads(PANO.read_text(encoding="utf-8"))
    gorevler = veri if isinstance(veri, list) else veri.get("gorevler", [])
    degisen = []
    for t in gorevler:
        gid = t.get("id")
        if gid in BACKFILL and not t.get("cikti"):
            t["cikti"] = BACKFILL[gid]
            degisen.append(gid)
    if degisen:
        PANO.write_text(json.dumps(veri, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print("guncellenen:", degisen or "(yok)")


if __name__ == "__main__":
    main()
