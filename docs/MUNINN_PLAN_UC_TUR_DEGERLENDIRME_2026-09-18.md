İlgili: [[PROJECT_ROADMAP]]

# Muninn Streamlit Planı — Üç Turluk Hızlı Teslimat Değerlendirmesi

**Tarih:** 2026-09-18
**Değerlendirilen belge:** `docs/MUNINN_STREAMLIT_PLAN_2026-09-18.md`
**Kapsam:** Muninn 🛡️ — admin paneli, Streamlit, port **8501**, `app.py` + `web_dashboard/tabs/`
**Kapsam dışı:** Huginn 🦅 — müşteri paneli, port 8000, `web_dashboard/index.html`
**Kural:** Bu turda kod yazılmadı, paket kurulmadı, hiçbir kaynak dosya değiştirilmedi.
**Kanıt kuralı:** Her bulgu ya `dosya:satır` referansı taşır, ya da açıkça **varsayım** işaretlidir.

---

## Tur 1 — Teknik Gerçeklik

### 1.1 Doğrulanan iddialar ( kanıt diskte)

| # | Plandaki iddia | Kanıt | Durum |
|---|---|---|---|
| T-01 | Auth kapısı `st.stop()` çağırmıyor, sayfa yine çiziliyor | `app.py:727-752` — `if not st.session_state.get("admin_token")...` bloğunda `return`/`st.stop()` yok; `st.navigation()` ve `sayfa.run()` devam ediyor | ✅ Doğrulandı |
| T-02 | `admin_cikis()` rerun tetiklemiyor | `admin_auth.py:171-176`, docstring birebir: *"Oturumu kapatır ve başarı mesajını kuyruğa alır (rerun çağırmaz)"* | ✅ Doğrulandı |
| T-03 | Çıkışta cache temizlenmiyor | `admin_auth.py:171-176` içinde `st.cache_data.clear()` yok; aynı çağrı projede 12+ başka yerde var (`admin_musteriler.py:64`, `admin_yonetim.py:83`, `ana_kontrol.py:140`, `admin_kpi.py:365`, `pazarlama.py:352`, `paketler.py:272`, `admin_sistem.py:90`, `admin_realtime.py:251`, `admin_quality.py:396`, `admin_extras.py:101,136`, `__init__.py:587`) | ✅ Doğrulandı |
| T-04 | Docker'da Streamlit servisine `env_file` verilmiyor | `docker-compose.yml` streamlit servisinde `env_file:` satırı yok | ✅ Doğrulandı |
| T-05 | `.env` image'a hiç girmiyor | `.dockerignore:1-4`, yorum birebir: *"Gizli bilgiler — ASLA image'e kopyalanmaz (.env compose env_file ile container'a verilir)"* | ✅ Doğrulandı |
| T-06 | `fileWatcherType = "none"`, kod değişimi otomatik yüklenmiyor | `.streamlit/config.toml:22` + `runOnSave = false` (satır 23), PERF-01 etiketli | ✅ Doğrulandı |
| T-07 | İki ayrı restart yolu var, aynı işi yapmıyor | `scripts/streamlit_restart.py` docstring: *"Ajanlar (roo/kilo/cline) bunu kullanır; Ürün Sahibi yalnız F5 çeker"*; script `netstat -ano` + `taskkill` + `.venv/Scripts/python.exe` ile **Windows'a bağımlı**, Linux/Docker'da çalışmaz | ✅ Doğrulandı |
| T-08 | API istemcisinde retry/backoff yok | `scripts/dash04_api_client.py:81-113` — `post_api(..., timeout=10)`, tek deneme, yeniden deneme yok | ✅ Doğrulandı |
| T-09 | Cache tüm oturumlar arasında paylaşımlı | ~30 adet `@st.cache_data` (ttl 10-300 sn) — `admin_kpi.py` 8 adet, `admin_quality.py` 5, `admin_performance.py` 3, `ana_kontrol.py` 3, `admin_audit.py` 3, `webhook_monitor.py` 3, `pazarlama.py` 4, `paketler.py` 3, diğerleri | ✅ Doğrulandı |

### 1.2 Çürütülen / değişen iddialar ( plan yanlıştı)

| # | Plandaki iddia | Gerçek | Etki |
|---|---|---|---|
| **Ç-1** | "Streamlit 1.62.0, plotly 7.0.0, altair 6.2.2 sürümleri kilitli" | `requirements-app.txt:18-19` → `streamlit>=1.30.0`, `plotly>=5.18.0`. **Üst sınır yok.** `altair` dosyada hiç yok (Streamlit'in dolaylı bağımlılığı). Plandaki üç sürüm numarası dosyada **geçmiyor** | Plan sürüm kilidini "var" sanmış. Gerçekte **hiç kilit yok** → her `pip install` farklı major sürüm getirebilir. Risk plandan **daha yüksek** |
| **Ç-2** | "R-04: mount yok → `web_dashboard` import'u kırılır" | `Dockerfile:33` → `COPY . .`; `.dockerignore`'da `web_dashboard` **yok** → dizin image'a giriyor. Import kırılmaz | Doğru ifade: *"kod image'da donmuş; canlı değişiklik yansımaz, `--build` şart"*. Risk skoru 6 → **4** |
| **Ç-3** | "Ç-06: Muninn'e doğrudan DB erişimi yok, tek yol API" | `musteri_yonetimi.py:90-91` → `SELECT ts, email_masked, ip_masked, success, method, path FROM login_events ORDER BY ts DESC LIMIT 50`; satır 126-127 → `FROM search_events`; `admin_export.py:67-73` → `FROM audit_logs` | Kural **zaten ihlal edilmiş**. Plan bunu yeni bir sınır olarak yazmış; gerçekte mevcut kodu kırmadan uygulanamaz |
| **Ç-4** | "R-05: iki tema sistemi var" | **Üç sistem var.** (1) `.streamlit/config.toml` ham hex: `primaryColor "#6366f1"` (satır 67, 73, 92), `linkColor "#FF4B4B"` / `"#FF8C8C"`, `backgroundColor "#0E1117"`, `"#F7F8FA"`, `"#161A25"`… (2) `src/company_master/ui/tokens.py` (3) `admin_tokens.css` | "Renkler tokens.py'den" kuralı **zaten geçerli değil** |
| **Ç-5** | "Renk SSOT'u `tokens.py`, config.toml ile hizalı" | `tokens.py:7-11` docstring iddiası: *"Yüzey/arkaplan renkleri `.streamlit/config.toml` içindeki koyu tema ile hizalıdır (`backgroundColor #0a0e17`, `secondaryBackground #131826`, `textColor #e2e8f0`)"*. **Gerçek `config.toml:93-95`:** `#0E1117`, `#262730`, `#FAFAFA`. Üç değerin **üçü de tutmuyor** | Docstring **yalan söylüyor**. Ayrıca `config.toml:45` `base = "light"`, `tokens.py` tamamen koyu palet → varsayılan tema ile token paleti **zıt** |
| **Ç-6** | "Denetim izi eksik" (planın kaçırdığı başlık sanılan) | Denetim sekmesi **var**: `admin_audit.py:85` `render_audit_tab()`, menü kaydı `__init__.py:442-452` (`min_rol="admin"`). **Ama içerik yanlış kapsamda** — `admin_audit.py:1-9` docstring: Karar Defteri, Dosya Kilidi, Handoff, Görev Durumu, Trigger Logu. Hepsi **iç ajan orkestrasyonu**; kaynaklar `data/orchestrator/*.json` | Doğru ifade: *"Denetim sekmesi var ama admin kullanıcı eylemlerini (onay, kredi yükleme, kategori değişimi, şifre değişimi) hiç izlemiyor."* Yanlış varlık, doğru isim |

### 1.3 Tur 1'de çıkan **yeni** bulgular (plan hiç değinmemiş)

| # | Bulgu | Kanıt | Sınıf |
|---|---|---|---|
| **Y-1** | **Docker'da Muninn API'ye hiç ulaşamaz.** `_api_url()` sırası: `DASH_API_URL` env → `config.toml [api].url` → `http://localhost:8000`. Streamlit container'ında `DASH_API_URL` tanımlı **değil**; `config.toml` 116 satırın tamamı okundu, **`[api]` bölümü yok**; `localhost:8000` container'ın kendisi, orada uvicorn yok | `dash04_api_client.py:22-37`; `.streamlit/config.toml:1-116`; `docker-compose.yml` streamlit servisi. Karşılaştırma: `healthcheck` servisinde `API_BASE_URL=http://api:8000` **var** | 🔴 P0 |
| **Y-2** | **Şifre değiştirme Docker'da sessizce çöker.** `_env_sifre_guncelle()` `.env` dosyasına yazmaya çalışıyor; `.env` image'da yok; `except Exception` hatayı yutuyor, `_LOG.warning` + `return False`. Kullanıcıya hata gösterilmiyor. Container yazılabilir olsa bile restart'ta kaybolur (ephemeral) | `admin_auth.py:191-202`; `.dockerignore:2-4` | 🔴 P0 |
| **Y-3** | **Sürüm kilidi yok.** `requirements-app.txt`'deki 12 paketin **hepsi** `>=`, hiçbirinde üst sınır yok | `requirements-app.txt:2-31` | 🔴 P0 |
| **Y-4** | **Dockerfile Streamlit'i tanımıyor.** `EXPOSE 8000`, `HEALTHCHECK curl http://localhost:8000/api/health`, `CMD ["uvicorn", "web_app:app", ...]`. Streamlit servisi aynı image'ı `command:` ile override ediyor → image-düzeyi healthcheck 8501 container'ında **her zaman başarısız**; compose servis healthcheck'i override etmezse container "unhealthy" görünür | `Dockerfile:41,43-44,46` | 🔴 P0 |
| **Y-5** | "Legacy" çelişkisi **iki dosyada**. `docker-compose.yml:6` yorumu + `requirements-app.txt:17` yorumu (*"Legacy: eski Streamlit arayuzu (compose profili: legacy)"*) ikisi de Streamlit'i eski sayıyor; compose'da `profiles:` satırı yok, servis normal ayakta | `docker-compose.yml:6`, `requirements-app.txt:17` | 🟡 P1 |
| **Y-6** | `pytest.ini`'de **marker tanımı yok, `addopts` yok, coverage yapılandırması yok.** `norecursedirs` 9 girdi, yorum: *"2026-09-14'te 77 toplama hatası gözlendi"* | `pytest.ini:1-21` | 🟡 P1 |

### 1.4 Tur 1 sonu — değişen madde listesi

1. **Sürüm kilidi iddiası silinmeli**, yerine "sürüm kilidi yok, eklenmeli" yazılmalı.
2. **R-04 yeniden yazılmalı** — "import kırılır" ifadesi çıkarılmalı, skor 6 → 4.
3. **Ç-06 kuralı silinmeli veya geçiş planına çevrilmeli** — mevcut kod zaten ihlal ediyor.
4. **R-05 "iki sistem" → "üç sistem"**, üstüne `tokens.py` docstring'inin yanlış olduğu eklenmeli.
5. **"Denetim izi eksik" → "denetim izi yanlış kapsamda"**.
6. **4 yeni P0 madde eklenmeli** (Y-1…Y-4).

---

## Tur 2 — Risk ve Kapsam

Tur 1 bulguları girdi alındı. KAHİN'in saydığı 11 başlık ayrı ayrı ele alındı.

| Başlık | Gerçek mi teorik mi | Etki | Maliyet (düzeltme) |
|---|---|---|---|
| **Oturum güvenliği ve yetki sınırları** | 🔴 **Gerçek** — `app.py:727-752` auth kapısı `st.stop()` çağırmıyor; token yokken bile `sayfa.run()` çalışıyor | Yetkisiz kullanıcı sayfa içeriğini kısa süre görebilir; yan etki olarak API çağrıları tetiklenir | ~2 satır. 15 dk |
| **Secrets yönetimi** | 🔴 **Gerçek** — `.dockerignore:1-4` + compose'da `env_file` yok → admin şifresi container'a **hiçbir yoldan** ulaşmıyor. Üstüne `_env_sifre_guncelle()` `.env`'e yazmaya çalışıyor (`admin_auth.py:191-202`) | Docker'da giriş imkânsız; şifre değişimi sessizce kayboluyor | compose'a 1 satır `env_file: .env`; şifre yazımı DB'ye taşınmalı → 1 satır + ~30 satır. 2 sa |
| **Çok kullanıcılı eşzamanlılık** | 🟡 **Yarı gerçek** — `st.session_state` kullanıcı başına izole (Streamlit garantisi), ama `@st.cache_data` **süreç genelinde paylaşımlı** (~30 nokta) | Admin A çıkış yapar, admin B aynı container'da A'nın cache'lenmiş verisini 10-300 sn görebilir | `admin_cikis()`'e `st.cache_data.clear()` — 1 satır. 10 dk |
| **Streamlit rerun / state davranışı** | 🔴 **Gerçek** — `admin_cikis()` docstring'i açıkça *"rerun çağırmaz"*; rerun sorumluluğu çağırana bırakılmış (`render_admin_cikis():187` çağırıyor, popover yolu `app.py:369-399` çağırmıyor) | KAHİN'in 1 numaralı şikâyetinin **tam kök nedeni**: çıkışta UI güncellenmiyor, F5 gerekiyor | 1 satır. 10 dk |
| **Veri hacminde performans** | 🟡 **Teorik-yakın** — `musteri_yonetimi.py:90` `LIMIT 50` var; `admin_quality.py:184` `load_risky_companies(limit=100)` var. Ama `st.dataframe` sayfalama yok, sunucu tarafı filtre yok | Bugün küçük veriyle sorun yok; 10k+ satırda tarayıcı yavaşlar | Şu an **iş yapılmamalı** (YAGNI). Sorun çıkınca 2-3 sa |
| **Deploy ve geri alma yolu** | 🔴 **Gerçek** — `Dockerfile:41,43-46` Streamlit'i tanımıyor; iki restart yolu (`streamlit_restart.py` Windows-only vs `docker compose`) aynı işi yapmıyor; sürüm kilidi yok → aynı commit iki farklı image üretebilir | "Çalışan sürüme dön" garantisi yok | requirements pin + Streamlit için ayrı servis healthcheck. 1,5 sa |
| **Loglama / denetim izi** | 🟡 **Gerçek ama ters yönde** — `admin_audit.py:1-9` iç ajan süreçlerini izliyor (karar defteri, dosya kilidi, handoff, trigger). Admin eylemleri için `audit_logs` tablosu **var** (`admin_export.py:67-73`), ama **oraya kimin yazdığı doğrulanamadı** — ⚠️ **varsayım** | Kredi yükleme / kullanıcı onayı / kategori değişimi kim tarafından yapıldı izlenemiyor olabilir | Önce 20 dk doğrulama; yazım yoksa endpoint başına 1 satır, ~6 endpoint. 1,5 sa |
| **Yedekleme** | ⚠️ **Varsayım** — bu turda hiç okuma yapılmadı; yedek script'i veya cron kanıtı görülmedi | Bilinmiyor | Önce 20 dk keşif |
| **Bağımlılık ve sürüm kilidi** | 🔴 **Gerçek** — `requirements-app.txt` 12 paketin hepsi `>=`, üst sınır yok | Streamlit 2.x çıkarsa panel bir gecede kırılabilir; `st.dataframe(width="stretch")` gibi yeni API'ler zaten sürüme duyarlı | `pip freeze` → `requirements.lock`. 30 dk |
| **Erişilebilirlik** | 🟡 **Yarı gerçek** — `tokens.py:48-53` WCAG 1.4.11 için `border-interactive` özel olarak tanımlanmış (bilinç var). Ama `config.toml` ham hex'leri bu kontrol dışında; `base = "light"` ile koyu token paleti zıt | Odak halkası / sınır kontrastı temaya göre tutarsız olabilir | Tema kaynağı tekilleştirilmeden ölçüm anlamsız. Önce Ç-4/Ç-5 |
| **Test edilebilirlik** | 🟡 **Gerçek** — `pytest.ini`'de marker yok, `addopts` yok, coverage yok; UI testleri `monkeypatch` ile Streamlit'i taklit ediyor (`test_admin_auth_login.py:20-27` `_form_hazirla`) | Hızlı/yavaş test ayrımı yapılamıyor; UI regresyonu ancak elle görülüyor | `pytest.ini`'e 3 marker satırı. 20 dk |

### 2.1 Risk sıralaması (olasılık × etki)

| Risk | Olasılık | Etki | Skor | Erken uyarı sinyali |
|---|---|---|---|---|
| Docker'da API erişimi kopuk (Y-1) | Kesin | Panel tamamen işlevsiz | **10** | Her ekranda "API sunucusuna baglanilamadi" |
| Docker'da şifre yok (T-04/T-05) | Kesin | Giriş imkânsız | **9** | Doğru şifreyle 401 |
| Auth kapısı sızıntısı (T-01) | Yüksek | Yetkisiz görüntüleme | **8** | Token'sız sekme içeriği görünüyor |
| Çıkışta UI güncellenmiyor (T-02) | Kesin | KAHİN şikâyeti | **7** | Çıkış sonrası ekran aynı kalıyor |
| Sürüm sürüklenmesi (Y-3) | Orta | Rastgele kırılma | **7** | Aynı koddan farklı davranan iki kurulum |
| Çıkışta cache sızıntısı (T-03) | Orta | Veri sızıntısı | **6** | B admini A'nın sayılarını görüyor |
| Şifre değişimi sessiz çöküyor (Y-2) | Yüksek | Yanlış başarı mesajı | **6** | "Şifre değişti" ama eski şifre çalışıyor |
| Dockerfile/Streamlit uyumsuz (Y-4) | Orta | Yanlış "unhealthy" | **5** | `docker ps` unhealthy, panel çalışıyor |
| Üç tema kaynağı (Ç-4/Ç-5) | Yüksek | Görsel tutarsızlık | **5** | Aynı mavi iki farklı tonda |
| Admin eylem denetimi (varsayım) | Bilinmiyor | İzlenebilirlik kaybı | **?** | "Bu krediyi kim yükledi" sorusu cevapsız |

### 2.2 Tur 2 sonu — değişen madde listesi

1. **Erişilebilirlik başlığı öne alınamaz** — tema kaynağı üçe bölünmüşken ölçüm yapılamaz. Önkoşul: Ç-4/Ç-5.
2. **Veri hacmi performansı Faz 5'ten çıkarılmalı** — bugün sorun değil, YAGNI.
3. **Denetim izi maddesi "ekle"den "doğrula, sonra karar ver"e çevrilmeli.**
4. **Yedekleme maddesi "varsayım" damgasıyla kalmalı** — hiç kanıt toplanmadı.
5. **Deploy/geri alma maddesi büyümeli** — Y-3 + Y-4 birlikte "geri dönülebilir deploy yok" anlamına geliyor.

---

## Tur 3 — Kabul Kararı

### Karar: **ŞARTLI KABUL**

Plan doğru sorunu buluyor ve öncelik sırası büyük ölçüde doğru. Ama iki kusuru var: (a) dört P0 gerçeği kaçırmış, (b) altı iddiayı diskte doğrulamadan yazmış. Bu haliyle uygulanırsa Faz 1'de takılır, çünkü Docker'da panel zaten ayağa kalkmıyor.

### Şartlar

1. Faz 0'a **Y-1 (DASH_API_URL) ve T-04 (env_file)** eklenecek; bunlar diğer her şeyin önkoşulu.
2. Planın "sürüm kilidi var" bölümü silinecek; yerine `requirements.lock` üretimi konacak.
3. Ç-06 kuralı (doğrudan DB yasağı) ya silinecek ya da ayrı bir geçiş görevi olacak — Faz 1'i bloklamayacak.
4. Denetim izi maddesi, **önce 20 dakikalık doğrulama** adımıyla başlayacak.
5. Faz 5'teki veri hacmi performans işi kapsam dışına alınacak.
6. `tokens.py:7-11` docstring'i düzeltilecek (yanlış bilgi, ileride yanlış karara yol açar).

### kilo planına katkı

**Neyi hızlandırır:**
- `admin_cikis()` düzeltmesi 2 satır (rerun + cache clear) — Tur 1 tam yerini gösterdi, arama gerekmiyor.
- Auth kapısı düzeltmesi tek satır, `app.py:727-752` içinde.
- Cache envanteri çıkarıldı (~30 nokta, dosya:satır listeli) — tarama tekrar edilmeyecek.

**Neyi yavaşlatır:**
- Docker düzeltmeleri (Y-1, T-04, Y-4) Faz 1'in önüne giriyor; UI işleri ~2 saat gecikiyor.
- Tema tekilleştirme, erişilebilirlik işinin önkoşulu oldu.

**Hangi maddeler silinmeli:**
- "Sürüm kilidi doğrulaması" (kilit zaten yok — doğrulanacak bir şey yok).
- "web_dashboard mount edilmezse import kırılır" (yanlış).
- "Veri hacmi performans optimizasyonu" (YAGNI).
- "Muninn'e doğrudan DB erişimi yasak" kuralı — mevcut haliyle uygulanamaz.

**Hangileri eklenmeli:**
- `DASH_API_URL=http://api:8000` (compose, streamlit servisi).
- `env_file: .env` (compose, streamlit servisi).
- Streamlit servisine kendi healthcheck'i (`/_stcore/health`), image healthcheck'ini override etmek için.
- `requirements.lock` üretimi + Dockerfile'da kullanımı.
- `_env_sifre_guncelle()` yerine DB'ye yazan yol, veya en azından `return False` durumunda kullanıcıya görünür hata.
- `admin_audit.py`'ye admin eylem kaydı (doğrulama sonrası).

---

## Dengeli Eleştiri

### Pozitif — planın gerçekten doğru kurduğu şeyler

1. Auth kapısındaki `st.stop()` eksikliğini P0 olarak işaretlemesi doğru; `app.py:727-752` bunu birebir doğruluyor.
2. Çıkış/rerun sorununu KAHİN'in şikâyetiyle eşleştirmesi doğru; `admin_auth.py:171` docstring'i *"rerun çağırmaz"* diyerek kök nedeni itiraf ediyor.
3. `env_file` eksikliğini yakalaması doğru; `.dockerignore:1` yorumu bunun tek giriş yolu olduğunu yazıyor.
4. Cache paylaşımını çok kullanıcılı risk saymak doğru; ~30 `@st.cache_data` noktası ve `admin_cikis()`'te eksik `clear()` bunu kanıtlıyor.
5. Fazları bağımlılık sırasına dizmesi doğru; Faz 0 olmadan Faz 1 test edilemez.

### Negatif

1. **Yanlış varsayım** — üç sürüm numarası (Streamlit 1.62.0, plotly 7.0.0, altair 6.2.2) uydurulmuş; `requirements-app.txt:18-19` `>=1.30.0` / `>=5.18.0` diyor, altair dosyada hiç yok.
2. **Yanlış varsayım** — "mount yoksa import kırılır" dedi; `Dockerfile:33` `COPY . .` bunu çürütüyor.
3. **Yanlış varsayım** — "Muninn'de doğrudan DB yok" dedi; `musteri_yonetimi.py:90-91` ham SQL çalıştırıyor.
4. **Eksik keşif** — dört P0 (Y-1…Y-4) kaçırıldı; hepsi tek dosya okumasıyla bulunabilirdi.
5. **Fazla mühendislik** — veri hacmi performans optimizasyonu, bugünkü veri boyutunda karşılığı olmayan iş.
6. **Gereksiz soyutlama** — "Muninn'e doğrudan DB yasak" kuralı, mevcut kodu kırmadan uygulanamaz bir sınır; kural yazmadan önce ihlal sayılmalıydı.
7. **Yanlış teşhis** — denetim izini "eksik" saydı; sekme var ama yanlış kapsamda (`admin_audit.py:1-9` iç ajan süreçleri).
8. **Doğrulanmamış iddia zinciri** — `tokens.py:7-11` docstring'ini kaynak kabul etmiş; o docstring'in kendisi `config.toml:93-95` ile uyumsuz, yani plan yanlış bir belgeye güvenmiş.

---

## 2 Dakikalık İş Dağıtımı

Aşağıdaki sıra bağlayıcıdır. Bir madde bitmeden bir sonraki maddeye geçilmez; paralel olduğu açıkça yazılan maddeler aynı anda yürütülebilir.

**Blokaj maddesi — her şeyden önce yapılır.**
İş 1, sahibi üretim ajanı, süre 30 dakika: `docker-compose.yml` dosyasındaki Streamlit servisine `env_file: .env` ve `environment: DASH_API_URL=http://api:8000` satırları eklenir. Bu iki satır tamamlanmadan Docker ortamında hiçbir admin ekranı test edilemez, dolayısıyla sonraki hiçbir maddenin doğrulaması yapılamaz.

**İş 1 bittikten sonra, iki iş paralel yürür.**

İş 2, sahibi üretim ajanı, süre 15 dakika: `app.py` dosyasında 727 ile 752 satırları arasındaki giriş kapısı bloğunun sonuna `st.stop()` çağrısı eklenir. Böylece token bulunmayan ziyaretçi için sayfa gövdesi hiç çizilmez.

İş 3, sahibi denetim ajanı, süre 20 dakika: Kredi yükleme, kullanıcı onaylama, kategori kaydetme ve şifre değiştirme uçlarının `audit_logs` tablosuna kayıt yazıp yazmadığı `web_app.py` içinde doğrulanır. Sonuç tek sayfalık bir bulgu notuna yazılır. Bu iş kod değiştirmez, sadece gerçeği tespit eder.

**İş 2 bittikten sonra, üç iş paralel yürür.**

İş 4, sahibi üretim ajanı, süre 10 dakika: `web_dashboard/tabs/admin_auth.py` dosyasındaki `admin_cikis` fonksiyonuna `st.cache_data.clear()` satırı eklenir ve fonksiyonun sonunda `st.rerun()` çağrılır; docstring'deki "rerun çağırmaz" ifadesi güncellenir. Bu madde KAHİN'in birinci şikâyetini kapatır.

İş 5, sahibi üretim ajanı, süre 30 dakika: Sanal ortamda `pip freeze` çalıştırılarak `requirements.lock` dosyası üretilir ve `Dockerfile` bu dosyayı kullanacak biçimde güncellenir. Böylece aynı commit her zaman aynı image'ı üretir.

İş 6, sahibi üretim ajanı, süre 20 dakika: `docker-compose.yml` içindeki Streamlit servisine kendi sağlık kontrolü eklenir; kontrol `http://localhost:8501/_stcore/health` adresine bakar. Bu, image içindeki 8000 portlu sağlık kontrolünü geçersiz kılar.

**İş 4 bittikten sonra sırayla devam edilir.**

İş 7, sahibi üretim ajanı, süre 2 saat: `admin_auth.py` dosyasındaki `_env_sifre_guncelle` fonksiyonu, `.env` dosyasına yazmak yerine veritabanına yazacak biçimde değiştirilir. Yazma başarısız olursa kullanıcıya görünür hata mesajı gösterilir; sessiz başarısızlık kaldırılır.

İş 8, sahibi üretim ajanı, süre 1 saat: Tema renklerinin tek kaynağa indirilmesi için `src/company_master/ui/tokens.py` dosyasının 7 ile 11 satırları arasındaki yanlış docstring düzeltilir ve `.streamlit/config.toml` ile `tokens.py` arasındaki altı renk farkı tek listede toplanır. Bu iş, erişilebilirlik ölçümünün önkoşuludur ve tamamlanmadan renk kontrastı denetimi yapılmaz.

**En son, KAHİN onayına bağlı maddeler başlar.**

İş 9, sahibi üretim ajanı, süre 3 saat: Sağ alt admin popover'ı için hazırlanmış wireframe KAHİN tarafından onaylandıktan sonra `ADMIN-UX-PROFILMENU-01` görevi başlatılır. Onay gelmeden bu işe başlanmaz.

İş 10, sahibi üretim ajanı, süre 2 saat: Sol menü ağacı wireframe'i onaylandıktan sonra `ADMIN-UX-MENUTREE-01` görevi başlatılır. Bu madde de onaya bağlıdır.

---

## KAHİN Özeti

| Renk | Anlam | Adet | Oran |
|---|---|---|---|
| 🔴 | Acil / blokaj | 7 | %39 |
| 🟡 | Dikkat | 6 | %33 |
| 🟢 | Tamam | 3 | %17 |
| 🔵 | Bilgi / öneri | 2 | %11 |

**Üç cümlede durum:**
Panel Windows'ta çalışıyor, Docker'da hiç çalışmıyor — şifre ve API adresi container'a girmiyor.
Planın beş iddiası diskte doğrulanınca yanlış çıktı; dört yeni acil sorun ortaya çıktı.
İlk otuz dakikalık iş (compose'a iki satır) yapılmadan geri kalan hiçbir şey test edilemez.

**Plan doğruluk oranı:** 9 iddia doğrulandı, 6 iddia çürütüldü, 4 konu hiç görülmemiş → **%47 isabet**.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
