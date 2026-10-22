import json

with open('C:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json', encoding='utf-8') as f:
    d = json.load(f)

aktif = [t for t in d if t.get('durum') == 'aktif']
print(f'Aktif durumlu görevler: {len(aktif)}')
for t in aktif:
    print(f'  {t.get("task_id")}: {t.get("baslik")[:80]} | {t.get("sahip")} | {t.get("oncelik")}')

# Bekleyenleri de ara
bekleyen = [t for t in d if t.get('durum') == 'bekliyor']
print(f'\nBekleyen durumlu görevler: {len(bekleyen)}')
for t in bekleyen:
    print(f'  {t.get("task_id")}: {t.get("baslik")[:80]} | {t.get("sahip")} | {t.get("oncelik")}')

# Plan durumluları
plan = [t for t in d if t.get('durum') == 'plan']
print(f'\nPlan durumlu görevler: {len(plan)}')
for t in plan:
    print(f'  {t.get("task_id")}: {t.get("baslik")[:80]} | {t.get("sahip")} | {t.get("oncelik")}')