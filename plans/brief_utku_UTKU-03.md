# UTKU-03 — Hata Loglama Sistemi (Production Hazırlığı)

**Ajan:** Utku  
**Aciliyet:** P0 (Production blokaj riski)  
**Süre:** 2 saat  
**Tür:** Altyapı / Observability  
**Kilitli dosya:** `src/company_master/core/error_handling.py`  
**Bağımlılık:** Yok  
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

## Neden
Production'da hata gözlemlenebilirliği kritik. Şu an hata logları sadece stdout'a yazılıyor, merkezi loglama, alerting ve debugging altyapısı yok. SLA ihlali riski yüksek.

## Doğrulanacak varsayım
- Python `logging` modülü kullanılır
- Structured JSON log formatı (ELK/Datadog uyumlu)
- Log seviyeleri: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Context enrichment: request_id, user_id, trace_id
- Sensitive data masking (PII, secrets)
- File rotation + stdout output
- External aggregator ready (stdout JSON → Datadog/ELK)

## Adımlar
1. `src/company_master/core/error_handling.py` oluştur:
   - `setup_logging()` - merkezi logging konfigürasyonu
   - `get_logger(name)` - module-level logger factory
   - `LogContext` - context manager for request-scoped enrichment
   - `mask_sensitive()` - PII/secret masking utility
2. `web_app.py` entegrasyonu:
   - `setup_logging()` startup'ta çağrılsın
   - Global exception handler loglasın
   - Request middleware request_id/trace_id eklesin
3. Test dosyası: `tests/test_error_handling.py` (8+ test)
4. Kodlama denetimi temiz

## Kabul kriteri
- [ ] `error_handling.py` modülü oluşturuldu
- [ ] `web_app.py` startup'ta logging başlatıyor
- [ ] Global exception handler logluyor
- [ ] Request middleware context enrichment ekliyor
- [ ] PII/secret masking çalışıyor
- [ ] Structured JSON output (stdout)
- [ ] File rotation + stdout dual output
- [ ] `tests/test_error_handling.py` 8+ test geçiyor
- [ ] Kodlama denetimi temiz

## Kurallar
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id UTKU-03 --ozet "<özet>"`

## Ilgili Nodlar
- [[src/company_master/core/]]
- [[web_app.py]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/scripts/kodlama_denetim.py]]