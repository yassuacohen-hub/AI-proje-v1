# Gorev Panosu — Orkestrator

> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.
> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.

## Aktif Isler

| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |
|-------|--------|-------|---------|-------|----------|
| UTKU-02 | [UTKU] API endpoint optimizasyon - response time (2s) | utku | P1 | archive | src/api/endpoints.py |
| UTKU-04 | [UTKU] Veritabanı migration - index optimizasyon (1s) | utku | P1 | archive | src/company_master/schema/migrations/0020_index_optimization.sql |
| UTKU-05 | [UTKU] Kullanıcı kimlik doğrulama - token yenileme (2s) | utku | P0 | archive | src/auth/token_refresh.py |
| ORCH-01 | [ORCH] İş akışı koordinasyon - görev planlama (2s) | ihsan | P0 | archive | orchestration/workflow_coordinator.py |
| ORCH-02 | [ORCH] Bağımlılık yönetimi - görüntü grafiği (2s) | ihsan | P1 | archive | orchestration/dependency_graph.py |
| ORCH-03 | [ORCH] Görev dağıtımı - load balancing (2s) | ihsan | P0 | archive | orchestration/load_balancer.py |
| ORCH-04 | [ORCH] Hata toleransı - retry mekanizması (2s) | ihsan | P1 | archive | orchestration/retry_handler.py |
| ORCH-05 | [ORCH] İzleme ve metrikler - telemetri sistemi (3s) | ihsan | P0 | archive | orchestration/telemetry.py |
| ALTYAPI-TEST-FAILURE-FIX-02 | [ALTYAPI] Test hatasi duzelt -> tests/test_mcp.py | utku | P1 | archive | - |
| ALTYAPI-KILIT-TEMIZLE-01 | [ALTYAPI] Kilitleri duzelt -> file_locks.json | yasu | P2 | archive | - |
| TEST-AYARLAR-KAPSAM-01 | Kullanici Ayarlari sayfasi icin test iskeleti yaz | yasu | P2 | archive | - |
| ADLANDIRMA-GERIYE-01 | D-55 geriye donuk: rapor dosyalarindan ajan adini kaldir | ihsan | P3 | archive | - |
| V10-BELGE-01 | 6 curutulen iddiaya K1/K3/K4 duzeltme notu | ihsan | P1 | archive | - |
| WK-02 | OSB Tender Monitor - Real-time Tracking | - | P1 | archive | - |
| WK-03 | Proxy Rotation and IP Management | - | P2 | archive | - |
| TEST-EKLE-DENEME | test | ihsan | P2 | iptal | - |
| SCRAPE-006-QUALITY-AUDIT | [QA] Kazıma quality audit: D-250 field tamlık + D-310 kontrol (1s) | salih | P1 | plan | scripts/_kazima_dogrula.py, src/company_master/etl/quality_recalc.py |
| SCRAPE-007-FINAL-REPORT | [DOC] Kazıma dönem sonu raporu: coverage, cost=0 doğrulaması, v2.0 roadmap (1s) | ihsan | P2 | plan | plans/2026-10-01_kazima_verimlilik_ve_eksiklik_analizi.md, scripts/_kazima_dogrula.py |
| VERI-ODIN-EGITIM-VERISI-HAZIRLA | [VERI] Odin eğitim veri setini yaz → data/odin_training_data.csv (7d) | utku | P1 | iptal | data/odin_training_data.csv, scripts/odin_veri_hazirla.py, data/odin_veri_dogrulama_raporu.md |
| ALTYAPI-ODIN-EGITIM-PIPELINE | [ALTYAPI] Odin eğitim hattını yaz → scripts/odin_training_pipeline.py (7d) | utku | P1 | iptal | scripts/odin_training_pipeline.py, data/models/odin_model.bin, data/odin_training_metrics.csv |
| TEST-ODIN-PROMPT-INJECTION | [TEST] Odin müşteri modelini prompt-injection ile ölç → data/odin_injection_test_log.jsonl (7d) | salih | P1 | aktif | scripts/odin_prompt_injection_test.py, data/odin_injection_test_scenarios.json, data/odin_injection_test_log.jsonl |
| ALTYAPI-MIMIR-BAGLAM-01 | [ALTYAPI] Mimir baglam ucunu yaz -> odin_ai/mimir_servis.py (3s) | salih | P1 | aktif | src/company_master/odin_ai/mimir_servis.py |
| TEST-ODIN-REDTEAM-S1S4-I1I4-01 | [TEST] Urun sahibi red-team S1-S4 DIS + I1-I4 IC senaryolarini harness'e yaz → odin_injection_test_scenarios.json 36→44 + --rol ic (3s) | salih | P1 | aktif | tests/test_prompt_yukle_roller.py |
| TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01 | [TEST] conftest.py duzelt -> tests/conftest.py (3s) | salih | P1 | plan | tests/conftest.py |
| ORKESTRA-KIMLIK-ZINCIRI-01 | [ORKESTRA] Kimlik zinciri kaydını düzelt → plans/brief_ihsan_ORKESTRA-KIMLIK-ZINCIRI-01.md (1s) | ihsan | P1 | aktif | scripts/ajan_chat.py, scripts/gorev_kutusu.py |
| ALTYAPI-9ROUTER-MITM-PATCH-01 | [ALTYAPI] 9router MITM NODE_ENV patch kaliciligini denetle + clinepass OAuth testi olc -> bulgu_defteri.md (1s) | yasu | P2 | plan | C:/Users/yasin/AppData/Roaming/npm/node_modules/9router/app/.next-cli-build/server/chunks/915.js |

## Tamamlananlar

| Görev | Baslik | Sahip | Bitis |
|-------|--------|-------|-------|
| ALTYAPI-D66-BYPASS-TETIKLEME | [ALTYAPI] D-65 Is Durmaz Bypass Tetikleme -> pano_duzenleme (2s) | ihsan | 2026-09-24T01:28:33 |
| VERI-ADMIN-AKTIVITE-LOG-13 | [VERI] Kullanıcı aktivite log tablosunu yaz → migration 0017 (2s) | utku | 2026-09-24T19:25:07 |
| API-ADMIN-AKTIVITE-YAZ-14 | [API] Giriş/arama/AI olaylarını log'a yaz → web_app.py + arama uçları (2s) | utku | 2026-09-24T20:56:00 |
| DOC-ADMIN-DURUM-SENKRON-15 | [DOC] Bayat durum satırlarını düzelt → §8.4/§10 kanıtlı (1s) | ihsan | 2026-09-24T20:56:00 |
| API-ADMIN-CHURN-3SINYAL-16 | [API] Churn kuralını 3 sinyalli hâlde yaz → churn.py tam formül (2s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-DAU-17 | [UI] Gerçek DAU kartını yaz → admin_kpi.py aktivite sorgusu (2s) | utku | 2026-09-24T19:25:07 |
| API-ADMIN-KAYNAK-SAGLIK-18 | [API] Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ birikme hızı (2s) | yasu | 2026-09-24T23:38:00 |
| UI-ADMIN-CRAWL-KONTROL-19 | [UI] Crawl tetikle/durdur aksiyonunu yaz → operatör kontrol paneli (3s) | yasu | 2026-09-24T23:38:00 |
| UI-ADMIN-ARAMA-BOSLUK-20 | [UI] Sonuçsuz arama frekans raporunu yaz → içerik boşluk raporu (2s) | utku | 2026-09-24T20:56:00 |
| API-ADMIN-SUPHELI-AKTIVITE-21 | [API] Şüpheli aktivite kurallarını yaz → 3 sinyalli güvenlik uyarısı (3s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-UPSELL-22 | [UI] Upsell aday listesini yaz → satış aksiyon listesi (2s) | utku | 2026-09-24T20:56:00 |
| TEST-ADMIN-K2-AGIRLIK-23 | [TEST] K2 ağırlık şemasını denetle → test + SSOT kanıt (1s) | yasu | 2026-09-25T04:26:42 |
| DOC-ADMIN-V9-KUTUCUK-24 | [DOC] V9 §16.5 kutucuklarını düzelt → 6 madde (1s) | utku | 2026-09-24T20:56:00 |
| UI-ADMIN-FEATURE-FLAG-25 | [UI] Feature flag yönetim ekranını yaz → A5 MVP (3s) | utku | 2026-09-25T04:36:47 |
| API-ADMIN-MFA-26 | [API] MFA + hesap kilidi akışını yaz → A6 auth (4s) | utku | 2026-09-26T04:06:34 |
| UI-ADMIN-LTV-CAC-27 | [UI] LTV/CAC kartlarını yaz → K8 tamamlama (2s) | utku | 2026-09-25T22:31:25 |
| DOC-ADMIN-MULTITENANT-KARAR-28 | [DOC] Multi-tenant kararını belgele → KK-7 (1s) | utku | 2026-09-25T22:31:15 |
| TEST-BLOKE-FAKTOR-ARASTIRMA-01 | [TEST] Test hazirlik plani arastir → test_bloke_hazirlik.py (3s) | yasu | 2026-09-24T22:11:11.842076 |
| ALTYAPI-SECRETS-SETUP-01 | [ALTYAPI] Vault kurup .env template yaz → .env.example (2s) | ihsan | 2026-09-24T20:56:00 |
| ALTYAPI-DB-MIGRATION-01 | [ALTYAPI] v0016 → v0017 prod migration planı yaz → db_migrate_prod.sh (1s) | utku | 2026-09-26T14:48:08 |
| ALTYAPI-ADMIN-PANO-01 | [ALTYAPI] Task board 4 bolum yaz → render_task_board_tab.py (2s) | ihsan | 2026-09-24T20:56:00 |
| ORKESTRA-AI-CHAT-KOORDINASYON-01 | [ORKESTRA] Ajan arasi protokol yaz → ajan_chat_koordinasyon.py (3s) | ihsan | 2026-09-24T22:02:28 |
| ALTYAPI-VERI-GORUNURLUK-01 | [ALTYAPI] Katmanlı görünürlük & kontör sistemi → 0018 migration + 3 tablo (4s) | ihsan | 2026-09-25T22:48:38 |
| API-KVKK-KONTROL-25 | [API] Kontör endpoint entegrasyonu (match/ilan) → _charge_module_credit çağrısı | yasu | 2026-09-25T22:48:38 |
| TEST-VISIBILITY-ENTEGRASYON-27 | [TEST] E2E senaryo testi (visibility layer + kontör) → 5 scenario + 4 conflict | yasu | 2026-09-25T22:48:38 |
| UI-ADMIN-KVKK-MODU-26 | [UI] Admin KVKK mode toggle (strict ↔ lenient) → web_app POST endpoint | utku | 2026-09-25T22:29:48 |
| UI-ADMIN-KVKK-RAPOR-28 | [UI] KVKK maskeleme raporu → admin paneline ek sekme | utku | 2026-09-25T04:36:54 |
| DOC-VISIBILITY-KATMANI-29 | [DOC] Kullanıcı dokümanı (görünürlük katmanı + kontör) → markdown guide | utku | 2026-09-25T04:36:47 |
| API-LAYER2-DINAMIK-YÜKLEME-30 | [API] Layer 2 dinamik yükleme → plan_field_group tablosundan görünürlük oku | yasu | 2026-09-25T22:48:39 |
| KONTROL-KVKK-MASKELEME-31 | [KONTROL] KVKK maskeleme end-to-end test → admin panel e2e | yasu | 2026-09-25T22:48:39 |
| UI-KONTROL-PANOSU-32 | [UI] Admin kontrol panosu → maskeleme durum metriksleri | utku | 2026-09-25T04:36:47 |
| DOKUMAN-KVKK-FAQ-33 | [DOC] KVKK FAQ & sorun çözme → markdown troubleshooting guide | utku | 2026-09-25T04:36:47 |
| UTKU-01 | [UTKU] Veri şeması doğrulama - Core modülü (2s) | utku | 2026-09-25T20:30:00 |
| UTKU-03 | [UTKU] Hata loglama sistemi - production hazırlığı (2s) | utku | 2026-09-26T14:30:53 |
| YASU-01 | [YASU] Frontend bileşen kütüphanesi - temel UI (3s) | yasu | 2026-09-26T04:06:33 |
| YASU-02 | [YASU] Responsive tasarım - mobil uyumluluk (2s) | yasu | 2026-09-26T04:06:33 |
| YASU-03 | [YASU] Grafiksel dashboard - veri görselleştirme (3s) | yasu | 2026-09-26T04:06:33 |
| YASU-04 | [YASU] Durum yönetimi - state management (2s) | yasu | 2026-09-26T04:06:33 |
| YASU-05 | [YASU] Erişilebilirlik - WCAG 2.1 uyumu (2s) | yasu | 2026-09-26T04:06:34 |
| ADMIN-UX-GELIR-GRUP-01 | Gelir&Paketler grubu tamamla: executive+maliyet sekmelerini ust=gelir'e tasi | utku | 2026-09-25T23:21:54 |
| UI-ADMIN-MENU-D215216 | [UI] Admin menü ağacını düzelt → web_dashboard/tabs/__init__.py (3s) | utku | 2026-09-27T00:20:36 |
| RESEARCH-PONYTALE | Ponytail vs Caveman derinlemesine arastirma | ihsan | 2026-09-27T02:35:00 |
| DOC-SIRKET-MASTER-01 | [DOC] Sirket Master ana belgesi duzelt | utku | 2026-09-27T02:35:00 |
| REVIEW-ONAY-KUYRUGU-01 | Onay kuyrugundaki 2 teslimi denetle | yasu | 2026-09-27T02:35:00 |
| AGN-CREWAI-PILOT-01 | crewAI hibrit worker pilotu (metin uretimi deneyi) | ihsan | 2026-09-27T02:35:00 |
| ORKESTRA-DECISION-LOG-03 | [ORKESTRA] Karar defteri duzenleme ve validasyon | ihsan | 2026-09-27T02:35:00 |
| ORKESTRA-NAMING-AUDIT-02 | [ORKESTRA] D-55/D-57 adlandirma kurallari denetimi | ihsan | 2026-09-27T02:35:00 |
| ORKESTRA-BRIEF-TALIMAT-01 | [ORKESTRA] 4 brife talimat dosyasi yaz | yasu | 2026-09-27T02:35:00 |
| ORKESTRA-VAULT-TEKRAR-01 | [ORKESTRA] Vault isim tekrarlarini denetle | ihsan | 2026-09-27T02:35:00 |
| VAULT-ORPHAN-INCELEME-01 | [VAULT] Orphan nod siniflama: 3361 dosya, D-173 | orkestrator | 2026-09-27T02:35:00 |
| VERI-02 | [VERI] OSB ihale izleyicisini yaz → src/company_master/etl/scrapers/osb_tender_monitor.py (3s) | utku | 2026-10-01T19:21:19 |
| VERI-03 | [VERI] Proxy rotasyonunu yaz → src/company_master/etl/scrapers/proxy_rotation.py (2s) | utku | 2026-09-27T12:00:00 |
| VERI-04 | [VERI] Migration down dosyalarini tek ad standardina tasi → schema/migrations/down/ (3s) | ihsan | 2026-09-27T05:35:00 |
| API-07 | [API] 11 yeni rotayi envantere yaz + gecersiz buyer_id icin 404 dondur → src/api/ (2s) | utku | 2026-09-27T05:35:00 |
| UI-11 | [UI] admin_mfa + ana_kontrol basliklarini Section kalibina tasi → admin_mfa.py (2s) | utku | 2026-09-27T05:35:00 |
| DOC-D227-01 | [DOC] D-227: karar numarasi yalniz AGENTS.md'den verilir + mandal | orkestrator | 2026-09-27T05:35:00 |
| DOC-D228-01 | D-228: vault icinde paralel veri govdesi yasagi (data_worktree elendi) | kahin | 2026-09-27T08:26:16 |
| DOC-D229-01 | D-229: zaman damgali yedek git te izlenmez (65 artik elendi) | kahin | 2026-09-27T08:36:33 |
| DOC-D230-01 | D-230: gomulu govde kopyasi yasagi + mandal | kahin | 2026-09-27T10:36:28 |
| ORKESTRA-D231-01 | Onay kuyrugu arsive kor: pano_denetim arsive bakmiyordu | kahin | 2026-09-27T10:48:42 |
| ORKESTRA-D233-01 | Referansli yol kopya sanildi: AI proje v1/ butun olarak silindi, teslim kapisi kirildi | kahin | 2026-09-27T11:24:28 |
| VERI-NACE-SOZLUK-01 | [VERI] Resmi NACE listesini yaz → nace_codes tablosu (3s) | utku | 2026-09-28T19:38:49 |
| VERI-NACE-COKLU-01 | [VERI] Çoklu NACE kodunu yaz → company_industries.is_primary (3s) | utku | 2026-10-01T19:36:35 |
| VERI-NACE-TEMIZ-01 | [VERI] Sektör sayacı kirlenmesini düzelt → nace_code temizliği (2s) | utku | 2026-09-28T19:38:48 |
| VERI-NACE-KOLON-01 | [VERI] nace_validity kolon karışmasını düzelt → 86 satır (1s) | utku | 2026-09-28T19:38:49 |
| VERI-KAYNAK-BAG-01 | [VERI] Firma-kaynak bagini yaz → source_records.company_id (4s) | utku | 2026-09-30T19:41:16 |
| VERI-SEKTOR-01 | [VERI] Sektor sozlugunu yaz → 9689 kayitta sektor alani (3s) | utku | 2026-09-30T19:41:21 |
| VERI-KAYNAK-SIZINTI-01 | [VERI] Kaynak sizintisini duzelt → ostim icinde 102 ASO kaydi (2s) | utku | 2026-09-30T19:41:07 |
| VERI-HAYALET-TEMIZ-01 | [VERI] Hayalet kayitlari sil → companies 4591 fazlalik satir (3s) | utku | 2026-09-28T19:38:49 |
| VERI-IVEDIK-YENIDEN-01 | [VERI] Ivedik kaynak listesinden dusuruldu (KAHIN 2026-09-29) | yasu | - |
| ALTYAPI-AJAN-CAKISMA-01 | [ALTYAPI] Eszamanli ajan kacak kilit kapisini yaz → ajan_cakisma_kilidi.py (4s) | yasu | 2026-10-04T00:42:55 |
| ALTYAPI-SKILL-YAPISI-01 | [ALTYAPI] Skill sistemini tek havuzda birlestir → SKILLS_INDEX.md yaz (6s) | yasu | 2026-09-29T15:51:21 |
| ALTYAPI-TICARET-KANIT-01 | [ALTYAPI] Kanit katmanini yaz → skills/services/ticaret_sicili_kanit.py (2s) | yasu | 2026-09-29T15:51:21 |
| VERI-OSTIM-TAM-TARAMA-01 | [VERI] OSTIM detay verisini denetle → firmalar_tamamlanmis.jsonl (2s) | yasu | 2026-09-30T19:41:04 |
| TSG-PILOT-20 | [OSINT] TSG 20 firma pilot OLCUMU -> plans/rapor_yasu_TSG-PILOT-20.md (1g) | yasu | 2026-09-30T03:31:32 |
| VERI-TOBB2B-KESISIM-01 | [VERI] TOBB2B teklif havuzunu OSB verisiyle arastir → kesisim_raporu (5d) | yasu | 2026-09-30T19:41:13 |
| VERI-LONCA-FIRMA-01 | [VERI] lonca firma bilgi ucunt tarama ile olc → firma_kaydi_raporu (5d) | yasu | 2026-09-30T19:41:37 |
| VERI-TSG-04-YAZICI-01 | [VERI] TSG-04 yazma hattini yaz → company_events INSERT pipeline'i (3s) | utku | 2026-10-01T17:19:03 |
| VERI-NACE-ACILIM-01 | [VERI] NACE acilimini yaz → sunum.acilim_getir + musteri karti (3s) | utku | 2026-10-01T17:19:04 |
| VERI-NACE-SOZLUK-DIL-01 | [VERI] NACE sozluk basliklarini duzelt → 572 TR karakter (4s) | utku | 2026-10-01T17:19:04 |
| VERI-TSG-ESLEME-CASE-01 | [VERI] TSG ilan turu eslermesini duzel -> olay_esle normalize + canli unknown olcumu (1s) | utku | 2026-10-02T18:00:31 |
| VERI-TENDER-KOLON-01 | [VERI] D-308 tender sema kolon cevirisi -> osb_tender_monitor.py uyumlu hale getir (1s) | utku | 2026-10-02T22:25:17 |
| SCRAPE-001-DOCKER-SETUP | [DOCKER] PostgreSQL 16 + Kazıma servisi entegrasyonu → compose (2s) | utku | 2026-10-02T22:27:44 |
| SCRAPE-002-LEMMLESS-ANKARA-OSB | [KAZIMA] LLM-less: ostim.org.tr + ivedik.org.tr + baskentosb.org.tr → scrape_pages (3s) | utku | 2026-10-02T23:13:36 |
| SCRAPE-003-9ROUTER-JINA-FALLBACK | [KAZIMA] 9Router Jina-Reader fallback: yapı unknown sayfalar (2s) | yasu | 2026-10-04T01:04:46 |
| SCRAPE-004-QWEN-SINIFLANDIRMA | [KAZIMA] Qwen-7b-chat (9Router local): yapı unknown + sınıflandırma (2s) | yasu | 2026-10-04T03:31:05 |
| SCRAPE-005-KAZIMA-DOCKER-INTEGRATION | [DOCKER] Kazıma servisi: profile jobs, healthcheck, cron (1s) | utku | 2026-10-04T00:33:57 |
| VERI-SEMA-DOGRULA-01 | Şema Migrasyon Tutarsızlığını Düzelt (V7) | salih | 2026-10-01T17:19:04 |
| VERI-SEMA-DOGRULA-02 | Eksik Tablolar İçin Kod Taraması (entity_matches, api_usage_daily) | yasu | 2026-10-01T17:58:34 |
| VERI-SEMA-DOGRULA-03 | NACE Dil Kolonları Kontrol Raporu | yasu | 2026-10-01T17:58:44 |
| ALTYAPI-ODIN-UYARLAMA-01 | [ALTYAPI] Odin iç/müşteri endpoint ayrımını belgele → docs/ODIN_SECURITY_CHECKLIST.md (7d) | ihsan | 2026-10-04T14:27:38 |
| ALTYAPI-EVREN-PRIVATE-DOGRULAMA | [ALTYAPI] EVREN private eğitim hizmetini araştır → docs/EVREN_PRIVATE_EGITIM_DOGRULAMA.md (7d) | yasu | 2026-10-01T20:31:32 |
| ALTYAPI-ODIN-DENETIM-RAPORU | [ALTYAPI] Odin üretim öncesi GO/NO-GO kararını denetle → ALTYAPI-ODIN-DENETIM-RAPORU_2026-10-31_denetim.md (10d) | yasu | 2026-10-01T17:59:33 |
| VERI-OSB-TEMIZLIK-01 | [VERI] 647 kimliksiz + 44 mukerrer kaydi sil -> osb_firma_dosyalari temiz (2s) | yasu | 2026-10-02T22:25:00 |
| ALTYAPI-RAG-EMBEDDER-01 | [ALTYAPI] Sahte hash embedder'i sil -> odin_ai/rag.py (2s) | yasu | 2026-10-02T22:23:50 |
| VERI-RAG-KORPUS-01 | [VERI] Firma kayitlarini korpusa yaz -> vector/service.py (3s) | utku | 2026-10-02T18:00:31 |
| VERI-RISK-MOTORU-01 | [VERI] Sekiz risk skoru tablosunu yaz → 0046_risk_skorlari.sql (4s) | utku | 2026-10-02T22:25:35 |
| VERI-ENTITY-GRAPH-01 | [VERI] Firma ilişki ağı v0 yaz → 0047_entity_graph.sql (4s) | yasu | 2026-10-02T22:24:08 |
| DOC-VENDOR-DD-ARASTIRMA-01 | [DOC] Faz 5 tedarikçi denetim kapsamını araştır → docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md (4s) | yasu | 2026-10-02T22:24:27 |
| DOC-GLOBAL-INTEL-ARASTIRMA-01 | [DOC] Faz 6 küresel istihbarat ağı kapsamını araştır → docs/FAZ6_GLOBAL_INTEL_KAPSAM.md (4s) | utku | 2026-10-03T17:00:29 |
| VERI-SKOR-MOTORU-01 | [VERI] Need/Fit/Timing/Ensemble dort skor tablosu -> 0049_firsat_skorlari.sql (5-10g) | utku | 2026-10-02T22:24:45 |
| VERI-TOBB2B-BUYUTME-01 | [VERI] TOBB2B pilot buyutme - tobb2b.org.tr ucretsiz, genis Id araligi (3-5g) | yasu | 2026-10-02T18:22:32 |
| ALTYAPI-PANO-ARSIV-CAKISMA-02 | [ALTYAPI] B-01 pano<->arsiv task_id cakismasi: 105 kayit yeniden cikti (eski 17 kapanis sonrasi) | ihsan | 2026-10-03T16:41:10 |
| ALTYAPI-9ROUTER-ANAHTAR-01 | [ALTYAPI] 9Router anahtar guncelleme betigini yaz -> scripts/ninerouter_anahtar_guncelle.py (2s) | yasu | 2026-10-04T00:36:28 |
| ALTYAPI-OPENROUTER-ARAC-01 | [ALTYAPI] continue_haftalik_bildir.py + or_*.py betiklerini kalici yaz -> scripts/ commit + zamanlanmis gorev (2s) | yasu | 2026-10-04T03:31:20 |
| VERI-OSTIM-HREF-FILTRE-01 | [VERI] OSTIM detay kaziyicida href filtresini duzelt -> ostim_detail_scraper.py + brave 100 firma pilot (3s) | utku | 2026-10-04T00:49:25 |
| VERI-APIFY-BUTCE-01 | [VERI] Apify kullanimini olc ve 10 dolar tavanina sabitle -> docs/APIFY_BUTCE.md + kota kodu (2s) | utku | 2026-10-04T00:35:45 |
| VERI-PAKET-FIYAT-SENKRON-01 | [VERI] sync_paket_fiyatlari.py betigini denetle ve DB ile esle -> paketler.py fiyat_katalogu tek kaynak (2s) | yasu | 2026-10-04T03:31:32 |
| TEST-SIMULASYON-B17-KIRIK-01 | [TEST] Simulasyon B-17 sablon uyarilari + 3 kirik testi duzelt -> pytest yesil, simulasyon exit 0 (2s) | utku | 2026-10-04T00:34:19 |
| ALTYAPI-MIMIR-HABER-KUSU-01 | [ALTYAPI] F2 haber kusu: KAYNAK_HARITASI paket kaynaklariyla genislet → arac_dongusu.py + test (3s) | utku | 2026-10-04T00:34:46 |
| ALTYAPI-KREDI-CUZDANI-01 | [ALTYAPI] F3 kredi cuzdani: kullanim_log + kredi_hareket semasi ve yazma kapisi → 0050_kredi_cuzdani.sql + kredi.py (4s) | yasu | 2026-10-04T00:36:09 |
| VERI-INGEST-ASO-GLOB-01 | [VERI] ingest_aso glob daralt: rapor dosyalari firma kaydi sanilmasin | utku | 2026-10-04T00:35:05 |
| UI-ADMIN-KAYNAKLAR-SAYFA-34 | [UI] Veri Kaynakları sayfasını yaz -> admin_kaynaklar.py, 0050 kazıma tabloları tek yerde (4s) | utku | 2026-10-04T03:25:27 |
| UI-ADMIN-CRAWL-TASI-35 | [UI] Crawl Kontrolü bloğunu Webhook'tan Veri Kaynakları sayfasına taşı -> tek OSINT adresi (2s) | utku | 2026-10-04T03:31:45 |
| UI-ADMIN-SON-KAZIMA-KART-36 | [UI] Ana Kontrol'e Veri Kaynakları giriş kartını yaz -> GIRIS_KARTLARI 5. kart, son kazıma tek tıkla (1s) | utku | 2026-10-04T03:13:01 |
| UI-ADMIN-ACIKLAMA-METIN-37 | [UI] SECTIONS aciklama metinlerini düzelt -> menü ipucu admin dilinde, jargonsuz (2s) | utku | 2026-10-04T03:31:58 |
| UI-ADMIN-REHBER-ALAN-38 | [UI] TabTanimi.rehber alanını yaz -> 6 dağınık _hg_rehber okuyucusu tek kapıdan geçer (3s) | utku | 2026-10-04T03:32:17 |
| VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01 | [VERI] ASO ikiz ingest yolunu sil -> tek kanonik dosya + etl/ingest_aso.py tek yükleyici (3s) | utku | 2026-10-04T03:38:07 |
| VERI-WEB-SITESI-ZENGINLESTIR-01 | [VERI] website_domain zenginleştirme kaynağını yaz -> unvan arama + canlı HTTP doğrulama, 7343 boş alana gerçek site (4s) | utku | 2026-10-04T17:01:04 |
| ALTYAPI-GOREV-AT-KAPI-01 | [ALTYAPI] gorev_at.py cmd_at'i duzelt -> kapi_gecer() kilit kapisindan gecer (3s) | yasu | 2026-10-04T03:32:28 |
| ALTYAPI-ODIN-MASKE-V3-01 | [ALTYAPI] maskeleme_odin() V1/V2/V3 kaynak ayrımı + V3 endpoint (2s) | utku | 2026-10-04T20:15:44 |
