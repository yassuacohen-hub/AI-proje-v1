İlgili: [[PROJECT_ROADMAP]]

# Muninn Admin Paneli — Streamlit Planı (2026-09-18)

> **Format:** İlk tur plan → **İkinci Tur Revizyonu** (6 zorunlu başlık) → **Fark listesi** → KAHİN özeti.
> **Bu turda kod yazılmadı, paket kurulmadı.** Tüm bulgular diskteki dosyalardan okunarak doğrulandı.

---

## 0) Kapsam ve Terminoloji (önce bu netleşsin)

| Terim | Karşılığı | Kapsam |
|---|---|---|
| **Muninn** 🛡️ | Admin paneli, **Streamlit**, port **8501**, `app.py` + `web_dashboard/tabs/` | ✅ **BU PLANIN KONUSU** |
| **Huginn** 🦅 | Müşteri paneli, saf HTML/CSS/JS, port **8000**, `web_dashboard/index.html` | ❌ **Kapsam dışı** |
| **Odin** ⚡ | Çekirdek kütüphane `src/company_master/` | 🔶 Sadece UI bileşenleri ödünç alınır |
| "stermit" | **Streamlit** (KAHİN netleştirmesi 2026-09-18) | — |

### Kapsam kayması itirafı (şeffaflık notu)

| Tur | Varsayılan kapsam | Sonuç |
|---|---|---|
| Revizyon 1 | Admin (Streamlit) | ❌ Yanlış varsayıldı sanıldı |
| Revizyon 2 | Müşteri (vanilla JS) | ❌ Kapsam ters çevrildi |
| **Revizyon 3 (bu doküman)** | **Admin = Muninn = Streamlit** | ✅ KAHİN onaylı |

**Ders:** Belirsiz terim doküman içine "açık soru" olarak bırakılmaz; **doküman yazılmadan önce netleştirilir.** İkinci tur metodolojisinin varlık sebebi tam olarak budur.

---

## 1) İlk Tur Plan Özeti

> ⚠️ Aşağıdaki özet `docs/UI_STACK_DEGERLENDIRME_2026-09-18.md` Revizyon 2'den gelir ve **müşteri paneli için yazılmıştı**. Buraya yalnız *taşınabilir kısımları* için konur.

### 1.1 Taşınan karar: yeni paket alınmıyor

| # | Öneri | Karar | Muninn için hâlâ geçerli mi? |
|---|---|---|---|
| 1 | Untitled UI | 🔴 ELE | ✅ Evet — ücretli (~300-500 $) |
| 2 | Flowbite Pro | 🔴 ELE | ✅ Evet — ücretli (~200 $) |
| 3 | Tremor | 🔴 ELE | ✅ Evet — React; Streamlit'te çalışmaz |
| 4 | Next.js + Tailwind | 🔴 ELE | ✅ Evet — Streamlit'in yerine geçer, migration |
| 5 | shadcn/ui | 🔴 ELE | ✅ Evet — React zorunlu |
| 6 | Aceternity UI | 🔴 ELE | ✅ Evet — React + tanıtım sayfası işi |
| 7 | TanStack Table | 🔴 ELE | ✅ Evet — `st.dataframe` zaten var |
| 8 | React Flow | 🟡 ERTELE | 🔶 Kısmen — ilişki ağı gerçek boşluk, ama React |

**Muninn'e taşınan sonuç: 🟢 0 yeni paket, 0 ₺.** 7/8 öneri React ekosisteminde; Streamlit sunucu tarafı Python render ettiği için hiçbiri **doğrudan** kullanılamaz.

### 1.2 Taşınmayan kısım

A1–A9 adım tablosu (`index.html` / `style.css` / `app.js`) **tamamen düşer** — o dosyalar Huginn'e ait, Muninn'in dosyaları değil.

### 1.3 İlk turun zımni varsayımları (ikinci turda test edilecek)

| # | Varsayım | Doğrulandı mı? |
|---|---|---|
| V1 | "Auth çalışıyor, sadece görsel iş var" | ❌ **YANLIŞ** — bkz. R-01 |
| V2 | "Streamlit tek kullanıcılı, izolasyon sorun değil" | ❌ **YANLIŞ** — bkz. S-03 |
| V3 | "Docker'da Streamlit legacy profilde, opsiyonel" | ❌ **YANLIŞ** — bkz. O-01 |
| V4 | "Ana sayfa verisi gerçek" | ❌ **YANLIŞ** — bkz. U-01 |
| V5 | "İş ~18,5 sa ≈ 2,5 gün" | ❌ Fazla iyimser — bkz. §D |

**5/5 varsayım yanlış çıktı.** İlk tur olduğu gibi uygulansaydı 4 P0 hata sessizce taşınacaktı.

---

# 2) İkinci Tur Revizyonu

---

## §A — Risk Envanteri

Ölçek: Olasılık (O) ve Etki (E) → 1 düşük · 2 orta · 3 yüksek. **Risk = O × E.** 6+ = 🔴, 4-5 = 🟡, ≤3 = 🟢.

### A.1 Teknik Riskler

| Kod | Risk | O | E | Skor | Erken uyarı sinyali | Azaltma aksiyonu |
|---|---|:-:|:-:|:-:|---|---|
| **R-01** | **Auth gate bloke etmiyor.** `app.py:728` içindeki `if not admin_token` bloğunda `st.stop()` / `return` **yok**; modal `kapatilabilir=False` olsa bile akış `st.navigation()` → `sayfa.run()` → `render_sidebar/topbar/footer/chat` ile devam ediyor. Token'sız kullanıcı sayfa gövdesini görebilir. | 3 | 3 | **9 🔴** | Tarayıcıda giriş yapmadan sekme içeriğinin arkada render olması; DOM'da veri görünmesi | Modal'dan hemen sonra `st.stop()`. Ek olarak `render_icerik()` girişinde ikinci kapı (defense-in-depth). **Faz 0'da yapılır, diğer her şeyden önce.** |
| **R-02** | `admin_cikis()` (`admin_auth.py:171-176`) yalnız 3 anahtarı temizliyor (`admin_token`, `admin_email`, `_force_auth_gate`). `current_section`, `reset_email_gate`, `_sifre_unuttum` ve `@st.cache_data` içeriği kalıyor → çıkış sonrası eski verinin ekranda kalması. | 3 | 3 | **9 🔴** | "Çıkış"tan sonra sayfa yenilenmeden eski e-postanın/verinin görünmesi | Beyaz liste yerine **kara liste dışı her şeyi temizle**: korunacak anahtarlar sabit listede, gerisi `st.session_state.clear()`. Ardından `st.cache_data.clear()` + `st.rerun()`. |
| **R-03** | `env_file: .env` **Streamlit servisinde tanımlı değil** (api, telegram-bot, telegram-periodic'te var). `ADMIN_EMAIL`/`ADMIN_PASSWORD` container'a geçmez. | 3 | 3 | **9 🔴** | Docker'da giriş çalışmıyor ama yerelde çalışıyor; `_env_kimlik()` boş dönüyor | `docker-compose.yml` streamlit servisine `env_file: .env` ekle. Tek satır. |
| **R-04** | `./web_dashboard` streamlit servisine **mount edilmemiş**, ama `app.py` `from web_dashboard.tabs import ...` yapıyor → image içinden geliyor. Kod değişince canlıya yansımaz, `--build` şart. | 3 | 2 | **6 🔴** | Dosya değişti, panel eski davranıyor; "restart ettim ama olmadı" | Ya dev için `./web_dashboard:/app/web_dashboard` mount eklenir, ya da "her değişiklikte `--build`" kuralı yazılır. **Seçim KAHİN'e (bkz. K-2).** |
| **R-05** | Tema iki ayrı sistemden geliyor: `src/company_master/ui/styles.py` (`tum_css`) ve Streamlit'in kendi tema ayarı (`aktif_tema()`). Senkron bozulursa kontrast düşer. | 2 | 2 | 4 🟡 | Karanlık temada açık renk kart; okunmayan metin | Tek SSOT: `tokens.py`. Chart içinde sabit renk kodu yazılmaz (mevcut kural). `test_style_css.py` genişletilir. |
| **R-06** | `web_dashboard/tabs/__init__.py` menü SSOT'u `frozen=True` dataclass tuple'ı; menü ağacı değişiminde `url_path` kırılırsa eski bağlantılar ölür. | 2 | 2 | 4 🟡 | 404 / boş sayfa; `_eski_adresi_cevir()` tetiklenmiyor | Her yeniden adlandırmada `ESKI_URL` haritasına satır eklenir. Test: her `SECTIONS` girdisi için `tab_url_getir()` dönüyor mu. |
| **R-07** | `tests/test_mcp_transport.py` toplama hatası — süit yeşil sayılamıyor. | 3 | 1 | 3 🟢 | `pytest` collection error | Faz 0'da düzelt veya `pytest.ini`'de geçici `--ignore`, gerekçe yorumu ile. |

### A.2 Operasyonel Riskler

| Kod | Risk | O | E | Skor | Erken uyarı sinyali | Azaltma aksiyonu |
|---|---|:-:|:-:|:-:|---|---|
| **O-01** | **`docker-compose.yml` kendi kendisiyle çelişiyor.** Satır 6 yorumu: `Eski Streamlit arayuzu: docker compose --profile legacy up -d streamlit`. Gerçek: satır 43-44 `# ---- Streamlit Admin Panel (Muninn SUPER ADMIN) — Ana profil ----`, servis tanımında **`profiles:` anahtarı YOK** → varsayılan profilde çalışıyor. | 3 | 2 | **6 🔴** | Yeni kişi `--profile legacy` yazıyor, servis zaten ayakta; ya da `docker compose up -d` beklenmedik şekilde 8501'i açıyor | Yorum satırı güncellenir: "Streamlit Admin (Muninn): `docker compose up -d streamlit` — ana profil". Yorum ≠ gerçek durumu **Faz 0 kapsamında** kapatılır. |
| **O-02** | İki restart yolu var: `scripts/streamlit_restart.py` (yerel, `fileWatcherType=none`) ve `docker compose up -d --build streamlit`. Hangisinin canlı olduğu belirsiz → "düzelttim ama görünmüyor". | 3 | 2 | **6 🔴** | Aynı port iki kez dinlenmeye çalışılıyor; değişiklik yansımıyor | Tek kural yazılır: **yerel geliştirme = script, Docker = compose.** İkisi aynı anda çalıştırılmaz. Faz 0 çıktısı. |
| **O-03** | `st.session_state` sunucu belleğinde; `restart: unless-stopped` ile container yeniden başladığında **tüm oturumlar düşer**. | 2 | 2 | 4 🟡 | Deploy sonrası herkes giriş ekranında | Kabul edilen davranış olarak yazılır; ya da token `st.query_params`/cookie'ye taşınır (kapsam artışı, bkz. K-3). |
| **O-04** | Healthcheck `/_stcore/health` yalnız Streamlit'in ayakta olduğunu söyler; **API 8000 düşse bile yeşil** kalır. Panel boş veri gösterir. | 2 | 2 | 4 🟡 | Tüm KPI 0, hata yok | Panelde üst şeritte "API bağlantısı" durumu gösterilir (mevcut `post_api` hatası yakalanır). |
| **O-05** | 4 görevlik zincir (`ADMIN-UX-LOGOUT-01` → `PROFILMENU` → `MENUTREE` → `AYARLAR-SAYFA`) **kurulu ama hiçbiri başlamadı**; kod yazımı 7 turdur erteleniyor. | 3 | 2 | **6 🔴** | Pano'da aynı 4 görev gün boyu `bekliyor` | Bu doküman onaylanır onaylanmaz Faz 0 + Faz 1 **aynı gün** başlar. Karar noktası K-1. |

### A.3 Ürün Riskleri

| Kod | Risk | O | E | Skor | Erken uyarı sinyali | Azaltma aksiyonu |
|---|---|:-:|:-:|:-:|---|---|
| **U-01** | **Ana sayfa sahte veri gösteriyor.** `ana_kontrol.py:68-84` `load_webhook_stats()` her alanı `0` döndüren placeholder. Sonuç: donut grafik hiç çizilmiyor, "Uyarılar" hep `st.success("Sistem iyi durumda")`. **Panel her koşulda "her şey yolunda" diyor.** | 3 | 3 | **9 🔴** | Webhook gerçekten hata alırken panel yeşil | Ya gerçek veri bağlanır (`/api/webhooks/apify/metrics` **mevcut**, `web_app.py:442`), ya da kart açıkça "veri yok" durumuna alınır. **Sahte yeşil, hatadan beterdir.** |
| **U-02** | 6 üst / 23 alt sekme — bilgi mimarisi dağınık; admin aradığını bulamıyor. | 3 | 2 | **6 🔴** | Sürekli "şu ayar nerede" sorusu | `UX_MENU_AGACI_WIREFRAME` planı: 5 üst / 18 alt. Faz 3. |
| **U-03** | Admin kendi ayarlarını menüden yapıyor; KAHİN "sadece sağ-alt popover'dan" dedi. İki yol açık kalırsa kural bozulur. | 2 | 2 | 4 🟡 | Ayarlar hem menüde hem popover'da | Menüden "Ayarlar" kaldırılır **aynı** fazda popover tamamlanır. Tek fazda, yarım bırakılmaz. |
| **U-04** | Wireframe onayı alınmadan kod yazılırsa yeniden yapım riski. | 2 | 3 | **6 🔴** | Ekran hazır, KAHİN "böyle değildi" diyor | Her sayfa için wireframe zorunlu (mevcut kural). İki wireframe zaten onay bekliyor. |

### A.4 Streamlit'e Özgü Riskler (KAHİN'in ayrı başlık talebi)

| Kod | Konu | Streamlit'in gerçek davranışı | Bizdeki durum | Risk | Aksiyon |
|---|---|---|---|:-:|---|
| **S-01** | **State yönetimi** | `st.session_state` yalnız **o tarayıcı sekmesi + o sunucu süreci** için yaşar. Disk/DB yok. | Token burada tutuluyor (`admin_token`). | 🔴 | Token'ın kaybolması "güvenli hata" (giriş ekranı) olduğu için kabul edilebilir — **ama R-02 temizlik hatası kabul edilemez.** |
| **S-02** | **Rerun davranışı** | Her widget etkileşiminde **script baştan sona yeniden çalışır**. `main()` dosya sonunda doğrudan çağrılıyor — fonksiyon değil, script davranışı. | 23 sekme, her rerun'da menü ağacı + CSS yeniden üretiliyor. | 🟡 | `@st.cache_data(ttl=…)` mevcut (30/60 sn). Menü SSOT'u `frozen` dataclass + modül seviyesi tuple → zaten ucuz. **Yeni kural: render fonksiyonu içinde ağ çağrısı cache'siz yapılmaz.** |
| **S-03** | **Çok kullanıcılı oturum izolasyonu** | `st.session_state` sekme başına **izole**, ama `@st.cache_data` **tüm kullanıcılar arasında paylaşımlı**. | `load_kpi_data()`, `load_performance_data()` argümansız → global cache. Şu an tüm adminler aynı veriyi görmeli, sorun yok. | 🟡 | **Demir kural yazılır:** kullanıcıya özel veri çeken fonksiyon `@st.cache_data` ile sarılmaz, ya da cache anahtarına kullanıcı kimliği parametre olarak girer. İhlali test ile yakala. |
| **S-04** | **Auth** | Streamlit'in yerleşik auth'u yok; gate elle yazılır ve **`st.stop()` ile akışı kesmek zorundadır.** | Kesmiyor (R-01). | 🔴 | R-01 aksiyonu. |
| **S-05** | **Performans** | Rerun başına tüm görünür widget'lar yeniden kurulur; ağır tablo/grafik doğrudan maliyet. | plotly birincil (mevcut karar), `st.dataframe` yerleşik. | 🟢 | Yeni grafik kütüphanesi eklenmez (`streamlit-echarts` zaten "eklenmesin" kararlı). |
| **S-06** | **Deploy modeli** | Streamlit **WebSocket** üzerinden çalışır; reverse proxy / timeout / sticky session gerektirir. Tek süreç = tek bellek. | Tek container, `ports: 8501:8501`, önünde proxy yok. | 🟡 | Bugün tek kullanıcı ölçeğinde sorun değil. Proxy/TLS ihtiyacı doğarsa ayrı iş; şimdi **YAGNI**. |

### A.5 Risk Özeti

| Renk | Adet | Oran |
|---|:-:|:-:|
| 🔴 Yüksek (6+) | 10 | **%45** |
| 🟡 Orta (4-5) | 9 | %41 |
| 🟢 Düşük (≤3) | 3 | %14 |
| **Toplam** | **22** | %100 |

**En kritik 4 (skor 9):** R-01 auth geçirgen · R-02 çıkış temizlemiyor · R-03 kimlik container'a geçmiyor · U-01 panel sahte yeşil.
Dördü de **görsel iş değil, doğruluk işi.** Bu yüzden Faz 0 var.

---

## §B — Çakışma Önleyici Aksiyonlar

Her satır: **çakışma noktası → önleyici kural (sınır / sahiplik / isim alanı / sözleşme).**

### B.1 Muninn ↔ Huginn

| # | Çakışma | Kanıt | Önleyici kural |
|---|---|---|---|
| **Ç-01** | `web_dashboard/` dizini **iki ürünü birden** barındırıyor: müşteri (`index.html`, `css/`, `js/`) + admin (`tabs/`, `charts.py`). | Dizin listesi | **Sahiplik sınırı:** `web_dashboard/tabs/**` = Muninn. `web_dashboard/{index.html,css,js}` = Huginn. **Bu plan `tabs/` dışına çıkmaz.** Dizin bölünmesi ayrı iş (tek yönlü kapı, bkz. §E). |
| **Ç-02** | `web_dashboard/css/admin_tokens.css` adı "admin" diyor ama **müşteri panelinde** kullanılıyor. | `index.html` | **İsim alanı kuralı:** yeniden adlandırma şimdi yapılmaz (Huginn'i kırar). Muninn tarafında **bu dosyaya dokunulmaz**; admin stilleri yalnız `src/company_master/ui/styles.py`'dan gelir. Yanıltıcı ad `ADLANDIRMA-GERIYE-01` kapsamına yazılır. |
| **Ç-03** | `web_dashboard/js/app.js` içinde **admin fonksiyonları var**: `loadAdminPending`, `adminApprove`, `adminReject`, `adminLoadCredit`, `loadAdminCategories`, `adminSaveCategory`, `adminEditCategory`, `adminToggleCategory`, `openTasks`/`_isTaskAdmin`. Aynı iş Muninn'de de yapılıyor. | 94 fonksiyonluk tarama | **Sözleşme:** Aynı işlevin **iki arayüzü olabilir, iki iş mantığı olamaz.** Her ikisi de `web_app.py` uçlarını çağırır; iş kuralı asla istemci tarafında yazılmaz. Muninn'de yeni admin işlevi eklenirken önce "Huginn'de var mı" kontrolü. |
| **Ç-04** | Tema iki sistem: `styles.py`/`tokens.py` (Python, Muninn) ↔ `css/theme.css`+`theme.js` (Huginn). | Dosya listesi | **İsim alanı:** Muninn CSS'i `stil_enjekte(secici=…)` ile kapsamlanır; Huginn CSS dosyaları Muninn'e import edilmez. Renk SSOT'u tek: `tokens.py`. |

### B.2 Muninn ↔ `web_app.py` / Ortak API

| # | Çakışma | Kanıt | Önleyici kural |
|---|---|---|---|
| **Ç-05** | `web_app.py` (2838 satır) hem müşteri hem admin uçlarını barındırıyor. İki farklı auth: `require_api_key()` (müşteri, 193-252) vs `require_admin()` (admin, 2146-2165). | Dosya haritası | **Sözleşme:** `/api/admin/*` **yalnız** `require_admin`, diğerleri **yalnız** `require_api_key`. Yeni admin ucu eklenirse `Depends(require_admin)` zorunlu. Test: her `/api/admin/` yolunun dependency'si denetlenir (AST taraması — `test_sec_auth_01.py` deseni mevcut). |
| **Ç-06** | Muninn `scripts/dash04_api_client.py` → `post_api()` ile API'ye bağlanıyor; **panel API'siz çalışmaz**. | `admin_auth.py` | **Sınır:** Muninn'e doğrudan DB erişimi eklenmez; tek yol API. İstisna olursa gerekçe dokümante edilir. |
| **Ç-07** | `_auth_rate_guard()` (260-278) 4 auth ucuna bağlı; Muninn tarafında tekrar deneme döngüsü kurulursa 429 alır. | `web_app.py` | **Kural:** UI'da otomatik yeniden deneme yok; 429 kullanıcıya açık mesajla gösterilir (mevcut test: `test_admin_login_6_istekte_429`). |

### B.3 Port / Dizin / Bağımlılık

| # | Çakışma | Mevcut | Önleyici kural |
|---|---|---|---|
| **Ç-08** | Port tahsisi | 8000 = API+Huginn · 8501 = Muninn · 5433 = yerel PG (`localdb` profili) | **Sabit tahsis.** Yeni servis bu üçünü kullanamaz. |
| **Ç-09** | `package.json` **tamamen boş** (`dependencies: {}`, `devDependencies: {}`) | Doğrulandı | **Muninn Node bağımlılığı getirmez.** `package.json` bu planda **hiç açılmaz** — değişirse plan ihlal edilmiş demektir. |
| **Ç-10** | Python bağımlılıkları: Streamlit 1.62.0, plotly 7.0.0, altair 6.2.2 | Kurulu | **İkinci grafik kütüphanesi eklenmez.** plotly birincil (mevcut karar). `streamlit-echarts` ret kararı korunur. |
| **Ç-11** | UI bileşenleri `src/company_master/ui/components/` (11 adet: badge, button, card, dropdown, durum, input, modal, page, table, tooltip, topbar) | Mevcut | **Önce mevcut bileşen aranır.** Yeni bileşen ancak 11'inde karşılığı yoksa. Yeni bileşen aynı dizine, aynı `Bilesen` sözleşmesiyle. |
| **Ç-12** | Test dizini ortak (`tests/`), hem API hem UI hem admin | Mevcut | **İsim alanı:** Muninn testleri `tests/test_admin_*.py`. Streamlit mock'ları test başına yalıtılır (`monkeypatch` fixture — D-47). |
| **Ç-13** | Dosya kilidi: aynı dosyaya iki ajan | Pano kuralı | `gorev_ekle(..., dosyalar=[...])` zorunlu; `app.py` ve `tabs/__init__.py` **yüksek çekişmeli** — aynı anda tek görev. |

### B.4 Çakışma Özeti

13 çakışma noktası · **6'sı 🔴 aktif risk** (Ç-01, Ç-03, Ç-05, Ç-09, Ç-10, Ç-13) · 7'si kural yazımıyla kapanıyor.
**Hiçbiri kod taşıma/migration gerektirmiyor** — hepsi sınır ve sözleşme meselesi. Bu iyi haber: %0 yeniden yapım.

---

## §C — Verimlilik (YAGNI)

### C.1 Atılacak işler (yapılmayacak)

| İş | Neden atılıyor |
|---|---|
| React/Next.js/Tailwind'e geçiş | Streamlit'in yerine geçer; tüm panel yeniden yazılır. KAHİN kısıtı 3. |
| Tremor / shadcn / Untitled UI / Flowbite / Aceternity | React zorunlu + 2'si ücretli. Kısıt 1 ve 2. |
| TanStack Table | `st.dataframe` yerleşik, sıralama/filtre var. |
| `streamlit-echarts` | plotly kurulu; ikinci grafik kütüphanesi. Önceki kararla ret. |
| Figma entegrasyonu | ASCII wireframe yeterli; araç maliyeti + öğrenme süresi. |
| Cookie/DB tabanlı kalıcı oturum | Bugün tek-birkaç admin; `st.session_state` yeterli. **YAGNI** — S-01 kabul edilen davranış. |
| Reverse proxy + TLS + sticky session | Tek container, iç kullanım. İhtiyaç doğduğunda ayrı iş. |
| `web_dashboard/` dizin bölünmesi | Tek yönlü kapı; Huginn'i kırma riski. Sınır kuralıyla (Ç-01) yeterli. |
| `admin_tokens.css` yeniden adlandırma | Huginn'i kırar. `ADLANDIRMA-GERIYE-01`'e. |

**9 kalem atıldı.**

### C.2 Mevcut kod / stdlib / kurulu bağımlılıkla karşılanan

| İhtiyaç | Mevcut karşılığı |
|---|---|
| Sayfa yönlendirme | `st.navigation(..., position="hidden")` — kurulu, çalışıyor |
| Menü SSOT | `tabs/__init__.py` → `SECTIONS`, `ust_sayfalar()`, `alt_sekmeler()`, `gruplar()`, `ESKI_URL` |
| Rol filtresi | `ROL_SEVIYE`, `gorunur_bolumler(rol)` |
| Modal | `ui/components/modal.py` → `Modal(...).streamlit(govde_fn=…)` |
| Sağ-alt profil menüsü | `st.popover` **yerleşik** — `_hesap_karti_popover()` (`app.py:369-399`) zaten var, konumu/içeriği düzeltilecek |
| Tasarım jetonları | `ui/tokens.py` (Indigo #6366f1 SSOT) |
| CSS enjeksiyonu | `ui/styles.py` → `tum_css()`, `stil_enjekte()` |
| Grafik | plotly 7.0.0 + altair 6.2.2 (kurulu) |
| Tablo | `st.dataframe` (yerleşik) |
| Önbellek | `@st.cache_data(ttl=…)` (yerleşik) |
| Webhook metrikleri | `/api/webhooks/apify/metrics` **zaten var** (`web_app.py:442`) → U-01'in çözümü yeni kod değil, **bağlama** işi |
| Şifre değiştirme | `/api/admin/change-password` + `render_sifre_degistir()` mevcut |
| Testler | pytest + `monkeypatch`; `test_style_css.py`, `test_admin_auth_login.py` desenleri hazır |

**13 ihtiyacın 13'ü mevcut araçlarla karşılanıyor.**

### C.3 Gerçekten yeni kod isteyen

| İş | Tahmini boyut | Neden kaçınılmaz |
|---|---|---|
| `st.stop()` + ikinci kapı (R-01) | ~5 satır | Güvenlik; mevcut kodda yok |
| Oturum temizliği yeniden yazımı (R-02) | ~15 satır | Mevcut 3 anahtarlık temizlik yetersiz |
| `env_file: .env` + yorum düzeltme (R-03, O-01) | ~2 satır YAML | Yapılandırma hatası |
| Profil popover içeriği + konum (KAHİN madde 2) | ~80 satır | `st.popover` var ama içerik/konum/deep-link yok |
| Menü ağacı yeniden gruplama (KAHİN madde 3) | `SECTIONS` veri düzenlemesi | Veri değişimi, mantık değil |
| `admin_kullanici_ayarlari.py` (KAHİN madde 4) | ~120 satır | Sayfa yok |
| Webhook kartı gerçek veriye bağlama (U-01) | ~20 satır | Placeholder yerine mevcut uç |
| Testler | ~150 satır | Test edilmemiş iş teslim edilmez |

### C.4 Yeni bağımlılık

**Önerilen yeni bağımlılık: 🟢 YOK (0 adet, 0 ₺).**
Gerekçe/alternatif tablosu doldurulmasına gerek kalmadı — C.2'de 13/13 karşılandı.

---

## §D — Teslim Planı

Süreler saat cinsinden: **İyimser / Beklenen / Kötümser.**

### Faz 0 — Doğruluk Onarımı ( her şeyden önce)

**Neden ilk:** Görsel iş, güvenli olmayan bir panelin üstüne yapılırsa yanlış güven üretir. 4 adet skor-9 riskin 3'ü burada kapanır.

| # | İş | Dosya | İ / B / K |
|---|---|---|---|
| 0.1 | Auth gate `st.stop()` + `render_icerik()` ikinci kapı (R-01) | `app.py` | 0,5 / 1 / 2 |
| 0.2 | `env_file: .env` + "legacy" yorumu düzelt (R-03, O-01) | `docker-compose.yml` | 0,25 / 0,5 / 1 |
| 0.3 | Restart tek kural dokümantasyonu (O-02) | `docs/AJAN_DETAY.md` §20 | 0,25 / 0,5 / 1 |
| 0.4 | `test_mcp_transport.py` toplama hatası (R-07) | `tests/` | 0,5 / 1 / 3 |
| 0.5 | Testler: token'sız erişim engellendi mi | `tests/test_admin_auth_gate.py` (yeni) | 1 / 1,5 / 2,5 |
| | **Faz 0** | | **2,5 / 4,5 / 9,5** |

**Bitti kriteri:** Token'sız istekte sayfa gövdesi render **edilmiyor** (test kanıtı) · Docker'da giriş çalışıyor · süit yeşil · `kodlama_denetim.py` temiz.

---

### Faz 1 — Oturum/Çıkış Senkronu (`ADMIN-UX-LOGOUT-01`, P0)

| # | İş | Dosya | İ / B / K |
|---|---|---|---|
| 1.1 | `admin_cikis()` tam temizlik + cache temizliği (R-02) | `admin_auth.py` | 0,5 / 1 / 2 |
| 1.2 | Çıkış sonrası anında `st.rerun()` + giriş ekranı | `app.py`, `admin_auth.py` | 0,5 / 1 / 2 |
| 1.3 | Giriş akışını bozmama regresyon testi | `tests/test_admin_auth_login.py` | 0,5 / 1 / 2 |
| | **Faz 1** | | **1,5 / 3 / 6** |

**Bitti kriteri:** Çıkışta sayfa yenilemeden giriş ekranı · `session_state` içinde token/e-posta kalmıyor · mevcut 49 giriş testi yeşil.
**Bağımlılık:** Faz 0 (0.1 ile aynı dosya).

---

### Faz 2 — Sağ-Alt Profil Popover (`ADMIN-UX-PROFILMENU-01`, P0)

**Ön koşul: wireframe onayı (K-4).**

| # | İş | Dosya | İ / B / K |
|---|---|---|---|
| 2.1 | Wireframe (popover ASCII + deep-link haritası) | `docs/UX_PROFIL_POPOVER_WIREFRAME_*.md` | 0,5 / 1 / 1,5 |
| 2.2 | `_hesap_karti_popover()` konum + içerik: admin bilgisi, Ayarlar, Şifre Değiştir, Dil, Yardım, Çıkış | `app.py` veya `ui/components/profil_menu.py` | 2 / 3,5 / 6 |
| 2.3 | Deep-link: her madde ilgili sayfa+bölüme (`url_path` + anchor) | `app.py`, `tabs/__init__.py` | 1 / 2 / 4 |
| 2.4 | İkon seti: sade, monokrom, küçük (CSS/emoji; yeni paket yok) | `ui/styles.py` | 0,5 / 1 / 2 |
| 2.5 | Testler | `tests/test_admin_profil_menu.py` (yeni) | 1 / 1,5 / 3 |
| | **Faz 2** | | **5 / 9 / 16,5** |

**Bitti kriteri:** Popover sağ-alta yakın, sağa açılıyor · 6 madde çalışıyor · her madde doğru bölüme gidiyor · çıkış Faz 1 akışını kullanıyor.
**Bağımlılık:** Faz 1 (çıkış maddesi).

---

### Faz 3 — Menü Ağacı (`ADMIN-UX-MENUTREE-01`, P1)

**Ön koşul: `UX_MENU_AGACI_WIREFRAME_2026-09-18.md` onayı (K-5).**

| # | İş | Dosya | İ / B / K |
|---|---|---|---|
| 3.1 | `SECTIONS` yeniden gruplama: 6 üst/23 alt → 5 üst/18 alt | `tabs/__init__.py` | 1,5 / 3 / 5 |
| 3.2 | Menüden "Ayarlar" kaldır (U-03) | `tabs/__init__.py` | 0,25 / 0,5 / 1 |
| 3.3 | `ESKI_URL` haritası — kırılan bağlantı yok (R-06) | `tabs/__init__.py` | 0,5 / 1 / 2 |
| 3.4 | `render_sidebar()` grup başlıkları | `app.py` | 1 / 1,5 / 3 |
| 3.5 | Testler: her `SECTIONS` girdisi çözümleniyor + eski URL yönleniyor | `tests/test_menu_agaci.py` (yeni) | 1 / 1,5 / 3 |
| | **Faz 3** | | **4,25 / 7,5 / 14** |

**Bitti kriteri:** 5 üst/18 alt · eski URL'ler yönleniyor · "Ayarlar" menüde yok (yalnız popover'da).
**Bağımlılık:** Faz 2 (Ayarlar yalnız popover'da kalmalı — **yarım bırakılmaz**).

---

### Faz 4 — Kullanıcı Ayarları Sayfası (`ADMIN-UX-AYARLAR-SAYFA-01`, P1)

| # | İş | Dosya | İ / B / K |
|---|---|---|---|
| 4.1 | Wireframe | `docs/UX_KULLANICI_AYARLARI_WIREFRAME_*.md` | 0,5 / 1 / 1,5 |
| 4.2 | Sayfa: profil + şifre değiştir + sıfırla (mevcut uçlar) | `tabs/admin_kullanici_ayarlari.py` (yeni) | 2 / 3,5 / 6 |
| 4.3 | `SECTIONS` kaydı + popover deep-link bağlama | `tabs/__init__.py`, `app.py` | 0,5 / 1 / 2 |
| 4.4 | Testler | `tests/test_admin_kullanici_ayarlari.py` (yeni) | 1 / 1,5 / 3 |
| | **Faz 4** | | **4 / 7 / 12,5** |

**Bitti kriteri:** Admin profilini ve şifresini tek sayfadan yönetiyor · popover'dan buraya deep-link çalışıyor.
**Bağımlılık:** Faz 2 (deep-link hedefi) + Faz 3 (menü kaydı).

---

### Faz 5 — Ana Sayfa Doğruluğu + Yerleşim (U-01, U-02)

**Ön koşul: `UX_ANA_SAYFA_WIREFRAME_2026-09-18.md` onayı (K-5).**

| # | İş | Dosya | İ / B / K |
|---|---|---|---|
| 5.1 | `load_webhook_stats()` → `/api/webhooks/apify/metrics` gerçek veri (U-01) | `tabs/ana_kontrol.py` | 1 / 2 / 4 |
| 5.2 | Veri yoksa "veri yok", sahte `st.success` kaldırılır | `tabs/ana_kontrol.py` | 0,5 / 1 / 2 |
| 5.3 | Onaylı wireframe yerleşimi (6 şerit, plotly) | `tabs/ana_kontrol.py` | 2 / 4 / 7 |
| 5.4 | 3 durum (yükleniyor/boş/hata) + kontrast ≥4.5:1 | `ui/styles.py`, `ana_kontrol.py` | 1 / 2 / 4 |
| 5.5 | Testler | `tests/test_ana_kontrol.py` | 1 / 1,5 / 3 |
| | **Faz 5** | | **5,5 / 10,5 / 20** |

**Bitti kriteri:** Hiçbir kart sahte veri göstermiyor · boş durum açıkça "veri yok" · wireframe'e uygun.

---

### D.1 Toplam ve Kritik Yol

| Faz | İyimser | Beklenen | Kötümser |
|---|---:|---:|---:|
| 0 — Doğruluk | 2,5 | 4,5 | 9,5 |
| 1 — Çıkış | 1,5 | 3,0 | 6,0 |
| 2 — Popover | 5,0 | 9,0 | 16,5 |
| 3 — Menü | 4,25 | 7,5 | 14,0 |
| 4 — Ayarlar sayfası | 4,0 | 7,0 | 12,5 |
| 5 — Ana sayfa | 5,5 | 10,5 | 20,0 |
| **TOPLAM** | **22,75 sa** | **41,5 sa** | **78,5 sa** |
| **≈ gün (8 sa)** | **~3 gün** | **~5 gün** | **~10 gün** |

**Kritik yol:** `Faz 0 → Faz 1 → Faz 2 → Faz 3 → Faz 4`. Beşi de zincirli, paralelleşmiyor (hepsi `app.py` veya `tabs/__init__.py`'ye dokunuyor → Ç-13 kilit çekişmesi).
**Faz 5 tek paralelleşebilir iş** — yalnız `ana_kontrol.py`'ye dokunur, Faz 1'den sonra bağımsız yürütülebilir.

> ⚠️ İlk tur "~18,5 sa ≈ 2,5 gün" diyordu. Gerçekçi beklenen **41,5 sa ≈ 5 gün** — **%124 sapma.** Sebep: ilk tur yalnız görsel işi sayıyordu; Faz 0 ve testler hesapta yoktu.

### D.2 İlk Teslim Dilimi Önerisi

**Faz 0 + Faz 1 = 4 / 7,5 / 15,5 sa ≈ 1 gün.**
Çıktı: panel **güvenli** (token'sız içerik sızmıyor), **çıkış doğru çalışıyor**, Docker'da **giriş çalışıyor**. Görsel değişiklik yok ama 4 skor-9 riskin 3'ü kapanıyor.

---

## §E — Geri Dönüş Planı

### E.1 Faz Bazlı Geri Alma

| Faz | Geri alma yolu | Süre | Veri kaybı |
|---|---|---|---|
| 0 | `git revert` — 3 dosya, şema/veri dokunulmadı | ~5 dk | Yok |
| 1 | `git revert` — `admin_auth.py` + `app.py` | ~5 dk | Aktif oturumlar düşer (kabul) |
| 2 | `git revert` — popover yeni dosya/blok, izole | ~10 dk | Yok |
| 3 | 🟠 `git revert` **+ `ESKI_URL` haritası korunmalı** — kullanıcı yer imleri yeni URL'ye alışmış olabilir | ~20 dk | Yer imleri kırılabilir |
| 4 | `git revert` — yeni dosya sil + `SECTIONS` satırı geri | ~10 dk | Yok |
| 5 | `git revert` — tek dosya | ~5 dk | Yok |

### E.2 Tek Yönlü Kapılar (geri dönülemez / pahalı)

| # | Karar | Neden tek yönlü | Bu planda? |
|---|---|---|---|
| **TY-1** | `web_dashboard/` dizinini Muninn/Huginn olarak bölmek | Import yolları, Docker mount, `serve_dashboard()` yolu, tüm testler kırılır | ❌ **YAPILMIYOR** (Ç-01 sınır kuralıyla) |
| **TY-2** | Streamlit'ten React/Next.js'e geçiş | Tüm panel yeniden yazılır; dönüş yok | ❌ **YAPILMIYOR** |
| **TY-3** | `url_path` yeniden adlandırma (Faz 3) | Dış bağlantılar/yer imleri kırılır; `ESKI_URL` olmadan telafisi yok | 🟠 **YAPILIYOR** — zorunlu azaltma: her yeniden adlandırma **aynı commit'te** `ESKI_URL` satırı ile |
| **TY-4** | Menüden "Ayarlar"ı kaldırmak | Kullanıcı alışkanlığı; popover olmadan admin ayarlarına ulaşamaz | 🟠 **YAPILIYOR** — Faz 3, **yalnız Faz 2 bittikten sonra**. Sıra bozulursa admin kilitlenir. |
| **TY-5** | `.env` içine `ADMIN_PASSWORD` yazan `_env_sifre_guncelle()` | Dosyaya yazar, eski değer kaybolur | 🟡 Mevcut davranış — dokunulmuyor, ama Faz 4'te farkında olunmalı |
| **TY-6** | DB şema değişikliği | Migration geri alma pahalı | ❌ **YOK** — bu planda şema değişmiyor |

**Özet:** 6 tek yönlü kapıdan **4'ü hiç açılmıyor**, 2'si (TY-3, TY-4) açılıyor ama zorunlu azaltma kuralıyla bağlı.

### E.3 Genel Güvenlik Ağı

- Her faz **tek commit**, faz adı commit mesajında.
- Faz başında dal (`branch`) mevcut; `chore/monorepo-merge` üzerinde çalışılıyor.
- Her faz sonunda **tam süit** çalıştırılır; kırmızı ile sonraki faza geçilmez.
- `kodlama_denetim.py` temiz olmadan teslim yok.

---

## §F — Karar Noktaları (KAHİN onayı gereken yerler)

| # | Karar | Ne zaman | KAHİN'e lazım olan bilgi | Onay yoksa ne olur |
|---|---|---|---|---|
| **K-1** | **Bu planı onayla, Faz 0 başlasın** | Şimdi | Bu doküman + §A risk tablosu. Faz 0 görsel değişiklik getirmez, güvenlik ve doğruluk onarır. | 4 görevlik zincir 8. tura erteleniyor; panel token'sız erişime açık kalıyor |
| **K-2** | **Docker: `./web_dashboard` mount edilsin mi?** | Faz 0 (0.2) | **Seçenek A:** mount eklenir → geliştirmede anında yansır, prod'da image dışı dosyaya bağımlılık. **Seçenek B:** mount yok → her değişiklikte `--build` (~1-2 dk). **Önerim: B** (prod tutarlılığı; yerelde zaten `streamlit_restart.py` var) | Faz 0 yarım kalır, R-04 açık kalır |
| **K-3** | **Oturum kalıcılığı: container restart'ta oturumlar düşsün mü?** | Faz 1 öncesi | **Seçenek A (önerim):** Düşsün — kabul edilen davranış, 0 ek kod, güvenli hata. **Seçenek B:** Cookie/DB token → +6-12 sa, yeni güvenlik yüzeyi. YAGNI diyorum. | Faz 1 kapsamı belirsiz |
| **K-4** | **Profil popover wireframe onayı** | Faz 2 başı | ASCII wireframe + 6 maddenin deep-link hedef tablosu (üretilecek) | Faz 2 başlamaz (wireframe kuralı) |
| **K-5** | **Bekleyen 2 wireframe onayı** (`UX_MENU_AGACI_*`, `UX_ANA_SAYFA_*`) | Faz 3 ve Faz 5 öncesi | İki doküman hazır, onay bekliyor | Faz 3 ve Faz 5 bloke |
| **K-6** | **U-01: sahte veri ne olsun?** | Faz 5 (5.1) | **Seçenek A (önerim):** `/api/webhooks/apify/metrics` gerçek veriye bağla (~2 sa). **Seçenek B:** Kartı tamamen kaldır. **Seçenek C:** "Veri yok" durumuna al (~0,5 sa). Kabul edilemez olan tek şey mevcut durum: hep yeşil. | Panel yanlış güven üretmeye devam eder |
| **K-7** | **Faz 5 paralel yürüsün mü?** | Faz 1 sonrası | Faz 5 tek dosyaya dokunuyor (`ana_kontrol.py`), kilit çakışması düşük. Paralel = takvim ~1 gün kısalır. | Seri devam; sorun değil |

**Acil olan tek karar: K-1.** Diğerleri ilgili faz geldiğinde sorulur.

---

# 3) Fark Listesi — İlk Tur ↔ İkinci Tur

| # | Konu | İlk tur | İkinci tur | Neden değişti |
|---|---|---|---|---|
| **F-01** | **Kapsam** | Müşteri paneli (Huginn, vanilla JS, 8000) | **Admin paneli (Muninn, Streamlit, 8501)** | KAHİN: "stermit" = Streamlit; müşteri paneli kapsam dışı |
| **F-02** | **Dosyalar** | `index.html`, `style.css`, `app.js` | `app.py`, `web_dashboard/tabs/**`, `docker-compose.yml`, `ui/` | Kapsam değişti; dosya kümesi tamamen farklı |
| **F-03** | **A1-A9 adım tablosu** | 9 adım, ~18,5 sa | **Tamamen düştü** | Huginn dosyalarına aitti |
| **F-04** | **Faz 0 (Doğruluk Onarımı)** | ❌ Yoktu | ✅ **Eklendi, ilk sıraya** | 4 adet skor-9 risk bulundu; görsel işten önce doğruluk |
| **F-05** | **Risk envanteri** | ❌ Yoktu | ✅ **22 risk, O×E skorlu** | KAHİN'in 1. zorunlu başlığı |
| **F-06** | **Streamlit'e özgü riskler** | ❌ Yoktu | ✅ **6 madde ayrı başlık (S-01…S-06)** | KAHİN'in açık talebi |
| **F-07** | **Çakışma analizi** | ❌ Yoktu | ✅ **13 çakışma + önleyici kural** | KAHİN'in 2. zorunlu başlığı |
| **F-08** | **Süre tahmini** | 18,5 sa (tek sayı) | **22,75 / 41,5 / 78,5 sa (3 senaryo)** | Tek sayı sahte kesinlik; Faz 0 + testler hesapta yoktu. **Sapma %124** |
| **F-09** | **Geri dönüş planı** | ❌ Yoktu | ✅ **Faz bazlı + 6 tek yönlü kapı** | KAHİN'in 5. zorunlu başlığı |
| **F-10** | **Karar noktaları** | Tek onay ("A1-A4 yazayım mı") | **7 karar noktası, seçenekli** | KAHİN'in 6. zorunlu başlığı |
| **F-11** | **Yeni paket kararı** | 0 paket | **0 paket (değişmedi)** | ✅ Tek taşınan sonuç. Gerekçe değişti: React uyumsuzluğu, ücret değil |
| **F-12** | **Auth durumu** | "Çalışıyor varsayıldı" | **🔴 Gate geçirgen (kanıt: `app.py:728`)** | Kod okundu, varsayım yıkıldı |
| **F-13** | **Ana sayfa verisi** | "Gerçek varsayıldı" | **🔴 Placeholder, hep 0 (kanıt: `ana_kontrol.py:68-84`)** | Kod okundu |
| **F-14** | **Docker durumu** | "Legacy profil, opsiyonel" | **🔴 Ana profil + `env_file` eksik + mount eksik** | `docker-compose.yml` tamamı okundu |
| **F-15** | **Faz sırası** | Görsel → test | **Güvenlik → çıkış → popover → menü → ayarlar → görsel** | TY-4: popover bitmeden menüden Ayarlar kaldırılırsa admin kilitlenir |

**15 fark · 11'i ikinci turda ortaya çıkan yeni bilgi · 4'ü doğrudan yanlış varsayım düzeltmesi.**

**İkinci turun net kazancı:** 4 adet skor-9 hata (auth geçirgen, çıkış temizlemiyor, Docker kimlik eksik, panel sahte yeşil) **kod yazılmadan önce** yakalandı. İlk tur olduğu gibi uygulansaydı dördü de görsel işin altına gömülecekti.

---

# 4) KAHİN (Ürün Sahibi) Özeti

| Renk | Bulgu | Oran / Sayı |
|---|---|---|
| 🟢 | Yeni paket **gerekmiyor**, para harcanmıyor | **0 paket · 0 ₺** |
| 🟢 | İhtiyaçların tamamı elimizdeki araçlarla karşılanıyor | **13/13 · %100** |
| 🟢 | 9 iş kalemi gereksiz bulundu ve atıldı | **9 kalem atıldı** |
| 🟢 | Tek yönlü (geri dönülemez) kararların çoğu hiç açılmıyor | **6'dan 4'ü · %67 kapalı** |
| 🟡 | Risklerin yarısına yakını yüksek seviyede | **10/22 · %45 kırmızı** |
| 🟡 | Gerçek süre ilk tahminin iki katından fazla | **18,5 sa → 41,5 sa · +%124** |
| 🟡 | Fazlar birbirine bağlı, paralel çalışılamıyor | **6 fazdan 5'i zincirli · %83** |
| 🔵 | 13 çakışma noktasının hepsi kural yazımıyla kapanıyor | **%0 yeniden yapım** |
| 🔵 | İlk teslim dilimi kısa: panel güvenli hale gelir | **~1 gün (Faz 0 + Faz 1)** |
| 🔴 | **Panel giriş yapılmadan içerik gösterebiliyor** | Güvenlik açığı · skor **9/9** |
| 🔴 | **Çıkış yapınca eski bilgiler ekranda kalıyor** | Skor **9/9** |
| 🔴 | **Docker'da admin şifresi panele hiç ulaşmıyor** | Skor **9/9** |
| 🔴 | **Ana sayfa her koşulda "her şey yolunda" diyor** — veri sahte, hep sıfır | Skor **9/9** · yanlış güven |

### Bir cümlelik sonuç

Panel **görsel olarak değil, doğruluk olarak** bozuk: giriş kapısı kapanmıyor, çıkış temizlemiyor, Docker'da şifre geçmiyor ve ana sayfa sahte "yeşil" gösteriyor — bu dördü **1 günde** kapanır, görsel işler ondan sonra sağlam zemine oturur.

### Şimdi ne bekliyorum

**Tek onay: K-1.** "Faz 0 + Faz 1 başlasın" dersen, o gün panel güvenli hale gelir. Diğer 6 karar noktası ilgili faz geldiğinde ayrıca sorulacak.

---

**Not:** Bu dokümanda kod yazılmadı, paket kurulmadı, hiçbir dosya değiştirilmedi. Tüm bulgular `app.py`, `docker-compose.yml`, `web_dashboard/tabs/`, `web_app.py`, `package.json` dosyalarından **okunarak** doğrulandı.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
