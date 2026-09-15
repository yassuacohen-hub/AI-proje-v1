import json, pathlib, sys
ROOT = pathlib.Path(r'C:\Huginn Data Projesi\Huginn Data Insights')
task_file = ROOT / 'data' / 'orchestrator' / 'task_board.json'
with open(task_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

for t in data:
    if t.get('task_id') == 'DEV-01':
        t['sahip'] = 'gelistirici'
        t['durum'] = 'done'
        t['oncelik'] = 'P1'
        t['not'] = 'GitHub Actions CI/CD pipeline tamamlandı: ci.yml güncellendi (lint, test+coverage, security), deploy-staging.yml ve nightly-etl.yml eklendi. 3010 test geçti, 3 atlandı, 126 uyarı.'
        break

with open(task_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Görev panosu güncellendi.')