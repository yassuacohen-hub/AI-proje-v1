# D-172 — Pano Senkronizasyon Hatası (Kök Neden Analiz)

**Tarih:** 2026-09-22 · **Durum:** Araştırıldı · **Şiddet:** Orta

## Olay
3 görev (DOC-SIRKET-MASTER-01, ALTYAPI-KILIT-YOL-FIX-01, ALTYAPI-PANO-ENCODING-FIX-01) worktree `task_board.json`'dan "kayboldu" fakat merkez `Huginn Data Insights/data/orchestrator/task_board.json`'da mevcut kaldı.

Utku: "Worktree board'dan kaldırılmış, ama raporlar HDI merkezinde mevcut. Worktree board'a geri eklendi."

Sonuç: Worktree görev sayısı 297 → 300 (+3), merkez 340 kaldı.

## Bulgulan Panolar ve Durumları

| Konum | Toplam | DOC-SIRKET-MASTER-01 | ALTYAPI-KILIT-YOL-FIX-01 | ALTYAPI-PANO-ENCODING-FIX-01 |
|---|---|---|---|---|
| Merkez (`Huginn Data Insights/data/orchestrator`) | 340 | ✅ review | ✅ review | ✅ review |
| Merkez Worktree (`Huginn Data Insights/data_worktree/orchestrator`) | 337 | plan | ❌ YOK | ❌ YOK |
| Worktree (`worktree klasoru/data/orchestrator`) | 300 | ✅ review (yeni eklendi) | ✅ review (yeni eklendi) | ✅ review (yeni eklendi) |

**Notlar:**
- Merkez worktree kopyası zamanı geçmiş (en azından 2 görev eksik)
- Worktree kopyası şu anda merkez ile tutarlı (3 görev eklendikten sonra)

## Kök Neden

**Yapısal sorun:** İki bağımsız pano ağacı var, senkronizasyon mekanizması yok.

1. **Merkez pano** (`Huginn Data Insights/data/orchestrator/task_board.json`):
   - İhsan UI görevleri, sistem görevleri, raporlar buraya yazılıyor
   - 340 görev, 3 merkez görev review durumunda

2. **Worktree pano** (`worktree klasoru/data/orchestrator/task_board.json`):
   - Utku operasyon görevleri
   - 300 görev (yeni eklemelerden sonra)
   - Merkez ile senkronize değil

3. **pano_denetim.py**:
   ```python
   PANO_DOSYA = Path(__file__).resolve().parents[1] / "data/orchestrator/task_board.json"
   ```
   Script worktree'de çalıştığında worktree panasına bakar, merkez görevleri görmez.

4. **Tetik sistemi (trigger.py)**:
   - Worktree'nin `data/orchestrator/triggers/` altında çalışır
   - Merkez görevleri görmez

5. **Potansiyel senaryo:**
   - Merkez'de görev oluşturuldu (review)
   - Worktree pano senkronizasyonu yapılmadı
   - Utku "görev yok" dedi
   - Utku manuel olarak ekledi

## Kanıt Durumu (D-66)

3 görevin tamamında raporlar ve kanıtlar merkez'de var:

| Görev | Rapor | Dosya Değişikliği | Test | Sonuç |
|---|---|---|---|---|
| DOC-SIRKET-MASTER-01 | 1581 bayt | `task_board.json` başlık mojibake düzelt | kodlama_denetim.py ✅ | ✅ ONAYLANDI |
| ALTYAPI-KILIT-YOL-FIX-01 | 1213 bayt | `file_locks.json` 9 stale kilit sil | kilit mekanizması 5 test ✅ | ✅ ONAYLANDI |
| ALTYAPI-PANO-ENCODING-FIX-01 | 1183 bayt | `task_board.json` 91 alan mojibake düzelt | kodlama_denetim.py ✅ | ✅ ONAYLANDI |

## Çözüm (D-172 Düzeltmesi)

### Seçenek 1: Dinamik Pano Yönlendirmesi
`pano_denetim.py` ve `trigger.py` merkez panasını okusunlar:
```python
# worktree'de çalışsa da merkez panasına bak
PANO_DOSYA = Path("c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json").resolve()
```
**Riski:** Merkez ve worktree pano mantığı çakışabilir (iki sistem birbirine girebilir).

### Seçenek 2: Senkronizasyon Script'i
Saatlik: `Huginn Data Insights/data/orchestrator/task_board.json` → `worktree klasoru/data/orchestrator/task_board.json` (review görevleri kopyala)

**Riski:** Zaman gecikmesi, çatışma yönetimi karmaşık.

### Seçenek 3: İçten Dış Mimariye Geçiş (Tavsiye)
Worktree panosu yalnızca Utku'nın operasyon görevleri tutarsa, merkez panolar başka (UI/sistem) tutarsa → net ayrım. Tetik sistemi worktree'de kalsın.

Bu durumda 3 görev aslen merkez'de tamamlandı, worktree'de görülmedi çünkü iki sistem ayrı. Worktree'ye ekleme doğru eylem.

## Tavsiye

1. **Hemen:** 3 görev onaylanabilir (kanıt ve rapor OK).
2. **Sonra:** Pano mimarisi karar verilmeli:
   - Tek pano (merkez yönetir) mi?
   - Çift pano (operasyon ayrı) mı?
   - Hangi görevler hangi panada?
3. Seçilirse D-172 prosedürü dökümante edilsin.

## İlgili Belgeler
- `scripts/pano_denetim.py` — senkronizasyon oku/yaz
- `src/company_master/orchestrator/trigger.py` — tetik sistem
- `ANA_KURALLAR.md` Kural 7 (D-77: Pano Disiplini)
