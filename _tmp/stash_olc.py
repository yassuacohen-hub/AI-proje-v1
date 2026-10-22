"""Stash/HEAD/d5299819 ORTAK_TASARIM karsilastirma (salt okunur)."""
import subprocess as s, re

F = "docs/MUSTERI_PANEL_ORTAK_TASARIM.md"


def blob(rev):
    r = s.run(["git", "show", f"{rev}:{F}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else ""


for rev in ["d5299819", "HEAD", "stash@{0}", "stash@{0}^2"]:
    t = blob(rev)
    print(rev, "satir", t.count("\n"),
          "moji", t.count("\u00c3\u0082"),
          "4.8b", len(re.findall(r"^### 4\.8b", t, re.M)),
          "4.8.C", len(re.findall(r"^#### 4\.8\.C", t, re.M)),
          "marker", len(re.findall(r"^(<<<<<<<|>>>>>>>)", t, re.M)))
wt = open(F, encoding="utf-8", errors="replace").read()
print("wt satir", wt.count("\n"), "4.8b", len(re.findall(r"^### 4\.8b", wt, re.M)),
      "4.8.C", len(re.findall(r"^#### 4\.8\.C", wt, re.M)))
# messages.jsonl anahtarlari
import json
with open("data/orchestrator/chat/messages.jsonl", encoding="utf-8-sig") as f:
    ilk = [json.loads(next(f)) for _ in range(1)]
print("ilk kayit anahtarlari", list(ilk[0].keys()))
