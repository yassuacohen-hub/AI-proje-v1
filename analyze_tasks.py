import json
with open('Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
print(f'Total tasks: {len(tasks)}')

by_agent = {}
by_status = {}
by_priority = {}

for t in tasks:
    agent = t.get('sahip', 'YOK')
    status = t.get('durum', 'YOK')
    priority = t.get('oncelik', 'YOK')
    
    by_agent[agent] = by_agent.get(agent, 0) + 1
    by_status[status] = by_status.get(status, 0) + 1
    by_priority[priority] = by_priority.get(priority, 0) + 1

print('\nPer Agent:')
for a, c in sorted(by_agent.items(), key=lambda x: -x[1]):
    print(f'  {a}: {c}')

print('\nPer Status:')
for s, c in sorted(by_status.items(), key=lambda x: -x[1]):
    print(f'  {s}: {c}')

print('\nPer Priority:')
for p, c in sorted(by_priority.items(), key=lambda x: -x[1]):
    print(f'  {p}: {c}')

# Active tasks per agent
active = {}
for t in tasks:
    if t.get('durum') in ['aktif', 'devam', 'in_progress']:
        agent = t.get('sahip', 'YOK')
        active[agent] = active.get(agent, 0) + 1

print('\nActive per Agent:')
for a, c in sorted(active.items(), key=lambda x: -x[1]):
    print(f'  {a}: {c}')

# Done tasks per agent
done = {}
for t in tasks:
    if t.get('durum') == 'done':
        agent = t.get('sahip', 'YOK')
        done[agent] = done.get(agent, 0) + 1

print('\nDone per Agent:')
for a, c in sorted(done.items(), key=lambda x: -x[1]):
    print(f'  {a}: {c}')

# Archive tasks per agent
archive = {}
for t in tasks:
    if t.get('durum') == 'archive':
        agent = t.get('sahip', 'YOK')
        archive[agent] = archive.get(agent, 0) + 1

print('\nArchive per Agent:')
for a, c in sorted(archive.items(), key=lambda x: -x[1]):
    print(f'  {a}: {c}')

# Ihsan tasks
ihsan_tasks = [t for t in tasks if t.get('sahip') == 'ihsan']
print(f'\nIhsan tasks: {len(ihsan_tasks)}')
for t in ihsan_tasks:
    print(f"  {t.get('id', 'NO-ID')}: {t.get('durum')} [{t.get('oncelik')}] {t.get('baslik', '')[:60]}")

# Active tasks detail
print('\n=== AKTIF GÖREVLER ===')
for t in tasks:
    if t.get('durum') in ['aktif', 'devam', 'in_progress']:
        print(f"  {t.get('id')}: {t.get('sahip')} [{t.get('oncelik')}] {t.get('baslik')[:80]}")

# Plan tasks detail
print('\n=== PLAN GÖREVLERİ ===')
for t in tasks:
    if t.get('durum') == 'plan':
        print(f"  {t.get('id')}: {t.get('sahip')} [{t.get('oncelik')}] {t.get('baslik')[:80]}")

# Bekleyen tasks detail
print('\n=== BEKLEYEN GÖREVLER ===')
for t in tasks:
    if t.get('durum') == 'bekliyor':
        print(f"  {t.get('id')}: {t.get('sahip')} [{t.get('oncelik')}] {t.get('baslik')[:80]}")