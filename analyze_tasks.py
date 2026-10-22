import json

with open('C:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json', encoding='utf-8') as f:
    d = json.load(f)

from collections import Counter
durumlar = Counter(t.get('durum', 'N/A') for t in d)
print('Görev Durumları:')
for k, v in durumlar.most_common():
    print(f'  {k}: {v}')

ajanlar = Counter(t.get('sahip', 'N/A') for t in d)
print('\nAjan Başına Görev:')
for k, v in ajanlar.most_common():
    print(f'  {k}: {v}')

oncelikler = Counter(t.get('oncelik', 'N/A') for t in d)
print('\nÖncelikler:')
for k, v in oncelikler.most_common():
    print(f'  {k}: {v}')

aktif = [t for t in d if t.get('durum') in ['bekliyor', 'devam ediyor', 'acik']]
print(f'\nAktif Görevler: {len(aktif)}')
for t in aktif:
    print(f'  {t.get("task_id")}: {t.get("baslik")[:60]} | {t.get("sahip")} | {t.get("oncelik")} | {t.get("durum")}')

# P0/P1 kritik görevler
kritik = [t for t in d if t.get('oncelik') in ['P0', 'P1'] and t.get('durum') in ['bekliyor', 'devam ediyor', 'acik']]
print(f'\nKritik Aktif Görevler (P0/P1): {len(kritik)}')
for t in kritik:
    print(f'  {t.get("task_id")}: {t.get("baslik")[:60]} | {t.get("sahip")} | {t.get("oncelik")} | {t.get("durum")}')