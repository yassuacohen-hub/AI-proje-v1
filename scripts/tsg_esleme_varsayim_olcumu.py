"""VERI-TSG-ESLEME-CASE-01 — varsayım ölçümü (D-224, D-238).

Brif üç varsayım koyuyor:
  V1) `olay_esle` + `ILAN_TURU_ESLEME` tek kaynak.
  V2) `company_events.event_type` kolonu var.
  V3) Canlı COUNT sorgusu yapılabilir.

Ayrıca brifin NEDEN bölümündeki iddiayı sınıyor:
  "306/326 kanıt kaydında event_type=NULL **çünkü eşleşme başarısız**"
Bu, eşleşmenin başarısız olduğu *anlamına gelir*. Kanıt dosyalarının kaçında
gerçekten `il_turu` DOLDUR? Boşsa NULL beklenen davranıştır ve iddia çürür.

Salt okunur. Hiçbir şey yazmaz.
"""

import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KANIT = os.path.join(KOK, "data", "kanit")

sys.path.insert(0, KOK)
from skills.services.ticaret_sicili_kanit import _asciiye, olay_esle  # noqa: E402


def v1_tek_kaynak() -> None:
    print("== V1 tek kaynak ==")
    kokler = ("src", "scripts", "skills", "tests")
    eslesen: list[str] = []
    kok = KOK
    for ad in kokler:
        for dirpath, _dirs, files in os.walk(os.path.join(kok, ad)):
            if any(x in dirpath for x in ("_ARSIV", "backups", "__pycache__")):
                continue
            for f in files:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dirpath, f)
                try:
                    s = open(p, encoding="utf-8").read()
                except (OSError, UnicodeDecodeError):
                    continue
                if "ILAN_TURU_ESLEME" in s or "def olay_esle" in s:
                    eslesen.append(os.path.relpath(p, kok))
    print(f"  tanim/import eden dosya: {len(eslesen)}")
    for x in eslesen:
        print(f"    -> {x}")


def v2_sema() -> None:
    print("== V2 company_events.event_type ==")
    dosya = os.path.join(KOK, "src", "company_master", "schema", "migrations", "0037_tsg_olay_hatti.sql")
    if os.path.exists(dosya):
        s = open(dosya, encoding="utf-8").read()
        print(f"  0037 dosyasi: VAR, event_type kolonu: {'event_type' in s}")
    else:
        print("  0037 dosyasi: YOK -> migrasyon adi farkli olabilir")
    for ad in sorted(os.listdir(os.path.join(KOK, "src", "company_master", "schema", "migrations"))):
        if ad.startswith("003") and ad.endswith(".sql"):
            p = os.path.join(KOK, "src", "company_master", "schema", "migrations", ad)
            try:
                s = open(p, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            if "company_events" in s:
                print(f"  {ad}: company_events + event_type={'event_type' in s}")


def v3_canli() -> None:
    print("== V3 canli DB ==")
    try:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(KOK, ".env"))
        import psycopg

        dsn = os.environ.get("DATABASE_URL")
        if not dsn:
            print("  HATA: DATABASE_URL yok -> V3 tutmuyor, dur")
            return
        with psycopg.connect(dsn, connect_timeout=15) as bag:
            with bag.cursor() as cur:
                cur.execute("select table_schema from information_schema.tables where table_name='company_events'")
                satirlar = cur.fetchall()
                print(f"  company_events sema sayisi: {len(satirlar)} -> {[r[0] for r in satirlar]}")
                cur.execute(
                    "select count(*) from information_schema.columns "
                    "where table_schema='public' and table_name='company_events' and column_name='event_type'"
                )
                print(f"  public.event_type kolonu: {cur.fetchone()[0]}")
                cur.execute(
                    "select coalesce(event_type,'<NULL>') as et, direction, count(*) "
                    "from public.company_events group by 1,2 order by 3 desc"
                )
                print("  -- event_type x direction --")
                toplam = 0
                for et, dr, adet in cur.fetchall():
                    print(f"     {et[:60]:60s} {str(dr):10s} {adet}")
                    toplam += adet
                print(f"  TOPLAM: {toplam}")
    except Exception as exc:  # noqa: BLE001
        print(f"  HATA: {type(exc).__name__}: {exc}")


def kanit_olcumu() -> None:
    """Brif'in '306 NULL çünkü eşleşme başarısız' iddiasının sınaması."""
    print("== Kanit dosyalari: il_turu dolulugu ==")
    if not os.path.isdir(KANIT):
        print(f"  HATA: {KANIT} yok")
        return
    dosyalar = [f for f in os.listdir(KANIT) if f.endswith(".json")]
    dolu = 0
    bos = 0
    turler: dict[str, int] = {}
    eslesen = 0
    eslesmeyen = 0
    for ad in dosyalar:
        try:
            rec = json.load(open(os.path.join(KANIT, ad), encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(rec, list):
            kayitlar = rec
        elif isinstance(rec, dict) and "il_turu" in rec:
            kayitlar = [rec]
        else:
            kayitlar = rec.get("ilanlar") or rec.get("kayitlar") or [] if isinstance(rec, dict) else []
        for k in kayitlar:
            if not isinstance(k, dict):
                continue
            t = (k.get("il_turu") or "").strip()
            if t:
                dolu += 1
                turler[t] = turler.get(t, 0) + 1
            else:
                bos += 1
                continue
            if olay_esle(t)[0]:
                eslesen += 1
            else:
                eslesmeyen += 1
    print(f"  dosya: {len(dosyalar)} | il_turu DOLU: {dolu} | il_turu BOS: {bos}")
    print(f"  dolu olanlardan eslesen: {eslesen} | eslesmeyen (unknown): {eslesmeyen}")
    print(f"  benzersiz il_turu: {len(turler)}")
    for t, adet in sorted(turler.items(), key=lambda x: -x[1])[:20]:
        et, dr = olay_esle(t)
        print(f"     [{adet:3d}] {_asciiye(t)[:66]:66s} -> {et} / {dr}")


if __name__ == "__main__":
    v1_tek_kaynak()
    print()
    v2_sema()
    print()
    v3_canli()
    print()
    kanit_olcumu()
