"""Canli PostgreSQL'de TSG tesliminin durumunu olcer.

Yerel dosya aramasi ise sonucu getirdi: DB uzak bir Postgres (Supabase pooler).
Bu script:
  1) company_events tablosunun var oldugunu dogrular
  2) event_type IS NULL sayisini olcer (teslim oncesi 404, sonrasi 387 olmali)
  3) TSG kayitlarini ilan turune gore dagutir (ozellikle 'unknown')
  4) kanit dosyalariyla eslestirme oranini olcer (319/407 bekleniyor)
"""

import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from sqlalchemy import create_engine, text  # noqa: E402


def _find_root():
    here = Path(__file__).resolve().parent
    for c in [here, *here.parents]:
        if (c / ".env").exists() and "DATABASE_URL" in (c / ".env").read_text(encoding="utf-8"):
            return c
    return here


ROOT = _find_root()
url = None
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if line.strip().startswith("DATABASE_URL="):
        url = line.split("=", 1)[1].strip()
        break

if not url:
    print("HATA: DATABASE_URL yok")
    raise SystemExit(1)

# Sifre olusturma; sadece hata durumunda goster
gizli = url.split("@")[0].split("://")[0] + "@***"
print(f"1) BAGLANTI: {gizli}")

eng = create_engine(url, pool_pre_ping=True)
with eng.connect() as c:
    print("\n2) TABLO KONTROLU")
    var = c.execute(text(
        "select column_name from information_schema.columns "
        "where table_name='company_events' order by ordinal_position"
    )).fetchall()
    kolonlar = [r[0] for r in var]
    print(f"   company_events kolonlari ({len(kolonlar)}): {', '.join(kolonlar)}")
    print(f"   event_type kolonu var mi: {'EVET' if 'event_type' in kolonlar else 'HAYIR'}")

    print("\n3) event_type boslugu (teslim oncesi 404 -> teslim sonrasi 387 beklenir)")
    n = c.execute(text(
        "select count(*) from company_events where event_type is null or event_type=''"
    )).scalar()
    print(f"   event_type IS NULL/bos toplam: {n}")

    print("\n4) TSG kaynakli kayitlar")
    try:
        ts = c.execute(text(
            "select count(*) from company_events where event_source='TSG'"
        )).scalar()
        print(f"   event_source='TSG' kayit: {ts}")
        dagilim = c.execute(text(
            "select coalesce(nullif(event_type,''),'(bos)') as t, count(*) "
            "from company_events where event_source='TSG' "
            "group by 1 order by 2 desc limit 15"
        )).fetchall()
        print("   ilk 15 event_type dagilimi:")
        for t, adet in dagilim:
            print(f"     {t:34} {adet}")
        unk = c.execute(text(
            "select count(*) from company_events where event_source='TSG' "
            "and (event_type='UNKNOWN' or event_type='unknown')"
        )).scalar()
        print(f"   UNKNOWN kalan: {unk}")
    except Exception as e:
        print(f"   TSG sorgusu hata: {type(e).__name__}: {str(e)[:160]}")

    print("\n5) kanit <-> kayit eslesmesi")
    kanitlar = list((ROOT / "data" / "kanit").rglob("*.json"))
    guidler = set()
    for k in kanitlar:
        try:
            d = json.loads(k.read_text(encoding="utf-8"))
        except Exception:
            continue
        for alan in ("source_guid", "guid", "ilan_guid"):
            if isinstance(d, dict) and d.get(alan):
                guidler.add(str(d[alan]))
                break
    print(f"   kanit dosyasi: {len(kanitlar)}, cikarilan guid: {len(guidler)}")
    if guidler:
        try:
            eslesen = c.execute(text(
                "select count(*) from company_events where source_guid = any(:g)"
            ), {"g": list(guidler)}).scalar()
            toplam = c.execute(text("select count(*) from company_events")).scalar()
            print(f"   kanitla eslesen kayit: {eslesen}")
            print(f"   toplam kayit: {toplam}  ->  eslesmeyen: {toplam - eslesen}")
        except Exception as e:
            print(f"   eslestirme sorgusu hata: {type(e).__name__}: {str(e)[:160]}")
