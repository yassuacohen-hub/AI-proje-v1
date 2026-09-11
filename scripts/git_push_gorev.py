#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GIT-01: Gorev bitisi secmeli git commit + push yardimcisi (hibrit push stratejisi).

Kullanim:
    python scripts/git_push_gorev.py --mesaj "GIT-01: push altyapisi" src/... docs/...
    python scripts/git_push_gorev.py --mesaj "..." --dosya-liste liste.txt

Davranis (add -A YOK — sadece verilen dosyalar):
1. Verilen dosyalar `git add` edilir (diskte olmayan ama takipte olanlar silinme olarak eklenir).
2. Koordinasyon dosyalari (AGENT_SYNC, task_board, gorev_panosu, handoffs) otomatik dahil.
3. Calisma agaci kirliyse `pull --rebase --autostash` ile uzak dal hizalanir.
4. Push basarisizsa 2 deneme (VPN kaynakli gecici ag hatalari icin bekleme ile).
5. Commit edecek icerik yoksa sessizce 0.

Cikis kodlari: 0 basari/bosan, 1 kullanim hatasi, 2 rebase catisma (manuel cozum gerek).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KOORDINASYON = [
    "AGENT_SYNC.md",
    "data/orchestrator/task_board.json",
    "data/orchestrator/gorev_panosu.md",
    "data/orchestrator/handoffs.json",
    "data/orchestrator/AGENT_SYNC.md",
]


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def dal_adi() -> str:
    r = git("rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.strip() or "main"


def push_yap(dal: str, deneme: int = 2, bekle: int = 5) -> bool:
    """pull --rebase --autostash + push; ag hatalarinda tekrar dener."""
    for i in range(1, deneme + 1):
        r = git("pull", "--rebase", "--autostash", "origin", dal)
        if r.returncode != 0:
            print(f"[git_push_gorev] pull --rebase basarisiz: {r.stderr.strip()[:300]}", file=sys.stderr)
            return False
        r = git("push", "origin", dal)
        if r.returncode == 0:
            return True
        print(f"[git_push_gorev] push denemesi {i}/{deneme} basarisiz: {r.stderr.strip()[:300]}", file=sys.stderr)
        if i < deneme:
            time.sleep(bekle)
    return False


def main() -> int:
    p = argparse.ArgumentParser(description="Gorev bitisi secmeli commit + push")
    p.add_argument("--mesaj", required=True, help="Commit mesaji (TASK_ID ile baslamasi onerilir)")
    p.add_argument("--dosya-liste", help="Satir basina dosya yolu iceren dosya")
    p.add_argument("dosyalar", nargs="*", help="Commit edilecek dosya/dizin yollari")
    args = p.parse_args()

    dosyalar: list[str] = list(args.dosyalar)
    if args.dosya_liste:
        liste = Path(args.dosya_liste)
        if liste.exists():
            dosyalar += [l.strip() for l in liste.read_text(encoding="utf-8").splitlines() if l.strip()]
        else:
            print(f"[git_push_gorev] liste dosyasi yok: {liste}", file=sys.stderr)
            return 1

    # Koordinasyon dosyalari her zaman dahil (degismemisse commit'te etkisi olmaz)
    dosyalar += KOORDINASYON

    eklenecek: list[str] = []
    for d in dict.fromkeys(dosyalar):
        if not d:
            continue
        hedef = ROOT / d
        if hedef.exists():
            eklenecek.append(d)
        else:
            takipte = git("ls-files", "--", d).stdout.strip()
            if takipte:
                eklenecek.append(d)  # silinmis ama takipte -> add silmeyi ekler
            else:
                print(f"[git_push_gorev] atlandi (yok): {d}")

    if not eklenecek:
        print("[git_push_gorev] eklenecek dosya yok")
        return 0

    r = git("add", "--", *eklenecek)
    if r.returncode != 0:
        print(f"[git_push_gorev] add hatasi: {r.stderr.strip()[:300]}", file=sys.stderr)
        return 1

    bos = git("diff", "--cached", "--quiet").returncode == 0
    if bos:
        print("[git_push_gorev] commit edecek icerik yok")
        return 0

    r = git("commit", "-m", args.mesaj)
    if r.returncode != 0:
        print(f"[git_push_gorev] commit hatasi: {r.stderr.strip()[:300]}", file=sys.stderr)
        return 1

    dal = dal_adi()
    print(f"[git_push_gorev] commit OK ({dal}): {args.mesaj[:70]}")
    if push_yap(dal):
        print(f"[git_push_gorev] push OK (origin/{dal})")
        return 0
    print("[git_push_gorev] PUSH BASARISIZ — 2 deneme tukendi; daha sonra tekrar deneyin "
          "(catisma varsa: git status + manuel rebase)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
