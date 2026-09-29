from datetime import datetime, timedelta, timezone
from src.company_master.admin_audit import supheli_basarisiz_giris, supheli_skor

utc = timezone.utc
now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=utc)

olaylar_test = [
    {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=1), "detay": {}},
    {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=2), "detay": {}},
    {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=3), "detay": {}},
    {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=4), "detay": {}},
    {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=5), "detay": {}},
    {"olay_tipi": "giris", "basarili": False, "olay_zamani": now - timedelta(minutes=6), "detay": {}},
]

# Check time window
pencere_bas = now - timedelta(minutes=5)
print(f"Window start: {pencere_bas}")

for o in olaylar_test:
    oz = o["olay_zamani"]
    in_window = oz >= pencere_bas
    print(f"  {oz} >= {pencere_bas} = {in_window}")

# Test
from src.company_master.admin_audit import supheli_basarisiz_giris
result = supheli_basarisiz_giris(olaylar_test, now=now, pencere_dk=5, esik=5)
print(f"supheli_basarisiz_giris result: {result}")

skor = supheli_skor(olaylar_test, now=now)
print(f"supheli_skor: {skor}")