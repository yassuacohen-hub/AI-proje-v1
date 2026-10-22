import json
path = r'c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json'
with open(path, 'r', encoding='utf-8') as f:
    tasks = json.load(f)

for t in tasks:
    if t.get('id') == 'API-V1-NETWORK-REPORT-01':
        t['durum'] = 'tamamlandi'
        t['tamamlanma_tarihi'] = '2026-10-14'
        t['aciklama'] = '[TAMAMLANDI] GET /v1/companies/{vkn}/network + full-report endpointleri, network_router.py modulu, fraud.py\'ye get_fraud_dict/apply_kvkk_mask fonksiyonlari, test_api_v1_network.py testleri gecti (3 passed, 2 skipped). Web_app.py entegrasyonu tamamandi.'
        t['gereken_testler'] = 'tests/test_api_v1_network.py - 3 passed, 2 skipped (VKN veritabanında yok)'
        print(f"Updated {t.get('id')}: durum={t.get('durum')}")

with open(path, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print("Task board güncellendi")