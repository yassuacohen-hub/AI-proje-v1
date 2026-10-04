"""Kayıp sozluk: 20 etiketli DB satiri + kanit guid uzerinden JOIN.

Onceki deneme 0 sonuc verdi: kanit dosyasindaki guid alani DB'deki
`source_guid` ile ayni degil. Dogru yol `tsg_yazici._source_guid_olustur`
ile guid'i kanittan yeniden uretmek.
"""

import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.company_master.etl.tsg_yazici import (  # noqa: E402
    kanit_dosyalarini_oku, _source_guid_olustur,
)

from sqlalchemy import create_engine, text  # noqa: E402

# --- DB'deki 20 etiketli satir ---
url = None
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if line.strip().startswith("DATABASE_URL="):
        url = line.split("=", 1)[1].strip()
        break

eng = create_engine(url, pool_pre_ping=True)
with eng.connect() as c:
    dolu = c.execute(text(
        "select source_guid, event_type, direction from company_events "
        "where event_type is not null and event_type <> ''"
    )).fetchall()
print(f"1) DB etiketli satir: {len(dolu)}")
for g, et, dr in dolu:
    print(f"   {g}  {et}  {dr}")

db_map = {str(g): (et, dr) for g, et, dr in dolu}

# --- kanit -> guid yeniden uretimi ---
dosyalar = kanit_dosyalarini_oku()
print(f"\n2) KANIT dosyasi: {len(dosyalar)}")

ciftler = defaultdict(set)
bulunmayan = []
for d in dosyalar:
    tur = (d.get("il_turu") or "").strip()
    if not tur:
        continue
    try:
        g = _source_guid_olustur(d)
    except Exception as e:
        print(f"   guid hatasi: {type(e).__name__}: {e}")
        break
    if g in db_map:
        ciftler[tur].add(db_map[g])
    else:
        bulunmayan.append((tur, g))

print(f"3) JOIN: {len(ciftler)} farkli il_turu eslesti, {len(bulunmayan)} bulunamadi")

harita, coklu = {}, []
for tur, vals in sorted(ciftler.items()):
    if len(vals) == 1:
        et, dr = next(iter(vals))
        harita[tur] = {"event_type": et, "direction": dr}
    else:
        coklu.append((tur, sorted(vals)))

print(f"\n4) HARITA: {len(harita)} tekil, {len(coklu)} celiskili")
for tur, v in sorted(harita.items()):
    print(f"   {tur:44} -> {v['event_type']:26} / {v['direction']}")
for tur, v in coklu:
    print(f"   CELISKI {tur}: {v}")

# --- DB'deki etiketli guid'lerin kanitta karsiligi var mi? (geri kontrol) ---
karsi = {db_map[g] for g in db_map if any(
    _source_guid_olustur(d) == g for d in dosyalar if (d.get("il_turu") or "").strip()
)}
kapsam = len(karsi) / len(db_map) if db_map else 0
print(f"\n5) KAPSAM: DB'deki {len(db_map)} etiketli guid'den {len(karsi)} tanesi kanittan turetildi (%{kapsam:.0f})")

def slug(m):
    s = unicodedata.normalize("NFKD", m).encode("ascii", "ignore").decode()
    return "_".join(s.upper().replace("-", " ").split()).lower()

uyumsuz = [t for t, v in harita.items() if slug(t) != v["event_type"]]
print(f"6) SLUG KURALI: {len(harita) - len(uyumsuz)}/{len(harita)} uyumlu")
for t in uyumsuz:
    print(f"   {t:44} slug={slug(t):26} db={harita[t]['event_type']}")

out = ROOT / "scripts" / "_ilan_turu_esleme_kurtarma.json"
out.write_text(json.dumps(harita, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n7) YAZILDI: {out.relative_to(ROOT)}")
