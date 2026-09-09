# Project State



Bağlantılar: [[00-Home]] · [[TODO]] · [[CHANGELOG]] · [[01_sirket_master_ana_belgesi]]



## Proje Adı



Ankara B2B Company Master — V1.0



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

- PostgreSQL migration seti canlı Supabase sunucusuna uygulandı: 4 migration (0001–0004), 22 tablo eksiksiz oluşturuldu.
- PostgreSQL 17 `pg_dump` kurulumu yapıldı; `scripts/supabase_backup.py` PATH fallback mekanizması ile güncellendi ve ilk sıkıştırılmış tam veritabanı yedeği alındı (`backups/supabase_20260902_001559.sql.gz`).

- ETL pipeline prototipi tamamlandı: `src/company_master/etl/pipeline.py` ile 8.313 OSTİM firması `source_records` tablosuna bulk aktarıldı (content_hash dedup, idempotent). `db/connection.py` Supabase psycopg URL düzeltildi.

- Normalizasyon + arama motoru tamamlandı: `0005` migration (`companies.source_record_id` FK) + `etl/normalize.py` ile 8.313 firma `companies` tablosuna aktarıldı (idempotent). `search/engine.py` pg_trgm ILIKE arama motoru; test sorguları çalıştı.

- Entity resolution entegrasyon tamamlandı: `etl/entity_resolution.py` VKN/fuzzy matching ile `source_records` → `companies` eşleştirme, `entity_resolution` tablosuna sonuç yazar.

- Telegram bot entegrasyon: `scripts/telegram_polling.py` — komut yetkilendirme, `/restart_etl`, `/set_status`, `/daily_report` (09:00). Kullanım rehberi: `scripts/README_TELEGRAM.md`.

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



## Çözülen Kararlar



### Kod / Belge Uyumsuzluğu (2026-09-01)



- **Karar:** Seçenek A — Ayrı Modül

- **Uygulama:** `src/` modülleri `src/data_quality_toolkit/` altına taşındı. Company Master için `src/company_master/` paket iskeleti oluşturuldu. data_quality_toolkit artık ETL boru hattında yardımcı bileşen olarak kullanılacak.



## 2026-09-01 (v0.2) — Canlı Veri Entegrasyonu



- OSTİM scraper düzeltildi (selector rewrite)

- İlk sayfa scrape: data/ostim/firmalar_sayfa1.jsonl

- Kalite raporu: data/ostim/kalite_raporu.md

- Streamlit arayüzüne bağlandı: http://localhost:8501

- Arama + filtre + CSV indirme aktif



## 2026-09-01 — Telegram Bot Entegrasyonu



- [@Huginn_Insights_Bot](https://t.me/Huginn_Insights_Bot) aktif

- Test mesajı başarıyla gönderildi (message_id: 5)

- Polling başlatıldı, `/status`, `/gorev`, `/rapor` komutları çalışıyor

- Token `.env`'de saklanıyor, `.gitignore`'da gizli

- Rehber: `V10/09_kurallar_ve_promptlar/09_telegram_bot_rehberi.md`


## 2026-09-06 — Scraper Yenileme ve Kalite Duzeltmeleri

- Ivedik OSB scraper yeniden calisir hale getirildi (`ivedikosb.org.tr`)
- Baskent OSB scraper yeniden calisir hale getirildi (`baskentosb.org`)
- Ivedik: ~3354 firma toplandi
- Baskent: 1446 firma toplandi (tek sayfa)
- Tum scraper ciktileri ingest edildi: 4584 yeni firma eklendi
- Veritabani toplam: 13,591 firma
- Kod kalitesi acil duzeltmeleri tamamlandi (task_board, web_app, scrapers)
- Web dashboard API ve frontend duzeltmeleri yapildi
- Testler: 104 passed, 1 warning



## 2026-09-07 � Kalite Skoru �yile�tirmeleri ve Faz 4 Ba�lang�c�

### Tamamlanan
- NULL source_record_id temizli�i: 1,200 firma source_records'a ba�land� (P4-2)
- Website backfill: 5,035 firman�n website_domain alan� raw_website'den dolduruldu
- Kalite skoru form�l� yeniden tasarland�:
  - Telefon(15), Email(10), Web(10), NACE(15), Adres(10), Vergi(10), Parsel(5)
  - Yeni bonuslar: source_record_id(+5), payload(+5)
  - Ceza oranlar� d���r�ld�
- Ortalama kalite skoru: 22.66 � 63.94 (10,105 firma)
- P4-3 web kaz�ma test edildi: 3,065 site scrape, 0 yeni VKN bulunamad� � blocked

### Ek Metrik �nerisi (Faz 5)
- Yeni kalite skoru ek metrikleri �nerildi ve dok�mante edildi:
  - AI proje v1/V10/12_kalite_metrikleri/01_kalite_skoru_ek_metrikleri.md
- �nerilen metrikler: i� ilan� say�s�(0-8), �al��an say�s�(0-7), sosyal medya(0-5),
  e-posta validasyonu(0-3), telefon format�(0-2), veri g�ncelli�i(0-8), kaynak �e�itlili�i(0-5)
- P5-1 ile P5-5 task_board'a eklendi, ajan g�r��leri bekleniyor

### A��k Sorular
- Web kaz�ma VKN i�in etkisiz ��kt�. MERSIS API veya GIB vkn.gov.tr denenecek mi?
- Yeni ek metriklerin a��rl�klar�na di�er ajanlar ne diyecek?
- Veri g�ncelli�i metri�i i�in otomatik scrape zamanlamas� kurulacak m�?
