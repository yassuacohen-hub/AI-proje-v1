# ORKESTRA-KARAR-DEFTERI-AUDIT-01 Brif

**Görev:** [ORKESTRA] Karar defterini audit et → eksik/tekrar/orphan raporu (30m)

## İş Maddeleri

1. **decision_log.jsonl'i oku:** `data/orchestrator/decision_log.jsonl` — her satır JSON karar kaydı (D-XX formatı).

2. **Audit kontrolleri:**
   - **Geçerli D-XX numaralandırması:** Kaydın `decision_id` alanı D-<2 digit sayı> kalıbında mı? (D-00 ila D-99 geçerli)
   - **Tekrarlayan kayıt:** Aynı `decision_id` birden fazla satırda var mı? → Döngü ve hata rapor et
   - **Eksik alanlar:** Her kaydın zorunlu alanları: `decision_id`, `kahin_onayi`, `tarih`, `ozet` → eksik alanları not et
   - **Orphan kaydı:** Karar `task_id` refine etmişse, o görev task_board.json'da var mı? Yoksa orphan (bağlantısız) kaydı
   - **JSON sözdizimi:** Geçerli JSON satırı mı, parse edilebilir mi?
   - **Tarih geçerliliği:** `tarih` ISO 8601 formatında mı?

3. **Eksik kaydı tespit et:**
   - Karar bulunmayan task_board görevleri (örn. iptal/stale gitmeden önce karar log'a entry yok)
   - "Orphan" kararlar (hiçbir görevle bağlantısı olmayan D-XX)

4. **Rapor yaz:** `data/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_rapor_2026-09-20_denetim.md`
   - Toplam karar sayısı
   - Geçerli kayıt sayısı
   - **Geçersiz kayıtlar tablosu:** decision_id | sorun | satır numarası | önerilen düzeltme
   - Tekrarlayan decision_id'ler (listele)
   - Orphan kararlar (listele)
   - Eksik task_id referans kararları (listele)

## Test Komutu

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
    print('decision_log.jsonl bulunamadi')
"
```

## Sonuç Dosyası

- Rapor: `data/orchestrator/ORKESTRA-KARAR-DEFTERI-AUDIT-01_rapor_2026-09-20_denetim.md`
- Yeni görev açılmadı (sadece rapor)
