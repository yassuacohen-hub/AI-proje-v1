
## 2026-09-09 — Faz 3b: Yerel PostgreSQL + Git init ✅

**Yerel PostgreSQL (Docker, `localdb` profili):**
- `postgres:16-alpine` → `localhost:5433` (db: `huginn`, şifre: `LOCAL_PG_PASSWORD` env, default `huginn_local_dev`), container `huginndatainsights-db-1` healthy
- Taze backup alındı (`backup_20260909_123933.zip`, 23 tablo / 37.197 satır)
- **restore_db.py JSONB fix:** CSV'den gelen Python-repr JSON değerleri (`{'...` tek tırnak) PostgreSQL JSONB parser'ını çökertiyordu → `_json_fix` (parse/NULL) + `_json_param` (psycopg `Json` adapter, SQLite fallback `json.dumps`) eklendi
- Restore sonucu: **14.000 companies + 8.905 entity_resolution + 14.000 source_records + 270 kvkk yedek + 4 sources**
- **Performans: ~30x hızlanma** — COUNT 11.2 ms, ILIKE arama 11.6 ms (Supabase: 300-900 ms network roundtrip)

**Git:**
- Repo init + ilk commit: **631 dosya** (`95c2f11`) + JSONB fix commit'i (`2603f16`)
- `.gitignore` doğrulandı: `.env`, `backups/`, `AI proje v1/`, `*.db` dışarıda (gizli veri repo'ya girmiyor)
- Remote henüz yok — GitHub repo + PAT bekleniyor (gh CLI kurulu değil)

**Kullanım:** yerel ortamda çalışmak için `.env.local` dosyasına `DATABASE_URL=postgresql+psycopg://huginn:huginn_local_dev@localhost:5433/huginn` yazmak yeterli. Supabase (üretim) etkilenmedi.

## 2026-09-09 — Docker Faz 2-3: Motor ayağa kalktı, API konteynere taşındı ✅

**Faz 2 (motor):** `docker-desktop` WSL dağıtımı Stopped takılıydı → `wsl --shutdown` + Docker Desktop yeniden başlatma ile çözüldü (**Running**). WSL güncellemesi + yeniden başlatma sonrası bu sıfırlama gerekti.

**Faz 3 (build + çalıştırma):**
- `docker compose build api` → image `huginndatainsights-api` (python:3.12-slim, non-root, HEALTHCHECK) — build OK
- `docker compose up -d api` → **Up (healthy)**, port 8000
- `env_file: .env` runtime inject (image'e gömülmez, `.dockerignore` güvenli) · `restart: unless-stopped` → bilgisayar açılışında otomatik başlar

**Sunucu geçişi (tek 8000 kuralı):**
- Windows uvicorn supervisor emekliye ayrıldı: Startup kısayolu kaldırıldı, bat döngüsü + uvicorn durduruldu
- Artık tek dinleyici: Docker proxy (PID 8384) — `web_server_task.bat` arşivde kalsın (geri dönüş planı)
- Doğrulama: health=200 (konteynerden), kpi 2.9s (soğuk) → **0.39s** (ılık, bağlantı havuzu + cache)

**Yan iş:** change_notify baseline recalc sonrası tazelendi (14.000 firma) — yarın 08:00 raporu sahte alarm üretmez.

**Kazanımlar:** (1) Sunucu artık konteynerde — host bağımsız, Docker restart policy ile süreklilik. (2) Supabase gecikmesi (~300ms) conteynerden de aynı; kalıcı düşük gecikme için sıradaki adım `--profile localdb` yerel PostgreSQL + backup restore.


## 2026-09-09 — P4-4: Kalite Recalc + Performans Profili (done)

**1) Kalite recalc (Y7 temizliği sonrası):** `quality_recalc_fast.py` (set-based, timeout'suz).
- Ortalama skor **53.37 → 40.08** (4.636 çöp e-posta artık boş sayılıyor — skorlar gerçeği yansıtıyor)
- Skor ≥60: 7.721 → 5.428 | Dağılım: 60-79: 4.866, 40-59: 1.465, 20-39: 2.438, 0-19: 4.669

**2) Performans profili (P4-4):** kalıcı araç `scripts/perf_report.py`
- API latency: health 8ms; DB'li endpointler 330-920ms → gecikmenin tabanı **Supabase network roundtrip** (~300ms)
- **EXPLAIN ANALYZE:** arama sorgusu trigram indeks kullanıyor (`idx_companies_legal_name_trgm`, 0.02ms) → DB tarafı hızlı, sorun yok
- **BULGU + FIX:** `api_companies` cache'i yazıyor ama hiç okumuyordu (hit rate %0). `cache_get` sorgu öncesine eklendi → **2914ms → 3.1ms (940x)** tekrar eden isteklerde. TTL 300s, maske durumu anahtarda
- Öneri: kalıcı düşük gecikme için yerel PostgreSQL (Docker Faz 3) veya read-replica

**Sunucu:** uvicorn supervisor (`web_server_task.bat`) ile güncel kodda yeniden başlatıldı, health=200 ✅


## 2026-09-09 — Y7: KVKK Maskeleme + Veri Temizliği (done)

**Kapsam:** KVKK incelemesi (VKN/e-posta görünürlük politikası) → API sunum katmanı kuralları + DB temizliği + testler.

**Bulgular (tarama):**
- DB'de **270 bireysel e-posta** (gmail/hotmail/yahoo/yandex/outlook/icloud) sızıntısı — politika §3.1 ihlali.
- Şahıs adı toplanmıyor (`company_contacts` yalnızca kanal tipi) — §3 uyumlu ✅.
- PII doluluk: tel=8.974, email=8.994→8.724, vkn=40 (total 14.000).

**Uygulanan:**
1. **`web_app.py` maskeleme:** `_mask_email` (`in***@akkor.com.tr`), `_mask_phone` (`905***00`), `apply_kvkk_mask`. İki anahtar: istek bazlı `?mask=1` VEYA kalıcı `DASH_MASK_PII=1` env (müşteri dağıtım modu). Kapsam: `/api/companies`, `/api/companies/export`, `/api/company/{id}`. Unvan/web/VKN açık kalır (PO kararı §4: kamuya açık). Cache anahtarına maske durumu eklendi (maskeli/maskesiz karışmaz).
2. **Temizlik:** `scripts/kvkk_email_temizle.py` — 270 kayıt yedek tabloya (`kvkk_bireysel_email_yedek`) alınıp NULL'landı; teyit: bireysel e-posta = **0**, email sayısı 8994→8724 (tam eşleşme). Telefon/email newline taraması: 0 (temiz).
3. **Politika:** `03_kvkk_ve_veri_politikasi.md`'ye **§4.5 API Dağıtım Katmanı** bölümü (PII matrisi, iki anahtarlı maskeleme, müşteri senaryoları: deneme=maskeli / lisans=tam).
4. **Testler:** 6 yeni test (unit: maske fonksiyonları; API: mask=1 maskeli, default maskesiz, DB'de bireysel e-posta=0 kalıcı güvence).

**Canlı doğrulama:** maskesiz `'905542287200'`/`'info@akkor.com.tr'` → maskeli `'905***00'`/`'in***@akkor.com.tr'` ✅

**⚠️ Ek keşif (önemli):** Maske testi sayesinde ortaya çıktı — "dolu" görünen 4.636 e-posta (`'[]'`, `'null'` vb. JSON çöpü) ve 658 telefon çöp değerdi; `scripts/kvkk_cop_deger_temizle.py` ile NULL'landı (@-siz 3 email dahil). **Gerçek email doluluğu 8.724 değil ≈4.085 (%29).** Sonuç: kalite skorları email'i dolu sanan kayıtlar için yüksek hesaplanmış — **bir sonraki quality recalc'ta skorlar düşebilir** (doğru davranış; kalite ajanına not).



## 2026-09-09 — Web Sunucusu Süreklilik Çözümü (bağlantı kesilme fix)

**Sorun:** `http://127.0.0.1:8000/static/index.html` sık sık bağlantı kesilmesi veriyordu. Kök sebep: sunucu korumasız ön-planda çalışıyordu; process/terminal kapandığında servis ölüyordu.

**Çözüm (telegram bot'taki supervisor modeliyle aynı):**
- `scripts/web_server_task.bat` (YENİ): uvicorn'u sonsuz döngüde çalıştırır; çökerse 10 sn içinde yeniden başlatır, `logs/web_server.log`'a kaydeder.
- Startup kısayolu: `%APPDATA%\...\Start Menu\Programs\Startup\Huginn Web Server.lnk` → bilgisayar açılışında otomatik başlar. (Not: `schtasks /sc onlogon` yönetici izni istediği için kısayol yöntemi seçildi — telegram bot'ta da aynı yol kullanılmıştı.)
- **Dayanıklılık testi:** uvicorn bilerek öldürüldü (10:43:40) → 14 sn sonra `health=200` (otomatik toparlandı). ✅

**Ayrıca:** Y9 testleri yeniden koşuldu → **19 passed** (`tests/test_api_companies.py`, 22.6 sn, 0 fail).

## 2026-09-09 — DENET-4/5/6/7: Proje temizliği ve dosya düzeltme (done)

Kullanıcı onayı ile "yarım kalan temizlik/dosya düzeltme işleri" tamamlandı
(`AI proje v1/V10/07_referanslar/09_proje_denetimi_2026-09-09.md`):

**DENET-4 (geçici dosyalar):** `cop_kutusu_2026_09_09/DENET_arsiv_2026_09_09/`
altına taşındı — scripts geçici 19 dosya (`_tmp*`, `_probe*`, `_test*`,
`temp_match_stats.py`, `_fix_regex2.py`, `--help`), tests `_y9_sonuc*.txt` (3).
35MB `logs/ingest_ostim_detail.log` → gzip (0.65MB), orijinali kaldırıldı.
**DENET-5:** `C:\Projeler\Huginin Data Insights` (yazım hatası klasörü) yalnızca
1 bayt `scripts` içeriyordu, gerçek veri yok → klasör kaldırıldı.
**DENET-6:** `project_state.md` (doğru UTF-8) tek kaynak ilan edildi; mojibake'li
`project_state_iso.md`/`project_state_utf8.md` kopyaları arşivlendi (referans yok,
yalnızca `.obsidian/workspace.json` — o da yeni yolu gösteriyor).
**DENET-7:** Kök SQLite kopyaları (company_master.db, test.db = eski 8313 kayıt,
data/ankara_osb.db = 0B) arşivlendi; `backups/company_master_pre_dedup_*.db`
gerçek yedeği yerinde bırakıldı.
Pano: DENET-4/5/6/7 → done. Toplam **69/76** done. Gereksiz referans kontrolü:
hiçbir py/md/json `_iso`/`_utf8` e bağımlı değil; testler kırılmadı.

---
## 2026-09-09 — Y2 tamamlama: ETL/web_app parite + ASCII kalinti temizligi (done)

**Sorun:** `src/company_master/etl/normalize.py` ESKI ASCII sozlugu kullaniyordu
(TIC./STI./MUH. uretiyordu); web_app.py Y9'da Turkce kisaltmalara gecmisti. DB'de
kaynak bazinda ASCII kalinti: ostim 2452, ivedik 670, baskent 368 (toplam ~3.490).
API okumada web_app yeniden normalize ettigi icin Y9 testleri gizliyordu; ama
DB tuketicileri (change_notify, raporlar) ASCII kaliyordu.
**Cozum:** `etl/normalize.py` `web_app.normalize_company_name` / `extract_trade_name`
fonksiyonlarina delege ediyor (lazy import + ASCII yedek). Geriye donuk backfill:
14.000 firmanin **9.704'u** yeniden normalize edildi (yalnizca degisenler UPDATE).
ASCII kalinti -> **0**. Parite testi (etl == web_app) orneklerde OK.
change_notify baseline **14.000 firma** ile tazelendi (yanlis alarm onlendi).
Y9 testleri: **21 passed**.
**Ivedik notu:** raw `firmalar.jsonl` (3.354 satir) yalniz **14 benzersiz unvan**
iceriyor (ornek: "ALİ EŞREF ERKANİ" x224) — kaynak veri zayif; P1-1 (VPN engeli)
ile iliskili; dedup / tekrar scrape ayri gorev (P4-5). Baskent temiz (761 unique).
Pano Y2 -> done (63/69).

---

## 2026-09-09 — Telegram bot Scheduler + Y2: Ivedik/Baskent ingest (done)

**Bot Scheduler:** `schtasks` (admin) "ErIsIm engellendI" verdi; PowerShell
`Register-ScheduledTask` ile "Huginn Telegram Bot" kuruldu (ONLOGON, restart x3/1dk,
pille de calisir). `schtasks /query` -> Ready. Bot zaten calisiyordu (PID 8240,
baslama 01:53); yeni komutlar icin yeniden baslatma gerekiyor (polling Sureci eski
kodu tutuyor).
**Y2:** `source_records` 10105 -> `scripts/ingest_ivedik_baskent.py` (pipeline.py
deseni: content_hash dedup, ensure_source) `--count` once: ivedik 3134 + baskent 761
yeni. Yazildi: ivedik 3134 + baskent 761 -> source_records **14000**, sources 4.
Normalize on-kontrol: 2000 hamda bos unvan 0, ilk500 kucuk-harf sizinti 0.
`python -m company_master.etl.normalize`: once --only 5 (5/5), sonra tam **4768**.
Dagilim: ostim 9513, ivedik 3134, baskent 761, aso 592 = 14000; kucuk-harfli legal 0.
Pano Y2 -> done (63/69).

---

## 2026-09-09 — Y9: Web API Testleri (done) + Telegram komut aciklamalari

**Baslangic:** `tests/_y9_sonuc2.txt` (01:23) 1 fail / 36 pass: `test_ascii_kisaltma_kalintisi_yok`
`'AKSAM MOTOR ... TIC.LTD...'` kaydinda TIC. kalmis gorunuyordu. Suphe: `_tr_rx_key`
nokta-bitim bakisi `TIC.LTD.` bitisik zincirinde eslesmeyi engelliyordu.
**Kontrol:** normalize dogrudan testte `'AKSAM MOTOR VE DIS TIC.LTD.STI.'` ->
`'AKSAM MOTOR VE DIS TİC.LTD.ŞTİ.'` — TIC. donusmus (mechanizma OK).
`limit=500` probe: 500 kayitta ASCII kalinti **0**. Eski fail kaydi (limit=30, ilk sayfa)
su anki siralamada ilk 30'da degil — API `ORDER BY data_quality_score DESC` ama
test `limit=30` ile ilk sayfayi taradigi icin veri sirasi degisince fail kayboldu;
ayni kayit normalize sonrasi TIC. icermiyor.
**Bitis:** tam suit background job: **37 passed** (`tests/_y9_sonuc3.txt`). Pano Y9 -> done (62/69).
**Ek:** Telegram `/help` + `scripts/README_TELEGRAM.md` aciklamali hale getirildi;
`/degisiklik` `/gunluk` `/izleme` komutlari eklendi (change_notify motoru uzerinden).

---

## 2026-09-09 — Y14: Degisiklik Bildirimi (done)

**Baslangic:** Telegram altyapisi vardi (`telegram_bot.py` send_message,
`telegram_polling.py` komutlar, 09:00 daily rapor) ama Y14'un istedigi
"yeni firma / skor degisimi" tetiklemeli bildirim yoktu.
**Bitis:** `scripts/change_notify.py` (YENI) + `change_notify_task.bat` + Scheduler gorevi.
- Snapshot: `data/orchestrator/change_notify_state.json` (company_id -> ad+skor).
- Modlar: `--baseline` (izleme baslat) / `--check` (degisiklikte bildir, yoksa sessiz)
  / `--daily` (gunluk ozet) / `--no-send` (kuru test).
- Mesaj turleri: yeni firma listesi, skoru esigi asan (±10) degisimler, silinen kayit sayisi.
- Dogrulama: unit senaryo (1 yeni + 1 silinen + 1 skor degisimi) OK; baseline 9.227 firma;
  `--check --no-send` "Degisiklik yok"; gercek `--daily` Telegram'a ulasti (OK).
- Scheduler: "Huginn Change Notify" her gun 08:00 (backup 03:00 sonrasi).

---

# Huginn — Çalışma Günlüğü (İş Notları)

> Her görev için: başlangıç notu → yapılan iş → bitiş notu.
> Görev panosu: `data/orchestrator/task_board.json`

---

## 🟦 GÖREV 1 — P4-6: Backup/Restore Otomasyonu
**Tarih:** 2026-09-08 | **Sahip:** devops | **Başlangıç durumu:** plan

### Başlangıç Notu
- DB: PostgreSQL (Supabase, `aws-0-eu-west-2.pooler.supabase.com`)
- **pg_dump / psql YOK** (Windows'ta kurulu değil) → Python tabanlı export gerekiyor
- `backups/` klasöründe 2026-09-02 tarihli 2 eski `.sql.gz` yedeği var (nasıl alındığı belirsiz)
- Risk: P4-5 (duplicate temizleme) yıkıcı bir işlem → **önce yedek altyapısı kurulmalı**

### Yapılan İş
1. **`scripts/backup_db.py`** — pg_dump gerektirmeyen yedekleyici:
   - SQLAlchemy inspector ile tüm tabloları CSV olarak export eder (22 tablo)
   - `manifest.json` içerir: tarih, maskeli DB URL, kolon şemaları, satır sayıları
   - `--keep N` retention (eski yedekleri siler), `--list` ile mevcut yedekleri listeler
2. **`scripts/restore_db.py`** — geri yükleme:
   - `--dry-run` (içerik gösterir, değişiklik yapmaz), `--drop` (tabloyu düşürüp kurar — yıkıcı)
   - Şema bilgisi manifest'ten; SQLite/PostgreSQL tip dönüşümü yapar
3. **`scripts/backup_task.bat`** + **Windows Task Scheduler görevi "Huginn DB Backup"**
   - Her gün 03:00, `--keep 7`, log: `logs/backup.log`
   - İptal için: `schtasks /Delete /TN "Huginn DB Backup" /F`

### Doğrulama
- ✅ Yedek: `backup_20260908_084933.zip` — 22 tablo, 28.349 satır, 2.97 MB
- ✅ Restore dry-run: manifest okuma ve tablo listeleme başarılı
- ✅ Batch uçtan uca: `backup_20260908_085122.zip` + `logs/backup.log` yazıldı
- ✅ Scheduler: `\Huginn DB Backup` → Ready, sonraki çalışma 09.09.2026 03:00

### Bitiş Notu
**done.** pg_dump yokluğuna rağmen tam otomatik yedekleme kuruldu. P4-5 (yıkıcı dedup işlemi) artık güvenli — yedek garanti altında.

---

## 🟦 GÖREV 2 — P4-5: Veri Seti Doğrulama ve Duplicate Temizleme
**Tarih:** 2026-09-08 | **Sahip:** data | **Başlangıç durumu:** plan

### Başlangıç Notu
- Önceki yedek: `backup_20260908_085122.zip` (geri dönüş garantisi var)
- DB: PostgreSQL (Supabase). `companies` 9.319, `source_records` 10.105, `entity_resolution` 8.905 satır
- Plan: (1) duplicate analizi → (2) rapor → (3) temizlik stratejisi → (4) uygulama + doğrulama

### Yapılan İş
- `scripts/dedup_apply.py`: dry-run/--apply, tek transaction, audit CSV
- Eşleştirme: company_id + kanonik unvan bazlı; **92 duplicate silindi**
- Sonuç: `companies` 9.319 → **9.227**; ardından kalite yeniden hesabı ortalama **22.66 → 64.04** (`quality_recalc_fast.py`, set-based)

---

## 2026-09-09 — Docker Konteynerleştirme Faz 1 (altyapı hazırlığı)

**Tespit:** Docker CLI 29.7.2 + Compose v5.5.1 kurulu; ancak **WSL2 kurulumu bozuk**
(`Wsl/CallMsi/Install/REGDB_E_CLASSNOTREG`) → Docker Linux engine 500 dönüyor.
Eski Dockerfile/compose eski sürümden kalmaydı: Streamlit çağırıyor, `test.db`
mount ediyordu, **`.dockerignore` yoktu (`.env` image'e girecekti!)**, psycopg
requirements'ta eksikti.

**Faz 1 (bu oturum, engine'siz tamamlandı):**
- `Dockerfile`: python:3.12-slim, HEALTHCHECK, non-root, yalnız curl
- `.dockerignore` (YENİ): `.env`, `backups/`, `AI proje v1/`, `__pycache__` image dışı
- `docker-compose.yml` yeniden yazıldı: `api` (ana servis), `db` postgres:16-alpine
  (profile: `localdb`, host port 5433), streamlit/scraper/healthcheck/telegram-bot
  (profile: `legacy`) — `docker compose config` → **OK**
- `requirements-app.txt`: `psycopg[binary]` eklendi (API psycopg3 kullanıyor)
- `.env.example` (YENİ): şablon değişkenler

**Faz 2 (bekliyor — kullanıcı admin onayı):** WSL2 onarımı:
`wsl --install --no-distribution` (yönetici PowerShell) + yeniden başlatma →
Docker Desktop restart → `docker compose build api` → `/api/health` doğrulama.
**Faz 3:** `--profile localdb` ile yerel PG ayağa kaldır, `backup_db.py` dump'ını
`restore_db.py` ile yükle → Y9 testleri + P4-4 EXPLAIN ANALYZE pooler timeout'suz koşar.