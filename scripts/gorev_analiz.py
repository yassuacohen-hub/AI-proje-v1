import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

# Windows terminal Unicode fix
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# JSON dosyasını yükle
with open('Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Tarih hesaplaması (3 ay önceki tarih)
current_date = datetime.fromisoformat('2026-09-23')
three_months_ago = current_date - timedelta(days=90)

# Sınıflandırma kategorileri
status_counts = defaultdict(int)
owner_tasks = defaultdict(lambda: defaultdict(int))
review_tasks = []
old_tasks = []
empty_owner_tasks = []

# Analiz
for task in tasks:
    task_id = task.get('task_id', task.get('id', 'UNKNOWN'))
    baslik = task.get('baslik', 'Başlık Yok')
    sahip = task.get('sahip', None)
    durum = task.get('durum', 'unknown')
    baslangic = task.get('baslangic', '')
    
    # Status sayma
    status_counts[durum] += 1
    
    # Owner bazında sayma
    if sahip:
        owner_tasks[sahip][durum] += 1
    else:
        empty_owner_tasks.append({
            'task_id': task_id,
            'baslik': baslik,
            'durum': durum
        })
    
    # Review görevleri
    if durum == 'review':
        review_tasks.append({
            'task_id': task_id,
            'baslik': baslik,
            'sahip': sahip if sahip else '(Boş)',
            'baslangic': baslangic
        })
    
    # Eski görevler (3 aydan eski)
    if baslangic:
        try:
            task_date = datetime.fromisoformat(baslangic)
            if task_date < three_months_ago:
                old_tasks.append({
                    'task_id': task_id,
                    'baslik': baslik,
                    'sahip': sahip if sahip else '(Boş)',
                    'baslangic': baslangic
                })
        except:
            pass

# Rapor oluştur
report = []
report.append("SINIFLAMA RAPORU")
report.append("=" * 50)
report.append(f"Toplam Görev: {len(tasks)}")
report.append(f"Done: {status_counts.get('done', 0)}")
report.append(f"Review: {status_counts.get('review', 0)}")
report.append(f"Aktif: {status_counts.get('aktif', 0)}")
report.append(f"Plan: {status_counts.get('plan', 0)}")
report.append(f"İptal/Arşiv: {status_counts.get('iptal', 0) + status_counts.get('archive', 0)}")
report.append("")

# Diğer durumlar
other_statuses = {k: v for k, v in status_counts.items() 
                  if k not in ['done', 'review', 'aktif', 'plan', 'iptal', 'archive']}
if other_statuses:
    report.append("Diğer Durumlar:")
    for status, count in sorted(other_statuses.items()):
        report.append(f"  {status}: {count}")
    report.append("")

report.append("\nSAHİP BAZINDA:")
report.append("-" * 50)

for owner in sorted(owner_tasks.keys()):
    statuses_list = owner_tasks[owner]
    total = sum(statuses_list.values())
    status_str = ", ".join([f"{s}: {c}" for s, c in sorted(statuses_list.items())])
    report.append(f"- {owner}: {total} görev ({status_str})")

report.append("\n\nREVİEW GÖREVLERİ (Detaylı):")
report.append("-" * 50)
if review_tasks:
    for task in sorted(review_tasks, key=lambda x: x['task_id']):
        report.append(f"[{task['task_id']}] {task['baslik'][:60]}... | {task['sahip']} | {task['baslangic']}")
else:
    report.append("Review görevleri yok.")

report.append("\n\nUYARI:")
report.append("-" * 50)

if old_tasks:
    report.append(f"[!] Eski görevler ({len(old_tasks)} adet) - 3 aydan eski (2026-06-23 öncesi):")
    for task in old_tasks[:10]:  # İlk 10'unu göster
        report.append(f"  [{task['task_id']}] {task['baslik'][:50]}... | {task['baslangic']}")
    if len(old_tasks) > 10:
        report.append(f"  ... ve {len(old_tasks) - 10} görev daha")
else:
    report.append("[i] Eski görev yok.")

if empty_owner_tasks:
    report.append(f"\n[!] Boş sahip görevleri ({len(empty_owner_tasks)} adet):")
    for task in empty_owner_tasks[:5]:  # İlk 5'ini göster
        report.append(f"  [{task['task_id']}] {task['baslik'][:50]}... ({task['durum']})")
    if len(empty_owner_tasks) > 5:
        report.append(f"  ... ve {len(empty_owner_tasks) - 5} görev daha")
else:
    report.append("\n[i] Boş sahip görevleri yok.")

# Raporu yazdır
print("\n".join(report))

# Detaylı istatistikler
print("\n\n" + "=" * 50)
print("DETAYLI İSTATİSTİKLER")
print("=" * 50)
print(f"\nToplam görev sayısı: {len(tasks)}")
print(f"Toplam sahibi olan görev: {len(tasks) - len(empty_owner_tasks)}")
print(f"Boş sahipli görev: {len(empty_owner_tasks)}")
print(f"Review aşamasında görev: {len(review_tasks)}")
print(f"3 aydan eski görev: {len(old_tasks)}")
