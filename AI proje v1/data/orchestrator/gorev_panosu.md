[[Huginn Data Insights/data_worktree/orchestrator/gorev_panosu.md]]

# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| P3-2 | VKN web kazima genisle (sadece footer degil, tum sayfa) | web_kazima | plan | blocked | - |
| Y10 | MERSIS VKN zenginlestirme pipeline'i | gelistirici | P1 | blocked | src/company_master/etl/mersis_api.py |
| Y11 | GIB VKN dogrulama entegrasyonu | arastirmaci | P1 | plan | - |
| P6-1 | Ã„Â°Ã…Å¸ ilanlarÃ„Â± ve ÃƒÂ§alÃ„Â±Ã…Å¸an sayÃ„Â±sÃ„Â± veri toplama (LinkedIn API + web kazÃ„Â±ma) | web_kazima | P1 | cancelled | src/company_master/etl/job_postings_scraper.py |
| P7-1 | DB Migration 0007 - Job Intelligence tablolari | gelistirici | P0 | plan | src/company_master/db/migrations/0007_job_intelligence.sql |
| P7-2 | Job Intelligence modul yapisi olusturma | mimar | P0 | plan | src/company_master/intelligence/job_intelligence/ |
| P7-5 | Ã„Â°SKUR Scraper | web_kazima | P1 | plan | src/company_master/intelligence/job_intelligence/sources/iskur.py |
| P7-6 | Kariyer.net Scraper | web_kazima | P2 | plan | src/company_master/intelligence/job_intelligence/sources/kariyer_net.py |
| Y21 | ARASTIRMA: ISKUR kurumsal eslestirme verisi (acik API + risk analizi) | arastirmaci |  | plan | - |
| Y23 | Odeme entegrasyonu (iyzico/Stripe) - otomatik kredi satisi | gelistirici |  | plan | - |
| Y24 | Uye e-posta dogrulama linki + Telegram hosgeldin raporu | gelistirici |  | plan | - |
| Y26 | Enterprise API key yonetimi + kullanim raporu | gelistirici |  | plan | - |
| P8-5 | Is ilani takip motoru: teknoloji donusumu analizi | arastirmaci | P2 | plan | - |
| P8-7 | Is ilani takip motoru: cografi genisleme analizi | backend | P2 | plan | - |
| X01 | ARASTIRMA: GIB VKN dogrulama (acik API + KVKK) - scripts/gib_vkn_lookup.py devami | arastirmaci | P1 | plan | - |
| X02 | BUG: VKN zenginlestirme (MERSIS + web footer) pipeline tamamlama | gelistirici | P1 | blocked | - |
| X03 | MATCH v3: buyer profili skorlari (olcek uyumu + sertifika + amac yonu) | gelistirici | P2 | plan | - |
| X04 | UYELIK: sifre sifirlama + kurumsal e-posta dogrulama + Telegram hosgeldin | gelistirici | P2 | plan | - |
| X05 | Y26: API key yonetimi - rotasyon + kullanim metrikleri + tier rate limit | gelistirici | P2 | plan | - |
| TG-01 | Telegram bot mesaj gonderme sorununu giderme (env, yetki, komutlar, yollar, servis, testler) | kilo | P0 | aktif | scripts/telegram_polling.py, src/company_master/utils/telegram_bot.py, src/company_master/telegram/bot_service.py |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| T1 | Ivedik scraper implementasyonu | gelistirici | 2026-09-06T20:58:44 |
| T2 | MERSIS API basvurusu takibi | arastirmaci | 2026-09-06T20:58:44 |
| T3 | Sema tasarimi | mimar | 2026-09-06T20:58:44 |
| T3b | Sema tasarimi | mimar | 2026-09-06T20:58:44 |
| P0-1 | OSTÃ„Â°M detay scrape tamamla (~1961/8313) | web_kazima | 2026-09-03T14:18:36 |
| P0-2 | Scrape bitince ingest Ã¢â€ â€™ VKN Ã¢â€ â€™ kalite recalc | gelistirici | 2026-09-03T14:18:36 |
| P0-3 | Kalite skoru 6.53 Ã¢â€ â€™ 50+ hedefine yÃƒÂ¼kselt | kalite | 2026-09-06T22:54:31 |
| P1-1 | Ã„Â°vedik OSB scraper implementasyonu | gelistirici | 2026-09-07T00:43:00 |
| P1-2 | BaÃ…Å¸kent OSB scraper implementasyonu | gelistirici | 2026-09-07T00:43:00 |
| P1-3 | ASO mevcut veriyi ingest et (488KB) | gelistirici | 2026-09-06T15:16:53 |
| P1-4 | Multi-OSB merger: ~19.000 firma | gelistirici | 2026-09-06T18:00:25 |
| P1-5 | NACE: kalan 1266 sektÃƒÂ¶rsÃƒÂ¼z firma | arastirmaci | 2026-09-06T21:38:08 |
| P1-6 | Telegram bot arka plan servisi | gelistirici | 2026-09-06T11:37:43 |
| P2-1 | MERSÃ„Â°S/Ticaret Sicili API entegrasyonu | arastirmaci | 2026-09-06T20:58:44 |
| P2-2 | State dashboard (Streamlit) | gelistirici | 2026-09-06T10:54:48 |
| P2-3 | ZamanlanmÃ„Â±Ã…Å¸ scrape (gÃƒÂ¼nlÃƒÂ¼k refresh) | web_kazima | 2026-09-06T23:13:13 |
| P2-4 | Entity resolution threshold optimizasyonu | kalite | 2026-09-06T21:38:08 |
| P2-5 | Ã„Â°ÃƒÂ§ ajan otomatik gÃƒÂ¶rev atama | gelistirici | 2026-09-06T16:26:51 |
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
| P4-3 | OSTIM detay sayfasindan vergi_no kazima (mevcut footer scripti genisle) | web_kazima | 2026-09-09T12:52:19.915474 |
| P4-4 | Dashboard performans izleme ve slow query optimization | backend | 2026-09-09T11:32:51 |
| P4-5 | Veri seti dogrulama ve duplicate temizleme | data | 2026-09-08T09:26:22 |
| P4-6 | Backup/restore otomasyonu (pg_dump + cron) | devops | 2026-09-08T08:54:26 |
| Y1 | /api/companies coklu kaynak destegi (source IN (...)) | backend | 2026-09-08T00:15:02 |
| Y2 | Ivedik + Baskent OSB verilerini ingest et (scraper kodu hazir) | gelistirici | 2026-09-09T02:46:53 |
| Y3 | Turkce case-insensitive arama (i->i, s->s normalize) | backend | 2026-09-08T00:15:02 |
| Y4 | Ana kural ingest-time'a tasinmasi + DB migrasyonu (KELIME olarak) | backend | 2026-09-08T00:15:02 |
| Y5 | Dashboard pagination + kolon siralama | frontend | 2026-09-08T00:18:38 |
| Y6 | API key auth + rate limiting | backend | 2026-09-08T00:21:47 |
| Y7 | KVKK incelemesi: VKN/e-posta gorunurluk politikasi | arastirmaci | - |
| Y8 | Skeleton loading + bos alan 'zenginlestir' rozetleri | frontend | 2026-09-08T00:23:07 |
| Y9 | Web API testleri (pytest, /api/companies filtreleri) | kalite | 2026-09-09 |
| Y12 | Kalite skoru yeniden agirliklandirma (VKN dolduktan sonra) | kalite | 2026-09-08T09:26:22 |
| Y13 | Musteri watchlist + kayitli filtreler | frontend | 2026-09-08T00:30:59 |
| Y14 | Degisiklik bildirimi (yeni firma/skor degisimi -> Telegram) | gelistirici | 2026-09-09T01:35:00 |
| P5-1 | Kalite skoru ek metrikleri tasarÃ„Â±mÃ„Â± | kalite | 2026-09-09T01:21:43 |
| P5-2 | Sosyal medya varlÃ„Â±Ã„Å¸Ã„Â± metriÃ„Å¸i | web_kazima | 2026-09-09T01:21:43 |
| P5-3 | Veri gÃƒÂ¼ncelliÃ„Å¸i metriÃ„Å¸i | backend | 2026-09-09T01:21:43 |
| P5-4 | Telefon format validasyonu | gelistirici | 2026-09-09T01:21:43 |
| P5-5 | Kaynak ÃƒÂ§eÃ…Å¸itliliÃ„Å¸i metriÃ„Å¸i | kalite | 2026-09-09T01:21:43 |
| DENET-2 | Karakter kodlama (mojibake) dÃƒÂ¼zeltmesi | koordinator | 2026-09-09T03:06:59 |
| DENET-3 | AGENTS.md tekrar eden blok temizliÃ„Å¸i + gorev panosu kurali eklendi | koordinator | 2026-09-09T03:06:59 |
| DENET-1 | Git deposu baslatma (git init + ilk commit) | devops | 2026-09-09T03:06:59 |
| DENET-4 | Kok dizin gecici/deneme dosyalarinin temizlenmesi | devops | 2026-09-09T03:49:48 |
| DENET-5 | Yazim hatali 'Huginin Data Insights' klasorunun durumu netlestirilmeli | koordinator | 2026-09-09T03:49:48 |
| DENET-6 | project_state.md kopyalarinin (iso/utf8) birlestirilmesi | mimar | 2026-09-09T03:49:48 |
| DENET-7 | company_master.db / test.db amacinin dokumante edilmesi | backend | 2026-09-09T03:49:48 |
| P6-2 | E-posta DNS MX doÃ„Å¸rulama implementasyonu | backend | 2026-09-09T05:02:16 |
| P7-3 | Company Matcher (eslestirme motoru) | gelistirici | - |
| P7-4 | Company Career Pages Scraper | web_kazima | 2026-09-09T21:00:24 |
| P7-7 | Job Postings Ingest Script | gelistirici | 2026-09-09T21:00:24 |
| P7-8 | Job Signals Analyzer | arastirmaci | 2026-09-09T21:00:24 |
| P7-9 | Intelligence Scorer | arastirmaci | 2026-09-09T21:00:24 |
| P7-10 | Intelligence Scores Recalc Script | gelistirici | 2026-09-09T16:42:48 |
| P7-11 | Post-scrape workflow entegrasyonu | gelistirici | 2026-09-09T12:50:18 |
| BILDIRIM-SISTEM-V2 | SISTEM V2 raporu: Docker + yerel PostgreSQL + git otomasyonu devrede | tumu | - |
| Y15 | Arama sorgu: yerel DB trigram index'i kur ve dogrula | kalite | - |
| Y16 | ARASTIRMA: dashboard'a sektor/market zekasi katmani (V9 market brain MVP) | arastirmaci | 2026-09-09 |
| Y17 | ARASTIRMA: e-ticaret/firma API'lerinden yeni veri kaynaklari (TOBB, il ozu, harbors) | arastirmaci | 2026-09-09T11:54:00 |
| Y18 | ARASTIRMA: Telegram musterisi icin abonelik/rate plan tasarimi | arastirmaci | 2026-09-09T12:00:00Z |
| Y19 | ARASTIRMA: V9 smart matching (musteri-firma eslestirme) MVP prototipi | gelistirici | - |
| Y20 | BUG: connection.py DATABASE_URL env override testlerde sqlite'a dusuyor | gelistirici | - |
| Y22 | MATCH v2: eslestirme yonu secimi (tedarikci/musteri/rakip) + yonlu NACE haritasi | gelistirici | 2026-09-09 |
| Y25 | product_categories yonetim arayuzu (admin panel) | frontend | 2026-09-09 |
| P8-1 | Is ilani takip motoru: kaynak oncelikleme ve erisim stratejisi | web_kazima | 2026-09-09T20:26:00Z |
| P8-2 | Is ilani takip motoru: firma eslestirme ve normalize | gelistirici | 2026-09-09T20:30:00 |
| P8-3 | Is ilani takip motoru: buyume sinyali skorlama | arastirmaci | 2026-09-09T23:15:01 |
| P8-4 | Is ilani takip motoru: risk sinyali skorlama | arastirmaci | 2026-09-09T23:20:00 |
| P8-6 | Is ilani takip motoru: yatirim ve olcekleme sinyalleri | arastirmaci | 2026-09-09T23:55:00 |
| P8-8 | Is ilani takip motoru: kurumsal rapor ve medya entegrasyonu | web_kazima | 2026-09-09T23:47:38 |
