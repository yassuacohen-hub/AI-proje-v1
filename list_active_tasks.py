import json
import os

# Use absolute path
task_board_path = os.path.join(os.getcwd(), "Huginn Data Insights", "data", "orchestrator", "task_board.json")

with open(task_board_path, encoding='utf-8') as f:
    data = json.load(f)

# Filter active tasks (not done, archive, iptal)
active_statuses = ['active', 'pending', 'in_progress', 'aktif', 'bekliyor', 'plan']
active_tasks = [t for t in data if t.get('durum', '').lower() in active_statuses]

print(f"AKTİF GÖREVLER: {len(active_tasks)} adet\n")
print(f"{'Task ID':<45} | {'Öncelik':<6} | {'Sahip':<8} | {'Durum':<10} | Başlık")
print("-" * 140)

for t in sorted(active_tasks, key=lambda x: (x.get('oncelik') != 'P0', x.get('oncelik') != 'P1', x.get('sahip', ''))):
    task_id = t.get('task_id', '')[:44]
    oncelik = t.get('oncelik', '')
    sahip = t.get('sahip', '')[:7]
    durum = t.get('durum', '')[:9]
    baslik = t.get('baslik', '')[:60]
    print(f"{task_id:<45} | {oncelik:<6} | {sahip:<8} | {durum:<10} | {baslik}")

print(f"\nToplam: {len(active_tasks)} aktif görev")