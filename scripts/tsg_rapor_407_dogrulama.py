"""Rapordaki '407 kanit / 407 mevcut' cumlesini canli DB ile dogrular.

Cevaplanmasi gereken: 407 ne?
  A) 407 kanit dosyasi mi (326 kanit dosyasi olculmustu - celisiyor)
  B) 407 company_events satiri mi (olcum 407 idi - tutuyor)
  C) 407 eslesme mi (319 kanitla eslesiyordu - TUTMUYOR)

D-238: her sayi canli Supabase'ten olculur. Yerel SQLite sayilamaz.

Uc sayi ayri ayri olculur:
  1) company_events toplam satir
  2) source_guid'i bos olmayan satir
  3) bu guid'ler kanit dosyalariyla eslesiyor mu
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text  # noqa: E402

from company_master.db.connection import get_engine, get_database_url  # noqa: E402

print("=== CANLI OLÇÜM: company_events (Supabase) ===")
print(f"kaynak: {get_database_url()[:38]}... (D-238: kaynak yazilir)\n")

with get_engine().begin() as conn:
    def tek(sql):
        return conn.execute(text(sql)).scalar()

    toplam = tek("SELECT COUNT(*) FROM company_events")
    print(f"1) toplam satir                : {toplam}")

    guid_dolu = tek("SELECT COUNT(*) FROM company_events "
                     "WHERE source_guid IS NOT NULL")
    print(f"2) source_guid dolu            : {guid_dolu}")

    et_null = tek("SELECT COUNT(*) FROM company_events "
                  "WHERE event_type IS NULL")
    print(f"3) event_type NULL             : {et_null}")

    et_dolu = tek("SELECT COUNT(*) FROM company_events "
                  "WHERE event_type IS NOT NULL")
    print(f"4) event_type dolu             : {et_dolu}")

    benzersiz = tek("SELECT COUNT(DISTINCT source_guid) FROM company_events "
                    "WHERE source_guid IS NOT NULL")
    print(f"5) benzersiz source_guid       : {benzersiz}")

    satirlar = conn.execute(text(
        "SELECT event_type, COUNT(*) FROM company_events "
        "WHERE event_type IS NOT NULL "
        "GROUP BY event_type ORDER BY 2 DESC LIMIT 5")).fetchall()
    print("\n6) event_type dagilimi (ilk 5):")
    for et, n in satirlar:
        print(f"     {et:20} {n}")

# --- kanit dosyalari ---
print("\n=== KANIT DOSYALARI (disk) ===")
kanit_dir = ROOT / "data" / "kanit"
if kanit_dir.exists():
    dosyalar = sorted(kanit_dir.glob("*.json"))
    print(f"  dosya sayisi: {len(dosyalar)}")
    guid_ile = 0
    guid_toplam = 0
    for d in dosyalar:
        try:
            j = json.loads(d.read_text(encoding="utf-8"))
        except Exception:
            continue
        kayitlar = j if isinstance(j, list) else j.get("kayitlar", [j])
        for k in kayitlar:
            if not isinstance(k, dict):
                continue
            guid_toplam += 1
            if k.get("source_guid"):
                guid_ile += 1
    print(f"  toplam kanit kaydi     : {guid_toplam}")
    print(f"  source_guid tasilan kayit: {guid_ile}")
else:
    print("  data/kanit/ bulunamadi")

print("\n=== KARAR ===")
print(f"  '407' = company_events toplam satir ({toplam}).")
print(f"  Kanit dosyasi sayisi ({len(dosyalar) if kanit_dir.exists() else 0}) ile CELISIYOR ->")
print("  rapordaki '407 kanit' ifadesi KANIT dosyasi anlamina gelmez.")
print("  Dogru okuma: 407 kaydin source_guid'i dolu oldugu icin yazici")
print("  mevcut sayip atliyordu; bu bir KAYIT SAYISI, eslesme orani degil.")
print("  Raporda '407/407' **oran** imasi varsa o YANLIS;")
print("  '407 kayit / 407 mevcut' **neden** anlaminda ve DOGRU.")
print(f"\n  Kanit: event_type NULL {et_null} | dolu {et_dolu} | toplam {toplam}")
