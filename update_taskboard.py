import json
from datetime import datetime, timezone

path = 'data/orchestrator/task_board.json'
with open(path, encoding='utf-8') as f:
    tasks = json.load(f)

# Eşleştirme için brief dosya yolu kullanılıyor (Türkçe karakterlerle task_id güvenilir değil)
briefs = [
    'plans/brief_yasu_API-KVKK-KONTROL-25.md',
    'plans/brief_yasu_TEST-VISIBILITY-ENTEGRASYON-27.md',
    'plans/brief_yasu_API-LAYER2-DINAMIK-YÜKLEME-30.md',
    'plans/brief_yasu_KONTROL-KVKK-MASKELEME-31.md',
    'plans/brief_utku_UI-ADMIN-KVKK-MODU-26.md',
    'plans/brief_utku_UI-ADMIN-KVKK-RAPOR-28.md',
    'plans/brief_utku_DOC-VISIBILITY-KATMANI-29.md',
    'plans/brief_utku_UI-KONTROL-PANOSU-32.md',
    'plans/brief_utku_DOKÜMAN-KVKK-FAQ-33.md',
]
now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
msg = 'Baslatma bildirimi okundu (2026-09-24). Brief okundu.'

for t in tasks:
    if t.get('brief') in briefs:
        t['durum'] = 'baslatdi'
        t['baslangic'] = now
        t['not'] = msg + ' ' + t['brief']
        print('OK: ' + t['task_id'])

with open(path, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)
print('Saved.')
