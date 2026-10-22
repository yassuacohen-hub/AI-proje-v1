import json
import sys
sys.path.insert(0, r'Huginn Data Insights/data/orchestrator/tasks/ANKARA-15-OSB-KOORDINAT-OLCUM-01')
from os_kontrol import validate_koordinatlar

with open(r'Huginn Data Insights/data/orchestrator/tasks/ANKARA-15-OSB-KOORDINAT-OLCUM-01/koordinat_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

valid, message = validate_koordinatlar(data['coordinates'])
print(f'VALIDASYON SONUCU:')
print(f'  Valid: {valid}')
print(f'  Message: {message}')