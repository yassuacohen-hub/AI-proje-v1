# -*- coding: utf-8 -*-
"""firmalar_full.jsonl'ye NACE bilgisi ve vergi_no placeholder ekler."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ostim" / "firmalar_full.jsonl"
TMP = ROOT / "data" / "ostim" / "firmalar_full_enriched.jsonl"
MAP = ROOT / "data" / "nace_to_ostim_sektor.json"

TURKISH = [("ı","i"),("ş","s"),("ğ","g"),("ç","c"),("ö","o"),("ü","u"),("İ","I")]

def norm(s):
    if not s: return ""
    s = s.lower()
    for tr, asc in TURKISH: s = s.replace(tr, asc)
    return s

mapping = json.loads(MAP.read_text(encoding="utf-8"))
sektor_to_nace = {}
for key, d in mapping.items():
    if key == "_meta": continue
    sektor = d.get("sektor")
    if not sektor: continue
    nace_list = []
    for nace in d.get("nace_codes", []):
        nace_list.append({
            "code": nace["code"],
            "name_tr": nace.get("name_tr", ""),
            "relevance": nace.get("relevance", "Orta"),
        })
    if nace_list:
        sektor_to_nace[sektor] = nace_list

nace_kw_index = []
for key, d in mapping.items():
    if key == "_meta": continue
    for nace in d.get("nace_codes", []):
        for kw in nace.get("keywords", []):
            if kw:
                nace_kw_index.append((norm(kw), nace["code"], nace.get("name_tr","")))

def pick_nace_from_sektor(sektor):
    if not sektor or sektor not in sektor_to_nace:
        return (None, None, "none")
    liste = sorted(sektor_to_nace[sektor], key=lambda n: (n["relevance"] != "Yuksek", n["code"]))
    if liste:
        n = liste[0]
        return (n["code"], n["name_tr"], "high" if n["relevance"] == "Yuksek" else "medium")
    return (None, None, "none")

def predict_nace_from_unvan(unvan):
    if not unvan: return (None, None, "none")
    u = norm(unvan)
    for kw, code, name in nace_kw_index:
        if kw in u:
            return (code, name, "medium")
    return (None, None, "none")

total = 0
nace_dolu = 0
sektor_dolu = 0
conf_dist = {"high":0, "medium":0, "low":0, "none":0}
with open(DATA, "r", encoding="utf-8") as fi, open(TMP, "w", encoding="utf-8") as fo:
    for line in fi:
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        total += 1
        if rec.get("sektor"):
            sektor_dolu += 1
            code, name, conf = pick_nace_from_sektor(rec["sektor"])
        else:
            code, name, conf = predict_nace_from_unvan(rec.get("unvan", ""))
        rec["nace_code"] = code
        rec["nace_name_tr"] = name
        rec["nace_confidence"] = conf
        rec["vergi_no"] = None
        rec["nace_source"] = "sektor_reverse" if rec.get("sektor") and code else ("unvan_keyword" if code else "none")
        conf_dist[conf] += 1
        if code: nace_dolu += 1
        fo.write(json.dumps(rec, ensure_ascii=False) + "\n")

backup = DATA.with_suffix(".backup2.jsonl")
if not backup.exists():
    shutil.copy2(DATA, backup)
DATA.unlink()
TMP.rename(DATA)

print(f"Toplam: {total}")
print(f"Sektorlu: {sektor_dolu}")
print(f"NACE kodu eklenen: {nace_dolu} ({nace_dolu*100/max(total,1):.1f}%)")
print(f"Guven dagilimi: {conf_dist}")
print(f"Yedek: {backup}")
print(f"Guncellenen: {DATA} ({DATA.stat().st_size:,} bytes)")
