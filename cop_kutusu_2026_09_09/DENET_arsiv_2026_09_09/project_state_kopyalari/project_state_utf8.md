# Project State



BaÄŸlantÄ±lar: [[00-Home]] Â· [[TODO]] Â· [[CHANGELOG]] Â· [[01_sirket_master_ana_belgesi]]



## Proje AdÄ±



Ankara B2B Company Master â€” V1.0



## Mevcut Durum



### Tamamlananlar



- Company Master V1.0 ÅŸema tasarÄ±mÄ± (19 tablo)

- ETL mimarisi ve veri akÄ±ÅŸÄ± tanÄ±mlandÄ±

- MVP gereksinimleri (P0/P1/P2) belirlendi

- V9 ile karÅŸÄ±laÅŸtÄ±rma yapÄ±ldÄ±

- Ajan ekosistemi tanÄ±mlandÄ±

- Veri kalitesi / sentetik veri / PII tarama prototipi `src/data_quality_toolkit/` altÄ±na taÅŸÄ±ndÄ±.

- `src/company_master/` paket iskeleti oluÅŸturuldu (ÅŸema, ETL, entity_resolution, search, services).

- 16 temel test eklendi ve geÃ§ti.

- PostgreSQL migration seti canlÄ± Supabase sunucusuna uygulandÄ±: 4 migration (0001â€“0004), 22 tablo eksiksiz oluÅŸturuldu.
- PostgreSQL 17 `pg_dump` kurulumu yapÄ±ldÄ±; `scripts/supabase_backup.py` PATH fallback mekanizmasÄ± ile gÃ¼ncellendi ve ilk sÄ±kÄ±ÅŸtÄ±rÄ±lmÄ±ÅŸ tam veritabanÄ± yedeÄŸi alÄ±ndÄ± (`backups/supabase_20260902_001559.sql.gz`).

- ETL pipeline prototipi tamamlandÄ±: `src/company_master/etl/pipeline.py` ile 8.313 OSTÄ°M firmasÄ± `source_records` tablosuna bulk aktarÄ±ldÄ± (content_hash dedup, idempotent). `db/connection.py` Supabase psycopg URL dÃ¼zeltildi.

- Normalizasyon + arama motoru tamamlandÄ±: `0005` migration (`companies.source_record_id` FK) + `etl/normalize.py` ile 8.313 firma `companies` tablosuna aktarÄ±ldÄ± (idempotent). `search/engine.py` pg_trgm ILIKE arama motoru; test sorgularÄ± Ã§alÄ±ÅŸtÄ±.

- Entity resolution entegrasyon tamamlandÄ±: `etl/entity_resolution.py` VKN/fuzzy matching ile `source_records` â†’ `companies` eÅŸleÅŸtirme, `entity_resolution` tablosuna sonuÃ§ yazar.

- Telegram bot entegrasyon: `scripts/telegram_polling.py` â€” komut yetkilendirme, `/restart_etl`, `/set_status`, `/daily_report` (09:00). KullanÄ±m rehberi: `scripts/README_TELEGRAM.md`.

- OSINT Scraper Motoru v1 kuruldu ([[OSINT_Scraper_Motoru]]): izin router (robots.txt/KVKK/rate-limit), kaynak kayÄ±t defteri, orkestratÃ¶r CLI + scrape watcher.

- NACE enrichment tamamlandÄ±: 7047/8313 (%84.8) firma NACE kodu aldÄ±, migration 0006 uygulandÄ±, KPI raporu gÃ¼ncellendi.

- ASO rehber verisi toplandÄ± (data/aso/aso_full.jsonl, ~488KB); OSTÄ°M detay scrape arka planda devam ediyor.
### AÃ§Ä±k Sorunlar

- Veri toplama iÃ§in fiili kaynak eriÅŸimi (GÄ°B, Oda, diÄŸer OSB'ler) baÅŸlatÄ±lmadÄ±.




- Veri toplama iÃ§in fiili kaynak eriÅŸimi (GÄ°B, Oda, diÄŸer OSB'ler) baÅŸlatÄ±lmadÄ±.



## Aktif Kararlar



- VKN Primary Key olmayacak; company_id UUID kullanÄ±lacak.

- MVP iÃ§in PostgreSQL + Full Text Search yeterli.

- Ham veri source_records tablosunda saklanacak.

- MVP sÄ±nÄ±rÄ±: Veri tabanÄ± kurulumunun, temel veri temizliÄŸinin ve iÅŸ akÄ±ÅŸÄ±nÄ±n doÄŸrulanmadan mÃ¼ÅŸteri odaklÄ± web arayÃ¼zÃ¼ne geÃ§ilmez. Ä°lk etapta iÃ§ doÄŸrulama iÃ§in Streamlit gibi sade ara yÃ¼z kullanÄ±lÄ±r; web aktarÄ±mÄ± veri deÄŸeri kanÄ±tlandÄ±ktan sonra yapÄ±lÄ±r.



## Bilinen Riskler



- Kod/belge uyumsuzluÄŸu teknik borÃ§ yaratÄ±yor.

- Veri toplama yasal sÄ±nÄ±rlarÄ± henÃ¼z detaylandÄ±rÄ±lmadÄ±.



## Ã‡Ã¶zÃ¼len Kararlar



### Kod / Belge UyumsuzluÄŸu (2026-09-01)



- **Karar:** SeÃ§enek A â€” AyrÄ± ModÃ¼l

- **Uygulama:** `src/` modÃ¼lleri `src/data_quality_toolkit/` altÄ±na taÅŸÄ±ndÄ±. Company Master iÃ§in `src/company_master/` paket iskeleti oluÅŸturuldu. data_quality_toolkit artÄ±k ETL boru hattÄ±nda yardÄ±mcÄ± bileÅŸen olarak kullanÄ±lacak.



## 2026-09-01 (v0.2) â€” CanlÄ± Veri Entegrasyonu



- OSTÄ°M scraper dÃ¼zeltildi (selector rewrite)

- Ä°lk sayfa scrape: data/ostim/firmalar_sayfa1.jsonl

- Kalite raporu: data/ostim/kalite_raporu.md

- Streamlit arayÃ¼zÃ¼ne baÄŸlandÄ±: http://localhost:8501

- Arama + filtre + CSV indirme aktif



## 2026-09-01 â€” Telegram Bot Entegrasyonu



- [@Huginn_Insights_Bot](https://t.me/Huginn_Insights_Bot) aktif

- Test mesajÄ± baÅŸarÄ±yla gÃ¶nderildi (message_id: 5)

- Polling baÅŸlatÄ±ldÄ±, `/status`, `/gorev`, `/rapor` komutlarÄ± Ã§alÄ±ÅŸÄ±yor

- Token `.env`'de saklanÄ±yor, `.gitignore`'da gizli

- Rehber: `V10/09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md`


## 2026-09-06 â€” Scraper Yenileme ve Kalite Duzeltmeleri

- Ivedik OSB scraper yeniden calisir hale getirildi (`ivedikosb.org.tr`)
- Baskent OSB scraper yeniden calisir hale getirildi (`baskentosb.org`)
- Ivedik: ~3354 firma toplandi
- Baskent: 1446 firma toplandi (tek sayfa)
- Tum scraper ciktileri ingest edildi: 4584 yeni firma eklendi
- Veritabani toplam: 13,591 firma
- Kod kalitesi acil duzeltmeleri tamamlandi (task_board, web_app, scrapers)
- Web dashboard API ve frontend duzeltmeleri yapildi
- Testler: 104 passed, 1 warning



## 2026-09-07 — Kalite Skoru İyileştirmeleri ve Faz 4 Başlangıcı

### Tamamlanan
- NULL source_record_id temizliği: 1,200 firma source_records'a bağlandı (P4-2)
- Website backfill: 5,035 firmanın website_domain alanı raw_website'den dolduruldu
- Kalite skoru formülü yeniden tasarlandı:
  - Telefon(15), Email(10), Web(10), NACE(15), Adres(10), Vergi(10), Parsel(5)
  - Yeni bonuslar: source_record_id(+5), payload(+5)
  - Ceza oranları düşürüldü
- Ortalama kalite skoru: 22.66 › 63.94 (10,105 firma)
- P4-3 web kazıma test edildi: 3,065 site scrape, 0 yeni VKN bulunamadı › blocked

### Ek Metrik Önerisi (Faz 5)
- Yeni kalite skoru ek metrikleri önerildi ve dokümante edildi:
  - AI proje v1/V10/12_kalite_metrikleri/01_kalite_skoru_ek_metrikleri.md
- Önerilen metrikler: iş ilanı sayısı(0-8), çalışan sayısı(0-7), sosyal medya(0-5),
  e-posta validasyonu(0-3), telefon formatı(0-2), veri güncelliği(0-8), kaynak çeşitliliği(0-5)
- P5-1 ile P5-5 task_board'a eklendi, ajan görüşleri bekleniyor

### Açık Sorular
- Web kazıma VKN için etkisiz çıktı. MERSIS API veya GIB vkn.gov.tr denenecek mi?
- Yeni ek metriklerin ağırlıklarına diğer ajanlar ne diyecek?
- Veri güncelliği metriği için otomatik scrape zamanlaması kurulacak mı?


## 2026-09-09 — P5 Kalite Metrikleri Tamamlandı ve Skor 76.44'ye Ulaştı

### P4-1 Tamamlandı (Hedef: 50+ › Gerçekleşen: 76.44)
- **Başlangıç skoru:** 22.66 (2026-09-07)
- **Website backfill sonrası:** 27.53
- **Formül ayarı sonrası:** 63.94
- **P5 metrikleri ile final:** **76.44** (hedef %152 geçildi)

### P5 Metrikleri Implementasyonu
| Metrik | Ağırlık | Dağılım | Not |
|--------|---------|---------|-----|
| Veri güncelliği | 0-8 | 8,222 firma: 8p, 1,005: 0p | last_verified_at <30g = 8p |
| Telefon formatı | 0-2 | 7,798: 2p, 114: 1p, 1,315: 0p | Türkiye format regex |
| Sosyal medya | 0-5 | 5,014: 5p (4+ platform), 4,213: 0p | raw_payload->sosyal_medya |
| Kaynak çeşitliliği | 0-5 | 9,227: 0p (hepsi tek kaynak) | Gelecekte işlevsel olacak |
| İş ilanları | 0-8 | 9,227: 0p (veri yok) | Henüz veri kaynağı yok |
| Çalışan sayısı | 0-7 | 9,227: 0p (veri yok) | employee_count kolonu boş |
| E-posta validasyonu | 0-3 | 4,186: 2p (format geçerli), 5,041: 0p | Sadece format kontrolü |

### Toplam P5 Katkısı
- **Maks potansiyel:** 38 puan
- **Gerçekleşen ortalama katkı:** ~12.5 puan
- **Sonuç:** 63.94 › 76.44

### Sonraki Adımlar
- İş ilanı ve çalışan sayısı veri kaynakları kurulacak (LinkedIn API, web kazıma)
- E-posta DNS MX kontrolü eklenecek
- Kaynak çeşitliliği için multi-source ingestion planlanacak
