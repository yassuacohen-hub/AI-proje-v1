import json
with open('c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

from collections import Counter
status_counts = Counter(t.get('durum', 'unknown') for t in tasks)
print('=== DURUM DAGILIMI ===')
for s, c in sorted(status_counts.items()):
    print(f'  {s}: {c}')

# Active by agent
aktif = [t for t in tasks if t.get('durum') == 'aktif']
print(f'\n=== AKTIF ({len(aktif)}) ===')
by_agent = {}
for t in aktif:
    a = t.get('ajan') or t.get('sahip') or 'none'
    by_agent.setdefault(a, []).append(t)

for agent, items in sorted(by_agent.items()):
    print(f'\n  {agent} ({len(items)}):')
    for t in items:
        print(f'  - {t.get("id")}: {t.get("baslik")[:80]} | {t.get("oncelik")}')

# Pending P0/P1
pending = [t for t in tasks if t.get('durum') == 'pending' and t.get('oncelik') in ['P0', 'P1']]
print(f'\n=== BEKLEYEN P0/P1 ({len(pending)}) ===')
for t in pending[:30]:
    a = t.get('ajan') or t.get('sahip') or 'none'
    print(f'  {t.get("id")}: {t.get("baslik")[:80]} | {t.get("oncelik")} | ajan: {a}')

# Pending all
pending_all = [t for t in tasks if t.get('durum') == 'pending']
print(f'\n=== BEKLEYEN TUM ({len(pending_all)}) ===')
by_prio = {}
for t in pending_all:
    p = t.get('oncelik', 'P9')
    by_prio.setdefault(p, []).append(t)
for p in ['P0', 'P1', 'P2', 'P3']:
    if p in by_prio:
        print(f'  {p}: {len(by_prio[p])}')