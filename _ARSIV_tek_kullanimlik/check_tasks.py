import json
tasks = json.load(open('data/orchestrator/task_board.json', encoding='utf-8'))
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
for t in tasks:
    if t.get('brief') in briefs:
        print(t['task_id'] + ': ' + t['durum'] + ' (start: ' + (t.get('baslangic') or 'none') + ')')