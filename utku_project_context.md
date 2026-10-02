# utku_project_context.md — Oturum Hafızası (D-219)

Şablon: [[Huginn Data Insights/_ajan_context_sablon]] · Tavan 400 satır (D-219 Ek, 2026-10-02).

## KALDIĞIM YER

- **Konum:** `DOC-GLOBAL-INTEL-ARASTIRMA-01` **teslim edildi → `review`** (2026-10-02 23:50).
  `SCRAPE-002` de `review`'da. Commit `2ae39f8` (45 pre-commit testi geçti).
  Sonraki hedef: D-312 döngüsü — `bak`/`ajan_chat.py oku`; SCRAPE-005 hâlâ **bloke**.
- **Yapılanlar (2026-10-02 23:40 DOC-GLOBAL turu):**
  - `docs/FAZ6_GLOBAL_INTEL_KAPSAM.md` yazıldı (370 satır) + `hubs/PLAN_STRATEGY_HUB.md`
    B-14 kapanış satırı. Kod yazılmadı (brif: dokümantasyon görevi).
  - **Ölçülen toplam:** `osb_veri_denetim.py` → 8987 kayıt / 8296 tekil / 44 mükerrer /
    647 kimliksiz / 0 mojibake. `--self` muhasebe ok, `--kontrol 8987` exit 0.
  - **D-260 tuzağı:** 8987 `data/osb/` ham çıktıdır, **`companies` DEĞİL**
    (9412 = D-263/D-264 tarihli ölçüm, bu turda yeniden ölçülmedi).
  - **Ülke kolonu `companies`'ta YOK.** Ama projede **iki tutarsız ülke geleneği** var:
    `user_activity_log.ulke_kodu CHAR(2)` ISO 3166-1 (0017:20) ·
    `job_postings.location_country TEXT DEFAULT 'Türkiye'` (0013:20). İkisi de taşınmamış.
  - 5 engel: E1 ülke · E2 `tax_number` VKN odaklı · E3 NACE (NAICS 50 migration'da **0**) ·
    E4 `is_ankara` tek soruya cevap veren kolon · E5 Türkçe dil varsayımı.
  - **Öneri: Yol A (ertele)** — E1-E5 veri değil öncelik eksikliği; Yol B'nin bedeli
    ölçülmüş (D-249 / 0024 gocu 8140 sahte 0 buldu).
  - 3 bulgu `bulgu_defteri.md`'ye yazıldı (acil: ülke geleneği çatışması).
- **İki brif sapması (ikisi de neredeyse yanlış karara yol açıyordu):**
  1. Brif E3'te `entity_resolution/` dedi → orada `maketrans` **0 eşleşme**.
     Gerçek yer `api/core/normalize.py:602,681` + `etl/kaynak_bagla.py:22`.
  2. İlk `findstr` **boş** döndü, "ülke kolonu yok" yazmak üzereydim.
     Pozitif kontrol (`vkn` → 12 satır) PowerShell `\"` tırnaklamasının
     bozuk olduğunu gösterdi. **Boş sonuç, sağlam sonuç kadar güvenilir değildir.**
- **KRİTİK — çok ajanlı kirli ağaç:** `git add` sonrası `AGENTS.md` ve
  `scripts/gorev_kutusu.py` **başka ajanların staged** işi olarak geldi.
  `git restore --staged <dosya>` ile stage'ten çıkar, içeriğine dokunma.
  `git add -A` **asla**.
- **Yapılanlar (2026-10-02 SCRAPE-002 turu):**
  - `SCRAPE-002-LEMMLESS-ANKARA-OSB` → **teslim (review)**. 5 yeni dosya:
    `src/company_master/etl/scrape_kayit.py` (0050 tek yazıcı),
    `src/company_master/etl/scrape_kosu.py` (ortak koşu iskeleti),
    `scripts/kazima_{ostim,ivedik,baskent}.py`. Kanonik scraper'lara
    **dokunulmadı** (D-235 `sayfa_dongusu` bozulmadı).
    Canlı ölçüm: `scrape_pages=2`, `scrape_audit_log=5`, `scrape_errors=1`,
    **yinelenen=0**, `cost_usd<>0 → [0,0]`, `llm_used TRUE → [0,0]`.
    İdempotens kanıtlandı: 2. tur `yazilan=0 / atlanan=1` (iki kaynakta da).
  - `SCRAPE-001-DOCKER-SETUP` → teslim (review) öncül görev.
  - `VERI-SCOR-MOTORU-01`, `VERI-TENDER-KOLON-01`, `VERI-RISK-MOTORU-01` → review.
- **Ölçülen çalışma adresleri (brif ile çelişiyor — dosyaya bakmadan yazma):**
  `baskentosb.org.tr` → **DNS çözülmüyor** (Errno 11002), izin reddi → `scrape_errors`.
  `ivedik.org.tr` → DNS çözülmüyor; **çalışan** `www.ivedikosb.org.tr` (200, 15 kart).
  `ostim.org.tr/firmalar` → 200, 334267 bayt, 300 `div.col-lg-4.mb-3`,
  300 `a[href^='/firmalar/']`, **0 `<table>`** (brifin tablo varsayımı yanlış).
- **Kritik bağlam (SADECE bu dosyalara bak):**
  `src/company_master/etl/scrape_kayit.py` · `src/company_master/etl/scrape_kosu.py`
  · `tests/test_scrape_kayit_mandali.py`
  · `scripts/kazima_{ostim,ivedik,baskent}.py` ·
  `src/company_master/schema/migrations/0050_scrape_audit_log.sql` ·
  `src/company_master/utils/scraping_permission_router.py`
- **Sonraki adım:** teslim sonrası `bak --ajan utku` + `ajan_chat.py oku`;
  açık bulgular: (1) baskentosb ölü domain, (2) SKILL.md router imzası yanlış.
  **(3) birim testi ve `audit_kaydet` FK borcu KAPANDI (23:30 turu):**
  `tests/test_scrape_kayit_mandali.py` = 34 test, canlı DB'ye bağlanmaz,
  kırma denemesi kanıtlı. `audit_kaydet()` artık `audit_id` döndürüyor →
  hata kayıtları FK'li (canlı: error_id=2 → audit_id=7, orphan=0).
  İdempotens **3. kez** doğrulandı (hash'ler değişmedi).
- **Öz-eleştiri (KALICI — SİLİNMEZ)** — bu turda *yazılan belgenin yarım
  kalması* önemli bir tuzak: uzun markdown `write` çağrısı sessizce ortada
  kesilebiliyor ve tool "başarılı" diyor. Teslimden önce dosyanın **sonunu
  okumak** zorunlu; `grep` ile son başlığı aramak yetmiyor.
- **Görev:** `DOC-GLOBAL-INTEL-ARASTIRMA-01` (review) · `SCRAPE-002` (review) ·
  `SCRAPE-005-KAZIMA-DOCKER-INTEGRATION` (**bloke**, brif + locked path eksik) ·
  **Son okunan karar:** `D-323`

> **SCRAPE-002'de briften 3 yerde sapıldı — hepsi diskte ölçülerek bulundu.**
> (1) Brif `get_router("ostim.org.tr")` / `can_fetch()` diyor; gerçek API parametresiz
> `get_router()` → `.check(url) -> Decision(url,domain,allowed,reason)`.
> (2) Brif tablo seçicisi varsayıyor; OSTİM'de 0 `<table>`, gerçek yapı
> `div.col-lg-4.mb-3` + detay linkleri.
> (3) Brif `scrape_errors`'a `source_name`/`source_url` yazıyor; 0050 şemasında
> **bu kolonlar yok**, bağ yalnız `audit_id` FK'si. İlk yazım canlıda reddedildi.
> *Ders: kanonik scraper sınıfları ve migration dosyası briften önce okunur;
> brif özetdir, sözleşme değildir (D-224/D-267).*

> **Çalışma ağacı çöp dolu (2026-10-02 ölçümü).** `git status` yüzlerce dosya
> (başka ajanların `??` ve `M` dosyaları) listeliyor. **`git add -A` TEHLİKELİ** —
> başkasının işini commit'ler. Bu turda yalnız kendi 6 dosyam commit edildi;
> ortak dosyalar (`task_board.json`, `hubs/*`, ajan context'leri) elle bırakıldı.

> **Önceki turun notu (SCRAPE-001):** ayrıntı kendi raporunda —
> [[SCRAPE-001-DOCKER-SETUP_rapor_2026-10-02_uretim]].

> **SCRAPE-002 brifi AÇILABİLİR.** Panodaki yol `../.agents/skills/huginn-web-kazima/SKILL.md`
> goreli; vault kökünden çözülünce `C:\Huginn Data Projesi\.agents\...` = 16034 bayt,
> `Test-Path` True. Brif zaten **0050** yazıyor (D-323 düzeltmesi brife de işlemiş).
> **Ben bu turda iki kez aynı hatayı yaptım:** (1) "brif 0046 gösteriyor" → düzeltilmişti,
> (2) "brif yolu geçersiz, dosya yok" → **dosya vardı**. İkisi de diskte ölçülmeden
> söylendi (D-224/D-260). *D-220 kural 2 `.agents/`'i arama kapsamı dışı yapar; bu
> brif yolu, arama değil — brif diskte ve okunabilir.*

> **B-14 kapısı iki yer ister (2026-10-02 ölçümü):** teslim reddi
> "hafıza izi yok" dediğinde tek yazmak yetmiyor — `gorev_kutusu.py:_hafiza_hedefleri()`
> **SSOT hub'ı (`hubs/ADMIN_DASHBOARD_HUB.md`) + brif'te geçen hub'ları** arıyor.
> Konu hub'ı (OSINT) tek başına yetmiyor. Bu turda ilk deneme OSINT'e yazıp
> **reddedildi**, ikinci deneme ADMIN'e de yazınca geçti.

## Oturum Açılış (60 saniye, bu sırayla)

1. **§KALDIĞIM YER** — yukarıdaki blok.
2. **§Tuzaklar** + **§Sabitler** — okumazsan aynı hatayı tekrar ödersin.
3. `python -X utf8 scripts/gorev_kutusu.py bak --ajan utku`
4. `python -X utf8 scripts/chat_al.py --ajan utku --sadece-acik --limit 20`
   (D-210 cevap süresi: P0 5-10dk, P1 10-15dk, P2 15-30dk)
5. [[Huginn Data Insights/AGENTS]] son karar no ≠ `D-323` ise aradakileri oku (D-168).
6. Brifin **§Doğrulanacak varsayım** maddelerini koda karşı doğrula; tutmuyorsa chat aç, **uydurma**.
7. Bitirdiğinde: **teslim sonrası döngü** (§Sık Komutlar altındaki 6 adım).

**§KALDIĞIM YER pano ile çelişiyorsa pano üstündür.**

## Kimlik

- **Ajan:** `utku` (araç: kilo)
- **Rol:** Üretim/hacim ajanı — kod yazma, refactoring, test, CI/CD. Kilitli dosyalarda çalışır.
- **Kit:** `ADMIN-KİT` (D-196)
- **Mülkü:** `src/**`, `web_dashboard/**`, `tests/**` — kilit aldığım dosyalar
- **Mülkü değil:** `AGENTS.md` (yalnız KAHİN), SSOT dökümanı §7 dışı bölümler, başka ajanın açık kilidi
- **Rapor hattı:** teslim → `ihsan` onayı (P0/P1 elle, P2 ve altı `oto_nobetci.py` — D-46)

## Proje Temel Bilgileri

- **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` (görev başı oku, görev sonu §7'ye işle)
- **Kural kaynağı:** [[Huginn Data Insights/AGENTS]] — tek SSOT, kural kopyalamak yasak
- **Test:** `python -m pytest tests/ -q` → **son bilinen: 20 failed / 4260 passed / 12 skipped** (2026-09-26)
- **Hedef:** `TEST-BACKLOG-20` ile 20 → 0

## Sabitler (doğrulanmış gerçekler)

- Migration dizini `src/company_master/schema/migrations/` — `migrate.py` **burada**; `schema/migrate.py` **yok**, `db/migrate.py` ayrı dosya
- `0016_users_last_login.down.sql` + `0017_user_activity_log.down.sql` migrations **kökünde**, `down/` alt dizininde değil
- `down/` dizininde 16 dosya var, en az 19 bekleniyor
- Admin menü kökleri (D-214/D-215): 6 kök — Gelir Kapısı + Güvenlik Kapısı dahil

## Tuzaklar (aynı hatayı iki kez yapma)

- Pano görevi kod tabanında karşılığı olmayan dosyaya işaret ediyor → şablon/placeholder sızıntısı → **çapraz kontrol et, kod yazma**, chat aç (D-216: 8 görev bu yüzden arşivlendi)
- `migrate.py` üç ayrı yolda aranıyor → yanlış dosyayı düzenleme riski → yalnız `schema/migrations/migrate.py`
- İkiz dosya/şablon üretmek → D-211 ihlali → önce `glob` ile ara, varsa mevcut olanı düzenle

### 2026-10-02 eklentisi (SCRAPE-001 turu)

- **B-14 "hafıza izi yok" reddi**: konu hub'ına tek başına yazmak **yetmiyor**.
  `ADMIN_DASHBOARD_HUB.md` + brif'te geçen hub **ikisi de** gerekiyor.
  → Teslimden önce `Select-String` ile iki dosyada da `task_id` aramak.
- **Göç numarası brif'te beyan, diskte gerçek**: planda `0046_scrape_audit_log.sql`
  yazıyordu, gerçekte 0046 `risk_skorlari` idi → 0050. **Numarayı brife körü körüne
  yazma, `Get-ChildItem migrations -Filter "00*.sql"` ile son numarayı ölç.**
  (D-323 bunu zaten karara bağladı; ben ölçümü tekrarladım.)
- **psycopg/psycopg2 bind + cast**: `conrelid=:t::regclass` **sözdizimi hatası**
  verir → `conrelid=to_regclass(:t)`. Ölçüm betiği ilk çalıştırmada tam burada
  düştü, ikinci denemede geçti. Bind'ı cast ile birleştirme.
- **`schema_versions.json` güncellenmez** (D-265/D-319): 23'te donmuş, göç
  defteri yalnız `public.schema_migrations`. Kanonik kapı: `scripts/goc_defteri.py`.
- **Yerel Docker DB ölçüm kaynağı değil** (D-238): `companies` 14000 (canlı 9412),
  `schema_migrations` 9 kayıt (diskte 50). Bayat pre-dedup döküm → ölçme, sadece
  konteyner sağlık kontrolü için kullan.
- **Telegram botu `getUpdates` = gerçek yan etki**: polling başlatmak bekleyen
  mesajları tüketir. `docker compose config --services` ile parse doğrula, **başlatma**.
- **D-183 ad kuralı, 3 dosyada ihlal ettim**: rapor adında ajan adı, geçici betikte
  teknik/İngilizce ad. **Sonradan ölçtüm: ihlal YOK.** Rapor `..._uretim.md`,
  ajan adı içermiyor; geçici betik zaten arşivde. Chat'e "ayrı görev açalım"
  dedim, geri aldım (22:25). **Bulgu:** kural bilgisi ≠ ihlal tespiti.
- **Pano `brief` yolu göreli olabilir — mutlak sanma:** `../.agents/...`
  vault kökünden çözülünce **var**. `Test-Path` göreli yolla False döndüğü
  için "yol yok" dedim; gerçek yol dışarıda. **D-224/1:** yol iddiası da beyandır.
- **`chat_al.py --ajan X`** zorunlu; `--hepsi` **olmaz** (bu bir ajan filtresidir).
  `--type` değerleri yalnız `hata|soru|koordinasyon|rapor|bilgi` — `duzeltme` **yok**,
  düzeltme `bilgi` tipine yazılır.

## Bilinen Açıklar (kapsam dışı backlog)

- Tam suite 20 failed — görev `TEST-BACKLOG-20` (6 faz, tek brif — D-217)

## Sık Komutlar

```bash
# pano
python -X utf8 scripts/gorev_kutusu.py liste --ajan utku
python -X utf8 scripts/gorev_kutusu.py bak --ajan utku        # salt okunur (D-69)
python -X utf8 scripts/gorev_kutusu.py basla --ajan utku     # TUKETICIDIR, dogrulama icin kullanma
python -X utf8 scripts/gorev_kutusu.py teslim --ajan utku --task-id <ID> --ozet "<ozet>"

# ajan chat (D-210 · gercek yol data/orchestrator/chat/messages.jsonl)
python -X utf8 scripts/chat_al.py --ajan utku --sadece-acik --limit 20
python -X utf8 scripts/chat_gonder.py --to <ajan|hepsi> --type hata|soru|koordinasyon|rapor|bilgi \
    --task-id <ID> --mesaj "<metin>"
# kimlik: python -X utf8 scripts/ajan_kimligi.py utku  (git config / .env KULLANMA - D-306)

# bulgu defteri (D-318 tek kanonik)
python -X utf8 scripts/bulgu_defteri.py ekle --task-id <ID> --rol utku \
    --renk acil|dikkat|tamam|oneri --ozet "<bulgu>" --karar "<islem>"
python -X utf8 scripts/bulgu_defteri.py islenmemis

# dogrulama
python -X utf8 scripts/kodlama_denetim.py --kapsam git
```

## Teslim Sonrası Zorunlu Döngü (D-312 · 2026-10-02 eklendi)

**Durmadan önce bu 6 adım sırayla:** rapor → bulgu defteri → ajan chat →
chat yorumu → wiki/hub → hafıza. Atlama = kural ihlali.

| # | Adım | Komut | Kural |
|---|------|-------|-------|
| 1 | **Rapor güncel mi** | `## Bulgular` boş değil, `## Eksik / erteleme` dolu | D-67 |
| 2 | **Bulgu defterini doldur** | `bulgu_defteri.py ekle` — teslimde **her** bulgu için | D-318 |
| 3 | **Ajan chat'i oku** | `chat_al.py --ajan utku --sadece-acik` | D-210 |
| 4 | **Yorum yaz** | Her açık mesaja `chat_gonder.py` ile cevap; @mention cevap zorunlu | D-210 |
| 5 | **Wiki + hub** | Raporun `## Ilgili Nodlar` ≥2 wikilink; yeni belge ilgili hub'a bağlanır | D-218, D-186 |
| 6 | **Hafızayı tazele** | `§KALDIĞIM YER` + Son okunan karar + yeni tuzak | D-219, D-237 |

> **2026-10-02'de 1, 2 ve 3 atlandı.** 17 açık mesaj vardı, hiçbiri okunmadı;
> bulgu defterine geç yazıldı; wikilink 3 ile sınırlı kalmıştı. Teslim `review`
> durumuna geçmiş olsa da döngünün yarısı yapılmamıştı. **Bir teslim raporu
> yazmak teslim değildir (D-55).**

## Oturum Günlüğü

### 2026-10-02 — SCRAPE-001 teslim (review) + teslim döngüsü atlandı

- **Teslim:** `SCRAPE-001-DOCKER-SETUP` → `review`. `0050_scrape_audit_log.sql`
  (+down) canlı; `Diskte 50 goc / defterde 50 kayit`; `scripts/_kazima_dogrula.py` 6/6.
  İki hata düzeltildi: `table_schema='public'` filtresi (D-253/4), yalan
  `veri-gocu:`/`dusen-iz:` beyanları (D-253/2). B-14 ilk denemede reddedildi
  (konu hub'ı yetmiyor, ADMIN hub'ı da gerekiyor), ikinci denemede geçti.
- **Ajan chat:** 17 açık mesaj vardı, **hiç okunmamıştı**. Sonradan okundu;
  D-183 iddiam çekildi, SCRAPE-002 kilidi ihsan'a bildirildi.
- **Düzeltmeler:** geçici betik SHA manifestli arşive; rapor 3→11 wikilink;
  ADMIN+OSINT hub satırlarına rapor/göç wikilink'i; bulgu defterine 3 kayıt.

### 2026-09-27 — VERI-KAYNAK-BAG-01 + VERI-NACE-SOZLUK-01 + VERI-NACE-TEMIZ-01 + TEST-BACKLOG-20 + VERI-HAYALET-TEMIZ-01 tamamlandı (onay bekliyor)

- **Görevler:** `VERI-KAYNAK-BAG-01` (P0), `VERI-NACE-SOZLUK-01` (P0), `VERI-NACE-TEMIZ-01` (P1), `TEST-BACKLOG-20` (P1), `VERI-HAYALET-TEMIZ-01` (P0)
- **Yapılan VERI-KAYNAK-BAG-01:**
  - Migration 0023: source_records.company_id kolonu eklendi + FK
  - 5252 eşleşme (37.5%): 34 vergi_no + 5218 isim birebir
  - FK doğrulandı (0 ihlal)
- **Yapılan VERI-NACE-SOZLUK-01:**
  - 4 kaynak birleşimi: xlsx_resmi (1547), turkiye_nace_json (2142), nace-rev-2-1.json (1562), nace-rev-2.json (1482)
  - 3319 NACE kodu yüklendi, seviye 6/4/2/1 dolu
  - Eşleşme %92.9 (4252/4574), 47.79.04 ve 47.79 var
- **Yapılan VERI-NACE-TEMIZ-01:**
  - 7614 NN.NN format düzeltildi (raw_nace'ten türetildi)
  - 675 altı haneli kırpıldı (valid 4 haneli parent'a)
  - 25 iki haneli NULL'a çekildi (98/71/16/78 - çoklu child)
  - 1 yetim kod düzeltildi (13.92.11)
  - Sonuç: NN.NN 8289 (valid), 6-digit 0, 2-digit 0, yetim 0
- **Yapılan TEST-BACKLOG-20:** 6 faz, 20 failed → 0, 348 test passed
- **Yapılan VERI-HAYALET-TEMIZ-01:** 4591 hayalet kayıt silindi, UNIQUE INDEX (migration 0022), vergi_no 761 korundu
- **Doğrulama:** Tüm 5 görev `review` durumunda, onay bekliyor
- **Kalan / bloke:** VERI-02 ve VERI-NACE-COKLU-01 bloke (P0 onayı bekliyor)
- **Öğrenilen tuzak:** 5 görev tek seferde onay kuyruğuna girdi, tek tek onaylanmalı

### 2026-09-26 — D-215/D-216 menü kaydı

- **Görev:** `UI-ADMIN-MENU-D215216`
- **Yapılan:** D-215 (Gelir Kapısı, paket_kredi taşıma, maliyet→Metrikler, Güvenlik Kapısı kök) + D-216 hayalet arşivleme geriye dönük panoya işlendi
- **Doğrulama:** `pytest tests/test_naming_audit.py -q` → 9 passed
- **Commit:** `9650bf1`
- **Kalan / bloke:** yok
- **Öğrenilen tuzak:** pano kaydı ile kod tabanı çapraz kontrol edilmeden görev alınmamalı (→ §Tuzaklar)

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle + **Son okunan karar** no'yu tazele.

## Öz-eleştiri (KALICI — SİLİNMEZ)

D-219: bu bölüm 200/400 satır tavanına **dahil değildir** ve arşiv rotasyonunda
**taşınmaz**. KAHİN kararı 2026-10-02: *"tüm ajanlar öz eleştirilerini cortex
dosyasında sabit tutsun, silmesinler."*

### 1. Dur — dosyayı açmadan kusum ilan etme (2026-10-02)

D-183'ün ad kuralını okudum ve chat'e "rapor adında ajan adı var, geçici betik
teknik ad, ayrı görev açalım" dedim. **Dosyalara bakmadan.**

Ölçüm: rapor `..._rapor_2026-10-02_uretim.md` — ajan adı **yok**, suffix
`_uretim`, D-55/D-183'e uyumlu. Gecici betik zaten arşive taşınmıştı. Yani
ihlal **yoktu**; olmayan bir borcu iki ajana bildirdim ve ayrı görev istedim.

**Kök neden:** kuralı bilmek, ihlali tespit etmek demek değil. "Şu kural var"
dediğimde karşıma **kanıt** koymadım. D-260'ın kendisi: beyan kanıt değildir —
ve beyanı **üreten** taraf için de geçerli.

**Ders:** bir kusum bildirirken önce `Get-ChildItem`/`Select-String` ile
somut kanıtı ekle. "Dosya şöyle olmalı" ile "dosya şöyle **duruyor**" aynı cümle
değil; ikincisini kanıtlamadan birincisini söyleme.

### 2. Teslim etmek döngüyü bitirmek değil (2026-10-02)

`gorev_kutusu.py teslim` çıktısı `review`'a geçti ve iş "bitti" görünürüne
girdi. **Hiçbir şeyin gerçekten kapanmadı:** 17 açık ajan chat mesajı
okunmamıştı (hepsi SLA aşımlı), bulgu defterine kayıt düşülmemişti, raporda 3
wikilink vardı, hub satırları rapora düz metin yol ile bağlıydı, hafıza
dosyam 5 günlük eski durumdaydı.

**Kök neden:** teslimi "pano durumu değişti" diye okudum. Teslim, döngünün
**ortasıdır** — D-312 teslim sonrası altı adım zorunludur (rapor → bulgu defteri
→ chat → yorum → wiki/hub → hafıza).

**Ders:** `teslim` komutundan sonra **bir daha komut çalıştırmadan oturumu
kapatma.** Altı adım bitene kadar tur kapanmış sayılmaz.

### 3. Ajan hafızası bayatlıyorsa ajan da bayatlıdır (2026-10-02)

`utku_project_context.md` 5 gündür güncellenmemişti; `§KALDIĞIM YER` "aktif iş
yok, 5 görev onay bekliyor" diyordu, gerçekte `SCRAPE-001` `aktif`'ti. Yeni
oturumda o satırdan başlasaydım **yanlış yerde** çalışmaya başlardım.

**Kök neden:** teslim sırasında `§KALDIĞIM YER` güncellenmedi. D-237 zaten
söylüyor: kapanan iş sahibinin context dosyasına geçmeli; teslim otomatik
yapmıyor, **ajan yapıyor**.

**Ders:** teslimden sonraki hafıza güncellemesi isteğe bağlı değil, teslimin
parçası. KALDIĞIM YER bloğu **tek blok, üzerine yazılır** — biriktirilmez
(D-219); biriktirilmiş günlük güncel durumu göstermez.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/_ajan_context_sablon]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/data/orchestrator/bulgu_defteri]] — teslim sonrası zorunlu
- [[Huginn Data Insights/data/orchestrator/SCRAPE-001-DOCKER-SETUP_rapor_2026-10-02_uretim]]
- [[scripts/chat_al]] · [[scripts/chat_gonder]] · [[scripts/bulgu_defteri]]
- [[scripts/gorev_kutusu]] · [[scripts/ajan_kimligi]] · [[scripts/goc_defteri]]
- [[src/company_master/schema/migrations/0050_scrape_audit_log]]
