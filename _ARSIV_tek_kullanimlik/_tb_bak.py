import json
d = json.load(open('data/orchestrator/task_board.json', encoding='utf-8'))
print("toplam", len(d))
for t in d[-5:]:
    print(t['task_id'], t.get('sahip'), t.get('durum'))
