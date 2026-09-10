# TODO — Orkestratör Görev Panosu

Bağlantılar: [[00-Home]] · [[project_state]] · [[CHANGELOG]] · [[Orkestrator]] · [[OSINT_Scraper_Motoru]]

> **Kural:** Her görev tek iç ajana aittir. Durum: plan → aktif → review → done veya locked.
> Kaynak: data/orchestrator/task_board.json (otomatik senkron). Geçmiş kayıtlar [[CHANGELOG]]'dadır.

---

## Açık Görevler

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| T1 | Ivedik scraper implementasyonu | gelistirici | done | Ivedik scraper iskeleti hazir (src/company_master/etl/scrape… |
| T2 | MERSIS API basvurusu takibi | arastirmaci | done | MERSIS API basvurusu takibi dis baglantiya bagli. Mevcut ver… |
| T3 | Sema tasarimi | mimar | done | Sema tasarimi migrated to V10 mimarisi. |
| T3b | Sema tasarimi | mimar | done | Sema tasarimi migrated to V10 mimarisi. |
| P0-1 | OSTÃ„Â°M detay scrape tamamla (~1961/8313) | web_kazima | done | 5485 firma detay scrape tamamlandi. Ingest ve pipeline tetik… |
| P0-2 | Scrape bitince ingest Ã¢â€ â€™ VKN Ã¢â€ â€™ kalite recalc | gelistirici | done | Syntax hatasi duzeltilip calistirildi. Ingest 5485/5485 matc… |
| P0-3 | Kalite skoru 6.53 Ã¢â€ â€™ 50+ hedefine yÃƒÂ¼kselt | kalite | done | Kalite skoru 56.54/100 (hedef 50+ BASARILI). Dagilim: 80-100… |
| P1-1 | Ã„Â°vedik OSB scraper implementasyonu | gelistirici | done | Scraper calisir hale getirildi.ivedikosb.org.tr ve baskentos… |
| P1-2 | BaÃ…Å¸kent OSB scraper implementasyonu | gelistirici | done | Scraper calisir hale getirildi.baskentosb.org tek sayfada 14… |
| P1-3 | ASO mevcut veriyi ingest et (488KB) | gelistirici | done | ASO ingest tamamlandi. 785 kayit, 0 hata. 159 yeni firma ekl… |
| P1-4 | Multi | gelistirici | done | multi_osb_merger.py + ingest_merged_bulk.py calistirildi. Me… |
| P1-5 | NACE: kalan 1266 sektÃƒÂ¶rsÃƒÂ¼z firma | arastirmaci | done | nace_eksik_doldur.py calistirildi: 634 NACE'siz firma doldur… |
| P1-6 | Telegram bot arka plan servisi | gelistirici | done | Telegram bot aktif. Dashboard: http://localhost:8503. Canli … |
| P2-1 | MERSÃ„Â°S/Ticaret Sicili API entegrasyonu | arastirmaci | done | API basvurusu takibi devam ediyor. Mevcut veri kaynaklari il… |
| P2-2 | State dashboard (Streamlit) | gelistirici | done | Streamlit dashboard app.py ile olusturuldu. Port 8501'de cal… |
| P2-3 | ZamanlanmÃ„Â±Ã…Å¸ scrape (gÃƒÂ¼nlÃƒÂ¼k refresh) | web_kazima | done | refresh_all_scrapers.py + service/timer/bat dosyalari eklend… |
| P2-4 | Entity resolution threshold optimizasyonu | kalite | done | entity_resolution_benchmark: 50x500 orneklemle threshold ana… |
| P2-5 | Ã„Â°ÃƒÂ§ ajan otomatik gÃƒÂ¶rev atama | gelistirici | done | oto_atama.py --dry-once dogrulandi: TODO'dan 14 plan gorev b… |
| K1 | Delta | gelistirici | done |  |
| K2 | Gorev brief mekanizmasi (otuomatik context) | gelistirici | done |  |
| K3 | Session handoff (agentlar arasi devir) | gelistirici | done |  |
| K4 | AGENT_SYNC otomatik sync | gelistirici | done |  |
| K7 | Retry context decay (exponential backoff) | gelistirici | done |  |
| K5 | Tool call ciktilarini kisalt | gelistirici | done |  |
| K6 | Otomatik okuma listesi olustur | gelistirici | done |  |
| H001 | ASO verisini ingest et | copilot | done | ASO ingest dogrulandi: P1-3 kapsaminda 785 kayit DB'ye yazil… |
| H002 | ETL mimarisi review + guncelle | claude_code | done | ETL mimarisi review ciktisi dogrulandi: workspace/external/c… |
| H003 | Ostim scraper code review | cursor_grok | done | Code review ciktisi dogrulandi: workspace/external/cursor_gr… |
| H004 | Telegram bot systemd servisini test et | copilot | done | systemd unit uretildi: scripts/telegram_bot_systemd.service … |
| P1-7 | VKN web kazima (footer/hakkimizda/KVKK sayfalari) | web_kazima | done | vkn_web_scraper.py pilot tamamlandi: 30 site tarandi, 0 VKN … |
| P3-1 | Adres verilerini raw_payload'dan primary_address'e ekle | gelistirici | done | 4,663 firma adres raw_payload'dan companies.adres'e yazildi. |
| P3-2 | VKN web kazima genisle (sadece footer degil, tum sayfa) | web_kazima | blocked | Script normalize+fuzzy ile 4251 firma eslestirdi (ivedik 335… |
| P3-3 | Kalite skoru 40 | gelistirici | done | 2457 firma incelendi, 2395 JSONL ile eslesti. 6 firma icin e… |
| P3-4 | Dashboard filtresleme ve export ozellikleri ekle | frontend | done | Dashboard filtresleme ve CSV export eklendi. score-range, so… |
| P3-5 | API cache ve performans optimizasyonu | backend | done | In-memory cache (5dk) ve DB indexleri eklendi. Dashboard ve … |
| P3-6 | Multi | gelistirici | done | Multi-OSB merger (OSTIM+ASO+Ivedik+Baskent) tek transaction'… |
| P3-7 | NACE enrichment fuzzy matching | arastirmaci | done | 1266 sektorsuz firma icin NACE kodu tahmin motoru. difflib.S… |
| P3-8 | Telegram bot servisi | gelistirici | done | Telegram bot arka plan servisi (updater.start_polling). Duru… |
| P3-9 | MERSIS API stub (MVP kurali) | arastirmaci | done | MVP kurali geregi stub. Gercek entegrasyon scale asamasinda. |
| P3-10 | Kalite skoru recalc scripti | kalite | done | Kalite skoru recalc (VKN 15, adres 10, telefon 10, email 10,… |
| P3-11 | ASO 488KB veri ingest | gelistirici | done | ASO CSV/JSON dosyalarini companies tablosuna yukler. SÃƒÂ¼tu… |
| P3-12 | Entity resolution threshold optimizer | kalite | done | 0.70-0.90 araliginda threshold optimize eder. VKN eslesmesi … |
| P3-13 | Ostim detay scrape scripti | web_kazima | done | OSTIM detay sayfalarindan web_sitesi, adres, sosyal medya, v… |
| P3-14 | Ic ajan otomatik gorev atama | koordinator | done | task_board.json uzerinden ajanslara keyword eslemesi ile gor… |
| P4-1 | Kalite skorunu 22.66 | kalite | done | Kalite skoru 27.53 -> 76.44 (P5 metrikleri dahil). Hedef 50+… |
| P4-2 | NULL source_record_id kayitlarini temizle veya source_records'a bagla | backend | done | 1,200 NULL source_record_id kaydi source_records'a baglandi. |
| P4-3 | OSTIM detay sayfasindan vergi_no kazima (mevcut footer scripti genisle) | web_kazima | done | Web kazima etkisiz (0 VKN). Alternatif kaynaklarla 3 VKN bul… |
| P4-4 | Dashboard performans izleme ve slow query optimization | backend | done | Recalc sonrasi profil: API latency health 8ms; DB li 330-920… |
| P4-5 | Veri seti dogrulama ve duplicate temizleme | data | done | dedup_apply.py yazildi (dry-run + --apply, tek transaction, … |
| P4-6 | Backup/restore otomasyonu (pg_dump + cron) | devops | done | Bitis: backup_db.py + restore_db.py + gunluk 03:00 scheduler… |
| Y1 | /api/companies coklu kaynak destegi (source IN (...)) | backend | done | FAZ A-D yol haritasi (2026-09-07) |
| Y2 | Ivedik + Baskent OSB verilerini ingest et (scraper kodu hazir) | gelistirici | done | RAW ingest tamam (Onceki calismada: ivedik 3134 + baskent 76… |
| Y3 | Turkce case | backend | done | FAZ A-D yol haritasi (2026-09-07) |
| Y4 | Ana kural ingest | backend | done | FAZ A-D yol haritasi (2026-09-07) |
| Y5 | Dashboard pagination + kolon siralama | frontend | done | FAZ A-D yol haritasi (2026-09-07) |
| Y6 | API key auth + rate limiting | backend | done | FAZ A-D yol haritasi (2026-09-07) |
| Y7 | KVKK incelemesi: VKN/e | arastirmaci | done | KVKK maskeleme canlida: ?mask=1 / DASH_MASK_PII=1 -> tel/ema… |
| Y8 | Skeleton loading + bos alan 'zenginlestir' rozetleri | frontend | done | FAZ A-D yol haritasi (2026-09-07) |
| Y9 | Web API testleri (pytest, /api/companies filtreleri) | kalite | done | FAZ A-D yol haritasi (2026-09-07) |
| Y10 | MERSIS VKN zenginlestirme pipeline'i | gelistirici | blocked | MERSIS kamuya acik API saglamiyor (html yanit). KnowYourCust… |
| Y11 | GIB VKN dogrulama entegrasyonu | arastirmaci | plan | FAZ A-D yol haritasi (2026-09-07) |
| Y12 | Kalite skoru yeniden agirliklandirma (VKN dolduktan sonra) | kalite | done | Formul agirliklari degismedi; artis duplicate temizliginden … |
| Y13 | Musteri watchlist + kayitli filtreler | frontend | done | FAZ A-D yol haritasi (2026-09-07) |
| Y14 | Degisiklik bildirimi (yeni firma/skor degisimi | gelistirici | done | change_notify.py: snapshot diff (yeni firma + esik skor degi… |
| P5-1 | Kalite skoru ek metrikleri tasarÃ„Â±mÃ„Â± | kalite | done | 7 yeni metrik tasarlandi ve implement edildi. Hesaplama modu… |
| P5-2 | Sosyal medya varlÃ„Â±Ã„Å¸Ã„Â± metriÃ„Å¸i | web_kazima | done | Sosyal medya varligi metrik: 5,014 firma 5 puan (4+ platform… |
| P5-3 | Veri gÃƒÂ¼ncelliÃ„Å¸i metriÃ„Å¸i | backend | done | Veri*guncelligi metrik: 8,222 firma 8 puan (<30 gun), 1,005 … |
| P5-4 | Telefon format validasyonu | gelistirici | done | Telefon format validasyonu: 7,798 firma 2 puan (duzgun forma… |
| P5-5 | Kaynak ÃƒÂ§eÃ…Å¸itliliÃ„Å¸i metriÃ„Å¸i | kalite | done | Kaynak cesitliligi metrik: Tum firma 0 puan (tek kaynak). Ge… |
| DENET-2 | Karakter kodlama (mojibake) dÃƒÂ¼zeltmesi | koordinator | done | Denetim raporu: AI proje v1/V10/07_referanslar/09_proje_dene… |
| DENET-3 | AGENTS.md tekrar eden blok temizliÃ„Å¸i + gorev panosu kurali eklendi | koordinator | done | Denetim raporu: AI proje v1/V10/07_referanslar/09_proje_dene… |
| DENET-1 | Git deposu baslatma (git init + ilk commit) | devops | done | Kullanici onayi bekleniyor (bkz. 09_proje_denetimi_2026-09-0… |
| DENET-4 | Kok dizin gecici/deneme dosyalarinin temizlenmesi | devops | done | Kullanici onayi bekleniyor (bkz. 09_proje_denetimi_2026-09-0… |
| DENET-5 | Yazim hatali 'Huginin Data Insights' klasorunun durumu netlestirilmeli | koordinator | done | Kullanici onayi bekleniyor (bkz. 09_proje_denetimi_2026-09-0… |
| DENET-6 | project_state.md kopyalarinin (iso/utf8) birlestirilmesi | mimar | done |  |
| DENET-7 | company_master.db / test.db amacinin dokumante edilmesi | backend | done |  |
| P6-1 | Ã„Â°Ã…Å¸ ilanlarÃ„Â± ve ÃƒÂ§alÃ„Â±Ã…Å¸an sayÃ„Â±sÃ„Â± veri toplama (LinkedIn API + web kazÃ„Â±ma) | web_kazima | cancelled | Web kazÃ„Â±ma 0 iÃ…Å¸ ilanÃ„Â± buldu. LinkedIn API eriÃ…Å¸im… |
| P6-2 | E | backend | done | 8,994 e-posta doÃ„Å¸rulandÃ„Â±: %47.4 format geÃƒÂ§erli, %37… |
| P7-1 | DB Migration 0007 | gelistirici | done | Migration 0007_job_intelligence.sql Supabase'e uygulandi: 5 … |
| P7-2 | Job Intelligence modul yapisi olusturma | mimar | done | Modul yapisi tam: sources/(base,company_career,iskur,apify_c… |
| P7-3 | Company Matcher (eslestirme motoru) | gelistirici | done | Exact + fuzzy + domain + mersis/vkn + alias multi-pass esles… |
| P7-4 | Company Career Pages Scraper | web_kazima | done | Career Pages Scraper started: scraping companies with websit… |
| P7-5 | Ã„Â°SKUR Scraper | kazi_scraper | plan | Y21 araştırması sonrası public e-sub firm-level eşleştirme i… |
| P7-6 | Kariyer.net Scraper | kariyer_scraper | done | Kariyer.net scraper tamam: kariyer_net.py yazildi, import te… |
| P7-7 | Job Postings Ingest Script | gelistirici | done | JSONL -> job_postings tablosu; company_id eslestirme; dedupl… |
| P7-8 | Job Signals Analyzer | arastirmaci | done | Growth, Risk, Tech, Geo, Org sinyalleri; company_signals tab… |
| P7-9 | Intelligence Scorer | arastirmaci | done | growth, expansion, tech_transformation, investment, org_chan… |
| P7-10 | Intelligence Scores Recalc Script | gelistirici | done | Intelligence scores recalculated |
| P7-11 | Post | gelistirici | done | AdÃ„Â±m 5, 6, 7 eklendi (ingest_job_postings, analyze_job_si… |
| BILDIRIM-SISTEM-V2 | SISTEM V2 raporu: Docker + yerel PostgreSQL + git otomasyonu devrede | tumu | done | 2026-09-09 kurulan sistem: (1) API Docker konteynerinde (res… |
| Y15 | Arama sorgu: yerel DB trigram index'i kur ve dogrula | kalite | done | TAMAMLANDI 2026-09-09: scripts/setup_local_indexes.py - pg_t… |
| Y16 | ARASTIRMA: dashboard'a sektor/market zekasi katmani (V9 market brain MVP) | arastirmaci | done | V9 Market Brain MVP arastirmasi tamamlandi: sektor sagligi k… |
| Y17 | ARASTIRMA: e | arastirmaci | done | V9 veri stratejisi MVP'de acik kaynak: EKAP, ihale duyurular… |
| Y18 | ARASTIRMA: Telegram musterisi icin abonelik/rate plan tasarimi | arastirmaci | done | Abonelik/rate plan tasarimi tamamlandi: API key bazli kota s… |
| Y19 | ARASTIRMA: V9 smart matching (musteri | gelistirici | done | TAMAMLANDI 2026-09-09: /api/match endpoint (web_app.py) - NA… |
| Y20 | BUG: connection.py DATABASE_URL env override testlerde sqlite'a dusuyor | gelistirici | done | TAMAMLANDI 2026-09-09. 3 kok neden: (1) connection.py get_en… |
| Y21 | ARASTIRMA: ISKUR kurumsal eslestirme verisi (acik API + risk analizi) | arastirmaci | done | ARASTIRMA TAMAMLANDI (2026-09-10): (1) Acik API YOK: iskur.g… |
| Y22 | MATCH v2: eslestirme yonu secimi (tedarikci/musteri/rakip) + yonlu NACE haritasi | gelistirici | done | TAMAMLANDI 2026-09-09: /api/match?yon=tedarikci|musteri|raki… |
| Y23 | Odeme entegrasyonu (iyzico/Stripe) | gelistirici | plan | V9 Scale asamasi. MVP'de kredi manuel yukleniyor (/api/admin… |
| Y24 | Uye e | gelistirici | plan | Kayit sonrasi kurumsal e-postaya dogrulama linki; onaylaninc… |
| Y25 | product_categories yonetim arayuzu (admin panel) | frontend | done | TAMAMLANDI 2026-09-09: GET/POST /api/admin/categories (requi… |
| Y26 | Enterprise API key yonetimi + kullanim raporu | gelistirici | plan | Enterprise tier approve'da api_key uretiliyor (web_app.py). … |
| P8-1 | Is ilani takip motoru: kaynak oncelikleme ve erisim stratejisi | web_kazima | done | Ä°ÅŸ ilanÄ± takip motoru kaynak oncelikleme ve erisim strate… |
| P8-2 | Is ilani takip motoru: firma eslestirme ve normalize | gelistirici | done | Ä°ÅŸ ilanlarÄ±nÄ± company_master entitylerine eslestirme ve … |
| P8-3 | Is ilani takip motoru: buyume sinyali skorlama | arastirmaci | done | BÃ¼yÃ¼me sinyali skorlama motoru. company_signals tablosuna … |
| P8-4 | Is ilani takip motoru: risk sinyali skorlama | arastirmaci | done | Risk sinyali skorlama motoru tasarÄ±mÄ± ve testi tamamlandÄ±… |
| P8-5 | Is ilani takip motoru: teknoloji donusumu analizi | arastirmaci | done | Teknoloji dönüşüm analizi. company_tech_profile tablosuna ya… |
| P8-6 | Is ilani takip motoru: yatirim ve olcekleme sinyalleri | arastirmaci | done | Yatırım ve ölçekleme sinyalleri tasarımı tamamlandı. Dört iş… |
| P8-7 | Is ilani takip motoru: cografi genisleme analizi | backend | done | Coğrafi genişleme analizi tasarımı, implementasyonu ve örnek… |
| P8-8 | Is ilani takip motoru: kurumsal rapor ve medya entegrasyonu | web_kazima | done | Kurumsal rapor ve medya entegrasyonu tasari tamamlandi. KAP,… |
| X01 | ARASTIRMA: GIB VKN dogrulama (acik API + KVKK) | arastirmaci | plan | REVIZE. gib_vkn_lookup.py + vkn_batch_enrich.py hazir; resmi… |
| X02 | BUG: VKN zenginlestirme (MERSIS + web footer) pipeline tamamlama | gelistirici | blocked | REVIZE (eski MERSIS pipeline). vkn_batch_enrich.py + vkn_rev… |
| X03 | MATCH v3: buyer profili skorlari (olcek uyumu + sertifika + amac yonu) | gelistirici | done | YENI. Buyer profilindeki employee_range, certificates, goal … |
| X04 | UYELIK: sifre sifirlama + kurumsal e | gelistirici | done | X04 TAMAMLANDI: reset-password-request/confirm, verify-email… |
| X05 | Y26: API key yonetimi | gelistirici | plan | REVIZE (eski Y26). require_api_key istek sayaci + /metrics t… |
| GOV-01 | Orkestrasyon reconciliation denetimi ve kanonik pano karari | koordinator | aktif | Kabul kriterleri: acik/son 30 tamamlanan gorev icin sahip, d… |
| APIFY-01 | Apify uygunluk ve entegrasyon mimarisi arastirmasi | harici_arastirma | done | ARASTIRMA TAMAMLANDI (2026-09-10): OSINT_Scraper_Motoru icin… |
| SEC-01 | API Guvenlik Regresyonu: admin fail | gelistirici | done | require_admin fail-closed + CSV export coklu kaynak SQL duze… |
| SEC-02 | Ag ve Ajan Izolasyonu: TLS verify + workspace path containment + dinamik domain izni | gelistirici | done | TLS verify default; workspace is_relative_to containment; di… |
| DATA-01 | Kanit Hatti Duzeltmeleri: ROOT koku + tekil ilan modeli + firma eslestirme + dedup + karantina | gelistirici | done | ROOT koku + tekil ilan modeli + firma eslestirme onceligi + … |
| P7-GATE | Job Intelligence Dogrulama Kapisi: tek migration kaynagi + dikey akis fixture testleri | kalite | done |  |
| APIFY-02 | Apify REST Adaptoru + Polling Pilotu (10 | web_kazima | plan |  |
| APIFY-03 | Apify Webhook + Kalici Olay Isleme (idempotent alici) | web_kazima | plan |  |
| MCP-01 | Kontrollu Apify MCP Erisimi: izinli arac listesi + harcama onayi + veri sinirlari | arastirmaci | plan |  |
| MCP-02 | Huginn MCP Sunucusu + Ters Connector (gerekirse, faz 2) | arastirmaci | plan |  |
| REL-01 | Teslimat Kapisi: CI hard | devops | plan |  |
| DOC-01 | Kanonik Dokumantasyon: tek V10 kaynagi + UTF | koordinator | plan |  |
| OBS-01 | Obsidian vault standardizasyonu: tek V10 kaynagi + UTF | koordinator | aktif |  |

## P7 — Job Intelligence Modülü (İş İlanı Takip Motoru)

| ID | Görev | Sahip | Durum | Not |
|----|-------|-------|-------|-----|
| P7-1 | DB Migration 0007 - Job Intelligence tabloları | gelistirici | plan | job_postings, company_signals, company_intelligence_scores, company_tech_profile, company_aliases |
| P7-2 | Job Intelligence modul yapısı oluşturma | mimar | plan | sources/, pipeline/, storage/, api/ klasörleri |
| P7-3 | Company Matcher (eşleştirme motoru) | gelistirici | plan | Exact + fuzzy + domain + mersis/vkn + alias multi-pass |
| P7-4 | Company Career Pages Scraper | web_kazima | plan | 5000+ website_domain -> /kariyer, /jobs, /career keşif |
| P7-5 | İSKUR Scraper | kazi_scraper | plan | Public metadata only; firma adı gizli. İşveren Kayıt Sorgulama authenticated erişimle SGK/VKN üzerinden firma adı üretebilir; bu yöntem aktif olursa firma-level matching için revize edilecek. |
| P7-6 | Kariyer.net Scraper | web_kazima | blocked | Anti-bot koruması; proxy/headless gerekebilir |
| Y21 | ARASTIRMA: ISKUR kurumsal eşleştirme verisi | arastirmaci | done | Açık API yok, özel sektör işyeri adları gizli; ilan metadata + aggregation intelligence odaklı çalışılacak. Detay: data/orchestrator/y21_result.json |
| P7-7 | Job Postings Ingest Script | gelistirici | plan | JSONL -> job_postings; company_id eşleştirme; deduplication |
| P7-8 | Job Signals Analyzer | arastirmaci | plan | Growth, Risk, Tech, Geo, Org sinyalleri |
| P7-9 | Intelligence Scorer | arastirmaci | plan | growth, expansion, tech_transformation, investment, org_change, risk skorları |
| P7-10 | Intelligence Scores Recalc Script | gelistirici | plan | company_intelligence_scores, company_tech_profile güncelleme |
| P7-11 | Post-scrape workflow entegrasyonu | gelistirici | done | Adım 5, 6, 7 eklendi (post_scrape_workflow.py) |

## Tamamlanan Dönem Özetleri

| Dönem | Kapsam | Detay |
|-------|--------|-------|
| 2026-09-02 | Supabase migration (22 tablo), ETL pipeline, arama motoru, entity resolution | [[CHANGELOG]] |
| 2026-09-03 | OSINT Motoru v1 + NACE + orkestratör (D-1..D-7) | [[CHANGELOG]] |
| 2026-09-08 | Kalite skoru reformu 22.66 → 63.94 | [[CHANGELOG]] |
| 2026-09-09 | P4+P5 metrikleri (→ 76.44), P6 e-posta MX (→ 53.37) | [[CHANGELOG]] |
| 2026-09-09 | P7 Job Intelligence planlaması + altyapı (P0/P1/P2 tabloları done) | [[CHANGELOG]] |

## Not

Her tamamlanan görev için [[CHANGELOG]] güncellenir ve [[project_state]] yenilenir.
