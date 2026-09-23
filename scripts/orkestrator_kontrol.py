# -*- coding: utf-8 -*-
"""Orkestratör pano kontrolü: açık görevler, kilitler, tetikler ve tutarsızlıklar.

Kullanım:
    set PYTHONIOENCODING=utf-8 && python -X utf8 scripts/orkestrator_kontrol.py

Çıktıda kontrol edilecek beklentiler:
    - "ÇAKIŞAN DOSYA" bölümü boş (aynı dosya birden çok açık görevde olmamalı)
    - "KİLİT TUTARSIZLIĞI" bölümü boş (done görevin kilidi kalmamalı)
    - "STALE tetik" satırı yok (done/review görev için bekleyen tetik olmamalı)
    - Her aktif ajan için beklenen sayıda aktif görev
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))
from src.company_master.orchestrator import task_board as tb  # noqa: E402

D = KOK / "data" / "orchestrator"
# ALTYAPI-DURUM-SOZLUK-01: kopya liste yok, tek kaynak task_board.
# ("cancelled" kaldirildi: panoda hicbir zaman uretilmeyen olu durumdu.)
KAPALI_DURUMLAR = tb.KAPALI_DURUMLAR


def _json_oku(yol: Path):
    return json.loads(yol.read_text(encoding="utf-8"))


def main() -> int:
    pano = _json_oku(D / "task_board.json")
    kilit = _json_oku(D / "file_locks.json")
    acik = [g for g in pano if g.get("durum") not in KAPALI_DURUMLAR]

    print("== AÇIK GÖREVLER (durum != done) ==")
    for g in sorted(acik, key=lambda x: (str(x.get("sahip")), str(x.get("durum")))):
        print(
            f"{g.get('sahip', '?'):10} {g.get('durum', '?'):9} {g.get('oncelik', '?'):3} "
            f"{g['task_id']:18} {g.get('baslik', '')[:60]} | dosya={len(g.get('dosyalar') or [])}"
        )

    print("\n== SAHİP/DURUM SAYIMI ==")
    print(Counter((g.get("sahip"), g.get("durum")) for g in acik))

    print("\n== KİLİTLER ==")
    locks = kilit.get("locks", kilit) if isinstance(kilit, dict) else {}
    for dosya, bilgi in sorted(locks.items()):
        print(f"  {dosya} -> {bilgi}")

    print("\n== KİLİT TUTARSIZLIĞI (done görevin dosyası hâlâ kilitli?) ==")
    done_ids = {g["task_id"] for g in pano if g.get("durum") == "done"}
    stale_kilit = 0
    for dosya, bilgi in sorted(locks.items()):
        tid = bilgi.get("task_id") if isinstance(bilgi, dict) else None
        if tid in done_ids:
            stale_kilit += 1
            print(f"  STALE: {dosya} ({tid})")

    print("\n== ÇAKIŞAN DOSYA (aynı dosya birden çok açık görevde) ==")
    dosya_map: dict[str, list[str]] = defaultdict(list)
    for g in acik:
        for f in g.get("dosyalar") or []:
            dosya_map[f].append(f"{g['task_id']}({g.get('sahip')})")
    cakisma = 0
    for f, ids in sorted(dosya_map.items()):
        if len(ids) > 1:
            cakisma += 1
            print(f"  {f}: {ids}")

    print("\n== MÜKERRER TASK_ID ==")
    print([k for k, v in Counter(g["task_id"] for g in pano).items() if v > 1])

    print("\n== TETİKLER ==")
    stale_tetik = 0
    for yol in sorted((D / "triggers").glob("*.jsonl")):
        kayitlar = [json.loads(s) for s in yol.read_text(encoding="utf-8").splitlines() if s.strip()]
        bek = [k for k in kayitlar if k.get("durum") == "bekliyor"]
        zincir = [k for k in kayitlar if k.get("durum") == "zincir_bekleme"]
        print(
            f"  {yol.stem}: toplam={len(kayitlar)} bekliyor={[k.get('task_id') for k in bek]} "
            f"zincir={[k.get('task_id') for k in zincir]}"
        )
        for k in bek:
            g = next((x for x in pano if x["task_id"] == k.get("task_id")), None)
            if g and g.get("durum") in ("done", "review"):
                stale_tetik += 1
                print(f"    STALE tetik: {k.get('task_id')} pano={g.get('durum')}")

    print(f"\n== ÖZET == çakışan dosya={cakisma} stale kilit={stale_kilit} stale tetik={stale_tetik}")
    return 0 if (cakisma == 0 and stale_kilit == 0 and stale_tetik == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
