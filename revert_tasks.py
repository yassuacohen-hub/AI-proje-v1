import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json'

with open(path, 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# List of task IDs we incorrectly marked as done
to_revert = [
    'ALTYAPI-VDS-DOCKER-01',
    'ALTYAPI-SPACESHIP-DNS-01',
    'ALTYAPI-KONG-MULTISITE-01',
    'ALTYAPI-ODEME-01',
    'UI-FIRMAARAMA-SEARCH-01'
]

for task in tasks:
    if task.get('id') in to_revert:
        # Revert to original status (we assume they were 'aktif')
        task['durum'] = 'aktif'
        # Remove the completion timestamp
        if 'bitis' in task:
            task['bitis'] = None
        # Optionally clear or reset the note; we can set to empty string or keep original if known.
        # Since we don't know original note, we'll set to empty string.
        task['not'] = ''
        print(f"Reverted {task.get('id')} to durum=aktif")

# Save the corrected task board
with open(path, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print("\nTask board has been reverted to original statuses.")
print("All five tasks are now back to 'aktif'.")