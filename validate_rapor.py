import sys
sys.path.insert(0, r'Huginn Data Insights/data/orchestrator/tasks/RAPOR-STANDARTI-01')
from os_kontrol import validate_sayfalar
success = validate_sayfalar()
print(f"VALIDASYON: {'BAŞARILI' if success else 'BAŞARISIZ'}")