# 🤖 MASTER AGENT DIRECTIVE: BULUT TAŞINMA VE AI EKOSİSTEM KURULUMU (REVİZE)

**Kullanıcı Rolü:** Sistem Mimarı ve Baş Geliştirici orkestratörsün
**Ajan Rolü:** Senior DevOps & Python AI Engineer (Sistem Kurulum ve Optimizasyon Uzmanı)

> **Revizyon kaydı (2026-10-01, İhsan/orkestratör):** Bu metin Ürün Sahibi'nin temel çalışmasıdır; repo ölçülerek düzeltildi. Değişen her madde `ÖLÇÜM:` ile, doğrulanamayan her madde `Varsayım:` ile işaretlidir. Orijinal metnin değiştirilmeyen bölümleri aynen korundu. Pano (`task_board.json`) bu revizyonla **değiştirilmedi**; görev listesi yalnızca bu belgede plandır, atama yoktur.

> **Taşınma notu (2026-10-01):** Dosya kökteki `tasinma-rehberi-v3.md`'den buraya taşındı (D-221 kök izin listesi: kökte plan belgesi duramaz; D-183 ad kuralı: `bulut_tasinma_rehberi`). Kökte yalnız 2 satırlık yönlendirme stub'ı kaldı; gövde tek yerde (D-211/D-212). Pano kontrol bulguları en altta "Pano kontrolü" bölümünde.

---

## 🚨 KRİTİK NOT 0 — İŞLETİM SİSTEMİ KARARI HÂLÂ BELİRSİZ (Karar sahibi: Ürün Sahibi)

Rehberin iki gövdesi birbiriyle çelişiyor: üst kısım **Windows Server** (~31 €/ay, +6 € lisans), alt kısım (V2 profili) **Ubuntu** (25,50 €/ay). Karar verilmeden Adım 2'den (runtime kurulumu) sonrası başlatılamaz.

| Ölçüt | Windows Server | Ubuntu + XFCE4/XRDP |
|---|---|---|
| Aylık maliyet | ~31 € | 25,50 € |
| OS boşta RAM | 3–4 GB + WSL2 katmanı | ~0,3 GB (XFCE) |
| Docker | Docker Desktop + WSL2 (`.wslconfig` 34 GB) | docker-ce, native; `.wslconfig` **gereksiz** |
| Repo scriptleri | `.bat`/`.ps1` olduğu gibi çalışır (`scripts/backup/setup_backup_scheduler.ps1`, `scripts/backup_task.bat`, `scripts/change_notify_task.bat`, `scripts/SETUP_TASK_SCHEDULER.bat`) | 4 Windows scripti → `sh` + cron'a çevrilir; `scripts/db_migrate_prod.sh` zaten var |
| D-86 (Windows cmd kuralı) | Geçerli | Vault AGENTS.md'ye Linux eki gerekir (KAHİN kararı) |
| Uzak masaüstü | RDP yerleşik / AnyDesk | XRDP (3389) |
| Obsidian | Windows kurulum | AppImage |

**Karar bekleniyor.** Bu belgedeki tüm adımlar OS-nötr yazıldı; OS'ye özgü farklar `[WIN]` / `[UBU]` etiketleriyle verildi. Orkestratör önerisi: Ubuntu (daha ucuz, Docker native, RAM boşa gitmez); bedeli 4 scriptin çevrilmesi ve D-86 eki.

---

## 🎯 ANA GÖREV VE BAĞLAM
Bu sunucudaki (Contabo Cloud VPS 12 - 12 vCPU, 48 GB RAM, 400 GB SSD) görevin; yerel bilgisayardaki tüm AI geliştirme ortamını, konuşma geçmişlerini, Obsidian bilgi tabanını, Python kazıma altyapısını ve Docker ekosistemini (n8n, 9router, PostgreSQL) sıfır veri kaybı ve maksimum performans ile kurmaktır.

Aşağıdaki teknik parametreler, kurallar ve iş adımları bu sunucudaki **tek gerçeğindir (SSOT)**; ancak repo ile çelişen her yerde **repo kazanır** (D-223: vault tek otorite).

NOT:
BU DOKUMAN URUN SAHİBİNİN TEMEL CALISMASIDIR ORKESTRATOR TUM SURECİ YONETİR VE GEREKLİ DEGISIKLIKLERI ARASTIRIP SISTEM DOSYALARINA BAKAR PLANLAR VE GEREKLI DEGISIKLIKLERI YAPARAK YENI AMA BAGLANTILI BIR PLAN HAZILAYABILIR
AMAC EKSİKSİZ VE KAYIPSIZ SUNUCU DEGISIMIDIR TUM DETAYLAR TOPLANMALI VE NIHAI REPO ILE ESLETIRILMELI KARSILASTIRILMALI VARSA EKSIKLER GIDERLIMELIDIR URUN SAHIBI REPONUN TAM KAPASITEILE TASINMASINI ISTEMEKTEDIR TUM DETAYLAR VE ALTYAPILAR GITHUB YAPILANDIRMASI GOZDEN GECIRILMELI DOKER ORGANIZE EDILMELI VE YEREL YEDEKLER ALINMALIDIR
1. GEREKLİ GEREKSİZ GÖRDÜĞÜN TÜM KLASÖRLER TAŞINABİLİR C://Huginn Data Projesi TAMAMI
2. AJAN KONUŞMALARI BAĞLAMLAR GÖREVLER WORKTREELER KONUŞMA GEÇMİŞLERİ TAŞINIP YENİ SUNUCUDA KURULACAK
3. REPO DIŞI TÜM AYARLAR 9ROUTER OBSİDYEN VS NE VARSA TAŞINSIN
4. TÜM AKTİF SON KOPYA REPO DIŞINDA PROJEYEDEK KLASORUNDE SAKLANSIN
5. SUNUCU KİRALANDIKTAN SONRA UZAK BAĞLANTI KURULARAK SUNUCU GEREKSİNİMLERİ AYARLARI YAPILARAK TAŞIMA YAPILSIN ÖN ENTEGRASYON YAPILSIN
6. GEREKLİ SKİLLER İNTERNETEN İNDİRİLSİN ORAK SKİL KLASORUNDE KULLANIMA AÇILSIN
7. ORKESTRÖR GEREKLİ GÖRDÜGÜNDE KONULARA MÜDAHALE EDEBİLSİN VEYA DOĞRU YOLU GÖSTERSİN ÖNERİLERDE BULUNSUN

---

## 📏 ÖLÇÜM BULGULARI — REHBER vs REPO (düzeltmelerin gerekçesi)

| # | Rehber (eski) | Repo (ölçülen) | Karar |
|---|---|---|---|
| 1 | DB `ai_core_platform` / `dev_ai_user` / `postgres:15-alpine` / `127.0.0.1:5432` | `Huginn Data Insights/docker-compose.yml`: `postgres:16-alpine`, `POSTGRES_DB: huginn`, `POSTGRES_USER: huginn`, `${LOCAL_PG_PASSWORD}`, port `5433:5432`, profil `localdb`. `.env.example`: üçüncü kimlik `postgres:password@localhost:5432` | **Tek kimlik: `huginn`/`huginn`, PG 16, `127.0.0.1:5433`.** PG 15 YASAK (16 dump → 15 restore başarısız). Şifre yalnız `.env` (D-73). Rehberdeki düz-metin şifre yanmış sayılır, kullanılmaz. |
| 2 | 9Router `9router/9router:latest`, port 8080 | Kod `NINEROUTER_URL` varsayılanı `http://localhost:20128` (`src/company_master/gateway/ninerouter_client.py`, `skills/services/ninerouter.py`, testler). Anahtar env adı **`NINEROUTER_KEY`**; `.env.example` yanlışlıkla `NINEROUTER_API_KEY` yazıyor | Host portu **20128**. Image adı `Varsayım:` doğrulanmadı; alternatif: Node ile native (`npx 9router`). `.env.example` düzeltilecek (TASIMA-004). |
| 3 | n8n aynı DB'yi (`ai_core_platform`) kullanır | Şema tek anlatıcı `goc_defteri.py` (D-251/D-265); n8n kendi tablolarını yazarsa defter drift verir | n8n **ayrı veritabanı** `n8n` (aynı Postgres, `createdb -U huginn n8n`). |
| 4 | Obsidian kasası `C:\Proceler\Obsidian-Kasa\` | Kasa = `Huginn Data Insights/` (repo içi), `.obsidian/` kökte (D-223/D-169) | Kasa repodan ayrılmaz; Obsidian'a repo klasörü hedef gösterilir. |
| 5 | Playwright + Browserless (3000) + residential proxy | Repo'da `playwright`/`browserless`/`connect_over_cdp` **0 sonuç**. Bağımlılıklar `requests`, `beautifulsoup4`, `rapidfuzz` (`requirements-app.txt`). D-310 Katman 4 (robots/rate-limit) + sıfır-maliyet kararı | Residential proxy **reddedildi** (ücretli + D-310). Browserless compose'da `profile: browser` olarak **uykuda** durur; SCRAPE-002 LLM-less yolu birincil. |
| 6 | `yedekle.bat` + `pg_dumpall` + xcopy | `scripts/backup/pg_backup.py` (pg_dump -Fc + .sql.gz), `pg_restore.py`, `pg_cleanup.py --days 30 --keep 14`, `setup_backup_scheduler.ps1` (**`C:\Projeler\...` hardcoded**), `scripts/supabase_backup.py`, `scripts/backup_db.py` (CSV zip) | `yedekle.bat` **yazılmaz**; mevcut scriptler kullanılır. Yol çatışması `C:\Proceler` vs `C:\Projeler` tek yola indirilir. |
| 7 | Compose 5 servis (NPM, postgres, n8n, 9router, browserless) | Repo compose: `app` (8000), `db`, `dashboard` (8501), profil `jobs`, profil `telegram` | Rehber compose'u repo compose'un **yerine geçmez, üstüne gelir**: `docker-compose.sunucu.yml` override dosyası. |
| 8 | Supabase geçişi anlatılmamış | `scripts/supabase_backup.py` var | TASIMA-001'de Supabase export zorunlu. |
| 9 | Restore sonrası şema doğrulaması yok | D-253: defter kaydı kanıt değildir | Restore → `python scripts/goc_defteri.py` eşitle → COUNT karşılaştırma. |
| 10 | Ajan hafızası: yalnız Cursor + Roo | Kökte `.kilo/` (backups, worktrees), `.roo/`, `.continue/`, `.agents/skills/`, `.kombai/`, `.n8nac/`; `data/orchestrator/task_board.json`, `logs/` | Tam liste Bölüm 2'de. |
| 11 | n8n iş akışları anlatılmamış | `n8nac-config.json`: instance `huginn-data`, proje `huginn-muninn`, `workflowsPath: workflows/huginn-muninn` | TASIMA-007: `npx --yes n8nac env status --json` → push. |
| 12 | Zamanlayıcı yeniden kaydı yok | 3 bat + 1 ps1 kayıt scripti | TASIMA-008. |

---

## ⚙️ KESİN TEKNİK PARAMETRELER (REVİZE)
*   **PostgreSQL:** image `postgres:16-alpine`, DB `huginn`, kullanıcı `huginn`, şifre **yalnız `.env` → `LOCAL_PG_PASSWORD`** (bu belgeye yazılmaz, D-73).
*   **Host portu:** `127.0.0.1:5433` → konteyner 5432. `DATABASE_URL=postgresql://huginn:${LOCAL_PG_PASSWORD}@localhost:5433/huginn`.
*   **n8n DB:** `n8n` (aynı sunucu, aynı kullanıcı).
*   **9Router:** `NINEROUTER_URL=http://localhost:20128`, `NINEROUTER_KEY=<.env>`.
*   **[WIN] WSL2 `.wslconfig`:** `memory=34GB`, `processors=8`. **[UBU]** yok; Docker native.
*   **Repo kök yolu (tek):** `[WIN] C:\Projeler\Huginn Data Projesi\` · `[UBU] /opt/huginn/Huginn Data Projesi/`. Vault: `<kök>/Huginn Data Insights/`. `setup_backup_scheduler.ps1` satır 11 bu yola güncellenir.
*   **Yedek dizini:** `[WIN] C:\SunucuYedekleri` · `[UBU] /var/backups/huginn` (D-229: zaman damgalı yedek git'te izlenmez).

---

## 🔒 GÜVENLİK VE PORT KISITLAMA (REVİZE)
1.  **PostgreSQL `5433`:** yalnız `127.0.0.1`.
2.  **9Router `20128`:** yalnız `127.0.0.1`; dış erişim gerekirse NPM üzerinden.
3.  **Nginx Proxy Manager `81`:** yalnız `ssh -L 8181:127.0.0.1:81` tüneli.
4.  **n8n `5678`:** yalnız `127.0.0.1`; dışarıya NPM + Let's Encrypt.
5.  **app `8000` / dashboard `8501`:** yalnız `127.0.0.1`; dışarıya NPM (opsiyonel).
6.  **browserless `3000`:** profil `browser` açılmadıkça konteyner yok.
7.  **`.env` asla taşınmaz; yeniden üretilir** ve tüm anahtarlar döndürülür (D-73/D-74). Rehberin eski sürümündeki düz-metin şifre geçersizdir.

---

## 📋 ADIM ADIM İŞ PLANI (OS-NÖTR)

### Adım 0: OS kararı (Ürün Sahibi) — kapı
Karar yoksa Adım 2'den ileri gidilmez.

### Adım 1: Yerel yedek paketi (PROJEYEDEK) — sunucu kiralanmadan önce
Bölüm 2'deki liste; `sha256` manifesti; `pg_backup.py` çıktısı dosya olarak kanıt (D-244).

### Adım 2: Runtime
*   `[WIN]` Servis temizliği → `wsl --install` → Docker Desktop (WSL2 motoru) → `.wslconfig` → `wsl --shutdown`.
*   `[UBU]` `apt install docker-ce docker-compose-plugin` → kullanıcıyı `docker` grubuna al → XFCE4 + XRDP (Bölüm 11).
*   Her iki OS: OpenSSH Server, `.ssh/config` `Host contabo-ai`.

### Adım 3: Repo + ajan hafızası aktarımı
`git clone` (iki ayrı repo var — D-255/1: dış kök ve vault) + hafıza dizinleri (Bölüm 2) + `.env` yeniden üret.

### Adım 4: Docker ekosistemi
`docker compose -f docker-compose.yml -f docker-compose.sunucu.yml --profile localdb up -d` (Bölüm 4). Ardından `docker exec <db> createdb -U huginn n8n`.

### Adım 5: DB geri yükleme + şema eşitleme
`python scripts/backup/pg_restore.py <dosya>` → `python scripts/goc_defteri.py` (eşitle) → `SELECT COUNT(*) FROM companies` eski = yeni.

### Adım 6: n8n + 9Router entegrasyonu
`npx --yes n8nac env status --json` → `workflowsPath` doğrula → push. 9Router config dizini + `NINEROUTER_KEY`. `curl http://localhost:20128/v1/models` yanıt verir.

### Adım 7: Zamanlayıcılar + ilk gece yedeği
`[WIN]` `setup_backup_scheduler.ps1`, `backup_task.bat`, `change_notify_task.bat`, `SETUP_TASK_SCHEDULER.bat`. `[UBU]` aynı komutlar cron'a (`0 3 * * *`). Ertesi sabah yedek dosyası kanıt.

### Adım 8: Kabul
Bölüm 9 kriterleri yeşil → Supabase kapatma kararı Ürün Sahibi'ne sunulur.

### Adım 9: Kazıma (ayrı hat, SCRAPE-001..007)
Playwright testi **yerine** SCRAPE-002 LLM-less (requests+bs4) ilk 5 firma — Bölüm 8.

---

## 🧭 GÖREV LİSTESİ — PLAN (ATAMA YOK, PANOYA YAZILMADI)

Durum: tümü `planned`, `sahip: —`. Panoya aktarım ancak Ürün Sahibi onayı + D-57 başlık + D-217 brif ile (orkestratör işi, D-77).

### Taşıma hattı

| ID | Başlık (D-57 taslak) | Dosyalar | Bağımlılık | Kabul kanıtı |
|---|---|---|---|---|
| TASIMA-000 | [KARAR] OS seçimi: Windows Server / Ubuntu | bu belge | — | Ürün Sahibi yazılı kararı; AGENTS.md D-NN |
| TASIMA-001 | [YEDEK] PROJEYEDEK paketi: git bundle + pg_backup + supabase_backup + ajan hafızası + sha256 manifest | `scripts/backup/pg_backup.py`, `scripts/supabase_backup.py`, Bölüm 2 listesi | — | manifest dosyası + `pg_restore --list` çıktısı |
| TASIMA-002 | [SUNUCU] Contabo VPS 12 kiralama + SSH anahtarı + uzak masaüstü + OpenSSH | `~/.ssh/config` | TASIMA-000 | `ssh contabo-ai` çalışır |
| TASIMA-003 | [RUNTIME] Docker kurulumu ([WIN] WSL2+Desktop+.wslconfig / [UBU] docker-ce) | `.wslconfig` (yalnız WIN) | TASIMA-002 | `docker info` RAM limiti görünür |
| TASIMA-004 | [REPO] Clone + hafıza dizinleri + `.env` yeniden üretim + `.env.example` `NINEROUTER_API_KEY→NINEROUTER_KEY` düzeltmesi | `.env.example`, `.kilo/`, `.roo/`, `.continue/`, `.agents/skills/` | TASIMA-003 | `git status` temiz; `.env` git'te yok |
| TASIMA-005 | [DOCKER] `docker-compose.sunucu.yml` override: NPM + n8n (ayrı DB) + 9router + browserless(uyku) | `Huginn Data Insights/docker-compose.sunucu.yml` | TASIMA-004 | `docker compose ps` 5+ servis healthy; 81/5433/20128 yalnız localhost |
| TASIMA-006 | [DB] pg_restore + goc_defteri eşitle + COUNT eşitliği | `scripts/backup/pg_restore.py`, `scripts/goc_defteri.py` | TASIMA-005 | `goc_defteri.py` 0 fark; COUNT eski=yeni |
| TASIMA-007 | [ENTEGRASYON] n8nac push + 9Router config + Let's Encrypt | `n8nac-config.json`, `workflows/huginn-muninn/` | TASIMA-005 | `n8nac env status` OK; `https://n8n.<alan>` 200 |
| TASIMA-008 | [OPS] Zamanlayıcı kayıtları + yol düzeltmesi (`setup_backup_scheduler.ps1`:11) + ilk gece yedeği | 3 bat + 1 ps1 / crontab | TASIMA-006 | Ertesi gün yedek dosyası |
| TASIMA-009 | [KABUL] pytest + COUNT + defter + erişim + Supabase kapatma önerisi | `tests/` | TASIMA-007, TASIMA-008 | Bölüm 9 tablosu yeşil; rapor Ürün Sahibi'ne |

### Kazıma hattı (panoda zaten `planned`, burada yalnız referans + bağ)

| ID | Başlık | Bu belgeyle bağ |
|---|---|---|
| SCRAPE-001-DOCKER-SETUP | PostgreSQL 16 + kazıma servisi → compose; migration 0046 | **TASIMA-005 ve TASIMA-006'dan sonra** (aynı compose/db) |
| SCRAPE-002-LEMMLESS-ANKARA-OSB | LLM-less: ostim/ivedik/baskent → scrape_pages | Eski Adım 6'nın (Playwright) yerini alır |
| SCRAPE-003-9ROUTER-JINA-FALLBACK | 9Router jina-reader fallback | 9Router 20128 (TASIMA-007) |
| SCRAPE-004-QWEN-SINIFLANDIRMA | Qwen local sınıflandırma | 9Router 20128 |
| SCRAPE-005-KAZIMA-DOCKER-INTEGRATION | kazima servisi, profile jobs, cron | TASIMA-008 zamanlayıcıyla aynı mekanizma |
| SCRAPE-006-QUALITY-AUDIT | D-250 + D-310 denetim | — |
| SCRAPE-007-FINAL-REPORT | dönem sonu raporu | — |

`Varsayım:` SCRAPE kayıtlarındaki `sahip` değerleri (devops/web-engineer/qa) kanonik ajan adı değildir; panoya dokunulmadı, onayla temizlenecek.

---

## 📦 BÖLÜM 1: GÜNCEL SUNUCU VE LOKASYON BİLGİLERİ
* Firma: Contabo · Paket: Cloud VPS 12 · 12 vCPU, 48 GB RAM, 400 GB SSD, 800 Mbit/s · Lokasyon: Germany.
* OS: **Karar bekliyor (Kritik Not 0).** Windows ~31 €/ay · Ubuntu 25,50 €/ay. Yıllık taahhütte kurulum ücreti muafiyeti (`Varsayım:` güncel kampanya doğrulanmalı).

---

## 🛠️ BÖLÜM 2: YEREL VERİ VE AI BAĞLAMLARININ TOPLANMASI (TAM LİSTE)

### 1. Repo ve vault
* `C:\Huginn Data Projesi\` tamamı — iki git deposu: dış kök + `Huginn Data Insights/` (D-255/1). Her ikisi için `git bundle create` + `git status` temiz kanıtı.
* `.obsidian/` (kökte) — tema/eklenti ayarları.

### 2. Ajan hafızası (repo içi, kökte)
`.kilo/` (backups/, backups_arşiv/, worktrees/, skills/), `.roo/skills/`, `.continue/`, `.agents/skills/` (9Router upstream + `huginn-web-kazima`), `.kombai/`, `.n8nac/`, `.vscode/`, `.github/`, `Huginn Data Insights/data/orchestrator/` (task_board.json, onay_kuyrugu.json, chat logları), `Huginn Data Insights/logs/`.

### 3. Ajan hafızası (repo dışı, kullanıcı profili)
* Cursor: `%APPDATA%\Cursor` (User\workspaceStorage, User\globalStorage) + `%USERPROFILE%\.cursor`
* VS Code eklenti depoları: `%APPDATA%\Code\User\globalStorage\` altındaki **tüm** `*.roo-cline`, `*.kilo-code`, `*continue*` klasörleri (`Varsayım:` yayıncı kimliği rehberdeki `roovet.roo-cline` olmayabilir; `dir` ile ölç, tahmin etme).
* VS Code ayarları: Settings Sync (GitHub) açık.
* `%USERPROFILE%\.agents\skills\` (küresel skill'ler, `.manifest.json` dahil).
* 9Router config dizini (`Varsayım:` yolu kurulum şekline bağlı; `9router_optimizer.py --backup` çıktısı ile ölç).

### 4. Veritabanları
* Yerel Postgres: `python scripts/backup/pg_backup.py` → `.dump` + `.sql.gz` (kanıt dosyası, D-244).
* Supabase: `python scripts/supabase_backup.py` → `backups/supabase_*.sql.gz`.
* SQLite test dosyaları varsa `yedekler/sqlite/` (D-242 tek çatı).

### 5. Sırlar
`.env` **taşınmaz**; anahtar listesi (adlar, değerler değil) not alınır; sunucuda yeni değerler üretilir (D-73).

---

## 🖥️ BÖLÜM 3: SUNUCU İLK KURULUM (OS'YE GÖRE)

### [WIN] Windows Server
1. Gereksiz servisler kapatılır (Xbox, telemetri, yazdırma).
2. AnyDesk/RustDesk + OpenSSH Server; Cursor/VS Code Remote-SSH.
3. `wsl --install` → yeniden başlat → Docker Desktop (WSL2 motoru).
4. `C:\Users\Administrator\.wslconfig`:
   ```ini
   [wsl2]
   memory=34GB
   processors=8
   ```
5. `wsl --shutdown`.

### [UBU] Ubuntu
Bölüm 11 (XFCE4 + XRDP) + `docker-ce`; `.wslconfig` yok, RAM sınırı compose `deploy.resources` ile.

---

## 🚀 BÖLÜM 4: DOCKER EKOSİSTEMİ — REPO COMPOSE'UN ÜSTÜNE OVERRIDE

Repo compose (`Huginn Data Insights/docker-compose.yml`: app, db, dashboard, jobs, telegram) **değişmez**. Yanına `docker-compose.sunucu.yml`:

```yaml
# Huginn Data Insights/docker-compose.sunucu.yml — yalnız sunucuda, repo compose ile birlikte
services:
  db:
    ports:
      - "127.0.0.1:5433:5432"      # ÖLÇÜM: repo zaten 5433; burada localhost'a kilitlenir
  app:
    ports:
      - "127.0.0.1:8000:8000"
  dashboard:
    ports:
      - "127.0.0.1:8501:8501"

  nginx-proxy-manager:
    image: jc21/nginx-proxy-manager:latest
    restart: always
    ports:
      - "80:80"
      - "443:443"
      - "127.0.0.1:81:81"
    volumes:
      - npm_data:/data
      - npm_letsencrypt:/etc/letsencrypt

  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    restart: always
    ports:
      - "127.0.0.1:5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=db
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n            # ÖLÇÜM: ayrı DB (D-251 drift önlemi)
      - DB_POSTGRESDB_USER=huginn
      - DB_POSTGRESDB_PASSWORD=${LOCAL_PG_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - WEBHOOK_URL=https://${N8N_HOST}/
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - db

  9router:
    image: 9router/9router:latest             # Varsayım: image adı doğrulanmadı; yoksa native `npx 9router`
    restart: always
    ports:
      - "127.0.0.1:20128:20128"               # ÖLÇÜM: kod varsayılanı 20128
    volumes:
      - ./9router/config:/app/config

  browserless:                                # uykuda: yalnız --profile browser ile kalkar
    image: browserless/chrome:latest
    profiles: ["browser"]
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - MAX_CONCURRENT_SESSIONS=5
      - CONNECTION_TIMEOUT=60000

volumes:
  npm_data:
  npm_letsencrypt:
  n8n_data:
```

Başlatma:
```bash
cd "<kök>/Huginn Data Insights"
docker compose -f docker-compose.yml -f docker-compose.sunucu.yml --profile localdb up -d
docker compose exec db createdb -U huginn n8n     # bir kez
```

`.env` ek anahtarlar: `LOCAL_PG_PASSWORD`, `N8N_HOST`, `NINEROUTER_URL=http://localhost:20128`, `NINEROUTER_KEY`.

### 🔒 NPM paneli (81)
`ssh -L 8181:127.0.0.1:81 <kullanıcı>@<IP>` → `http://127.0.0.1:8181` (ilk giriş admin@example.com / changeme → hemen değiştir).

### 🌐 Alan adı + Let's Encrypt
A kaydı `n8n` → sunucu IP. NPM: Proxy Host `n8n.<alan>` → `n8n:5678`, Block Common Exploits, SSL: Request new, Force SSL, HTTP/2.

---

## 🐍 BÖLÜM 5: PYTHON, NODE.JS, OLLAMA
* Python 3.11+ (PATH), `pip install --upgrade pip setuptools wheel virtualenv`; repo: `pip install -r requirements-app.txt`.
* Node.js LTS; `npm i -g n8nac` (AGENTS.md: npx başlangıç maliyetini kaldırır), `npm install -g @anthropic-ai/claude-code`.
* Ollama: `[WIN]` Windows kurulum · `[UBU]` `curl -fsSL https://ollama.com/install.sh | sh`; `ollama run llama3`. 9Router local model yolu SCRAPE-004 için.

---

## 📝 BÖLÜM 6: OBSIDIAN
Obsidian kurulur; kasa olarak **`<kök>/Huginn Data Insights/`** gösterilir (ayrı `Obsidian-Kasa` dizini **yok**, D-223). `.obsidian/` repodan gelir. Local REST API eklentisi opsiyonel; anahtarı `.env`'e.

---

## ⚡ BÖLÜM 7: IDE PERFORMANS (değişmedi)
Search/Watcher Exclude: `**/.git`, `**/node_modules`, `**/venv`, `**/.docker`, `**/postgres_data`, ek: `**/.kilo/backups*`, `**/yedekler`. Roo/Kilo bağlam limiti sınırlanır.

---

## 🕷️ BÖLÜM 8: WEB KAZIMA — SIFIR MALİYET, LLM-LESS ÖNCE (REVİZE)

Eski Playwright + Browserless + residential proxy şablonu **kaldırıldı**:
* ÖLÇÜM: repoda Playwright kullanımı yok; mevcut hat `requests` + `beautifulsoup4`.
* Residential proxy ücretlidir ve D-310 Katman 4 (robots.txt/rate-limit) ile çelişir → **reddedildi**.
* Browserless, profil `browser` altında uykuda; yalnız JS-render zorunlu bir kaynak ölçülürse ve Ürün Sahibi onaylarsa açılır (`ENABLE_PAID_FALLBACK=0` korunur).

Kazıma sırası ve kuralları: [[.agents/skills/huginn-web-kazima/SKILL]] · [[Huginn Data Insights/plans/2026-10-01_kazima_verimlilik_ve_eksiklik_analizi]] · SCRAPE-002 → 003 → 004.

İlk sunucu testi (eski Adım 6'nın yerine): `python scripts/kazima_ostim.py --limit 5` → `SELECT COUNT(*) FROM scrape_audit_log WHERE source_name='ostim.org.tr'` ≥ 1 (SCRAPE-001/002 tamamlandıktan sonra).

---

## 💾 BÖLÜM 9: YEDEKLEME + KABUL KRİTERLERİ (REVİZE)

`yedekle.bat` **yazılmaz**. Mevcut araçlar:

| İş | Komut | Zamanlama |
|---|---|---|
| Postgres dump | `python scripts/backup/pg_backup.py` | gece 03:00 (`setup_backup_scheduler.ps1` / cron) |
| Dump temizliği | `python scripts/backup/pg_cleanup.py --days 30 --keep 14` | aynı iş |
| Kilo yedek rotasyonu | `scripts/SETUP_TASK_SCHEDULER.bat` (Pazartesi 03:00) | mevcut |
| Supabase (geçiş dönemi) | `python scripts/supabase_backup.py` | geçiş bitene kadar |
| Hafıza dizinleri (Bölüm 2/2–3) | `robocopy /MIR` (WIN) · `rsync -a --delete` (UBU) → yedek dizini | aynı iş |

Yedekleme komutlarına **Bölüm 2/2–3 hafıza dizinleri** eklenmesi tek açık iş (TASIMA-008). Yedek git'te izlenmez (D-229).

### Kabul kriterleri (TASIMA-009)
| Kriter | Kanıt |
|---|---|
| `SELECT COUNT(*) FROM companies` eski = yeni | iki çıktı yan yana |
| `python scripts/goc_defteri.py` fark 0 | komut çıktısı |
| `pytest` yeşil | özet satırı |
| `npx --yes n8nac env status --json` OK + iş akışları push edilmiş | JSON çıktı |
| `curl localhost:20128/v1/models` 200 | çıktı |
| Dış ağdan 5433/81/20128/5678 kapalı | `nmap`/`Test-NetConnection` |
| İlk gece yedeği dosya olarak var | `ls` çıktısı |

---

## 💡 BÖLÜM 10: ÖNERİLER VE KISAYOLLAR (değişmedi)
* İmajlar `python:3.12-slim` (repo Dockerfile ile uyumlu).
* `[WIN]` `wsl free -h --giga` · `docker compose up -d --no-deps --build <servis>`.
* `.ssh/config`:
  ```text
  Host contabo-ai
      HostName SUNUCU_IP
      User Administrator        # [UBU] ubuntu / huginn
      IdentityFile ~/.ssh/id_ed25519
  ```

---

## 🐧 BÖLÜM 11: SEÇENEK 2 — UBUNTU + XFCE4 + XRDP (Karar bekliyor)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install xfce4 xfce4-goodies xrdp -y
sudo systemctl enable --now xrdp
echo xfce4-session > ~/.xsession && sudo systemctl restart xrdp
sudo ufw allow 3389/tcp            # tercihen yalnız kendi IP'nden: ufw allow from <IP> to any port 3389
sudo apt install docker-ce docker-compose-plugin -y && sudo usermod -aG docker $USER
```
Seçilirse ek işler: 4 Windows scripti → sh/cron (TASIMA-008 kapsamı), D-86 Linux eki (KAHİN kararı), Obsidian AppImage.

---

## 🧱 EK: V2 DONANIM PROFİLİ (korundu, kimlikler düzeltildi)
* Contabo Cloud VPS 12 · 12 vCPU · 48 GB · 400 GB · Germany.
* Docker RAM tavanı 34 GB / 8 vCPU; kalan 14 GB / 4 vCPU OS + Ollama + yerel Python.
* DB kimliği: Bölüm "Kesin Teknik Parametreler" (eski `ai_core_platform` kimliği **iptal**).
* Ağ: tek `default` compose ağı (ek `ai_network` gereksiz; repo compose zaten tek ağ).
* Kazıma: Bölüm 8 (Playwright/Browserless/proxy **iptal**).

---

## ⚠️ Eleştiri ve İyileştirme Notu
* Bu revizyonda doğrulanamayan 4 `Varsayım:` var (9Router image, Roo yayıncı kimliği, 9Router config yolu, Contabo kampanya). Hepsi TASIMA-001/004'te `dir`/`docker pull` ile ölçülmeden karara dönüşmez.
* Önceki plan `.env.example` anahtar adını ters yazmıştı; burada düzeltildi (TASIMA-004).
* Daha ucuz yol: Ubuntu; daha hızlı yol: Windows (script çevirisi yok). Karar Ürün Sahibi'nin.

---

## 🔎 Pano kontrolü (2026-10-01, taşıma öncesi kapı — D-222/D-260/D-238)

Taşıma hattı, panodaki açık işlerin üstüne kurulur; aşağıdaki üç `review` görevi kapanmadan TASIMA-006 (DB restore + COUNT) anlamsızdır çünkü taşınacak verinin doğruluğu tartışmalı.

| Görev (sahip utku) | Pano durumu | Denetim hükmü | Kanıt (dosya:satır) |
|---|---|---|---|
| VERI-TSG-04-YAZICI-01 | review | **RED** | `src/company_master/etl/tsg_yazici.py:88-92` `ilan_turu_normalize_et` etiketi `.upper()` yapar; `:188-189` bunu `olay_esle`'ye verir. `skills/services/ticaret_sicili_kanit.py:183-192` `olay_esle` **büyük/küçük harfe duyarlı** `dict.get`; `ILAN_TURU_ESLEME` (`:114-180`, 65 anahtar) anahtarları karışık harfli ("Değişiklik", "Nevi Değişikliği", "Kuruluş -", "İflas Başlatma"). Karışık harfli hiçbir anahtar **asla** eşleşemez → `(None, "unknown")`. **Düzeltme (2026-10-01, utku notu okununca):** 20/326 kanıtta `ilan_turu` dolu, kalan 306 **boş etiketten** `unknown` olur — bu hatadan değil. Hata yalnız dolu **20** etiketi vurur; kaçının yine de eşleştiği canlı ölçülmedi. Ek: `get_engine()` kapısı atlanmış (`create_engine(os.getenv("DATABASE_URL"))`), `_kisi_ve_rol_cikar` stub `(None, None)`, `event_type=None` satır yazılıyor. `tests/test_ticaret_sicili_kanit.py:131-139` yalnız kanonik harfle `olay_esle` çağırır; normalize→esle zinciri testsiz (D-288: yeşil test de beyandır). |
| VERI-NACE-ACILIM-01 | review | **DÜZELTME + ÖLÇÜM** | `src/company_master/sunum.py:249-276` `acilim_getir`: çıplak `except Exception: pass`, İngilizce bayat doctest, `lru_cache(512)` bayatlama. Teslim "535 boş" diyor, SOZLUK-DIL 10 sn sonra "0 boş" diyor — **sıralı, çelişki değil** (SOZLUK-DIL doldurmuş olabilir); yine de kanıtsız. Canlı: `SELECT COUNT(*) FROM nace_codes WHERE title IS NULL`. |
| VERI-NACE-SOZLUK-DIL-01 | review | **ÖLÇÜM GEREKLİ** | Yukarıdaki çelişki aynı SQL ile çözülür; sonuç gelmeden onay yok (D-260: teslim özeti kanıt değildir). |

**Acil görev durumu:** panoda `acil` alanı **yok** (şema: `oncelik` P0/P1/P2); açık P0 **0**. Chat satır 61/96/97 (VERI-02: `src/company_master/etl/scrapers/osb_tender_monitor.py:33,175,203,212` D-308 İngilizce şema sonrası hâlâ Türkçe kolon bağlıyor — **kırık**) panoda yalnız VERI-02 notu; ayrı görev yok, `BORC-TENDER-KOD-01` borç defterinin ana tablosunda yoktu (eklendi). VERI-NACE-COKLU-01 `aktif` ama hareketsiz. Bu belge pano yazmaz (D-77); aksiyon orkestratör turunda.

**Canlı SQL (D-238, onay öncesi zorunlu):**
```sql
SELECT COUNT(*) FROM nace_codes WHERE title IS NULL;
SELECT event_type, direction, COUNT(*) FROM company_events GROUP BY 1,2 ORDER BY 3 DESC;
```

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]] — D-73, D-86, D-221, D-222, D-223, D-229, D-244, D-251, D-253, D-255, D-260, D-288, D-310
- [[Huginn Data Insights/plans/2026-10-01_docker_taşıma_kazıma_entegrasyon_değerlendirmesi]]
- [[Huginn Data Insights/plans/2026-10-01_kazima_verimlilik_ve_eksiklik_analizi]]
- [[Huginn Data Insights/plans/9router_analiz_raporu]]
- [[Huginn Data Insights/plans/brief_utku_VERI-NACE-COKLU-01]]
- [[Huginn Data Insights/docs/BORC_DEFTERI]]
- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — §14 v2.8
- [[.agents/skills/huginn-web-kazima/SKILL]]
- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]]
- [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
- [[AGENTS]] — n8n-as-code bağlam kökü, `n8nac env status`
