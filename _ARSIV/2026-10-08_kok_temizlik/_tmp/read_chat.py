import json
path = "Huginn Data Insights/data/orchestrator/chat/messages.jsonl"
try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Toplam {len(lines)} mesaj:")
    for i, line in enumerate(lines[-10:]):  # son 10
        try:
            msg = json.loads(line)
            print(f"  [{i}] {msg['tarih']} {msg['kimden']} -> {msg['kime']} ({msg['type']}) [{msg.get('task_id','-')}] {msg['mesaj'][:80]}")
        except:
            pass
except FileNotFoundError:
    print("Dosya yok")