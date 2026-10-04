# SCRAPE-001-DOCKER-SETUP — Üretim Raporu

**Tarih:** 2026-10-02 · **Ajan:** Üretim/Hacim UTKU · **Görev:** `SCRAPE-001-DOCKER-SETUP`
**Kilitsiz çıktı:** `src/company_master/schema/migrations/0050_scrape_audit_log.sql` + `down/0050_scrape_audit_log.down.sql`

## Ne yapıldı

Kazıma denetim şeması **0050** numarasıyla canlıda: üç tablo (`scrape_audit_log`,
`scrape_pages`, `scrape_errors`), göç defterinde kayıtlı, kanonik kapıdan
`TAM`.

Bu turda iki iş yapıldı:

1. **Göç numarası çakışması çözülmüş bulundu.** VETO'mda bildirdiğim çakışma
   (plan `0046` istiyordu, diskte `0046_risk_skorlari.sql` vardı) üzerine
   göç **0050'ye taşınarak** yazılmış ve uygulanmış. Numara doğru seçilmiş:
   0046–0049 doluydu, 0050 serbest.
2. **Göçte üç hata düzeltildi** (aşağıda, kanıtlarıyla).

Docker tarafı brifin kendi komutlarıyla **canlı doğrulandı**.

## Değişen dosyalar

| Dosya | İş |
|---|---|
| `src/company_master/schema/migrations/0050_scrape_audit_log.sql` | 3 `information_schema` sorgusuna `table_schema='public'` eklendi; yanlış `veri-gocu:`/`dusen-iz:` beyanları kaldırıldı |
| `hubs/OSINT_VERI_TOPLAMA_HUB.md` | B-14 kapanış kaydı |
| `data/orchestrator/SCRAPE-001-DOCKER-SETUP_rapor_2026-10-02_uretim.md` | bu rapor |

## Test sonuçları

### Brifin kendi doğrulama komutu

```
python -X utf8 scripts/_kazima_dogrula.py
=== Kazıma Doğrulama Testi ===
✓ Migration 0050 uygulandı
✓ Kazıma tabloları (audit_log, pages, errors) mevcut
✓ UNIQUE (source_url, content_hash) dedup kısıtı var
✓ CHECK (cost_usd = 0) kısıtı çalışıyor
✓ scraping_permission_router.py (robots.txt + rate limit) var
✓ SHA256 hash fonksiyonu çalışıyor
✅ TÜM TESTLER GEÇTİ — Kazıma altyapısı hazır
```
**Çıkış kodu 0** — talimattaki beklenen çıktı bu.

### İdempotlik kanıtı (D-251/5) — ham bağlantıyla iki kez koşuldu

```
kosu 1: HATASIZ (CREATE TABLE atlandı)
kosu 2: HATASIZ
scrape_audit_log: AYNI  15 kolon | 4 index | 0 satır | 2 kısıt
scrape_pages:     AYNI  14 kolon | 6 index | 0 satır | 3 kısıt
scrape_errors:    AYNI   9 kolon | 3 index | 0 satır | 3 kısıt
SONUC: GEÇTİ
```

Kritik kısıt yerinde: `UNIQUE (source_url, content_hash)` (D-261 — içerik
hash'i **zaman damgası değil içerik** üzerinden; aynı içerik iki kez kazınırsa
ikinci satır reddedilir). Maliyet kapısı yerinde:
`CHECK (cost_usd = 0)` her iki tabloda da — ücretli fallback sızar diye.

### Docker canlı doğrulaması (brif §7.1)

| Kontrol | Sonuç |
|---|---|
| `docker compose --profile localdb up -d db` | `huginndatainsights-db-1` healthy, `postgres:16-alpine`, `0.0.0.0:5433` |
| API healthcheck | `HTTP 200 {"status":"ok"}` |
| Streamlit healthcheck (8501) | `HTTP 200 ok` |
| psql bağlantısı | `PostgreSQL 16.15 on x86_64-pc-linux-musl` |
| `goc_defteri.py` | `Diskte 50 göç, defterde 50 kayıt` |
| `kodlama_denetim.py --kapsam git` | `temiz: kodlama ihlali yok` (35 değişen dosya) |

## Bulgular

| # | Bulgu | Kanıt |
|---|---|---|
| 🟢 | **0046 çakışması çözüldü — 0050.** Göç `0046_risk_skorlari.sql`'in üstüne değil, boş olan `0050`'ye yazıldı. VETO panoya düştüğü için mi, KAHİN kararı mı bilmiyorum; sonuç doğru. | `Diskte 50 göç, defterde 50 kayıt`; `0050_scrape_audit_log.sql` var |
| 🟡 | **`information_schema` filtresizdi (3 yer) — D-253/4 ihlali.** `IF NOT EXISTS (SELECT 1 ... WHERE table_name='scrape_audit_log')` şema filtresi olmadan yazılmıştı. Supabase'de `auth`/`realtime`/`public` semaları ayrı; başka bir şemada aynı ad varsa **public tablo hiç oluşmaz**, göç sessizce "başarılı" der. **Düzeltildi**, kanıt: `filtreli sorgu: 3 · filtreSIZ sorgu: 0` | dosya satır 17/47/80 |
| 🟡 | **İki beyan yalandı.** Dosyanın sonunda `-- veri-gocu:` ve `-- dusen-iz: audit_log, pages, errors` vardı. (a) `veri-gocu:` **sema izi olmayan** saf veri göçleri içindir (D-267/7); bu göç 3 tablo + 13 indeks yaratıyor, izi var. (b) `dusen-iz` **bu göcün düşürdüğü izi** beyan eder; bu göç `audit_log`/`pages`/`errors` tablolarına hiç dokunmadı — ölçtüm, üçü de canlı şemada **yok** (`{'audit_log': 0, 'pages': 0, 'errors': 0}`), yani iddia hem yapılmamış hem doğru değil. **İkisi de kaldırıldı**, kanıt: `beyan satırı: 0` | dosya sonu |
| 🟢 | Yanlış beyan bugün zararsız çıktı (`0050` yine de `TAM` raporlandı — araç gerçek izi önceliklendiriyor). Ama yarın tablolar yanlışlıkla düşürülürse `veri-gocu:` defteri susturur, yani **yarınki gerçek alarmı bugünün yanlış beyanı maskeler** (D-267/7'nin yazdığı tam olarak bu). | `goc_defteri.py` → `0050_scrape_audit_log.sql  TAM  defterde` |
| 🔵 | **Telegram botu canlı başlatılmadı.** Profil doğrulandı: iki servis parse ediliyor, `scripts/telegram_polling.py` + `telegram_periodic.py` diskte, `.env`'de token anahtarı tanımlı. **Başlatmadım** çünkü `getUpdates` polling'i bekleyen mesajları tüketir — bu gerçek bir dış yan eti ve kapsam dışı. | `docker compose --profile telegram config --services` → 4 servis |
| 🟡 | **Yerel konteyner DB'si bayat bir döküm.** `companies` **14000** satır, `schema_migrations` **9** kayıt — oysa diskte 50 göç var. Canlı Supabase 9412 firma / 50 kayıt. Yani `db` konteyneri şema tarafından sağlıklı ama **içerik olarak üretimin gerisinde**. D-238 gereği bu ayrı bir konu; yerel DB'ye 41 göç uygulamadım. | `SELECT count(*) FROM companies` → 14000 |
| 🟡 | **`0044`/`0045` göçleri `VERI` raporlanıyor.** İkisi de `dusen-iz` beyanı taşıyor ve tüm izleri düşürülmüş → geriye iz kalmıyor → araç `VERI` diyor. Bu **doğru davranış**, kusur değil; kayda geçirdim çünkü `VERI` etiketi ilk bakışta "veri göçü" sanılıyor. | `0044_tender_remaining_columns.sql  VERI  defterde` |
| 🔴 | **`SCRAPE-002` zincir kilidi açılmaz.** Panodaki brief yolu `.agents/skills/huginn-web-kazima/SKILL.md` — bu dosya **vault dışında** (`C:\Huginn Data Projesi\.agents\`), D-220 kuralı 2 gereği arama kapsamı dışı ve göreli yol olarak **diskte yok**. `SCRAPE-002` bu teslimden sonra otomatik düşecek ama brifini açamayacak. Göç dosyasını da `0046_scrape_audit_log.sql` diye gösteriyor (yine eski numara). | `durum: zincir_bekleme`; brif yolu diskte yok |

## Eksik / erteleme

1. **Telegram botu canlı test edilmedi** — config düzeyinde doğrulandı, konteyner
   başlatılmadı (bekleyen mesaj tüketimi yan etkisi). Ayrı görev.
2. **Yerel konteyner DB'sine 41 göç uygulanmadı** — D-238 gereği yerel DB
   ölçüm kaynağı değil; ayrı görev ve ayrı karar.
3. **`SCRAPE-005` kapsamı bu teslimin dışında** — `depends_on`,
   `CRAWL_ENABLED`, `restart: on-failure`, `cpus: 2`, `memory: 2G`,
   `/health`+5000, `scrapers/Dockerfile` eksik. Ayrı görev, ayrı teslim.
4. **SCRAPE-002 brif yolu geçersiz** — yukarıdaki kırmızı bulgu; orchestrator
   alanında (brief dosyası + pano `dosyalar` alanı 0050'ye çekilmeli).

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]] — kararların tek SSOT'u
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]] — alan kapanış kaydı
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — B-14 teslim kapısı kaydı
- [[plans/2026-10-01_docker_taşıma_kazıma_entegrasyon_değerlendirmesi]] — kaynak plan (0046 beyanı)
- [[src/company_master/schema/migrations/0050_scrape_audit_log.sql]] — teslim edilen göç
- [[src/company_master/schema/migrations/down/0050_scrape_audit_log.down.sql]] — geri alma
- [[scripts/_kazima_dogrula.py]] — 6/6 kabul doğrulaması
- [[scripts/goc_defteri.py]] — `Diskte 50 goc / defterde 50 kayit` kanıtı
- [[utku_project_context]] — ajan kalıcı hafızası (D-219)
- [[Huginn Data Insights/_ajan_context_sablon]] — hafıza şablonu

**Kararlar:** D-251/5 (idempotent göç) · D-253/4 (sema filtresi zorunlu) ·
D-261 (`UNIQUE(source_url, content_hash)`) · D-267/7 (`veri-gocu:` beyanı) ·
D-310 (Beş Katmanlı Kontrol) · D-238 (ölçüm canlı DB'de) · D-323 (0046→0050 taşıma) ·
D-219 (ajan hafızası) · D-218 (wikilink zorunluluğu)