#!/usr/bin/env python3
"""
Otonom Watchdog Mekanizması - İhsan (Baş Ajan Orkestratör)
Her 5 dakikada bir çalışır, ajan yüklerini ve kritik yolu izler.
Tetikleyiciler aşılırsa otomatik chat uyarısı ve yük dengeleme loglar.
"""

import hashlib
import json
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

TASK_BOARD = Path('c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json')
AGENT_REGISTRY = Path('c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/agent_registry.json')
CHAT_LOG = Path('c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/chat/messages.jsonl')
WATCHDOG_ALERT = Path('c:/Huginn Data Projesi/watchdog_alert_chat.json')
WATCHDOG_LOG = Path('c:/Huginn Data Projesi/watchdog_remediation_log.json')

CAPACITIES = {'ihsan': 2, 'utku': 3, 'bilo': 2, 'nur': 2, 'salih': 5, 'nisa': 3, 'yasu': 0, 'mimir': 0}

THRESHOLDS = {
    'agent_utilization_pct': 150,
    'utku_active_tasks': 5,
    'review_queue_p0_p1_age_hours': 48,
    'yasu_task_detected': True
}

def load_tasks():
    with open(TASK_BOARD, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze():
    tasks = load_tasks()
    
    # Agent load
    agent_load = {}
    for t in tasks:
        if t.get('durum') in ('pending', 'in_progress', 'review', 'plan', 'aktif', 'bekliyor'):
            agent = t.get('sahip', 'unknown')
            priority = t.get('oncelik', 'P3')
            agent_load.setdefault(agent, {'total': 0, 'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0, 'tasks': []})
            agent_load[agent]['total'] += 1
            agent_load[agent][priority] = agent_load[agent].get(priority, 0) + 1
            agent_load[agent]['tasks'].append(t)
    
    # Review queue age (P0/P1 in review)
    review_queue = []
    for t in tasks:
        if t.get('durum') == 'review' and t.get('oncelik') in ('P0', 'P1'):
            review_queue.append(t)
    
    # Blocked tasks
    done_ids = set(t.get('task_id', '') for t in tasks if t.get('durum') in ('done', 'archive', 'tamamlandı'))
    blocked = []
    for t in tasks:
        if t.get('durum') in ('pending', 'in_progress', 'review', 'plan', 'aktif', 'bekliyor'):
            deps = t.get('dependencies', [])
            if deps:
                blocked_deps = [d for d in deps if d not in done_ids]
                if blocked_deps:
                    blocked.append({'task_id': t['task_id'], 'blocked_by': blocked_deps, 'owner': t.get('sahip')})
    
    # Yasu tasks
    yasu_tasks = [t for t in tasks if t.get('sahip') == 'yasu' and t.get('durum') in ('pending', 'in_progress', 'review', 'plan', 'aktif', 'bekliyor')]
    
    return {
        'timestamp': datetime.now().isoformat(),
        'agent_load': agent_load,
        'review_queue': review_queue,
        'blocked': blocked,
        'yasu_tasks': yasu_tasks,
        'capacities': CAPACITIES
    }

def check_triggers(analysis):
    alerts = []
    
    # Agent utilization
    for agent, data in analysis['agent_load'].items():
        cap = analysis['capacities'].get(agent, 0)
        if cap > 0:
            pct = (data['total'] / cap) * 100
            if pct > THRESHOLDS['agent_utilization_pct']:
                alerts.append(f"AGENT_OVERLOAD: {agent} % {pct:.0f} (kapasite {cap}, aktif {data['total']})")
    
    # Utku active tasks
    utku_data = analysis['agent_load'].get('utku', {})
    if utku_data.get('total', 0) > THRESHOLDS['utku_active_tasks']:
        alerts.append(f"UTKU_OVERLOAD: {utku_data['total']} aktif görev (eşik {THRESHOLDS['utku_active_tasks']})")
    
    # Review queue P0/P1 age
    if analysis['review_queue']:
        alerts.append(f"REVIEW_QUEUE: {len(analysis['review_queue'])} P0/P1 review görev bekliyor")
        for t in analysis['review_queue']:
            alerts.append(f"  - {t['task_id']} [{t['oncelik']}] {t['sahip']}: {t['baslik'][:60]}")
    
    # Blocked tasks
    if analysis['blocked']:
        alerts.append(f"BLOCKED_TASKS: {len(analysis['blocked'])} görev bloklu")
        for b in analysis['blocked']:
            alerts.append(f"  - {b['task_id']} bekliyor: {b['blocked_by']} (sahip: {b['owner']})")
    
    # Yasu tasks
    if analysis['yasu_tasks'] and THRESHOLDS['yasu_task_detected']:
        alerts.append(f"YASU_TASKS: {len(analysis['yasu_tasks'])} görev yasu'da (HASTA - yeniden dağıtım gerek)")
        for t in analysis['yasu_tasks']:
            alerts.append(f"  - {t['task_id']} [{t['oncelik']}] {t['durum']}: {t['baslik'][:60]}")
    
    return alerts

# --- Aynı uyarı mandalı (D-434, ihsan 24.10) --------------------------------
# ÖLÇÜLEN KÖK NEDEN: daemon 5 dk'da bir BİREBİR AYNI metni chat'e yazdı;
# messages.jsonl 164 kopya ile 216 KB / ~54.000 token oldu. Ajanlar her chat
# okumada bu çöpü yutuyor → bağlam tavanı → utku "düşünme modundan çıkamıyor",
# aynı raporu tekrar yazıyor, komut alamıyor (PO gözlemi 24.10 16:35).
# KURAL: içerik imzası değişmedikçe chat'e YENİ satır YAZILMAZ. Durum sadece
# watchdog_alert_chat.json'da (üzerine yazılır, sabit boyut) güncellenir.
IMZA_DURUM = Path('c:/Huginn Data Projesi/watchdog_son_imza.json')


def _uyari_imza(alerts):
    """Zaman damgasından bağımsız içerik imzası (aynı yük = aynı imza)."""
    govde = "\n".join(a.strip() for a in alerts)
    return hashlib.sha256(govde.encode('utf-8')).hexdigest()


def _son_imza_oku():
    try:
        with open(IMZA_DURUM, 'r', encoding='utf-8') as f:
            return json.load(f).get('imza')
    except (OSError, ValueError):
        return None


def _son_imza_yaz(imza, tekrar_sayisi):
    try:
        with open(IMZA_DURUM, 'w', encoding='utf-8') as f:
            json.dump({
                "imza": imza,
                "tekrar_sayisi": tekrar_sayisi,
                "ilk_yazim": datetime.now().isoformat(),
                "son_gorilme": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def send_chat_alert(alerts):
    """Chat loguna watchdog uyarısı yaz (D-210 format).

    D-434: aynı içerik imzası zaten yazıldıysa chat'e YENİ satır eklenmez;
    yalnız uyarı dosyası (sabit boyut) tazelenir. Böylece otomatik uyarılar
    ajanların bağlamını şişiremez.
    """
    imza = _uyari_imza(alerts)
    icerik = "🚨 WATCHDOG TETİKLENDİ\n" + "\n".join(alerts)

    # Sabit-boylu dosya her turda tazelenir (harici alım için), kayıp yok.
    with open(WATCHDOG_ALERT, 'w', encoding='utf-8') as f:
        json.dump({"timestamp": datetime.now().isoformat(), "alerts": alerts},
                  f, ensure_ascii=False, indent=2)

    if imza == _son_imza_oku():
        print("[WATCHDOG] Aynı uyarı zaten chat'te (D-434 mandalı) - "
              "chat'e YENİ satır yazılmadı, yalnız uyarı dosyası tazelendi.")
        return

    msg = {
        "timestamp": datetime.now().isoformat(),
        "from": "ihsan",
        "to": "all",
        "type": "watchdog_alert",
        "priority": "CRITICAL",
        "content": icerik,
        "metadata": {"source": "watchdog_daemon", "auto": True, "imza": imza[:12]}
    }

    with open(CHAT_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(msg, ensure_ascii=False) + '\n')

    _son_imza_yaz(imza, 1)
    print(f"[WATCHDOG] Chat uyarısı gönderildi: {len(alerts)} tetikleyici "
          f"(imza {imza[:12]})")

def log_remediation(analysis, alerts):
    """Yük dengeleme aksiyonlarını logla"""
    remediation = {
        "timestamp": datetime.now().isoformat(),
        "triggered_by": alerts,
        "current_loads": {a: d['total'] for a, d in analysis['agent_load'].items()},
        "actions": []
    }
    
    # Auto remediation logic
    for agent, data in analysis['agent_load'].items():
        cap = analysis['capacities'].get(agent, 0)
        if cap > 0 and (data['total'] / cap) * 100 > THRESHOLDS['agent_utilization_pct']:
            # Move plan tasks to available agents
            plan_tasks = [t for t in data['tasks'] if t.get('durum') == 'plan']
            if plan_tasks:
                remediation['actions'].append({
                    "from": agent,
                    "action": "move_plan_tasks",
                    "count": len(plan_tasks),
                    "tasks": [t['task_id'] for t in plan_tasks]
                })
    
    if analysis['blocked']:
        remediation['actions'].append({
            "action": "resolve_blocked",
            "blocked_count": len(analysis['blocked']),
            "details": analysis['blocked']
        })
    
    if analysis['yasu_tasks']:
        remediation['actions'].append({
            "action": "redistribute_yasu",
            "count": len(analysis['yasu_tasks']),
            "target_groups": ["CORE", "BACKUP"]
        })
    
    with open(WATCHDOG_LOG, 'w', encoding='utf-8') as f:
        json.dump(remediation, f, ensure_ascii=False, indent=2)
    
    print(f"[WATCHDOG] Remediation loglandı: {len(remediation['actions'])} aksiyon")

def trigger_gorev_kutusu(action, task_id=None):
    """gorev_kutusu.py'yi tetikle (bilo/utku/salih için)"""
    try:
        cmd = ['py', '-3', 'scripts/gorev_kutusu.py', action]
        if task_id:
            cmd.append(task_id)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd='c:/Huginn Data Projesi')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def run_once():
    print(f"\n[WATCHDOG] {datetime.now().isoformat()} - Analiz başlıyor...")
    analysis = analyze()
    alerts = check_triggers(analysis)
    
    if alerts:
        print(f"[WATCHDOG] 🚨 {len(alerts)} TETİKLEYİCİ:")
        for a in alerts:
            print(f"  {a}")
        send_chat_alert(alerts)
        log_remediation(analysis, alerts)
        
        # Auto: Move plan tasks from overloaded agents
        for agent, data in analysis['agent_load'].items():
            cap = analysis['capacities'].get(agent, 0)
            if cap > 0 and (data['total'] / cap) * 100 > THRESHOLDS['agent_utilization_pct']:
                plan_tasks = [t for t in data['tasks'] if t.get('durum') == 'plan']
                for t in plan_tasks:
                    # D-434: bu satır ALDATICIYDI — "görev çekiliyor" yazıp hiçbir
                    # şey yapmıyordu; orkestratör bile bunu "watchdog utku'ya 4 görev
                    # yükledi" diye okudu (24.10 ölçümü). Gerçek: yalnız ÖNERİ.
                    # Pano değişikliği yapmaz; değişiklik ihsan onayı ister (D-77).
                    print(f"[WATCHDOG] ÖNERİ (uygulanmadı): {agent} aşırı yüklü, "
                          f"plan görevi başkasına devredilebilir: {t['task_id']}"
                          f" — onay için: gorev_kutusu.py devret --task-id {t['task_id']}"
                          f" --yeni-ajan <ajan>")
    else:
        print("[WATCHDOG] ✅ Tüm eşikler normal")
    
    return alerts

def daemon_mode():
    print("[WATCHDOG] Daemon modu başlatıldı (Ctrl+C ile durdur)")
    print(f"[WATCHDOG] Kontrol aralığı: {300} saniye (5 dakika)")
    try:
        while True:
            run_once()
            time.sleep(300)
    except KeyboardInterrupt:
        print("\n[WATCHDOG] Daemon durduruldu.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--daemon', action='store_true', help='Daemon modu (5 dk aralık)')
    parser.add_argument('--once', action='store_true', help='Tek seferlik çalıştır')
    args = parser.parse_args()
    
    if args.daemon:
        daemon_mode()
    else:
        run_once()