# ALTYAPI-KILIT-TEMIZLE-01: File Locks Temizliği

## Görev Özeti

`data/orchestrator/file_locks.json` dosyasındaki eski/stale kilit kayıtlarını temizle. Yalnızca aktif kilit dosyaları kalacak.

## Bağımlılıklar

- ✅ **file_locks.json** — mevcut (3 kayıt, bazıları stale olabilir)
- ✅ **İlgili dosyalar** — lock'lanmış olan dosyaların mevcudiyeti kontrol

## Çıktı

1. **Kilit analizi**:
   - Hangi dosyalar lock'lanmış?
   - Hangileri aktif, hangileri stale?

2. **Temizlik**:
   - Stale kilit kayıtlarını sil
   - Sadece aktif/geçerli kilit'ler kalsın

3. **Rapor**:
   - `[[Karar: File locks merkezi yönetimi]]`
   - `[[Kod: data/orchestrator/file_locks.json temizliği]]`

## Kurallar

- **D-55**: Brief dosyası adı `brief_yasu_ALTYAPI-KILIT-TEMIZLE-01.md`
- **D-87**: Resmi atama `python scripts/gorev_atama_otomatis.py --task-id ALTYAPI-KILIT-TEMIZLE-01 --ajan yasu`

## Sahibi

- **Sahip**: Yasu (`yasu`)
- **Görev Kimliği**: `ALTYAPI-KILIT-TEMIZLE-01`
- **Öncelik**: P2
- **Pano Durumu**: `aktif`

## Teslim

- Dosya: `data/orchestrator/file_locks.json` (temizlenmiş)
- Rapor dosyası: `data/orchestrator/ALTYAPI-KILIT-TEMIZLE-01_rapor_YYYY-MM-DD_yasu.md`

## Süre Tahmini

- **Analiz + temizlik**: ~10 min

## Tetik Zinciri

Sonraki: **İhsan görevleri** (UI-AYARLAR-SAYFA-01).
