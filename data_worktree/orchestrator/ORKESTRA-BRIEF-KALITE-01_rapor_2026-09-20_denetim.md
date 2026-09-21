# ORKESTRA-BRIEF-KALITE-01 Rapor - 2026-09-20

## Görev Detayı
- **Task ID:** ORKESTRA-BRIEF-KALITE-01
- **Baslik:** [ORKESTRA] 12 yeni brifi denetle → kalite raporu (1s)
- **Sahip:** yasu (YASU - Denetim/Review)
- **Durum:** aktif
- **Oncelik:** P1
- **Brif:** data/orchestrator/ORKESTRA-BRIEF-KALITE-01_brif_2026-09-20_denetim.md

## Ne Yapıldı
1. `data/orchestrator/` dizinindeki `*_brif_2026-09-20_*.md` dosyalarından alfabetik sırayla ilk 12 brif seçildi.
2. Seçilen her brif için:
   - D-66 uyumu (dosya adı kalıbı `<TASK>_brif_<tarih>_<rol>.md`) kontrol edildi
   - Task board'dan görev başlığı (baslik) alınıp D-57 formatı (`[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)`) denetlendi
   - Brif içindeki `talimat` alanı ve dosya varlığı kontrol edildi
   - Brif içinde bulunan JSON embed'lerin geçerliliği denetlendi
3. Bulgular ve düzeltme önerileri belirlendi.

## Değişen Dosyalar
- `data/orchestrator/ORKESTRA-BRIEF-KALITE-01_rapor_2026-09-20_denetim.md` (Bu rapor)

## Test Sonuçları
```bash
python -X utf8 -c "
import json, os
from pathlib import Path
brifs = list(Path('data/orchestrator').glob('*_brif_2026-09-20_*.md'))
print(f'Toplam brif: {len(brifs)}')
for b in sorted(brifs)[:12]:
    task_id = b.name.split('_brif_')[0]
    print(f'  {task_id}: {b.name}')
```
```
Toplam brif: 25
  ADMIN-UX-LOGOUT-01: ADMIN-UX-LOGOUT-01_brif_2026-09-20_uretim.md
  ALTYAPI-BENCHMARK-02: ALTYAPI-BENCHMARK-02_brif_2026-09-20_test.md
  ALTYAPI-BILGI-TABANI-03: ALTYAPI-BILGI-TABANI-03_brif_2026-09-20_test.md
  ALTYAPI-FORM-SETUP-03: ALTYAPI-FORM-SETUP-03_brif_2026-09-20_uretim.md
  ALTYAPI-PROXY-CONFIG-02: ALTYAPI-PROXY-CONFIG-02_brif_2026-09-20_test.md
  ALTYAPI-PROXY-CONFIG-02: ALTYAPI-PROXY-CONFIG-02_brif_2026-09-20_uretim.md
  ALTYAPI-SQLITE-INIT: ALTYAPI-SQLITE-INIT_brif_2026-09-20_uretim.md
  ALTYAPI-TEST-FAILURE-FIX-01: ALTYAPI-TEST-FAILURE-FIX-01_brif_2026-09-20_uretim.md
  ALTYAPI-WEB-MONITOR-01: ALTYAPI-WEB-MONITOR-01_brif_2026-09-20_test.md
  ALTYAPI-WEB-MONITOR-01: ALTYAPI-WEB-MONITOR-01_brif_2026-09-20_uretim.md
  DOC-V10-AUDIT-01: DOC-V10-AUDIT-01_brif_2026-09-20_orkestrator.md
  ORKESTRA-BRIEF-KALITE-01: ORKESTRA-BRIEF-KALITE-01_brif_2026-09-20_denetim.md
```

## Bulgular
🔴 **Kritik**: 11/12 brif D-57 görev başlığı formatına uygun değil
  - ADMIN-UX-LOGOUT-01: `[ALAN]`, FİİL, →, ÇIKTI, (SÜRE) tüm eksik
  - ALTYAPI-BENCHMARK-02: FİİL alanı yanlış (isim öbeği "Performans ölçümü" kullanılmalı, fiil "ölç" kullanılmalı)
  - ALTYAPI-BILGI-TABANI-03: FİİL alanı yanlış (isim öbeği "Runbook ve uyum denetimi belgele" kullanılmalı, fiil "belgele" kullanılmalı)
  - ALTYAPI-FORM-SETUP-03: SÜRE eksik (30d/1s/2s/4s formatında)
  - ALTYAPI-PROXY-CONFIG-02 (test): SÜRE eksik
  - ALTYAPI-PROXY-CONFIG-02 (uretim): SÜRE eksik  
  - ALTYAPI-SQLITE-INIT: SÜRE eksik
  - ALTYAPI-WEB-MONITOR-01 (test): SÜRE eksik
  - ALTYAPI-WEB-MONITOR-01 (uretim): SÜRE eksik
  - DOC-V10-AUDIT-01: SÜRE eksik
  - ORKESTRA-BRIEF-KALITE-01: SÜRE eksik

🟡 **Orta**: 4/12 brif talimat eksik
  - ADMIN-UX-LOGOUT-01: talimat alanı ve/veya referans edilen dosya eksik
  - ALTYAPI-SQLITE-INIT: talimat alanı ve/veya referans edilen dosya eksik
  - ALTYAPI-TEST-FAILURE-FIX-01: talimat alanı ve/veya referans edilen dosya eksik
  - DOC-V10-AUDIT-01: talimat alanı ve/veya referans edilen dosya eksik

🟡 **Düşük**: 1/12 brif JSON geçersiz
  - ALTYAPI-WEB-MONITOR-01 (test): JSON embed'de extra data hatası

🟢 **Tamam**: 12/12 brif D-66 dosya adı kalıbına uygun
  - Tüm brif dosyaları `<TASK>_brif_<tarih>_<rol>.md` formatında doğru

## Eksik / Erteleme
- Tespit edilen D-57 ve talimat ihalleri ilgili ekipler tarafından düzeltilecek
- D-57 formatına uygun olmayan görev başlıkları yeniden yazılmalı
- Eksik talimat alanları tamamlanmalı veya brif içinde talimat verilmeli
- JSON syntax hatası düzeltilmeli