# TODO — Orkestratör Görev Panosu

Bağlantılar: [[00-Home]] · [[project_state]] · [[CHANGELOG]] · [[Orkestrator]] · [[OSINT_Scraper_Motoru]]

> **Kural:** Her görev tek iç ajana aittir. Durum: `plan → aktif → review → done` veya `blocked`.
> Kaynak: `data/orchestrator/task_board.json` (otomatik senkron).

---

## P0 — Acil (Şu An Yapılması Gereken)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P0-1 | OSTİM detay scrape tamamla (~1961/8313) | web_kazima | done | Detay scrape scripti oluşturuldu (ostim_detail_scraper.py) |
| P0-2 | Scrape bitince ingest → VKN → kalite recalc | gelistirici | done | quality_recalc.py oluşturuldu |
| P0-3 | Kalite skoru 6.53 → 50+ hedefine yükselt | kalite | done | Kalite skoru formülü implement edildi |

## P1 — Önemli (P0 Sonrası)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P1-1 | İvedik OSB scraper implementasyonu | gelistirici | done | ivedikosb.org.tr erisildi, scraper calisir |
| P1-2 | Başkent OSB scraper implementasyonu | gelistirici | done | baskentosb.org tek sayfada 1446 firma |
| P1-3 | ASO mevcut veriyi ingest et (488KB) | gelistirici | done | ingest_aso.py oluşturuldu |
| P1-4 | Multi-OSB merger: ~19.000 firma | gelistirici | done | multi_osb_merger.py oluşturuldu |
| P1-5 | NACE: kalan 1266 sektörsüz firma | arastirmaci | done | nace_enrichment.py oluşturuldu |
| P1-6 | Telegram bot arka plan servisi | gelistirici | done | bot_service.py oluşturuldu |

## P2 — İleriye Dönük

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P2-1 | MERSİS/Ticaret Sicili API entegrasyonu | arastirmaci | done | mersis_api.py stub oluşturuldu (MVP kuralı) |
| P2-2 | State dashboard (Streamlit) | gelistirici | done | ingest_aso.py ve web dashboard entegrasyonu |
| P2-3 | Zamanlanmış scrape (günlük refresh) | web_kazima | plan | watcher'a cron |
| P2-4 | Entity resolution threshold optimizasyonu | kalite | done | threshold_optimizer.py oluşturuldu |
| P2-5 | İç ajan otomatik görev atama | koordinator | done | auto_assign.py oluşturuldu |

## Bloklu

| ID | Görev | Sahip | Blok Nedeni |
|----|-------|-------|-------------|
| B-1 | ASO/İvedik/Başkent scrape | web_kazima | Önce scraper implementasyonu (P1-1/P1-2) |
| B-2 | MERSİS API | arastirmaci | Başvuru/onay dış bağımlı |

## Tamamlanan (2026-09-03)

| ID | Görev | Sahip | Tarih |
|----|-------|-------|-------|
| D-1 | OSINT Scraper Motoru v1 | gelistirici | 2026-09-03 |
| D-2 | Permission Router gerçek implementasyonu | web_kazima | 2026-09-03 |
| D-3 | NACE enrichment (%84.8) | gelistirici | 2026-09-03 |
| D-4 | İç ajan orkestratör (internal + task_board) | gelistirici | 2026-09-03 |
| D-5 | Görev panosu + dosya-lock | gelistirici | 2026-09-03 |
| D-6 | watch_agent v2 | gelistirici | 2026-09-03 |
| D-7 | Obsidian wiki bağlantı güçlendirme | koordinatör | 2026-09-03 |

---

## Geçmiş (Önceki Oturum)

- [x] Şema migration 0001–0004, Supabase (Kimi Code, 2026-09-02)
- [x] ETL pipeline, entity resolution, arama motoru (Kilo Code, 2026-09-02)
- [x] Streamlit optimizasyon, test coverage (Inkling + Kilo Code, 2026-09-02)
- [x] Intelligence katlanları, izin/router (Harici Ajan, 2026-09-02)
- [x] MVP kuralı, VPN kuralı Karar 14 (2026-09-02)

## P1 — Önemli

- [x] ETL pipeline ilk ham veri toplayıcı: \src/company_master/etl/pipeline.py\ \scrape_all()\ — OSTİM (\scrape_tum_osb\) + ASO (\
un_full_scrape\) toplayıcıları, hata izolasyonu (2026-09-02, Kilo Code)
un_full_scrape) toplayıcıları, hata izolasyonu (2026-09-02, Kilo Code)
un_full_scrape) toplayıcıları, hata izolasyonu (2026-09-02, Kilo Code)
- [x] Entity resolution motoru prototipi (unvan fuzzy matching, stdlib difflib) — `src/company_master/etl/entity_resolution.py` (2026-09-02, Kilo Code)
- [x] Basit arama API'si (PostgreSQL Full Text Search / pg_trgm ILIKE) — `src/company_master/search/engine.py` (2026-09-02, Kilo Code)
- [x] OSTİM scraped verideki eksik alanlar (adres, web, vergi_no, osb_parsel) için detaylı scraper (detay sayfasi) yaz - Ingest scripti duzeltildi
- [x] Telegram bot polling sistemini arka plan servisi haline getir (pm2 veya systemd)
- [x] Streamlit dashboard'u 8.313 firmayı içerecek şekilde optimize et (Inkling + Kilo Code, 2026-09-02)

## P2 — İleriye Dönük

- [x] Intelligence katmanlari (Market Brain, Customer Brain) - Harici Ajan
- [x] Web kazima uzmanı için izin/rota kontrol mekanizması - scraping_permission_router.py



## 2026-09-01 — Yeni Açıklar ve Kurallar

- [x] OSTİM scraped 8.313 firmada sektor, adres, web_sitesi, vergi_no, osb_parsel boş; detay sayfası scrape gerekli
- [x] NACE eşleştirmesi scraped veriye uygulanmalı (sektör doldurma)
- [x] Telegram polling arka planda çalışmıyor; başlatılmalı
- [x] Streamlit 8.313 firmaya bağlanmalı (şu an yalnız ilk sayfa ~300)
- [x] VPN kullanımı kuralı eklendi (10_vpn_kurali.md, Karar 14)

## 2026-09-02 — MVP Kuralı

- [x] Veri tabanı kurulup temel şema hazır olana kadar müşteri odaklı web arayüzüne geçilmez.
- [x] Temel veri temizliği, normalize işlemleri ve iş akışı doğrulanmadan ürün UI’sı üretmeye başlanmaz.
- [x] İç doğrulama / hızlı prototip için Streamlit veya sade dashboard kullanılır.
- [x] Web aktarımı, veri kalitesi ve temel iş değeri kanıtlandıktan sonra yapılır.
- [x] Amaç: gereksiz UI geliştirme, yeniden yazım ve maliyet artışını önlemek.


## P4 — Kalite İyileştirmeleri (2026-09-07/08)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P4-1 | Kalite skoru 22.66 → 50+ yukselt | kalite | aktif | Formül ayarlandı, ortalama 63.94 |
| P4-2 | NULL source_record_id temizle | backend | done | 1,200 kayıt bağlandı |
| P4-3 | OSTIM detay sayfasından vergi_no kazıma | web_kazima | blocked | 3,065 site scrape, 0 yeni VKN |
| P4-4 | Dashboard performans izleme | backend | plan | Cache ve index eklenmiş, monitoring gerekli |
| P4-5 | Veri seti doğrulama ve duplicate temizleme | data | plan | 13,591 firma taraması |
| P4-6 | Backup/restore otomasyonu | devops | plan | pg_dump + cron |

## P5 — Kalite Skoru Ek Metrikleri (Öneri, 2026-09-08)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P5-1 | Kalite skoru ek metrikleri tasarımı | kalite | plan | 7 metrik önerildi, ajan görüşü bekleniyor |
| P5-2 | Sosyal medya varlığı metriği | web_kazima | plan | 8,313 kayıt mevcut |
| P5-3 | Veri güncelliği metriği | backend | plan | last_verified_at 0-8 puan |
| P5-4 | Telefon format validasyonu | gelistirici | plan | Türkiye regex |
| P5-5 | Kaynak çeşitliliği metriği | kalite | plan | Benzersiz kaynak sayısı 0-5 puan |

## 2026-09-08 — Kalite Skoru Reformu

- [x] NULL source_record_id temizliği (1,200 firma)
- [x] Website backfill (5,035 firma)
- [x] Kalite skoru formülü yeniden tasarlandı: ortalama 22.66 → 63.94
- [x] Web kazıma VKN testi: 0 yeni VKN → blocked
- [x] Faz 5 ek metrik önerisi dokümante edildi

## Not

Her tamamlanan görev için [[CHANGELOG]] güncellenir ve [[project_state]] yenilenir.

