import json
import os

# Update task board
task_board_path = r'c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json'
with open(task_board_path, 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Find and update the task
for task in tasks:
    if task.get('id') == 'API-V1-NETWORK-REPORT-01':
        task['durum'] = 'tamamlandi'
        task['tamamlanma_tarihi'] = '2026-10-14'
        task['aciklama'] = '[TAMAMLANDI] GET /v1/companies/{vkn}/network + full-report endpointleri, network_router.py modulu, fraud.py\'ye get_fraud_dict/apply_kvkk_mask fonksiyonlari, test_api_v1_network.py testleri gecti (3 passed, 2 skipped). Web_app.py entegrasyonu tamamandi.'
        task['gereken_testler'] = 'tests/test_api_v1_network.py - 3 passed, 2 skipped (VKN veritabanında yok)'
        break

# Write back
with open(task_board_path, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print('Task API-V1-NETWORK-REPORT-01 marked as completed')