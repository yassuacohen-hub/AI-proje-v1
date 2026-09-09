# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| P3-2 | VKN web kazima genisle (sadece footer degil, tum sayfa) | web_kazima | plan | blocked | - |
| P4-3 | OSTIM detay sayfasindan vergi_no kazima (mevcut footer scripti genisle) | web_kazima | P1 | blocked | - |
| Y10 | MERSIS VKN zenginlestirme pipeline'i | gelistirici | P1 | blocked | src/company_master/etl/mersis_api.py |
| Y11 | GIB VKN dogrulama entegrasyonu | arastirmaci | P1 | plan | - |
| DENET-1 | Git deposu baslatma (git init + ilk commit) | devops | P1 | blocked | - |
| P6-1 | İş ilanları ve çalışan sayısı veri toplama (LinkedIn API + web kazıma) | web_kazima | P1 | cancelled | src/company_master/etl/job_postings_scraper.py |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| T1 | Ivedik scraper implementasyonu | gelistirici | 2026-09-06T20:58:44 |
| T2 | MERSIS API basvurusu takibi | arastirmaci | 2026-09-06T20:58:44 |
| T3 | Sema tasarimi | mimar | 2026-09-06T20:58:44 |
| T3b | Sema tasarimi | mimar | 2026-09-06T20:58:44 |
| P0-1 | OSTİM detay scrape tamamla (~1961/8313) | web_kazima | 2026-09-03T14:18:36 |
| P0-2 | Scrape bitince ingest → VKN → kalite recalc | gelistirici | 2026-09-03T14:18:36 |
| P0-3 | Kalite skoru 6.53 → 50+ hedefine yükselt | kalite | 2026-09-06T22:54:31 |
| P1-1 | İvedik OSB scraper implementasyonu | gelistirici | 2026-09-07T00:43:00 |
| P1-2 | Başkent OSB scraper implementasyonu | gelistirici | 2026-09-07T00:43:00 |
| P1-3 | ASO mevcut veriyi ingest et (488KB) | gelistirici | 2026-09-06T15:16:53 |
| P1-4 | Multi-OSB merger: ~19.000 firma | gelistirici | 2026-09-06T18:00:25 |
| P1-5 | NACE: kalan 1266 sektörsüz firma | arastirmaci | 2026-09-06T21:38:08 |
| P1-6 | Telegram bot arka plan servisi | gelistirici | 2026-09-06T11:37:43 |
| P2-1 | MERSİS/Ticaret Sicili API entegrasyonu | arastirmaci | 2026-09-06T20:58:44 |
| P2-2 | State dashboard (Streamlit) | gelistirici | 2026-09-06T10:54:48 |
| P2-3 | Zamanlanmış scrape (günlük refresh) | web_kazima | 2026-09-06T23:13:13 |
| P2-4 | Entity resolution threshold optimizasyonu | kalite | 2026-09-06T21:38:08 |
| P2-5 | İç ajan otomatik görev atama | gelistirici | 2026-09-06T16:26:51 |
| K1 | Delta-only board okuma (gorev_getir + locklar) | gelistirici | 2026-09-03T08:49:29 |
| K2 | Gorev brief mekanizmasi (otuomatik context) | gelistirici | 2026-09-03T08:52:58 |
| K3 | Session handoff (agentlar arasi devir) | gelistirici | 2026-09-03T08:59:40 |
| K4 | AGENT_SYNC otomatik sync | gelistirici | 2026-09-03T08:59:40 |
| K7 | Retry context decay (exponential backoff) | gelistirici | 2026-09-03T08:59:40 |
| K5 | Tool call ciktilarini kisalt | gelistirici | 2026-09-03T09:18:41 |
| K6 | Otomatik okuma listesi olustur | gelistirici | 2026-09-03T09:18:41 |
| H001 | ASO verisini ingest et | copilot | 2026-09-06T16:26:51 |
| H002 | ETL mimarisi review + guncelle | claude_code | 2026-09-06T16:26:51 |
| H003 | Ostim scraper code review | cursor_grok | 2026-09-06T16:26:51 |
| H004 | Telegram bot systemd servisini test et | copilot | 2026-09-06T16:26:51 |
| P1-7 | VKN web kazima (footer/hakkimizda/KVKK sayfalari) | web_kazima | 2026-09-06T21:38:08 |
| P3-1 | Adres verilerini raw_payload'dan primary_address'e ekle | gelistirici | 2026-09-07T10:00:50 |
| P3-3 | Kalite skoru 40-59 araligini 60+ yukselt | gelistirici | 2026-09-07T17:13:01.101278+00:00 |
| P3-4 | Dashboard filtresleme ve export ozellikleri ekle | frontend | 2026-09-07T10:42:59 |
| P3-5 | API cache ve performans optimizasyonu | backend | 2026-09-07T10:50:09 |
| P3-6 | Multi-OSB merger scripti (OSTIM+ASO+IB) | gelistirici | 2026-09-07T11:30:00 |
| P3-7 | NACE enrichment fuzzy matching | arastirmaci | 2026-09-07T11:30:00 |
| P3-8 | Telegram bot servisi | gelistirici | 2026-09-07T11:30:00 |
| P3-9 | MERSIS API stub (MVP kurali) | arastirmaci | 2026-09-07T11:30:00 |
| P3-10 | Kalite skoru recalc scripti | kalite | 2026-09-07T11:30:00 |
| P3-11 | ASO 488KB veri ingest | gelistirici | 2026-09-07T11:30:00 |
| P3-12 | Entity resolution threshold optimizer | kalite | 2026-09-07T11:30:00 |
| P3-13 | Ostim detay scrape scripti | web_kazima | 2026-09-07T11:30:00 |
| P3-14 | Ic ajan otomatik gorev atama | koordinator | 2026-09-07T11:30:00 |
| P4-1 | Kalite skorunu 22.66 -> 50+ yukselt (vergi_no ve adres eksikligi gider) | kalite | 2026-09-09T01:23:10 |
| P4-2 | NULL source_record_id kayitlarini temizle veya source_records'a bagla | backend | 2026-09-08T03:52:46 |
| P4-4 | Dashboard performans izleme ve slow query optimization | backend | 2026-09-09T11:32:51 |
| P4-5 | Veri seti dogrulama ve duplicate temizleme | data | 2026-09-08T09:26:22 |
| P4-6 | Backup/restore otomasyonu (pg_dump + cron) | devops | 2026-09-08T08:54:26 |
| Y1 | /api/companies coklu kaynak destegi (source IN (...)) | backend | 2026-09-08T00:15:02 |
| Y2 | Ivedik + Baskent OSB verilerini ingest et (scraper kodu hazir) | gelistirici | 2026-09-09T02:46:53 |
| Y3 | Turkce case-insensitive arama (i->i, s->s normalize) | backend | 2026-09-08T00:15:02 |
| Y4 | Ana kural ingest-time'a tasinmasi + DB migrasyonu (KELIME olarak) | backend | 2026-09-08T00:15:02 |
| Y5 | Dashboard pagination + kolon siralama | frontend | 2026-09-08T00:18:38 |
| Y6 | API key auth + rate limiting | backend | 2026-09-08T00:21:47 |
| Y7 | KVKK incelemesi: VKN/e-posta gorunurluk politikasi | arastirmaci | None |
| Y8 | Skeleton loading + bos alan 'zenginlestir' rozetleri | frontend | 2026-09-08T00:23:07 |
| Y9 | Web API testleri (pytest, /api/companies filtreleri) | kalite | 2026-09-09 |
| Y12 | Kalite skoru yeniden agirliklandirma (VKN dolduktan sonra) | kalite | 2026-09-08T09:26:22 |
| Y13 | Musteri watchlist + kayitli filtreler | frontend | 2026-09-08T00:30:59 |
| Y14 | Degisiklik bildirimi (yeni firma/skor degisimi -> Telegram) | gelistirici | 2026-09-09T01:35:00 |
| P5-1 | Kalite skoru ek metrikleri tasarımı | kalite | 2026-09-09T01:21:43 |
| P5-2 | Sosyal medya varlığı metriği | web_kazima | 2026-09-09T01:21:43 |
| P5-3 | Veri güncelliği metriği | backend | 2026-09-09T01:21:43 |
| P5-4 | Telefon format validasyonu | gelistirici | 2026-09-09T01:21:43 |
| P5-5 | Kaynak çeşitliliği metriği | kalite | 2026-09-09T01:21:43 |
| DENET-2 | Karakter kodlama (mojibake) düzeltmesi | koordinator | 2026-09-09T03:06:59 |
| DENET-3 | AGENTS.md tekrar eden blok temizliği + gorev panosu kurali eklendi | koordinator | 2026-09-09T03:06:59 |
| DENET-4 | Kok dizin gecici/deneme dosyalarinin temizlenmesi | devops | 2026-09-09T03:49:48 |
| DENET-5 | Yazim hatali 'Huginin Data Insights' klasorunun durumu netlestirilmeli | koordinator | 2026-09-09T03:49:48 |
| DENET-6 | project_state.md kopyalarinin (iso/utf8) birlestirilmesi | mimar | 2026-09-09T03:49:48 |
| DENET-7 | company_master.db / test.db amacinin dokumante edilmesi | backend | 2026-09-09T03:49:48 |
| P6-2 | E-posta DNS MX doğrulama implementasyonu | backend | 2026-09-09T05:02:16 |
