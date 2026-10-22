#!/usr/bin/env python3
"""
Güvenlik full.md dosyasından actionable task'leri çıkarır
AGENTS.md D-57 formatında: [ALAN] FİİL + NESNE → ÇIKTI (SÜRE)
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Any

def extract_tasks_from_security_doc(content: str) -> List[Dict[str, Any]]:
    """Güvenlik belgesinden task'leri regex ve pattern matching ile çıkarır"""
    
    tasks = []
    task_id_counter = 1
    
    # Pattern'ler: Kod blokları, "yazalım", "kurgulayalım", "oluşturalım", "entegre edelim" gibi eylem çağrıları
    action_patterns = [
        (r'kodlayalım|yazalım|kurgulayalım|oluşturalım|entegre edelim|açalım|kuralım|hazırlayalım|implement', 'CODE'),
        (r'test|doğrula|validate|pytest|unit test|integration test', 'TEST'),
        (r'doküman|belge|rapor|şablon|template|spec', 'DOC'),
        (r'deploy|kurulum|setup|install|configure|configürasyon', 'DEPLOY'),
        (r'güvenlik|security|hardening|firewall|ssl|mtls|encryption', 'SEC'),
        (r'veritabanı|database|migration|schema|index|tablo', 'DB'),
        (r'api|endpoint|router|gateway|kong', 'API'),
        (r'frontend|ui|dashboard|next\.js|shadcn|react|streamlit', 'FE'),
        (r'worker|celery|async|queue|batch|pipeline', 'WORKER'),
        (r'monitor|alert|watchdog|nöbetçi|observability|logging', 'MON'),
    ]
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Kod blokları başlangıcı (```python, ```sql, ```typescript, ```bash)
        if re.match(r'^```\w+', line.strip()):
            # Kod bloğunun açıklamasını bul (önceki satırlarda)
            context = ""
            for j in range(max(0, i-5), i):
                if lines[j].strip() and not lines[j].strip().startswith('#'):
                    context = lines[j].strip()
                    break
            
            # Kod bloğu tipini belirle
            lang_match = re.match(r'^```(\w+)', line.strip())
            lang = lang_match.group(1) if lang_match else 'code'
            
            # Alan belirle
            alan = 'BACKEND'
            if lang in ['sql']:
                alan = 'DB'
            elif lang in ['typescript', 'tsx', 'javascript', 'jsx']:
                alan = 'FE'
            elif lang in ['bash', 'sh', 'powershell', 'ps1']:
                alan = 'DEPLOY'
            elif 'test' in context.lower():
                alan = 'TEST'
            elif 'docker' in context.lower() or 'compose' in context.lower():
                alan = 'DEPLOY'
            elif 'kong' in context.lower() or 'gateway' in context.lower():
                alan = 'API'
            elif 'pydantic' in context.lower() or 'schema' in context.lower():
                alan = 'SEC'
            
            # Eylem fiili çıkar
            fiil = "Kodla"
            if 'test' in context.lower():
                fiil = "Test Et"
            elif 'deploy' in context.lower() or 'kur' in context.lower():
                fiil = "Deploy Et"
            elif 'config' in context.lower() or 'ayar' in context.lower():
                fiil = "Konfigüre Et"
            elif 'doküman' in context.lower() or 'belge' in context.lower():
                fiil = "Belgele"
            
            nesne = context[:80] if context else f"{lang} kod bloğu"
            cikti = f"{lang} artifact"
            sure = "2h" if alan in ['BACKEND', 'FE', 'API'] else "1h"
            
            # Task ID formatı: [ALAN]-[KISA_ACIKLAMA]-[SAYI]
            short_desc = re.sub(r'[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ]+', '-', nesne[:30]).strip('-').upper()
            task_id = f"{alan}-{short_desc}-{task_id_counter:03d}"
            task_id_counter += 1
            
            baslik = f"[{alan}] {fiil} + {nesne} → {cikti} ({sure})"
            
            # Ajan ata
            ajan_map = {
                'BACKEND': 'utku', 'API': 'utku', 'DB': 'utku', 'WORKER': 'utku', 'DEPLOY': 'utku',
                'FE': 'utku', 'SEC': 'salih', 'TEST': 'salih', 'MON': 'salih', 'DOC': 'yasu'
            }
            sahip = ajan_map.get(alan, 'utku')
            
            tasks.append({
                "task_id": task_id,
                "id": task_id,
                "baslik": baslik,
                "sahip": sahip,
                "oncelik": "P1" if alan in ['SEC', 'DEPLOY', 'API'] else "P2",
                "durum": "pending",
                "baslangic": None,
                "bitis": None,
                "dosyalar": [],
                "not": f"Kaynak: güvenlik full.md satır ~{i+1}. Bağlam: {context[:200]}",
                "source": "security_doc_analysis",
                "from_agent": "ihsan",
                "kanit": "",
                "mod": "code",
                "brief": "",
                "talimat": f"Güvenlik belgesinden çıkarılan task. Bağlam: {context[:300]}",
                "dependencies": []
            })
    
    # Ayrıca özel görev çağrıları için metin arama
    special_tasks = [
        # (pattern, alan, fiil, nesne, cikti, sure, sahip, oncelik)
        (r'analyze_tasks\.py.*çalıştır|task.*board.*doldur|taskboard.*populate', 'ORCH', 'Analiz Et', 'güvenlik full.md task çıkarımı', 'task_board.json güncelleme', '30m', 'ihsan', 'P0'),
        (r'watchdog|nöbetçi|alertmanager|prometheus.*alert', 'MON', 'Kur', 'Watchdog/Nöbetçi sistemi', 'alert rules + notification channels', '2h', 'salih', 'P1'),
        (r'validate-deployment\.ps1.*scheduler|task scheduler|windows.*startup', 'DEPLOY', 'Zamanla', 'Deployment validation cron', 'Scheduled task entry', '30m', 'utku', 'P1'),
        (r'mkcert|self.signed.*ca|certificate.*generate|mtls.*cert', 'SEC', 'Üret', 'mTLS sertifikaları (CA + cert/key)', 'kong.yml volumes için cert dosyaları', '1h', 'salih', 'P1'),
        (r'test_tobb_integration\.py.*koş|pytest.*tobb|tobb.*canlı.*test', 'TEST', 'Test Et', 'TOBB Card 02/04 canlı entegrasyon', 'API yanıt kanıtı + bakiye doğrulama', '1h', 'salih', 'P0'),
        (r'frontend.*boş|next\.js.*kur|create-next-app|shadcn.*init', 'FE', 'Kur', 'Next.js + Shadcn Admin boilerplate', 'frontend/ klasörü dolu', '2h', 'utku', 'P1'),
        (r'portproxy.*startup|netsh.*reboot|task scheduler.*portproxy', 'DEPLOY', 'Kalıcı Hale Getir', 'netsh portproxy reboot sonrası', 'Task Scheduler girişi', '30m', 'utku', 'P1'),
        (r'kong\.yml.*volume|kong.*mount|declarative.*config', 'API', 'Mount Et', 'kong.yml declarative config', 'Kong gateway hazır', '1h', 'utku', 'P1'),
        (r'pg_hba\.conf.*deploy|postgresql.*hardening|zero.trust', 'SEC', 'Uygula', 'PostgreSQL zero-trust pg_hba.conf', 'Sadece 172.16.0.0/12 erişim', '1h', 'salih', 'P1'),
        (r'quarantine.*processor|karantina.*döngü|repair.*worker|celery.*worker', 'WORKER', 'Kur', 'Karantina/Onarım Celery workerları', '3 worker + beat aktif', '2h', 'utku', 'P1'),
        (r'sse.*dashboard|mirmir.*radar|sonner.*toast|canlı.*sinyal', 'FE', 'Yaz', 'Mırmır SSE Dashboard (Next.js/Shadcn)', 'Canlı risk sinyali akışı UI', '3h', 'utku', 'P2'),
        (r'react.flow|neo4j.*graph|ilişki.*ağ|ortaklık.*harita', 'FE', 'Görselleştir', 'React Flow şirket ilişkileri ağı', 'Interaktif UBO/organ grafiği', '3h', 'utku', 'P2'),
        (r'cmdk|spotlight|komut.*paleti|hızlı.*arama', 'FE', 'Entegre Et', 'CMDK komut paleti arama çubuğu', 'Anasayfa Spotlight arama', '2h', 'utku', 'P2'),
        (r'tremor|grafik|kpi|metric|dashboard.*chart', 'FE', 'Ekle', 'Tremor Raw grafik bileşenleri', 'KPI kartları + trend grafikleri', '2h', 'utku', 'P2'),
        (r'escrow|tahkim|arbitration|iyzico.*sub.merchant', 'API', 'Implement Et', 'Escrow + Dijital Tahkim API', 'İhtilaç çözüm akışı', '3h', 'utku', 'P2'),
        (r'webhook.*sat|webhook.*signal|3 kredi|credit.*webhook', 'API', 'Yaz', 'Webhook sinyal satış endpointi', '3 kredi/sinyal faturalandırma', '2h', 'utku', 'P2'),
        (r'enterprise.*api|kurumsal.*gateway|650k|api gateway', 'API', 'Tasar', 'Enterprise API Gateway paketi', '650K TL/yıl tier spec', '2h', 'utku', 'P2'),
        (r'finansal.*model|net.kar|margin|profit.*calculator', 'DOC', 'Belgele', 'Finansal model ve karlılık analizi', 'Investor deck hazır', '1h', 'yasu', 'P2'),
        (r'kvkk|bdkk|compliance|masking|tc.kimlik|pii', 'SEC', 'Uygula', 'KVKK/BDDK maskeleme ve uyumluluk', 'PII koruma katmanı', '2h', 'salih', 'P1'),
        (r'docker.compose.*up|container.*başlat|stack.*deploy', 'DEPLOY', 'Başlat', 'Full stack Docker Compose deployment', '13 servis healthy', '2h', 'utku', 'P0'),
    ]
    
    for pattern, alan, fiil, nesne, cikti, sure, sahip, oncelik in special_tasks:
        if re.search(pattern, content, re.IGNORECASE):
            short_desc = re.sub(r'[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ]+', '-', nesne[:30]).strip('-').upper()
            task_id = f"{alan}-{short_desc}-{task_id_counter:03d}"
            task_id_counter += 1
            
            baslik = f"[{alan}] {fiil} + {nesne} → {cikti} ({sure})"
            
            tasks.append({
                "task_id": task_id,
                "id": task_id,
                "baslik": baslik,
                "sahip": sahip,
                "oncelik": oncelik,
                "durum": "pending",
                "baslangic": None,
                "bitis": None,
                "dosyalar": [],
                "not": f"Güvenlik belgesinden otomatik çıkarılan özel task. Pattern: {pattern}",
                "source": "security_doc_analysis",
                "from_agent": "ihsan",
                "kanit": "",
                "mod": "code",
                "brief": "",
                "talimat": f"Güvenlik belgesi analizi sonucu belirlenen task. {nesne} için {fiil.lower()} eylemi gerekli.",
                "dependencies": []
            })
    
    # Duplicate'leri temizle (baslik bazında)
    seen = set()
    unique_tasks = []
    for t in tasks:
        key = t['baslik']
        if key not in seen:
            seen.add(key)
            unique_tasks.append(t)
    
    return unique_tasks

def main():
    # Güvenlik belgesini oku
    with open('yedekler/güvenlik full.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Mevcut task_board.json'u oku
    with open('Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
        task_board = json.load(f)
    
    # Yeni task'leri çıkar
    new_tasks = extract_tasks_from_security_doc(content)
    
    print(f"Cikarilan yeni task sayisi: {len(new_tasks)}")
    for t in new_tasks:
        baslik_ascii = t['baslik'].replace('→', '->')
        print(f"  - {t['task_id']}: {baslik_ascii} [{t['sahip']}] {t['oncelik']}")
    
    # Mevcut task ID'leri topla
    existing_ids = {t['task_id'] for t in task_board}
    
    # Sadece yeni olanları ekle
    added = 0
    for t in new_tasks:
        if t['task_id'] not in existing_ids:
            task_board.append(t)
            added += 1
        else:
            print(f"  -> Zaten var, atlanıyor: {t['task_id']}")
    
    # Güncellenmiş task_board'u yaz
    with open('Huginn Data Insights/data/orchestrator/task_board.json', 'w', encoding='utf-8') as f:
        json.dump(task_board, f, ensure_ascii=False, indent=2)
    
    print(f"\nEklenen yeni task: {added}")
    print(f"Toplam task sayısı: {len(task_board)}")

if __name__ == "__main__":
    main()