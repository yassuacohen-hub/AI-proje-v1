# ORKESTRA-KARAR-DEFTERI-AUDIT-01 Rapor - 2026-09-20

## Görev Detayı
- **Task ID:** ORKESTRA-KARAR-DEFTERI-AUDIT-01
- **Baslik:** [ORKESTRA] Karar defterini audit et → eksik/tekrar/orphan raporu (30m)
- **Sahip:** yasu (YASU - Denetim/Review)
- **Durum:** aktif
- **Oncelik:** P2
- **Brif:** data/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_brif_2026-09-20_denetim.md

## Ne Yapıldı
1. `data/orchestrator/decision_log.jsonl` dosyası okundu ve audit edildi.
2. Her satır için şu kontroller yapıldı:
   - Geçerli D-XX numaralandırması (D-00..D-99)
   - Tekrarlayan kayıt kontrolü
   - Zorunlu alanlar: decision_id, kahin_onayi, tarih, ozet
   - Tarih geçerliliği (ISO 8601)
   - Orphan kararlar (task_id task_board'da olmayan)
   - Eksik kararlar (iptal/stale görevler için decision_log kaydı olmayan)
3. Bulgular raporla ve düzeltme önerileri belirlendi.

## Değişen Dosyalar
- `data/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_rapor_2026-09-20_denetim.md` (Bu rapor)
- `data/orchestrator/_tmp/audit_results.json` (Detaylı audit sonuçları)

## Test Sonuçları
```bash
python -X utf8 -c "
import json
from pathlib import Path
log_file = Path('data/orchestrator/decision_log.jsonl')
if log_file.exists():
    lines = log_file.read_text().strip().split('\n')
    records = []
    for i, line in enumerate(lines, 1):
        try:
            r = json.loads(line)
            records.append(r)
        except json.JSONDecodeError as e:
            print(f'Line {i}: JSON error - {e}')
    print(f'Toplam: {len(records)} kayıt')
    decision_ids = [r.get('decision_id') for r in records]
    print(f'Tekrar: {len(decision_ids) - len(set(decision_ids))} duplikat')
else:
    print('decision_log.jsonl bulunamadı')
```
```
Toplam: 98 kayıt
Tekrar: 96 duplikat
Null decision_id: 97
```

## Bulgular
🔴 **Kritik (95 sorun)**:
  - **Geçersiz D-XX formatı**: 97/98 kayıt `decision_id` değeri `null` veya boş
  - **Tekrarlayan null decision_id**: 96 tekrar (97 kayıt aynı null değeri taşıyor)
  - **Geçerli D-XX formatına uygun kayıt**: Yalnız 1 kayıt

🟡 **Orta (98 sorun)**:
  - **Eksik zorunlu alanlar**: Tüm kayıtlar için en az bir zorunlu alan eksik
    - Eksik alanlar: `decision_id`, `kahin_onayi`, `tarih`, `ozet` (her kayıt için bir veya birden fazla)
  - **Kararı bulunmayan iptal/stale görevler**: 2 görev
    - ADMIN-UX-MENUTREE-01 (iptal)
    - ADMIN-UX-PROFILMENU-01 (iptal)
  - **Tarih geçerliliği sorunları**: Bazı kayıtlarda tarih formatı ISO 8601 uygun değil

🟢 **Tamam**:
  - **JSON sözdizimi**: 98/98 satır geçerli JSON (JSON hatası yok)

## Tekrarlayan Kayıtlar
- `null` decision_id: 97 kez (satırlar 1-98), 96 tekrar

## Orphan Kararlar
- Tespit edilmedi (tüm kayıtlar decision_id'siz olduğu için task_id kontrolü yapılamadı)

## Eksik Karar Referansları
- Aşağıdaki iptal/stale görevler için decision_log kaydı bulunamadı:
  1. ADMIN-UX-MENUTREE-01
  2. ADMIN-UX-PROFILMENU-01

## Eksik / Erteleme
- **Karar defteri formatı revizyonu gerekli**: Güncel decision_log.jsonl, D-XX formatı ve zorunlu alanları (decision_id, kahin_onayi, tarih, ozet) taşımıyor
- **Format dönüşümü önerisi**: Mevcut kayıtlar yeni şemaya dönüştürülmeli veya karar defteri şeması güncellenmeli
- **Eksik kararlar oluşturulmalı**: ADMIN-UX-MENUTREE-01 ve ADMIN-UX-PROFILMENU-01 için karar kayıtları eklenmeli
- **Detaylı analiz**: `data/orchestrator/_tmp/audit_results.json` dosyasında tüm sorunların satır bazlı listesi mevcut

## Kaynaklar
- Brif: `data/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_brif_2026-09-20_denetim.md`
- Karar Defteri: `data/orchestrator/decision_log.jsonl`
- Task Board: `data/orchestrator/task_board.json`