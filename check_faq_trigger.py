import json

with open(r'C:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\triggers\utku.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'KVKK-FAQ' in line:
            print(line.strip())