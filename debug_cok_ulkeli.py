from datetime import datetime, timedelta, timezone
from src.company_master.admin_audit import (
    supheli_basarisiz_giris, supheli_cok_ulkeli_ip, supheli_gece_toplu_export,
    supheli_skor, supheli_etiket
)

utc = timezone.utc
now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=utc)

# Debug supheli_cok_ulkeli_ip
olaylar_ulkeler = [
    {"olay_zamani": now - timedelta(hours=i), "detay": {"ulke_kodu": "TR"}}
    for i in range(1, 4)  # TR, TR, TR -> 1 ülke
] + [
    {"olay_zamani": now - timedelta(hours=5), "detay": {"ulke_kodu": "DE"}}
]

print("Events:")
for o in olaylar_ulkeler:
    print(f"  {o['olay_zamani']} - {o['detay']}")

# Check time window
from src.company_master.admin_audit import _olay_zamani_al, _pencere_baslangic
pencere_bas = now - timedelta(hours=24)
print(f"Window start: {pencere_bas}")

for o in olaylar_ulkeler:
    oz = _olay_zamani_al(o)
    print(f"  {oz} >= {pencere_bas} = {oz >= pencere_bas}")

# Test the function
from src.company_master.admin_audit import supheli_cok_ulkeli_ip
result = supheli_cok_ulkeli_ip(olaylar_ulkeler, now=now, pencere_saat=24, esik=2)
print(f"Result: {result}")