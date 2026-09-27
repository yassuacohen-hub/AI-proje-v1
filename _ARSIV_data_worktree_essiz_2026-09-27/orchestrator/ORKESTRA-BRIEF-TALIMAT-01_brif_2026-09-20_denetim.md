# ORKESTRA-BRIEF-TALIMAT-01 Briefi

## GÖREV TANIMI
YASU, pano brifleme audit raporundan (ORKESTRA-BRIEF-KALITE-01) 4 görevin talimat alanı boş veya dosya yok bulgusu üzerine bu görevleri kur ve talimat dosyalarını oluştur.

Bulgular (ORKESTRA-BRIEF-KALITE-01_rapor satırlarından):
- ADMIN-UX-LOGOUT-01: talimat yok
- ALTYAPI-FORM-SETUP-03: talimat yok
- ALTYAPI-PROXY-CONFIG-02: talimat yok
- ALTYAPI-WEB-MONITOR-01: talimat yok

## İŞ MADDELERİ

1. **4 görevin talimat dosyasını panodan kontrol et:**
   - `python scripts/gorev_at.py pano` çıktısından görevler listele.
   - Herbir görev için `data/orchestrator/<TASK>_brif_*.md` dosyası var mı kontrol et.

2. **Her görev için talimat dosyası oluştur (basit şablon):**
   ```markdown
   # <TASK> Briefi
   
   ## GÖREV TANIMI
   ...
   
   ## İŞ MADDELERİ
   1. ...
   2. ...
   
   ## KENDİ-KONTROL
   - [ ] İş tamamlandı
   ```
   Dosyalar:
   - `data/orchestrator/ADMIN-UX-LOGOUT-01_brif_2026-09-20_denetim.md`
   - `data/orchestrator/ALTYAPI-FORM-SETUP-03_brif_2026-09-20_denetim.md`
   - `data/orchestrator/ALTYAPI-PROXY-CONFIG-02_brif_2026-09-20_denetim.md`
   - `data/orchestrator/ALTYAPI-WEB-MONITOR-01_brif_2026-09-20_denetim.md`

3. **Panodaki talimat alanlarını güncelle:**
   ```bash
   python scripts/gorev_at.py guncelle --task-id ADMIN-UX-LOGOUT-01 --talimat "data/orchestrator/ADMIN-UX-LOGOUT-01_brif_2026-09-20_denetim.md"
   python scripts/gorev_at.py guncelle --task-id ALTYAPI-FORM-SETUP-03 --talimat "data/orchestrator/ALTYAPI-FORM-SETUP-03_brif_2026-09-20_denetim.md"
   python scripts/gorev_at.py guncelle --task-id ALTYAPI-PROXY-CONFIG-02 --talimat "data/orchestrator/ALTYAPI-PROXY-CONFIG-02_brif_2026-09-20_denetim.md"
   python scripts/gorev_at.py guncelle --task-id ALTYAPI-WEB-MONITOR-01 --talimat "data/orchestrator/ALTYAPI-WEB-MONITOR-01_brif_2026-09-20_denetim.md"
   ```

4. **Rapor yaz:**
   - 4 dosya oluşturuldu.
   - 4 görev talimat güncellendi.
   - Çakışma veya sorun varsa belirt.

## KENDİ-KONTROL

```bash
# Talimat dosyaları var mı?
dir data/orchestrator/*-LOGOUT-01_brif*.md
dir data/orchestrator/*-FORM-SETUP-03_brif*.md
dir data/orchestrator/*-PROXY-CONFIG-02_brif*.md
dir data/orchestrator/*-WEB-MONITOR-01_brif*.md

# Pano güncellemesi
python scripts/gorev_at.py pano | findstr "LOGOUT-01\|FORM-SETUP-03\|PROXY-CONFIG-02\|WEB-MONITOR-01"
# Talimat alanı dolu görülmeli
```
