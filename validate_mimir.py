import sys
sys.path.insert(0, r'Huginn Data Insights/data/orchestrator/tasks/MIMIR-RAPOR-DD-01')
from os_kontrol import validate_raporlar
success = validate_raporlar()
print(f"VALIDASYON: {'BAŞARILI' if success else 'BAŞARISIZ'}")