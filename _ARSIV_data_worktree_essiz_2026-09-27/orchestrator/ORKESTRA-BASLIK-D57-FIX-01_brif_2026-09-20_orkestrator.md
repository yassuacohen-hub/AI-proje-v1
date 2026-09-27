# ORKESTRA-BASLIK-D57-FIX-01 Brifingi

## Görev Tanımı
Pano görev başlıklarını D-57 standardına uydurmak. ORKESTRA-BRIEF-KALITE-01 raporunda 11/12 brifte başlık formatı ihlali tespit edildi.

## D-57 Kalıbı
`[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)`

Kanonik ALAN: `UI`, `API`, `VERI`, `TEST`, `DOC`, `ALTYAPI`, `ORKESTRA`
Kanonik FİİL: `yaz`, `düzelt`, `taşı`, `sil`, `denetle`, `ölç`, `belgele`, `araştır`

## İş Maddeleri

1. **Düzeltilecek 11 başlık listesi:**
   - ADMIN-UX-LOGOUT-01: `[ADMIN-UX-LOGOUT-01] Yönetici çıkış → admin_logout.py (30m)` → `[UI] Yönetici çıkış uygulaması yaz → web_dashboard/tabs/admin_auth.py (1s)`
   - ALTYAPI-BENCHMARK-02: `[ALTYAPI] Performans ölçümü (API+Streamlit) → docs/raporlar/benchmark_2026-09-20.md (2s)` → `[ALTYAPI] Performans ölç → docs/raporlar/benchmark_2026-09-20.md (2s)`
   - ALTYAPI-BILGI-TABANI-03: `[ALTYAPI] Runbook ve uyum denetimi belgele → docs/RUNBOOK.md (2s)` → ✓ (zaten uyumlu: fiil "belgele" var)
   - ALTYAPI-FORM-SETUP-03: `[ALTYAPI] Form yardımcı fonksiyonları → src/.../forms/ (30m)` → `[ALTYAPI] Form fonksiyonları yaz → src/company_master/ui/forms/ (1s)`
   - ALTYAPI-PROXY-CONFIG-02 (test): `[ALTYAPI] Proxy yapılandırması test et` → `[ALTYAPI] Proxy yapılandırmasını denetle → config/nginx.conf (2s)`
   - ALTYAPI-PROXY-CONFIG-02 (uretim): `[ALTYAPI] Proxy yapılandırması üretim` → `[ALTYAPI] Proxy yapılandırmasını düzelt → config/nginx.conf (1s)`
   - ALTYAPI-SQLITE-INIT: `[ALTYAPI] SQLite veritabanı şeması` → `[ALTYAPI] SQLite şemasını yaz → src/company_master/db/init.py (1s)`
   - ALTYAPI-TEST-FAILURE-FIX-01: ✓ (zaten uyumlu)
   - ALTYAPI-WEB-MONITOR-01 (test): `[ALTYAPI] Web izleme (test)` → `[ALTYAPI] Web izlemesini denetle → src/.../monitoring/alert_rules.json (2s)`
   - ALTYAPI-WEB-MONITOR-01 (uretim): `[ALTYAPI] Web izleme (üretim)` → `[ALTYAPI] Web izlemesini yaz → src/.../monitoring/alert_rules.json (2s)`
   - DOC-V10-AUDIT-01: `[DOC] V10 audit belgesi yaz` → `[DOC] V10 audit belgesi yaz → docs/V10_AUDIT_2026-09-20.md (4s)`

2. **Panoyu güncelle:** `python scripts/gorev_at.py guncelle --task-id <ID> --baslik "<yeni başlık>"`
   11 görev için başlıkları yenile.

3. **Doğrula:**
   ```bash
   python -X utf8 -c "
   import json
   from pathlib import Path
   board = json.loads(Path('data/orchestrator/task_board.json').read_text())
   problem_ids = ['ADMIN-UX-LOGOUT-01', 'ALTYAPI-BENCHMARK-02', 'ALTYAPI-FORM-SETUP-03', 
                  'ALTYAPI-PROXY-CONFIG-02', 'ALTYAPI-SQLITE-INIT', 'ALTYAPI-WEB-MONITOR-01', 
                  'DOC-V10-AUDIT-01']
   for t in board:
       if t['task_id'] in problem_ids:
           baslik = t.get('baslik', '')
           parts = baslik.split(']', 1)
           if len(parts) > 1:
               icerik = parts[1].strip()
               if '→' in icerik and '(' in icerik and ')' in icerik:
                   print(f'✓ {t[\"task_id\"]}: uyumlu')
               else:
                   print(f'✗ {t[\"task_id\"]}: EXPECTED [ALAN] FİİL → ÇIKTI (SÜRE), GOT: {baslik}')
   "
   ```

## Self-Check

- [ ] 11 brif başlığı D-57 formatında: `[ALAN] FİİL → ÇIKTI (SÜRE)`
- [ ] ALAN ∈ {UI, API, VERI, TEST, DOC, ALTYAPI, ORKESTRA}
- [ ] FİİL ∈ {yaz, düzelt, taşı, sil, denetle, ölç, belgele, araştır}
- [ ] ÇIKTI = tek dosya yolu
- [ ] SÜRE ∈ {30d, 1s, 2s, 4s} (4 saat veya altı)

## Rapor

Başarıyla tamamlanırsa:
- Değişen dosyalar: `data/orchestrator/task_board.json` (11 satır başlık güncellendi)
- Test: 11/12 brif D-57 uyumlu olur (11/11 = %100)
- Rapor: `data/orchestrator/ORKESTRA-BASLIK-D57-FIX-01_rapor_2026-09-20_orkestrator.md`

Rapor dosyası 5 başlık içermelidir: Ne yapıldı, Değişen dosyalar, Test sonuçları, Bulgular, Eksik/Erteleme.
