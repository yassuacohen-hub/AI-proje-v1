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

- **Orkestratör QTK-01 tamamlandı**: `dispatch()`/`review()` senkronizasyonu, `handoff_ekle()` ile duplicate-safe `handoffs.json` kaydı, `scripts/quick_task.py` wrapper, `tests/orchestrator/test_dispatch_review.py` (36 test pass).
- **Orkestratör S-01..S-09 + Faz 4 (ORCH-01) tamamlandı**: task_board.json 23 göreve tamamlandı (baseline geri yazımı dahil), test kirliliği giderildi (tmp_path izolasyonu), `pytest.ini` eklendi, `quick_task.py` exit-code hatası düzeltildi, `test_quick_task.py` e2e testi eklendi (VALIDATE-01), DOCS-05/06 dokümanları yazıldı. Orchestrator test sonucu: 51 passed.
- **Orkestratör ORCH-01 devam bakımı (2026-09-11)**: QT-001 test artefaktı kapatıldı; AGENT_SYNC.md yarı-yazma bozulması panodan yeniden üretildi; `_write_json`/`_md_yaz`/`agent_sync_yaz`/`append_completion` atomik yazmaya geçirildi (tmp + `os.replace`). Orchestrator test sonucu: 53 passed.
- **Orkestratör ORCH-02 (2026-09-11)**: Pano-disk senkronu — paralel ajan işleri (APIFY-03, MCP-01/02/03, DOC-01) panoya işlendi (`scripts/_orch02_boardsync.py`, idempotent); kanıt tabanlı doğrulama disk çıktılarıyla yapıldı. Pano 34 görev; kalan açık iş P7-14 (aktif, kilo) ve P7-15 (plan, kilo).
- **Orkestratör ORCH-03 (2026-09-12)**: AGENT_SYNC otomatik senkron hook'u — `gorev_ekle/gorev_guncelle/lock_birak/handoff_yaz/handoff_ekle` sonrası `agent_sync_yaz()` otomatik tetiklenir (3 denemeli retry, `AUTO_SYNC` bayrağı, testlerde `tests/orchestrator/conftest.py` ile izole); kök + `data/orchestrator/` kopyası atomik ve özdeş yazılır. Bayatlık disiplin ihtiyacı kalktı. Testler 53 passed.
- **GIT-01 (2026-09-11)**: Hibrit git push stratejisi devrede — ajan bitince seçmeli push (`scripts/git_push_gorev.py` + `quick_task.py --push-dosyalar`) ve günde 2x planlı push (12:01/00:01, "Huginn Git Push" görevi). Temiz toplu push Parent-repo'ya yapıldı (dal `chore/monorepo-merge`, commit `2ba17c4`, 132 dosya); cop kutusu/.obsidian/.vscode/data-watch/test_agent depodan çıkarıldı. Push öncesi secret taraması (`scripts/_tmp/secret_tarama.py`): 139 dosya, TEMİZ.
- **P7-15 not (duplika/dogrulama)**: Supabase kontrolünde 10 grup firmanın aynı VKN'yi paylaştığı görüldü (toplam VKN dolu kayıt yalnızca 40/14.000); P7-15 (Signal Dashboard) çalışmasında küçük bir duplika/doğrulama temizliği işlenecek.

### Açık Sorunlar

- Veri toplama için fiili kaynak erişimi (GİB, Oda, diğer OSB'ler) başlatılmadı.

## Aktif Kararlar

- VKN Primary Key olmayacak; company_id UUID kullanılacak.

- MVP için PostgreSQL + Full Text Search yeterli.

- Ham veri source_records tablosunda saklanacak.

- MVP sınırı: Veri tabanı kurulumunun, temel veri temizliğinin ve iş akışının doğrulanmadan müşteri odaklı web arayüzüne geçilmez. İlk etapta iç doğrulama için Streamlit gibi sade ara yüz kullanılır; web aktarımı veri değeri kanıtlandıktan sonra yapılır.

- Görev panosu yönetimi ve kilitleme riskleri: Dosya kilitleme protokolü artık dokümante (DOCS-05, `docs/DOSYA_KILITLEME_PROTOKOLU.md`); P7-14 (kariyer_net.py) kilidi aktif görev için korunuyor. 2026-09-11'de paralel bir sürecin panoyu üzerine yazarak 6 görevi "plan"a döndürdüğü ve `task_board.json`'u bozduğu tespit edildi; baseline geri yazımı + idempotent `_rebuild_board_v2.py` ile telafi edildi. Paralel ajanlarla aynı dosyada çalışırken kilit protokolüne uyulmalı. 2026-09-11 devamında pano/AGENT_SYNC yazmaları atomik hale getirildi (tmp + `os.replace`); aynı yarışın tekrarı kalıcı olarak engellendi.
- Otomatik push yarışı: paralel ajanlar aynı anda push ederse `pull --rebase --autostash` + 2 deneme ile yönetiliyor; çatışma çıkarsa manuel rebase gerekir. Uzak daldaki tek yazar (kilo) bilinçli olarak push yapmıyor; planlı push'lar tek noktadan (bat) geçiyor.

## Bilinen Riskler

- Kod/belge uyumsuzluğu teknik borç yaratıyor.

- Veri toplama yasal sınırları henüz detaylandırılmadı.


## Yeni Eklenen Görevler

- P7-12: Apify Webhook Prod Hardening — Rate limiting, signature validation, Prometheus metrikleri, dead-letter queue, retry/backoff, health endpoint (done)
- P7-13: MCP -> OSINT Motoru Bridge — ApifyAdapter + HuginnMCPServer SourceRegistry entegrasyonu (done)
- P7-14: E2E Pipeline Test — Webhook -> ingest -> SignalAnalyzer -> IntelligenceScorer tam akış testi (aktif)
- P7-15: Signal Dashboard / Aggregation — company_signals + company_intelligence_scores -> Grafana/HTML dashboard (plan)
- REFACTOR-01: gorev_guncelle() not keyword argümanını temizle (done)
- TEST-01: Review başarısız senaryo testi ekle (done)
- VALIDATE-01: quick_task.py uçtan uca validasyonu (done)
- DOCS-04: Brief.package() ile brief.py package_birleştirme (done)
- DOCS-05: Dosya Kilitleme Protokolü Dokümanı (done)
- DOCS-06: Görev Panosu Kullanım Kılavuzu (done)
## Çözülen Kararlar

### Kod / Belge Uyumsuzluğu (2026-09-01)

- **Karar:** Seçenek A — Ayrı Modül

- **Uygulama:** `src/` modülleri `src/data_quality_toolkit/` altına taşındı. Company Master için `src/company_master/` paket iskeleti oluşturuldu. data_quality_toolkit artık ETL boru hattında yardımcı bileşen olarak kullanılacak.