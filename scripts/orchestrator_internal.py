#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Orkestratör Ajan CLI — iç ajan yönetimi köprüsü.

Kullanım:
    python scripts/orchestrator_internal.py ajanlar
    python scripts/orchestrator_internal.py gorev-ekle <id> <sahip> "<baslik>" [--oncelik P1] [--dosya rel/path ...]
    python scripts/orchestrator_internal.py gorev-guncelle <id> --durum aktif|review|done|blocked [--not "..."]
    python scripts/orchestrator_internal.py pano [--durum aktif]
    python scripts/orchestrator_internal.py lock <dosya>          # kim tutuyor?
    python scripts/orchestrator_internal.py kilitle <sahip> <task> <dosya>
    python scripts/orchestrator_internal.py birak <sahip> <dosya>
    python scripts/orchestrator_internal.py donem-raporu
"""
from __future__ import annotations

import argparse
import sys

# Windows cp1254 encoding fix (Unicode karakterler icin)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.orchestrator import internal, task_board  # noqa: E402


def cmd_ajanlar() -> int:
    print("== İç Ajanlar ==")
    for ajan in internal.ic_ajanlar().values():
        if not ajan.aktif:
            continue
        print(f"  [{ajan.ajid}] {ajan.display_name}")
        print(f"      yetkiler: {', '.join(ajan.yetki_alanlari)}")
        print(f"      kısıtlar: {', '.join(ajan.kisitlar)}")
    return 0


def cmd_gorev_ekle(args) -> int:
    try:
        t = task_board.gorev_ekle(
            task_id=args.task_id,
            baslik=args.baslik,
            sahip=args.sahip,
            oncelik=args.oncelik,
            dosyalar=args.dosya or None,
        )
    except ValueError as exc:
        print(f"HATA: {exc}")
        return 1
    except PermissionError as exc:
        print(f"LOCK HATASI: {exc}")
        return 2
    print(f"Görev eklendi: {t['task_id']} -> {t['sahip']} ({t['durum']})")
    return 0


def cmd_gorev_guncelle(args) -> int:
    fields: dict = {}
    if getattr(args, "not_", None):
        fields["not"] = args.not_
    if getattr(args, "sahip", None):
        # Sahip değişirse görevin kilitlediği dosyaları da yeni sahibe devret
        board = task_board.gorev_listesi()
        kayit = next((t for t in board if t["task_id"] == args.task_id), None)
        if kayit:
            for d in kayit.get("dosyalar", []):
                task_board.lock_birak(d, kayit["sahip"])
                task_board._lock_alan(args.sahip, d, args.task_id)
        fields["sahip"] = args.sahip
    t = task_board.gorev_guncelle(
        args.task_id,
        durum=args.durum,
        **fields,
    )
    if not t:
        print(f"Görev bulunamadı: {args.task_id}")
        return 1
    print(f"Güncellendi: {t['task_id']} -> {t['durum']}")
    return 0


def cmd_pano(args) -> int:
    board = task_board.gorev_listesi(durum=args.durum)
    print("== Görev Panosu ==")
    if not board:
        print("  (boş)")
        return 0
    for t in sorted(board, key=lambda x: (x["durum"], x["oncelik"])):
        # K5: Kisalt cikti (satir basi ~60 karakter)
        baslik = t["baslik"][:40]
        print(f"  [{t['durum'][:4]}] {t['task_id'][:12]:<12} {t['sahip'][:10]:<10} {baslik}")
    return 0


def cmd_lock(args) -> int:
    locks = task_board.locklar()
    if args.dosya in locks:
        lk = locks[args.dosya]
        print(f"{args.dosya} -> {lk['sahip']} (görev {lk['task_id']})")
    else:
        print(f"{args.dosya} -> sahipsiz")
    return 0


def cmd_kilitle(args) -> int:
    try:
        task_board._lock_alan(args.sahip, args.dosya, args.task)
    except PermissionError as exc:
        print(f"LOCK HATASI: {exc}")
        return 1
    print(f"Kilitlendi: {args.dosya} -> {args.sahip}")
    return 0


def cmd_birak(args) -> int:
    ok = task_board.lock_birak(args.dosya, args.sahip)
    print("Bırakıldı" if ok else f"Bırakılamadı ({args.dosya} {args.sahip} sahipli değil)")
    return 0 if ok else 1


def cmd_handoff_yaz(args) -> int:
    task_board.handoff_yaz(
        args.task_id,
        tamamlandi=args.tamamlandi,
        sonraki_adim=args.sonraki,
        dikkat_edilmesi=args.dikkat,
    )
    print(f"Handoff yazildi: {args.task_id}")
    return 0


def cmd_retry(args) -> int:
    stats = task_board.retry_istatistikleri(args.task_id)
    gorev = task_board.gorev_getir(args.task_id)
    if not gorev:
        print(f"Gorev bulunamadı: {args.task_id}")
        return 1
    print(f"Retry istatistikleri: {args.task_id}")
    print(f"  Deneme: {stats['attempts']}/{task_board.MAX_ATTEMPTS}")
    print(f"  Bekleme: {stats['backoff_sn']}s")
    print(f"  Context modu: {stats['context_mode']}")
    if stats["attempts"] >= task_board.MAX_ATTEMPTS:
        print("  MAX ATTEMPTS ulasildi - manual mudahele gerekir")
    return 0


def cmd_sync(args) -> int:
    task_board.agent_sync_yaz()
    print("AGENT_SYNC.md guncellendi (task_board'dan)")
    return 0


def cmd_brief(args) -> int:
    brief = task_board.gorev_brief(args.task_id)
    if not brief:
        print(f"Gorev bulunamadı: {args.task_id}")
        return 1
    print(brief)
    return 0


def cmd_donem_raporu() -> int:
    board = task_board.gorev_listesi()
    say = {"plan": 0, "aktif": 0, "review": 0, "done": 0, "blocked": 0}
    for t in board:
        say[t["durum"]] = say.get(t["durum"], 0) + 1
    print("== Dönem Raporu ==")
    print(f"  Toplam: {len(board)} | plan:{say['plan']} aktif:{say['aktif']} "
          f"review:{say['review']} done:{say['done']} blocked:{say['blocked']}")
    locks = task_board.locklar()
    print(f"  Aktif dosya-lock: {len(locks)}")
    for dos, lk in locks.items():
        print(f"    {dos} -> {lk['sahip']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="orchestrator-internal")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ajanlar")
    ph = sub.add_parser("handoff-yaz")
    ph.add_argument("task_id")
    ph.add_argument("--tamamlandi", required=True)
    ph.add_argument("--sonraki", default="")
    ph.add_argument("--dikkat", default="")

    pr = sub.add_parser("retry")
    pr.add_argument("task_id")

    ps = sub.add_parser("sync")
    sub.add_parser("donem-raporu")

    pb = sub.add_parser("brief")
    pb.add_argument("task_id")

    pe = sub.add_parser("gorev-ekle")
    pe.add_argument("task_id")
    pe.add_argument("sahip")
    pe.add_argument("baslik")
    pe.add_argument("--oncelik", default="P1")
    pe.add_argument("--dosya", action="append", default=[])

    pg = sub.add_parser("gorev-guncelle")
    pg.add_argument("task_id")
    pg.add_argument("--durum", choices=("plan", "aktif", "review", "done", "blocked"))
    pg.add_argument("--sahip")
    pg.add_argument("--not", dest="not_")

    pp = sub.add_parser("pano")
    pp.add_argument("--durum", choices=("plan", "aktif", "review", "done", "blocked"))

    pl = sub.add_parser("lock")
    pl.add_argument("dosya")
    pk = sub.add_parser("kilitle")
    pk.add_argument("sahip")
    pk.add_argument("task")
    pk.add_argument("dosya")
    pb = sub.add_parser("birak")
    pb.add_argument("sahip")
    pb.add_argument("dosya")

    args = p.parse_args(argv)

    if args.cmd == "ajanlar":
        return cmd_ajanlar()
    if args.cmd == "handoff-yaz":
        return cmd_handoff_yaz(args)
    if args.cmd == "retry":
        return cmd_retry(args)
    if args.cmd == "sync":
        return cmd_sync(args)
    if args.cmd == "brief":
        return cmd_brief(args)
    if args.cmd == "gorev-ekle":
        return cmd_gorev_ekle(args)
    if args.cmd == "gorev-guncelle":
        return cmd_gorev_guncelle(args)
    if args.cmd == "pano":
        return cmd_pano(args)
    if args.cmd == "lock":
        return cmd_lock(args)
    if args.cmd == "kilitle":
        return cmd_kilitle(args)
    if args.cmd == "birak":
        return cmd_birak(args)
    if args.cmd == "donem-raporu":
        return cmd_donem_raporu()
    return 1


if __name__ == "__main__":
    sys.exit(main())