# Project State

Bağlantılar: [[00-Home]] · [[TODO]] · [[CHANGELOG]] · [[01_sirket_master_ana_belgesi]]

## Proje Adı

Ankara B2B Company Master ” V1.0

## Mevcut Durum

### Tamamlananlar

- Company Master V1.0 şema tasarımı (19 tablo)

- ETL mimarisi ve veri akışı tanımlandı

- MVP gereksinimleri (P0/P1/P2) belirlendi

- V9 ile karşılaştırma yapıldı

- Ajan ekosistemi tanımlandı

- Veri kalitesi / sentetik veri / PII tarama prototipi `src/data_quality_toolkit/` altına taşındı.

- `src/company_master/` paket iskeleti oluşturuldu (şema, ETL, entity_resolution, search, services).

- 16 temel test eklendi ve geçti.

- PostgreSQL migration seti canlı Supabase sunucusuna uygulandı: 4 migration (0001“0004), 22 tablo eksiksiz oluşturuldu.
- PostgreSQL 17 `pg_dump` kurulumu yapıldı; `scripts/supabase_backup.py` PATH fallback mekanizması ile güncellendi ve ilk sıkıştırılmış tam veritabanı yedeği alındı (`backups/supabase_20260902_001559.sql.gz`).

- ETL pipeline prototipi tamamlandı: `src/company_master/etl/pipeline.py` ile 8.313 OSTİM firması `source_records` tablosuna bulk aktarıldı (content_hash dedup, idempotent). `db/connection.py` Supabase psycopg URL düzeltildi.

- Normalizasyon + arama motoru tamamlandı: `0005` migration (`companies.source_record_id` FK) + `etl/normalize.py` ile 8.313 firma `companies` tablosuna aktarıldı (idempotent). `search/engine.py` pg_trgm ILIKE arama motoru; test sorguları çalıştı.

- Entity resolution entegrasyon tamamlandı: `etl/entity_resolution.py` VKN/fuzzy matching ile `source_records` â†’ `companies` eşleştirme, `entity_resolution` tablosuna sonuç yazar.

- Telegram bot entegrasyon: `scripts/telegram_polling.py` ” komut yetkilendirme, `/restart_etl`, `/set_status`, `/daily_report` (09:00). Kullanım rehberi: `scripts/README_TELEGRAM.md`.

- OSINT Scraper Motoru v1 kuruldu ([[OSINT_Scraper_Motoru]]): izin router (robots.txt/KVKK/rate-limit), kaynak kayıt defteri, orkestratör CLI + scrape watcher.

- NACE enrichment tamamlandı: 7047/8313 (%84.8) firma NACE kodu aldı, migration 0006 uygulandı, KPI raporu güncellendi.

- ASO rehber verisi toplandı (data/aso/aso_full.jsonl, ~488KB); OSTİM detay scrape arka planda devam ediyor.
### Açık Sorunlar

- Veri toplama için fiili kaynak erişimi (GİB, Oda, diğer OSB'ler) başlatılmadı.

- Veri toplama için fiili kaynak erişimi (GİB, Oda, diğer OSB'ler) başlatılmadı.

## Aktif Kararlar

- VKN Primary Key olmayacak; company_id UUID kullanılacak.

- MVP için PostgreSQL + Full Text Search yeterli.

- Ham veri source_records tablosunda saklanacak.

- MVP sınırı: Veri tabanı kurulumunun, temel veri temizliğinin ve iş akışının doğrulanmadan müşteri odaklı web arayüzüne geçilmez. İlk etapta iç doğrulama için Streamlit gibi sade ara yüz kullanılır; web aktarımı veri değeri kanıtlandıktan sonra yapılır.

## Bilinen Riskler

- Kod/belge uyumsuzluğu teknik borç yaratıyor.

- Veri toplama yasal sınırları henüz detaylandırılmadı.

## Ã‡özülen Kararlar

### Kod / Belge Uyumsuzluğu (2026-09-01)

- **Karar:** Seçenek A ” Ayrı Modül

- **Uygulama:** `src/` modülleri `src/data_quality_toolkit/` altına taşındı. Company Master için `src/company_master/` paket iskeleti oluşturuldu. data_quality_toolkit artık ETL boru hattında yardımcı bileşen olarak kullanılacak.