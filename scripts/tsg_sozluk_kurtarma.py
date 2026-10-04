"""Kayıp ILAN_TURU_ESLEME sozlugunu canli DB'den geri cikarir.

Gerekce (D-224): sozlugu uydurmak yasak. Elimizde **olculmus** bir kaynak
var: 319 `company_events` satiri eski dogru kodla yazildi, `event_type` ve
`direction` dolu. Kanit dosyalariyla `source_guid` uzerinden eslestirilince
`il_turu -> (event_type, direction)` ciftleri dogrudan cikarilir.

Bu script sadece OKUR ve haritayi raporlar + JSON olarak diske yazar.
"""

import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]

# --- kanit dosyalarini oku: il_turu + guid ---
def kanitlari_oku():
    out = []
    for p in sorted((ROOT / "data" / "kanit").rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict):
            out.append((p.name, d))
    return out

kanitlar = kanitlari_oku()
print(f"1) KANIT: {len(kanitlar)} dosya")

# --- DB'den dolu satirlari cek ---
from sqlalchemy import create_engine, text  # noqa: E402

url = None
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if line.strip().startswith("DATABASE_URL="):
        url = line.split("=", 1)[1].strip()
        break

eng = create_engine(url, pool_pre_ping=True)
with eng.connect() as c:
    satirlar = c.execute(text(
        "select source_guid, event_type, direction from company_events "
        "where event_type is not null and event_type <> ''"
    )).fetchall()
print(f"2) DB: event_type dolu {len(satirlar)} satir")

db_map = {}
for guid, et, dr in satirlar:
    if guid:
        db_map[str(guid)] = (et, dr)

# --- kanit guid'lerini bul ---
def guid_bul(d):
    for a in ("source_guid", "guid", "ilan_guid", "id"):
        if d.get(a):
            return str(d[a])
    return None

# --- eslestir ---
ciftler = defaultdict(set)
bulunamayan = 0
for ad, d in kanitlar:
    g = guid_bul(d)
    tur = (d.get("il_turu") or "").strip()
    if not g or not tur or g not in db_map:
        bulunamayan += 1
        continue
    ciftler[tur].add(db_map[g])

print(f"3) ESLESTIRME: {len(ciftler)} farkli il_turu, bulunamayan {bulunamayan}")

# --- tekil olanlar: her tur icin tek cift olan harita ---
harita = {}
coklu = []
for tur, degerler in sorted(ciftler.items()):
    if len(degerler) == 1:
        et, dr = next(iter(degerler))
        harita[tur] = {"event_type": et, "direction": dr}
    else:
        coklu.append((tur, sorted(degerler)))

print(f"4) HARITA: {len(harita)} tekil, {len(coklu)} celiskili")

print("\n   il_turu -> event_type / direction")
for tur, v in sorted(harita.items()):
    print(f"     {tur:44} -> {v['event_type']:28} / {v['direction']}")

if coklu:
    print("\n   CELISKILI (haritaya alinmadi):")
    for tur, d in coklu:
        print(f"     {tur}: {d}")

# --- kontrol: slug kurali gecerli mi (ASCII -> lower, bosluk -> _) ---
def slug(metin):
    s = unicodedata.normalize("NFKD", metin).encode("ascii", "ignore").decode()
    return "_".join(s.upper().replace("-", " ").split()).lower()

uyumsuz = [t for t, v in harita.items() if slug(t) != v["event_type"]]
print(f"\n5) SLUG KURALI: {len(harita) - len(uyumsuz)}/{len(harita)} uyumlu")
for t in uyumsuz:
    print(f"     {t:44} slug={slug(t):28} db={harita[t]['event_type']}")

cikti = ROOT / "scripts" / "_ilan_turu_esleme_kurtarma.json"
cikti.write_text(
    json.dumps(harita, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"\n6) YAZILDI: {cikti.relative_to(ROOT)} ({len(harita)} anahtar)")
