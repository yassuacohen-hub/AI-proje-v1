# SCRAPE-002 — LLM-less Ankara OSB kazıma kayıt katmanı

**Tarih:** 2026-10-02 · **Rol:** Üretim/Hacim · **Görev:** `SCRAPE-002-LEMMLESS-ANKARA-OSB`
**Tetik:** 2026-10-02T22:18:40 · **Öncelik:** P0

## Ne yapıldı

Mevcut kanonik OSB kazıyıcılarını **yeniden kullanarak**, 0050 denetim şemasına
(`scrape_pages` / `scrape_audit_log` / `scrape_errors`) yazan kayıt katmanı kuruldu.

**Yeni dosyalar (5)**

| Dosya | Rol |
|---|---|
| `src/company_master/etl/scrape_kayit.py` | 0050 tablo kümesinin **tek yazıcısı** (`KazimaYazici`) |
| `src/company_master/etl/scrape_kosu.py` | Üç kaynağın ortak koşu iskeleti (`Kaynak`, `kosu`) |
| `scripts/kazima_ostim.py` | OSTİM sarmalayıcı |
| `scripts/kazima_ivedik.py` | İvedik sarmalayıcı |
| `scripts/kazima_baskent.py` | Başkent sarmalayıcı |

**Kanonik kazıyıcılara dokunulmadı:** `ostim_scraper.py`, `ivedik_scraper.py`,
`baskent_scraper.py`, `base_osfb_scraper.py` değiştirilmedi. D-235'in
`sayfa_dongusu()` sayfalama şablonu bozulmadı.

**Kapsam sınırı (bilinçli, D-211):** kayıt katmanı **firma çıkarımı yapmaz**.
Firma kaydı kanonik kazıyıcının işidir; burada yalnız ham içerik, SHA256
`content_hash`, denetim kaydı ve hata kuyruğu üretilir.

**Çalıştırılan komutlar (3 kaynak × 2 tur)**
```
python -X utf8 scripts/kazima_baskent.py   # izin reddi -> scrape_errors
python -X utf8 scripts/kazima_ostim.py     # 1 sayfa eklendi
python -X utf8 scripts/kazima_ivedik.py    # 1 sayfa eklendi
# 2. tur: ikisi de yazilan=0, atlanan=1
```

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `src/company_master/etl/scrape_kayit.py` | **yeni** — `KazimaYazici`, `KazimaSonuc`, `icerik_hash()`, `url_hash()` |
| `src/company_master/etl/scrape_kosu.py` | **yeni** — `Kaynak`, `kosu()` |
| `scripts/kazima_ostim.py` | **yeni** |
| `scripts/kazima_ivedik.py` | **yeni** |
| `scripts/kazima_baskent.py` | **yeni** |
| `data/_tmp/scrape002_*.py` | **geçici ölçüm betikleri** — sonrasında silindi |

Değiştirilen mevcut dosya: **yok**.

## Test sonuçları

Canlı Supabase ölçümü (`data/_tmp/scrape002_dogrula.py`, silindi):
`scrape_pages=2`, `scrape_audit_log=5`, `scrape_errors=1`, **yinelenen=0**.

| Kabul kriteri | Beklenen | Ölçülen | Sonuç |
|---|---|---|---|
| Aynı içerik ikinci kez yazılmaz | 0 yeni | `yazilan=0`, `atlanan=1` (iki kaynakta da) | ✅ |
| `scrape_pages` yinelenen satır | 0 | **0** | ✅ |
| `cost_usd <> 0` kayıt | 0 | `[0, 0]` (pages + audit) | ✅ |
| `llm_used IS TRUE` kayıt | 0 | `[0, 0]` (pages + audit) | ✅ |
| LLM/9Router çağrısı | yok | yok — `requests` + `BeautifulSoup` | ✅ |
| Ulaşılamayan kaynak sessiz geçmez | `scrape_errors` kaydı | 1 kayıt, retry planlı | ✅ |

Kod denetimi (`scripts/kodlama_denetim.py --kapsam kod`): **5 yeni dosya temiz**
(`utf8_bom`, `mojibake`, `dosya_sonu` sıfır). Kalan 45 ihlah **önceden var**,
başka ajanlara ait dosyalarda — bu işin kapsamı dışında, dokunulmadı.

Çalıştırılmış komut çıktısı:
```
SONUC = [OK] GECTI
ostim.org.tr  -> 334267 bayt, 300 kart, 300 detay linki
ivedik.org.tr -> 162159 bayt, 15 kart
baskentosb.org.tr -> izin reddi: robots.txt Disallow (DNS cozumlenmiyor)
```

## Bulgular

- 🟡 **`scrape_errors` kolonları brifte varsayılmış halde yazıldı ve canlı şema reddetti.**
  İlk yazımda `source_name` / `source_url` / `error_type` / `error_message`
  kolonları kullanıldı. 0050 gerçek şeması: `error_code`, `error_message`,
  `audit_id`, `page_id`, `retry_count`, `next_retry_at`, `fallback_tried` —
  **kaynak kolonu yok**, bağ yalnız `audit_id` FK'si üzerinden kuruluyor.
  Yazıcı şemaya göre yeniden yazıldı. *Ders: D-267/1 — sözlük kolonu tutmazsa
  `.get()` sessizce boş geçer; sema migration dosyasından okunur.*

- 🟡 **`baskentosb.org.tr` ölü domain.** `baskentosb.org.tr` ve
  `www.baskentosb.org.tr` DNS'ten çözülmüyor (`getaddrinfo failed [Errno 11002]`).
  Kalıcı scraper bu domaini kullanıyor. Replase alan adı bulunmadan bu kaynak
  kazınamaz. Kanıt `scrape_errors`'ta kalıcı.

- 🟡 **`ivedik.org.tr` da ölü; çalışan adres `www.ivedikosb.org.tr`.** Pano kaydı
  ve `sources` tablosundaki ad `ivedik.org.tr`. Kayıt katmanı kaynak adını
  **pano adı** olarak, ağ adresini **çalışan adres** olarak ayrı tutuyor;
  `scrape_audit_log.source_name='ivedik.org.tr'` ile `source_url` canlı
  adresi gösteriyor. Bu ikisinin ayrılması bilinçlidir ama kaynak tablosu
  adres bilgisi taşımadığı için ileride karışabilir.

- 🟡 **SKILL.md router çağrısı yanlış.** `.agents/skills/huginn-web-kazima/SKILL.md`
  örneği `get_router("ostim.org.tr")` ve `can_fetch()` diyor. Gerçek API:
  `get_router()` parametre almaz → `.check(url) -> Decision(url, domain, allowed, reason)`
  ve `.rate_limit(domain)`. Yazıcı gerçek API'yi kullanıyor; doküman düzeltilmeli.

- 🟡 **Aynı sayfa iki kez okunuyor.** Kayıt katmanı ve kanonik kazıyıcı aynı
  liste sayfasını birer kez çekiyor (2 istek). Tek çekim mümkündü ama
  kanonik scraper'lar `fetch_firma_liste()` içinde isteği gizliyor ve HTML'i
  dışarı vermiyor; tek çekim için onlara `son_istek` yakalama kancası
  eklemek gerekirdi. Şimdilik çift okuma kabul edildi (router 2.5 sn aralık).

- 🟡 **`ostim_scraper.py` ve `ostim_scraper_full.py` ikiz görünümlü.** Aynı
  `BASE_URL`, `OstimFirma`, `fetch_robots`, KVKK fonksiyonları iki dosyada
  da var. D-211 ikiz yapısı. Sahibine bildirildi, bu işin kapsamı dışı.

- 🔵 **`scrape_audit_log` her koşuda büyüyor (2 kayıt).** `scrape_pages`
  idempotent; denetim tablosu değil — çünkü denetimin amacı her denemeyi
  **görmektir**. İkinci koşu "aynı sonuç" kabul kriteri `scrape_pages` üzerinden
  ölçüldü, audit sayısı üzerinden değil.

## Eksik / erteleme

- **Başkent kaynağı kazınamadı** (ölü domain). Erteleme gerekçesi `scrape_errors`
  tablosunda; replase alan adı KAHİN kararı gerektirir.
- **`ostim.org.tr` liste sayfasının 300 detay linki kaydedilmedi** — yalnız
  liste sayfasının ham içeriği `scrape_pages`'a yazıldı. Detay sayfalarının
  kanonik kazıyıcı tarafından kapsanması bekleniyor; kayıt katmanı
  kapsamı dışında tutuldu.
- **Aynı liste sayfası iki kez okunuyor** (kayıt katmanı + kanonik kazıyıcı).
  Tek çekim için kanonik scraper'lara ham içerik yakalama kancası gerekir;
  kanonik dosyalara dokunulmadığı için açık borç olarak kalıyor.
- **Kodlama denetimi 45 önceden var ihlal** raporlanmış durumda; bu işin
  dosyaları temiz. Global temizlik ayrı iş kalemidir.

### Kapandı (teslim sonrası ikinci tur, 2026-10-02 23:30)

Aşağıdaki iki açık kalem bu turda kapatıldı; ölçüm canlı Supabase'ten alındı.

- 🟢 **`audit_kaydet()` artık `audit_id` döndürüyor.** Döndürmediği için
  `scrape_errors` kayıtları `audit_id` FK'siz kalıyordu — hata kaydı hangi
  kaynaktan geldiğine ulaşamıyordu. `url_hata_kaydet()` ayrıca aynı audit
  INSERT'ini ikinci kez yazıyordu (aynı SQL'in ikiz kopyası, D-211); o da silindi.
  Canlı kanıt: `error_id=1 → audit_id NULL` (önce), `error_id=2 → audit_id=7`
  (sonra), `audit_id_orphan=0`, kaynak izine ulaşabilen hata kaydı **2/2**.
- 🟢 **Birim mandalı yazıldı:** `tests/test_scrape_kayit_mandali.py` — **34 test**.
  Canlı DB'ye bağlanmaz; `get_engine` sahte motorla değiştirilir
  (ALTYAPI-TEST-HERMETIK-01). Kapsam: hash tekilliği (zaman damgasisiz),
  `ON CONFLICT (source_url, content_hash)`, `llm_used=false` + `cost_usd=0`,
  `scrape_errors`'ta **0050'da olmayan** `source_name`/`source_url` yazılmadığı,
  hata kodu 50 / mesaj 2000 kısaltması, retry penceresi, router API imzası,
  izin yoksa fetch yapılmaması, fetch hatasının kayda düşmesi, kırık ayıklayıcıda
  kaydın yine yazılması, kanonik kazıyıcılara dokunulmaması, INSERT hedeflerinin
  yalnız 0050 tabloları olması.
  **Kırma denemesi (D-256/4):** `scrape_errors`'a `source_name` kolonu geri
  kondu → mandal kırmızı verdi (`1 failed, 33 passed`) → geri alındı → 34/34.
- 🟢 **Idempotens 3. kez canlı doğrulandı:** OSTİM + İvedik `yazilan=0 /
  atlanan=1`; `content_hash` önekleri değişmedi (`0fc4e9657704` / `78ab8f1d676f`).
- 📋 Bulgu defterine 2 kapanış kaydı eklendi; iki hub satırındaki "birim testi
  yok" ifadesi güncellendi (bayat beyan bırakılmadı, D-260).

## İlgili Nodlar

- [[D-310]] — Agentik Web Kazıması Mimarisi (beş katmanlı kontrol)
- [[D-261]] — content_hash UNIQUE dedup (yinelenmeyi durdurmayan hash)
- [[D-267]] — uydurulmuş anahtar/sözlük sessiz kalır
- [[D-245]] — doluluk ≠ geçerlilik
- [[D-235]] — kazıyıcı sayfalama şablonu
- [[D-211]] — ikiz yapı yasağı
- [[D-238]] — canlı veritabanında ölçüm
- [[D-310]] katman 5 — denetim izi
- [[src/company_master/etl/scrape_kayit]] — 0050 tek yazma kapısı
- [[src/company_master/etl/scrape_kosu]] — ortak koşu iskeleti
- [[tests/test_scrape_kayit_mandali]] — 34 test birim mandalı
- [[scripts/kazima_ostim]] · [[scripts/kazima_ivedik]] · [[scripts/kazima_baskent]]
- [[plans/brief_utku_SCRAPE-002-LEMMLESS-ANKARA-OSB]] — görev brifi
- [[SCRAPE-001-DOCKER-SETUP_rapor_2026-10-02_uretim]] — 0050 göçünün sahibi