# Orphan Kuyruk Kayıtları Denetimi
**Tarih:** 2026-09-22  
**Bölüm:** Orkestratör Pano Hijyeni  
**Bulgu:** 4 kayıt kuyrukta onaylandi olarak yer alıyor ancak panodan yok.

---

## Olay Özeti

[`pano_denetim.py`](../../../scripts/pano_denetim.py) okuma-denetimi (read-only çalışma) şu kayıtları bildirdi:

```
[uyari/orphan] U-11: kuyrukta (onaylandi) var, panoda yok
[uyari/orphan] MIG-UI-01: kuyrukta (onaylandi) var, panoda yok
[uyari/orphan] MRK-05: kuyrukta (onaylandi) var, panoda yok
[uyari/orphan] ROO-REV-01: kuyrukta (onaylandi) var, panoda yok
```

---

## Detaylar

| Task ID | Kuyruk Durum | Onay Tarihi | Panoda | 
|---------|-------------|------------|--------|
| U-11 | onaylandi | 2026-09-15 | ✗ |
| MIG-UI-01 | onaylandi | 2026-09-15 | ✗ |
| MRK-05 | onaylandi | 2026-09-15 | ✗ |
| ROO-REV-01 | onaylandi | 2026-09-16 | ✗ |

Tüm 4 kayıt ~1 hafta öncesi onaylanmış; panodan hiç görülmüyor.

---

## Root Cause Analizi

### Seçenek 1: Görevler Hiç Panoya Eklenmedi

- Görevler onay kuyruğuna alındı (onay_kuyrugu.json)
- Ancak task_board.json'a hiç yazılmadı
- Orkestratör onayını işledi (kuyrukta onaylandi), pano güncelmedi
- İhtiyaç: board'a kaydedilmemiş onaylar yetim kalır

### Seçenek 2: Görevler Silindi/Arşivlendi

- Görevler daha önce panoda vardı
- Daha sonra silinmiş/arşivlenmiş
- onay_kuyrugu.json temizlenmedi (append-log tasarımı)
- İhtiyaç: tarihsel kuyruk ve pano ayrı şekilde diverge edebilir

### Seçenek 3: Veri Bozulması

- Export/import veya migration sırasında senkronizasyon kaybı
- Pano batch silindi ancak kuyruk yedek alınmamıştı

---

## Karar Seçenekleri

### A. Temiz Silme (Önerilen)

Kuyruktan 4 kayıt silinir. Gerekçe:
- Görevler panoda yok → teslim edilemez, işlenemiyor
- 7+ gün pasif kalmış → öncelik düşük
- D-66 kanıt zorunluluğu sağlanmamış (pano kaydı yok)

**Komut:**
```python
import json
from pathlib import Path

queue = json.loads(Path('data/orchestrator/onay_kuyrugu.json').read_text())
queue = [q for q in queue if q.get('task_id') not in ['U-11', 'MIG-UI-01', 'MRK-05', 'ROO-REV-01']]
Path('data/orchestrator/onay_kuyrugu.json').write_text(json.dumps(queue, indent=2, ensure_ascii=False))
```

### B. Araştırma + Geri Yükleme

Görevlerin arşiv dosyalarında yedekleri varsa restore edebilir. Ancak:
- Arşiv tarihini belirtmek gerekir
- Pano restore'u elle kaydedilmesi gerekebilir (D-77 disiplini)
- İşçilik yoğun

### C. Decision Log'a Kaydet + Bekle

Kaydedilmesi gerekir: bu 4 görev neden panoya geçişi kaybetti. İncelemede ek kayıtlar gözlenebilir.

---

## Tavsiye

**Seçenek A (Temiz Silme) —** Gerekçe:
1. Görevler hiç işlenmemiş (panoda yok → teslim edilemez)
2. 1 hafta pasif → hale-i hazırsızlık
3. Tarihsel onay kaydı korunur (kuyruk silmeyle ağır işlem değil)
4. pano_denetim.py raporu temiz olur, `hata=0`

Karar üreticiye aittir (orkestratör/ürün sahibi). Ancak silme öncesinde:
- Git history'de U-11/MIG-UI-01/MRK-05/ROO-REV-01 varsa kontrol et
- Arşiv dosyalarında yedek varsa kayıt tut

---

## Devam Adımları

- [ ] Karar: A/B/C seçeneklerinden bir seçin
- [ ] Seçenek A ise: kuyruk temizle + rapor kapat
- [ ] Seçenek B ise: arşiv araştır + restore planı
- [ ] Seçenek C ise: decision_log.py'ye "4 orphan kayıt incelemesi bekleniyor" kaydı
