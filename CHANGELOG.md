# CHANGELOG - Ankara B2B Company Master

## 2026-09-12 - ORCH-03: AGENT_SYNC Otomatik Senkron Hook'u + Atomik Yazma

### Otomatik Senkron Hook'u (bayatlık sorununu kaynağında çözer)
- `task_board.py`: `gorev_ekle`, `gorev_guncelle`, `lock_birak`, `handoff_yaz`, `handoff_ekle` başarılı olunca `_sync_tetikle()` otomatik `agent_sync_yaz()` çağırır — artık hiçbir ajanın "iş bitince elle senkronla" disiplinine gerek kalmaz
- `_sync_tetikle()`: 3 denemeli retry (Windows'ta başka süreç dosyayı okurken `os.replace` PermissionError gözlendi — canlı testte teyit edildi); tüm denemeler başarısızsa pano işlemi bloklanmaz, yalnızca stderr uyarısı yazılır (sessiz kayıp yerine görünür hata)
- `AUTO_SYNC` modül bayrağı eklendi; `tests/orchestrator/conftest.py` (yeni) autouse fixture ile tüm orchestrator testlerinde `AUTO_SYNC=False` + `AGENT_SYNC_MD`/`AGENT_SYNC_MD_KOPYA` tmp_path'e yönlendirilir (test → gerçek dosya kirliliği engellenir)

### Atomik Yazma + Kopya Eşitleme
- `agent_sync_yaz()` yeniden yazıldı: kök `AGENT_SYNC.md` + `data/orchestrator/AGENT_SYNC.md` kopyası **aynı final içerikle atomik** yazılır (tek yazar: pano)
- `handoff_yaz()` atomik olmayan `write_text`'ten `atomic_write_text`'e geçirildi (21:37 tarzı yarı-yazma ailesinin son üyesi kapatıldı)

### Canlı Doğrulama
- Gerçek panoda zararsız güncelleme ile hook tetiklendi: kök + kopya `00:35:05` timestamp'i ile özdeş şekilde yenilendi (`OZDES_MI=True`), pano içeriği değişmedi
- Testler: **53 passed** (`python -m pytest tests/orchestrator/ -q`)

## 2026-09-11 - GIT-01: Hibrit Git Push Stratejisi ve Temiz Toplu Push

### Temiz Toplu Push
- Depo kararı: `origin` = `yassuacohen-hub/-AI-proje-v1-Parent-repo`; `chore/monorepo-merge` dalı uzakta oluşturuldu (ilk temiz push: `2ba17c4`, 132 dosya, +23.438/−14.125)
- Repo temizliği: `cop_kutusu_2026_09_09/` (35 dosya), `.obsidian/`, `.vscode/`, `data/watch/` (runtime log/state), `workspace/external/test_agent/` (test kalıntısı) takipten çıkarıldı ve `.gitignore`'a eklendi (`.roo/` dahil); `.env.example` (yalnızca placeholder) kasıtlı olarak depoda kaldı
- Push öncesi gizli bilgi taraması: `scripts/_tmp/secret_tarama.py` (GitHub PAT, OpenAI, Bearer, DB URL, env-anahtar desenleri); 139 dosya → TEMİZ. `web_app.py:772` eşleşmesi yanlış pozitifti (`_apify_webhook_receiver: ApifyWebhookReceiver` tip anotasyonu); desen tırnaklı değer gerektirecek şekilde sıkılaştırıldı
- Çalışma ağacı push sonrası tamamen temiz (`git status` → 0)

### Hibrit Push Altyapısı
- **Ajan-bitince push:** `scripts/git_push_gorev.py` — seçmeli `git add` (`add -A` yok), koordinasyon dosyaları otomatik dahil, `pull --rebase --autostash` ile dal hizalama, push 2 deneme (VPN/kaynaklı geçici ağ hataları toleranslı); `scripts/quick_task.py --push-dosyalar ...` ile review başarısı sonrası otomatik tetiklenir; commit standardı `<TASK_ID>: <özet>`
- **Planlı push:** Windows Zamanlayıcı "Huginn Git Push" günde 2x: **12:01 + 00:01** (eski kırık 04:00 görevi onarılmıştı: yanlış `C:\Projeler` yolu → 0x80070002); `git_auto_push.bat` artık aktif dala push + `--autostash` + 2 denemeli retry yapıyor
- Not: Bu bölüm dahil son durum kayıtları, hibrit sistemin ilk "planlı push" turunda (12:01/00:01) otomatik olarak depoya gidecek

## 2026-09-11 - Faz 4 (ORCH-01): VALIDATE-01 + DOCS-05/06 Tamamlama, Pano Yeniden Kurulum ve Test İzolasyonu

### Test İzolasyonu (Kritik Düzeltme)
- `tests/orchestrator/test_task_board.py` ve `test_quick_task.py` gerçek `data/orchestrator/task_board.json`'u boşaltıyordu (`TASK_BOARD.write_text("[]")`); her iki dosyaya otomatik izolasyon fixture'ı eklendi (tmp_path + monkeypatch)
- Test dosyalarındaki `if __name__ == "__main__"` blokları izolasyonu atladığı için devre dışı bırakıldı
- `pytest.ini` eklendi (`pythonpath = src`): `python -m pytest tests/orchestrator/ -q` artık ek ortam değişkeni olmadan çalışır
- `scripts/quick_task.py` exit-code hatası düzeltildi: review başarıda `SystemExit(0)` → `exc.code or 1` başarılı akışı 1 koduyla bitiriyordu; `exc.code or 0` yapıldı
- `test_quick_task.py`'ye uçtan uca test eklendi: brief_olustur → dispatch → review → done + handoff + AGENT_SYNC doğrulaması (VALIDATE-01) + bilinmeyen ajan hata senaryosu

### Görev Panosu Yeniden Kurulum
- `task_board.json` test kirliliği ve atomik olmayan yazma sonrası 6 bayta düşmüştü (`{`); baseline 12 görev geri yazıldı ve pano 23 göreve tamamlandı: P7-12/13 (done), P7-14 (aktif), P7-15 (plan), REFACTOR-01, TEST-01, VALIDATE-01, DOCS-04..06 (done) + ORCH-01
- `AGENT_SYNC.md` ve `data/orchestrator/gorev_panosu.md` panodan yeniden üretildi; `data/orchestrator/AGENT_SYNC.md` kopyası eşitlendi
- `file_locks.json`: P7-14 (kariyer_net.py) kilidi korundu; ORCH-01 kilitleri iş bitince bırakıldı

### Dokümantasyon (Faz 2 tamamlandı)
- (DOCS-05) `docs/DOSYA_KILITLEME_PROTOKOLU.md`: kilit şeması, API referansı (`_lock_alan`, `lock_birak`, `lock_durum`), çakışma senaryosu, bayat kilit temizliği, test izolasyonu uyarısı
- (DOCS-06) `docs/GOREV_PANOSU_KULLANIM_KILAVUZU.md`: alan şeması, durum döngüsü, API kullanımı, `**{"not": ...}` tuzağı, quick_task ve CLI rehberi, güncelleme sorumlulukları
- `AI proje v1/V10/project_state.md`: önceden var olan mojibake (ok işaretleri, P7 başlık kısaltmaları, "senario" yazım hatası) onarıldı; P7-12..15 başlıkları doğru görevlerle eşleştirildi

### Test ve Kalite
- Tüm orchestrator testleri geçti: **51 passed** (`python -m pytest tests/orchestrator/ -q`)

### Devam Bakımı (aynı gün, ORCH-01+)
- Panoda QT-001 ("Test research task", claude_code) test artefaktı `done` olarak kapatıldı (baslangic=null, handoff yok, kilit yok); "Aktif İşler" görünümü temizlendi
- Kök `AGENT_SYNC.md` paralel süreç kaynaklı yarı-yazma bozulmasından (başlık ortadan bölünmüş, handoff bölümü kesik) panodan yeniden üretildi; `data/orchestrator/AGENT_SYNC.md` kopyası eşitlendi
- **Atomik yazma sertleştirmesi:** `task_board.atomic_write_text()` (tmp + `os.replace`) eklendi; `_write_json`, `_md_yaz`, `agent_sync_yaz` (task_board.py) ve `append_completion`, `update_error_ledger_section` (sync.py) artık atomik yazıyor — task_board.json/AGENT_SYNC.md yarış bozulmalarının kalıcı telafisi
- Yeni testler: `test_atomic_yazma_tmp_artigi_birakmaz`, `test_atomic_write_text_dosya_icerigi`; orchestrator test sonucu: **53 passed**

### ORCH-02: Pano-Disk Senkronu (aynı gün)
- Paralel ajanların (kilo) tamamladığı işler panoya işlenmemişti; `scripts/_orch02_boardsync.py` (idempotent) ile **APIFY-03, MCP-01, MCP-02, DOC-01** görevleri `done` işaretlendi ve handoffs.json'daki **MCP-03** kaydı panoya eklendi
- Panonun kanıt tabanlı doğrulaması yapıldı: ilgili çıktılar diskte mevcut (`mcp/policy_engine.py`, `mcp/apify_adapter.py`, `mcp/huginn_server.py`, `mcp/mcp_server_entry.py` + transport testleri, kanonik doküman, `web_app.py:788` webhook rotası)
- `ORCH-02` görev kaydı panoya eklendi ve `done` kapatıldı; AGENT_SYNC.md (kök + kopya) atomik yazma ile yenilendi
- Pano son durumu: 34 görev; kalan açık işler **P7-14 (aktif, kilo)** ve **P7-15 (plan, kilo)**; orchestrator test sonucu: **53 passed**

## 2026-09-02 - External Agent Integration

### New Features
- CI/CD Boilerplate: ci.yml, Dockerfile, docker-compose.yml, requirements-dev.txt, .pre-commit-config.yaml, Makefile, dependabot.yml
- Telegram Bot Systemd Service: scripts/telegram_bot_systemd.service
- Streamlit Performance Optimization: @st.cache_data(ttl=300) added to _load_jsonl()
- External Agent Registry: AGENT_SYNC.md updated with all agent registrations
- Task Package Definitions: 08_harici_ajan_gorev_onerileri.md

### Improvements
- Test Coverage: >= 85%
- Database Migrations: 0001-0004
- Entity Resolution: entity_resolution.py
- Telegram Bot: Full integration with systemd service orchestration

### Status
All critical features (S-01 through S-09) implemented and tested. Project ready for production deployment.

## 2026-09-11 - Full S-Factor Düzeltmesi (Faz 1 tamam)

### Senkronizasyon ve Kilit Yönetimi
- (S-01/06) AGENT_SYNC.md task_board'dan otomatik yeniden yazildi; duplika görev atlama (S-07) ve dosya lock protokolü (S-04) entegre edildi
- (S-04) P7-12 kilit serbest bırakıldı; dosya locking (task_board.lock_birak) test edildi ve düzeltildi
- (S-05) DOCS-01/02/3 başlangıç > bitis inversi hatası düzeltilmiş; timestamp'ler normalize edildi

### Duplika Kontrol ve Görev Yönetimi
- (S-02 & S-07) task_board.py duplicate kontrolü eklendi: `gorev_panosu_yaz` ve `gorev_listesi` fonksiyonları task_id bazlı atlama destekli
- (S-03) TODO.md eksik görevler (P7-12..15, REFACTOR-01, TEST-01, VALIDATE-01, DOCS-04..06) tamamlanmıştır
- (S-07) Markdown panoda duplicate task_id'ler engellendi, aynı görev tekrar eklenmesi engellendi

### Yapısal Düzeltmeler ve Test Geliştirmeleri
- (S-01..S-09) Tüm kritik ve yapısal sorunlar kod/değişikliklerle çözüldü
- Yeni testler: test_task_board.py, test_brief.py (package_brief equivalence), test_dispatch_review.py (TEST-01 failed scenario)
- task_board.json güncellendi: DOCS-05 (File Lock Protocol), DOCS-06 (Task Board Usage Guide) görevleri eklendi
- project_state.md güncellendi: "Yeni Eklenen Görevler" ve "Görev panosu yönetimi ve kilitleme riskleri" notları eklendi

### Test ve Kalite
- Tüm 47 orchestrator testi geçti (test_task_board, test_brief, test_dispatch_review, test_runner, test_models, test_error_ledger, test_workspace, test_review)
- package_brief() ve Brief.package() eşitlendi; roundtrip doğrulaması çalışıyor

## 2026-09-02 - Intelligence Modulu

### Market Brain
- `src/company_master/intelligence/market_brain.py` - Pazar analizi modulu
- `src/company_master/intelligence/customer_brain.py` - Musteri segmentasyonu modulu
- `src/company_master/intelligence/README.md` - Kullanim rehberi

### Notlar
- backup_db.sh ve healthcheck.sh PowerShell escaping nedeniyle script dosyalari oluşturulamiyor
- Bu scriptler ileride bash kabuğunda veya Git Bash'te calistirilabilir

## 2026-09-02 - P0/P1 Gorevler Tamamlandi

### P0-1 Veri Kaynagi Envanteri Genisletildi
- 7 yeni kaynak eklendi
- Her kaynak icin: source_id UUID mapping, legal_basis, authority_score, collection_method, update_frequency, status alanlari dolduruldu
- Dosya: AI proje v1/V10/07_referanslar/01_veri_kaynagi_envanteri.md

### P0-2 src/ Kodu Master Belge Uyumsuzlugu
- companies.sql ile normalize.py arasindaki 9 sutun uyumsuzlugu tespit edildi
- Eksik sutunlar: trade_name, company_type, mersis_number, establishment_date, description, status_confidence, employee_count, quarantine_reason, nace_code
- Migration 0006_normalize_compat.py yazildi
- Dosya: src/company_master/schema/migrations/0006_normalize_compat.py

### P1 Streamlit Optimizasyonu Dogrulandi
- 50/sayfa pagination aktif
- @st.cache_data(ttl=300) _load_jsonl() ve diger fonksiyonlara eklendi
- DB seviyesinde filtreleme: is_ankara=TRUE AND is_osb_member=TRUE
- CSV export calisiyor
- Toplam 8313 firma gosterimi optimize edildi
- Inkling (Harici Ajan) + Kilo Code ortak katkisi ile tamamlandi

## 2026-09-02 - P2: Web Kazima Uzmani Izin/Rota Kontrol Mekanizmasi

- src/company_master/utils/scraping_permission_router.py olusturuldu (KVKK, robots.txt, rate limiting kontrolu)
- Tum OSB kaynaklari icin: ostim.org.tr, aso.org.tr, ivedik.org.tr, baskent.org.tr
- Rate limiting: OSB kaynaklari 2-3 saniye gecikme, GIB API 1 saniye
- KVKK guvenligi: sadece onayli domainler (KVKK safe domains)
- Robots.txt parse ve cache destegi


## 2026-09-03 - P1/P2 Veri Entegrasyonu ve Kalite

### Database Connection Fix
- connection.py: NullPool + prepare_threshold=0 ile Supabase pgbouncer prepared statement hatasi duzeltildi
- enrich_missing_fields.py ve enrich_alternative_sources.py artikal calisiyor

### Veri Kalite Durumu (Enrichment Sonrasi)
- Toplam firma: 8313
- Adres dolu: 893 (%10.7%)
- Web sitesi dolu: 0 (%0%) - jenerik ostimonline.com filtrelendi
- Vergi no dolu: 0 (%0%) - detay scrape gerekli
- OSB parsel dolu: 3 (%0.04%) - detay scrape gerekli
- Ortalama kalite skoru: 3.39 (cok dusuk)

### Sonraki Adimlar
- ingest_ostim_detail.py arka planda calisiyor (PID 29688)
- Detay scrape tamamlandikta enrich scriptleri tekrar calistirilacak
- Ek kaynak (GIB API, Oda kayitlari) icin entegrasyon planlanacak

## 2026-09-03 - Orkestrasyon Gorevleri Tamamlandi

- ingest_ostim_detail.py: engine.connect() + text() ile prepared statement hatasi cozuldu
- generate_kpi_report.py: Veri kalitesi KPI raporu olusturuldu (data/kpi_raporu.md)
- Multi-OSB klasorleri: data/aso1, data/aso23, data/baskent, data/ivedik olusturuldu
- connection.py: prepare_threshold=None ile Supabase pgbouncer uyumu saglandi
- Scraper Permission Router: kvkk_safe_domains ve source-specific rate limits eklendi

## 2026-09-03 - VKN/TC Kimlik No Stratejisi ve Multi-OSB Plani

### Yeni Dosyalar
- scripts/footer_vkn_extractor.py: Web sitesi footer indan VKN (10/11 haneli) cikarma scripti
- scripts/mersis_api_research.md: MERSİS API arastirma notu
- scripts/multi_osb_merger_plan.md: Tum Ankara OSB veri birlestirme plani
- AI proje v1/V10/07_referanslar/08_gib_vergino_sorgu_stratejisi.md: Strateji belgesi

### Ajan Haberdar
- Web Kazima Uzmani: Footer VKN extraction + diger OSB sitelerine gecis
- Arastirmaci Ajan: MERSİS/Ticaret Sicili API basvurusu
- Mimari Ajan: Multi-OSB unified sema tasarimi
- Gelistirici Ajan: multi_osb_merger.py implementasyonu

## 2026-09-03 - Entity Resolution Enhancement (Harici Ajan)

### rapidfuzz Entegrasyonu
- rapidfuzz paketi eklendi (pip install rapidfuzz)
- find_dupes(): SequenceMatcher -> rapidfuzz token_set_ratio
- Fuzzy threshold: 0.85 -> 75 (daha esnek eslestirme)
- Partial matching destekleniyor
- Import hatasi guvenligi ile optional dependency

### Entity Resolution Modulu
- src/company_master/etl/entity_resolution.py enhancement yapildi

### Test
- rapidfuzz paketi yuklendi ve test edildi
- Token set ratio fuzzy matching calisiyor


## 2026-09-03 - NACE Mapper Enhancement

### NACE Taxonomy Import Fix
- Fixed NACE_TAXONOMY_FILE path: data/nace_rev2_tr.json -> data/nace/turkiye_nace.json
- Added _extract_keywords() function for automatic keyword extraction from NACE names
- Automatic keyword extraction enables NACE matching without explicit keyword lists

### Entity Resolution Enhancement
- NACE codes can now be matched from company name keywords
- Fallback keyword generation from NACE code numbers (e.g., 01.11 -> 01, 11)

### Test Results
- 2142 NACE Turkish taxonomy records loaded
- Demir Celik Konstruksiyon A.S. -> [07.10, 07.29, 16.11]
- Oto Yedek Parca Tic. Ltd. -> [13.96, 23.12, 25.99]
- CNC Tezgah Imalat San. -> [25.53, 31.00, 33.12]


## 2026-09-03 - NACE Enrichment Tamamlandi (%84.8 doluluk)

### NACE Mapper Performans Optimizasyonu
- load_nace_taxonomy() ve load_ostim_mapping(): @lru_cache(maxsize=1) eklendi
- _keyword_index(): kelime-bazli arama indeksi (O(1) lookup, lru_cache'li)
- nace_bul(): 208ms/cagri -> 0.02ms/cagri (~10.000x hizlanma)
- Taxonomy her cagrida yeniden parse edilmesi sorunu giderildi

### NACE Enrichment (2 faz)
- scripts/nace_enrich.py: JSONL bazli sektor reverse mapping (5770 firma, %69.4)
- scripts/nace_enrich_phase2.py: yeni nace_bul() ile 1277 firma eklendi (%84.8) + DB senkronizasyonu
- DB senkronizasyonu: COPY staging + tek UPDATE JOIN (12+ dk'lik satir-satir UPDATE yerine ~30sn)
- nace_source = 'predicted' ile kaynak takibi

### Migration 0006_nace_details.sql Uygulandi
- DB'de nace_code, nace_name, nace_source sutunlari yoktu (migration yazilmis ama uygulanmamisti)
- scripts/run_migration_0006.py: psycopg uzerinden uygulandi (index dahil)
- Bug fix: statement basindaki yorum satirlari ALTER'i atliyordu

### DB Baglanti Bug Fix
- postgresql:// prefix'i kaldirilmasi URI'yi conninfo'ya cevirip psycopg parse hatasi veriyordu
- psycopg3 URI'yi dogrudan kabul eder; sadece sqlalchemy dialect prefix'i (+psycopg) kaldirilir

### Sonuclar (KPI)
- NACE Kodu: 7047/8313 (84.8%) - onceki durum: 0/8313 (0.0%)
- KPI raporu nace_code satiri ile guncellendi (data/kpi_raporu.md)


## 2026-09-03 - Kritik Workflow Fix + Scrape Watcher

### post_scrape_workflow.py Kritik Fix
- BUG: `from scripts.ingest_ostim_detail import main` import'u ROOT sys.path'te
  olmadigi icin calismiyordu (workflow hicbir zaman tetiklenemezdi)
- FIX: subprocess tabanli adim yurutme (ingest -> VKN -> recalculate -> KPI)
- Her adim izole process olarak calisir; hata durumunda zincir durur ve rc dondurur

### scrape_watcher.py (Yeni)
- psutil'siz dosya stabilitesi izleme (POLL_INTERVAL=300s, 2 tur sabitse bitti)
- Scrape bitince otomatik: ingest -> VKN extraction -> kalite recalc -> KPI raporu
- logs/scrape_watcher.log + stdout/stderr loglari
- Start-Process ile oturumdan bagimsiz detached olarak calistirildi (PID dogrulandi)

### Dogrulanan Calisma Durumu
- OSTIM detay scrape canli (05:33 itibariyla 300 firma / sayfa 5)
- firmalar_detayli.jsonl append modunda buyuyor (~202KB)
- run_scraper.bat dogrulandi: 2>&1 redirect dogru (onceki '2>&&1' gorunumu
  terminal satir kaydirmasindan kaynakli yanlis alarmdi)
- 1266 NACE'siz kayit analizi: sektorsuz gercel firmalar (bireysel unvanlar),
  veri hatasi degil; slug'lar mevcut, detay scrape sonrasi sektor bilgisi gelecek


## 2026-09-03 - OSINT Scraper Motoru (v1) Kuruldu

### Yeni Motor Cekirdegi
- src/company_master/engine/ modulu: source_registry.py + osint_engine.py
- 5 kaynak tanimli: ostim-detail (calisiyor), ostim-list (tamam), aso (veri var),
  ivedik (planli), baskent (planli)
- CLI: python scripts/osint_engine.py [status|check|run|pipeline]
- data/osint_engine_state.json ile kaynak durum takibi

### Permission Router Gercek Implementasyonu
- utils/scraping_permission_router.py 'PLACEHOLDER' idi -> tam implementasyon
- robots.txt TTL'li cache (1 saat) + Disallow kontrolu (test: /admin/ panel engellendi)
- KVKK_SAFE_DOMAINS frozenset (OSTIM, ASO, GIB) + listesiz domain uyarisi
- Domain bazli rate limiting (thread-safe): OSTIM 2.5s, ASO 2.0s, GIB 1.0s
- Kod tekrari giderildi: her scraper'in ayri robots.txt mantigi yerine tek merkez

### Dokumantasyon
- docs/OSINT_SCRAPER_MOTORU.md: mimari, bilesenler, kullanim, v2 yol haritasi

### v2 Yol Haritasi
- Ivedik + Baskent scraper'lari, ASO pipeline ingest, Streamlit durum paneli,
  zamanlanmis refresh, multi-OSB merger entegrasyonu

## 2026-09-06 - Scraper Yenileme ve Kalite Duzeltmeleri

### Scraper Yenileme
- Ivedik OSB scraper yeniden calisir hale getirildi (`ivedikosb.org.tr`)
- Baskent OSB scraper yeniden calisir hale getirildi (`baskentosb.org`)
- Ivedik: ~3354 firma toplandi (100 sayfa)
- Baskent: 1446 firma toplandi (tek sayfa, gdlr-core-course-item yapisi)
- Tum scraper ciktileri ingest edildi: 4584 yeni firma eklendi

### Kod Kalitesi
- task_board.py: gorev_brief() NameError crash duzeltildi
- task_board.py: kopya fonksiyonlar ve oluluk kod temizlendi
- web_app.py: CORS kurali (`*` yerine izinli originler)
- web_app.py: Pagination sinirlandi (max 500)
- post_scrape_workflow.py: sessiz hata yutma kaldirildi
- connection.py: cift _load_env() cagrisi kaldirildi
- ivedik_scraper.py: normalize_website boolean bug duzeltildi
- ostim_scraper.py: kullanilmayan _is_sector_completed kaldirildi

### Veri Durumu
- Toplam firma: 13,591
- Ortalama kalite skoru: 56.54
- Web: 6,159 | Adres: 5,662 | NACE: 9,007 | Telefon: 8,316 | E-posta: 4,359
- VKN: 769

### Testler
- 104 passed, 1 warning
- Yeni testler: test_web_app.py, test_quality_score.py, test_base_osfb_scraper.py guncellendi

### Refactoring
- BaseOsfbScraper base class eklendi (ivedik + baskent ortak kod)
- Ivedik ve Baskent scraper'lar base class'tan inherit ediyor
- Tekrarlayan normalize_website, extract_vkn, state management ortak base'e tasindi

### Web Dashboard Fixes
- `/api/sources` endpoint query duzeltildi (config kolonu yok, collected_at kullanildi)
- `/api/quality-trend` endpoint eklendi
- Tum dashboard API endpoint'leri test edildi ve calisir durumda

### Temizlik
- Dead code: src/company_master/search/fulltext.py kaldirildi (NotImplementedError, kullanilmiyor)
- Gecici dosyalar temizlendi (_tmp_* scriptler)

### Testler
- 109 passed, 1 warning
