import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json'

with open(path, 'r', encoding='utf-8') as f:
    tasks = json.load(f)

to_check = [
    'ALTYAPI-VDS-DOCKER-01',
    'ALTYAPI-SPACESHIP-DNS-01',
    'ALTYAPI-KONG-MULTISITE-01',
    'ALTYAPI-ODEME-01',
    'UI-FIRMAARAMA-SEARCH-01'
]

print("Current status of reverted tasks:")
for task in tasks:
    if task.get('id') in to_check:
        print(f"{task.get('id')}: durum={task.get('durum')}, bitis={task.get('bitis')}, not='{task.get('not')}'")