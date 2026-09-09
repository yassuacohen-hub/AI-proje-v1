"""OSTİM scraped veriye NACE tabanlı sektör atama (kalıcı, dosya bazlı)."""
import json
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ostim" / "firmalar_full.jsonl"
TMP = ROOT / "data" / "ostim" / "firmalar_full_sektorlu.jsonl"
MAP = ROOT / "data" / "nace_to_ostim_sektor.json"

TURKISH = [("\u0131","i"),("\u015f","s"),("\u011f","g"),("\u00e7","c"),("\u00f6","o"),("\u00fc","u"),("\u0130","I")]

def norm(s: str) -> str:
    if not s: return ""
    s = s.lower()
    for tr, asc in TURKISH: s = s.replace(tr, asc)
    return s

mapping = json.loads(MAP.read_text(encoding="utf-8"))
kw_index: List[Tuple[str, str]] = []
for key, d in mapping.items():
    if key == "_meta": continue
    sektor = d.get("sektor")
    if not sektor: continue
    for nace in d.get("nace_codes", []):
        for kw in nace.get("keywords", []):
            if kw:
                n = norm(kw)
                if n: kw_index.append((n, sektor))

def tahmin(unvan: str):
    if not unvan: return None
    u = norm(unvan)
    for kw, sektor in kw_index:
        if kw in u: return sektor
    return None

total = 0
dolu = 0
with open(DATA, "r", encoding="utf-8") as fi, open(TMP, "w", encoding="utf-8") as fo:
    for line in fi:
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        total += 1
        if rec.get("sektor"):
            dolu += 1
        else:
            s = tahmin(rec.get("unvan", ""))
            rec["sektor"] = s
            if s: dolu += 1
        fo.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"Toplam: {total}, sektorlu: {dolu} ({dolu*100/max(total,1):.1f}%)")

DATA.replace(DATA.with_suffix(".backup.jsonl"))
TMP.replace(DATA)
print(f"Guncellendi: {DATA} ({DATA.stat().st_size} bytes)")

from collections import Counter
c = Counter()
with open(DATA, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            r = json.loads(line)
            c[r.get("sektor") or "<bos>"] += 1
print("\nSektor dagilimi (ilk 15):")
for s, n in c.most_common(15):
    print(f"  {s}: {n}")