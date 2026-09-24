from datetime import datetime, timedelta, timezone
from src.company_master.admin_audit import _ulke_kodu_al

# Test _ulke_kodu_al
test_event = {"olay_zamani": datetime.now(timezone.utc), "detay": {"ulke_kodu": "TR"}}
print(f"Detay dict: {_ulke_kodu_al(test_event)}")

test_event2 = {"olay_zamani": datetime.now(timezone.utc), "detay": "{\"ulke_kodu\": \"TR\"}"}
print(f"Detay JSON string: {_ulke_kodu_al(test_event2)}")

test_event3 = {"olay_zamani": datetime.now(timezone.utc), "detay": {}}
print(f"Empty detay: {_ulke_kodu_al(test_event3)}")