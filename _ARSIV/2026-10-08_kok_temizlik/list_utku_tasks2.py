import os, json
p = os.path.join('Huginn Data Insights', 'data', 'orchestrator', 'task_board.json')
if os.path.exists(p):
    data = json.load(open(p, encoding='utf-8'))
    utku_tasks = [t for t in data if t.get('sahip') == 'utku']
    print('Utkuya atanan görevler:')
    for t in utku_tasks:
        baslik = t.get('baslik', '')
        durum = t.get('durum', '')
        # Replace arrow characters
        for arrow in ['→', '←', '↔', '↕', '↖', '↗', '↘', '↙', '↚', '↛', '↝', '↞', '↟', '↠', '↡', '↢', '↣', '↤', '↥', '↦', '↧', '↨', '⇀', '⇁', '⇂', '⇃', '⇄', '⇅', '⇆', '⇇', '⇈', '⇉', '⇊', '⇋', '⇌', '⇍', '⇎', '⇏', '⇐', '⇑', '⇒', '⇓', '⇔', '⇕', '⇖', '⇗', '⇘', '⇙']:
            baslik = baslik.replace(arrow, '->')
            durum = durum.replace(arrow, '->')
        print(f'- {t.get("id")}: {baslik} [{durum}]')
else:
    print('Task board bulunamadı.')