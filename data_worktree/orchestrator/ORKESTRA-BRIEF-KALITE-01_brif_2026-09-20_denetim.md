# ORKESTRA-BRIEF-KALITE-01 Brif

**Görev:** [ORKESTRA] 12 yeni brifi denetle → kalite raporu (1s)

## İş Maddeleri

1. **Yeni 12 brifleri listele:** `data/orchestrator/` içinde son eklenen brifleri bul (tarih: 2026-09-20).

2. **Her brif için D-66 ve D-57 kontrol et:**
   - **D-66 compliance:** Brif dosyası var mı? → `<TASK>_brif_<tarih>_<rol>.md` kalıbı
   - **D-57 başlık kalıbı:** `[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)`
     - ALAN = 7 kanonik (UI, API, VERI, TEST, DOC, ALTYAPI, ORKESTRA)
     - FİİL = 8 kanonik (yaz, düzelt, taşı, sil, denetle, ölç, belgele, araştır)
     - ÇIKTI = tek dosya veya tek komut (yoksa görev bölünür)
     - SÜRE = 30d, 1s, 2s, 4s (üstü bölünür)
   - **Talimat dosyası:** Brif başında `talimat` alanı yazılı mı? Dosya diskte var mı?
   - **JSON sözdizimi:** Brif dosyası geçerli Markdown mi? (JSON embed varsa sözdizimi doğru mu)

3. **Eksiklikleri raporla:**
   - Eksik brif (tetik var, brif yok)
   - Yanlış dosya adı (kalıp dışı)
   - Başlık D-57'ye aykırı (5+ parça, eksik ÇIKTI/SÜRE)
   - Talimat dosyası refs yoksa brif içeriğini yazılı mı
   - JSON parse error

4. **Rapor yaz:** `data/orchestrator/ORKESTRA-BRIEF-KALITE-01_rapor_2026-09-20_denetim.md`
   - Kontrol edilen 12 brif listesi (task_id, başlık, D-57 uyum, D-66 uyum)
   - Eksikliklerin özeti (kaç tane, tip bazlı)
   - Düzeltme tavsiyesi (hangi brif yeniden yazılacak, kim sorumlabilir)

## Test Komutu

```bash
python -X utf8 -c "
import json, os
from pathlib import Path
brifs = list(Path('data/orchestrator').glob('*_brif_2026-09-20_*.md'))
print(f'Toplam brif: {len(brifs)}')
for b in sorted(brifs)[:12]:
    task_id = b.name.split('_brif_')[0]
    print(f'  {task_id}: {b.name}')
"
```

## Sonuç Dosyası

- Rapor: `data/orchestrator/ORKESTRA-BRIEF-KALITE-01_rapor_2026-09-20_denetim.md`
- Yeni görev açılmadı (sadece rapor)
