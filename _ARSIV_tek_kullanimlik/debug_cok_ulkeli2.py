from datetime import datetime, timedelta, timezone
from src.company_master.admin_audit import _ulke_kodu_al, _olay_zamani_al

utc = timezone.utc
now = datetime(2026, 9, 24, 12, 0, 0, tzinfo=utc)

olaylar_ulkeler = [
    {"olay_zamani": now - timedelta(hours=i), "detay": {"ulke_kodu": "TR"}}
    for i in range(1, 4)  # TR, TR, TR -> 1 ülke
] + [
    {"olay_zamani": now - timedelta(hours=5), "detay": {"ulke_kodu": "DE"}}
]

pencere_bas = now - timedelta(hours=24)

ulkeler = set()
for olay in olaylar_ulkeler:
    olay_zamani = olay["olay_zamani"]
    if olay_zamani >= datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc):
        ulke = olay.get("detay", {}).get("ulke_kodu")
        if ulke:
            print(f"Adding country: {ulke}")
            print(f"  Event time: {olay_zamani}")
            print(f"  >= {pencere_bas} = {olay_zamani >= pencere_bas}")

print("Done")

# Let me trace through the actual function
from src.company_master.admin_audit import supheli_cok_ulkeli_ip
result = supheli_cok_ulkeli_ip(olaylar_ulkeler, now=now, pencere_saat=24, esik=2)
print(f"Result: {result}")

# Let me add debug inside the function
from src.company_master import admin_audit
original_ulke_kodu_al = admin_audit._ulke_kodu_al
original_olay_zamani_al = admin_audit._olay_zamani_al

def debug_ulke_kodu_al(olay):
    result = original_ulke_kodu_al(olay)
    print(f"  _ulke_kodu_al({olay.get('detay')}) = {result}")
    return result

def debug_olay_zamani_al(olay):
    result = original_olay_zamani_al(olay)
    print(f"  _olay_zamani_al({olay.get('olay_zamani')}) = {result}")
    return result

admin_audit._ulke_kodu_al = debug_ulke_kodu_al
admin_audit._olay_zamani_al = debug_olay_zamani_al

result = supheli_cok_ulkeli_ip(olaylar_ulkeler, now=now, pencere_saat=24, esik=2)
print(f"Result: {result}")