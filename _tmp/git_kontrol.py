# -*- coding: utf-8 -*-
"""Merge/rebase durumu + cakisma isaretcisi + stage edilmis dosya olcumu. Yazmaz, yalniz _tmp/git_kontrol.txt."""
import subprocess
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
VAULT = KOK / "Huginn Data Insights"
CIKTI = Path(__file__).resolve().parent / "git_kontrol.txt"


def git(*a):
    r = subprocess.run(["git", *a], cwd=VAULT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (r.stdout + r.stderr).strip()


gitdir = git("rev-parse", "--git-dir")
gd = (VAULT / gitdir) if not Path(gitdir).is_absolute() else Path(gitdir)
out = [f"git-dir={gd}"]
for ad in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD"):
    out.append(f"  {ad}: {'VAR' if (gd / ad).exists() else 'yok'}")
out.append("unmerged: " + (git("diff", "--name-only", "--diff-filter=U") or "(yok)"))
out.append("stage edilmis: " + str(len([x for x in git("diff", "--cached", "--name-only").splitlines() if x])))
for f in ("data/orchestrator/ajan-chat.jsonl", "docs/MUSTERI_PANEL_ORTAK_TASARIM.md"):
    t = (VAULT / f).read_text(encoding="utf-8-sig", errors="replace").splitlines()
    n = sum(1 for s in t if s.startswith(("<<<<<<< ", ">>>>>>> ")) or s == "=======")
    out.append(f"isaretci {f}: {n} (satir={len(t)})")
out.append("durum -b:\n" + "\n".join(git("status", "-sb").splitlines()[:8]))
out.append("log:\n" + git("log", "--oneline", "-5"))
CIKTI.write_text("\n".join(out) + "\n", encoding="utf-8")
