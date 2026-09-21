# REV-BATCH-01 Çapraz İnceleme Raporu (cline — 2026-09-16)

**Kaynak:** commit `feea800` (dal `chore/monorepo-merge`, PR #14) · **Kapsam:** AUTH-GATE-01 + NAV-IA-01 + NAV-IA-02
**Mod:** YALNIZ OKU (kilo BATCH-02 ile aynı dosyalarda) — **hiçbir dosya değiştirilmedi; düzeltme yok.**

## Doğrulama
- Hedefli testler (test_auth_gate + test_dashboard_nav + test_musteri_yonetimi + test_admin_auth_login + test_api_integration): **183 passed** (15.3 sn)
- `kodlama_denetim --kapsam git`: **temiz** (BOM/NUL/mojibake yok)

## Bulgu Tablosu

| # | Bulgu | Seviye | Dosya:satır | Öneri |
|---|-------|--------|-------------|-------|
| Y-1 | **Auth uçlarında rate-limit yok.** `_RATE_LIMIT` yalnız tier/API-key dependency akışında (772-784) işliyor; POST login/reset-request/reset-confirm/change-password imzalarında limit dependency'si yok; global middleware yalnız (816). Brute-force/enum saldırısı sınırsız. | **YÜKSEK** | web_app.py:2487,2519,2532,2565 | IP bazlı sıkı limit (ör. 5/dk) dependency'si; `src/company_master/api/rate_limiter.py` yeniden kullanılabilir |
| Y-2 | **Kullanıcı var/yok sızması.** login: bilinen-user değil-admin → 403 "admin yetkisi gerekli", bilinen-admin yanlış şifre → 401 "gecersiz sifre", bilinmeyen → 401 "gecersiz email veya sifre"; reset-request: bilinmeyen → 404 "admin bulunamadi". Brief'in açık şartı: "kullanıcı var/yok ayrımı yapılmamalı". | **YÜKSEK** | web_app.py:2500-2516, 2525-2528 | login her durumda tek 401 mesajı; reset-request bilinmeyen emailde de `ok:true` (token sessizce atılır); UI tarafındaki `st.error(f"...{exc}")` aynı nedenle sızdırıyor |
| Y-3 | **`_env_kimlik()` DEBUG kapısı yok.** Brief şartı "`_env_kimlik` yalnız DEBUG=1"; kod her ortamda ADMIN_EMAIL/ADMIN_PASSWORD ile formu ön-dolduruyor (`value=env_sifre`) ve "🔐 Kimlik .env'den ön-dolduruldu" caption'ı bastırıyor. | **YÜKSEK** | web_dashboard/tabs/admin_auth.py:12-26,70-76 | `if os.getenv("DEBUG") != "1": return ("admin@huginn.local", "")`; caption yalnız DEBUG'da |
| Y-4 | **Misafir akışı ROL_ADMIN veriyor.** Misafir butonu `st.session_state["admin_token"] = "guest"` yazıyor (app.py ~716); `aktif_rol()` `admin_token dolu ⇒ ROL_ADMIN` diyor (app.py:151). Misafir tüm admin menüsünü görür (API 403'le dursa da U-10 filtresi UI'da aşılmış olur). `render_admin_login` guest'te "🔓 Oturum açık" + admin menü sayısı gösteriyor. | **YÜKSEK** | app.py:151, 714-719; admin_auth.py:62-68,49-56 | Ayrı anahtar kullan (`misafir=True`); `get_admin_token()` misafirde None döndürsün; aktif_rol `"guest"`i anon'a indirgesin |
| O-1 | **ESKI_URL ölü yönlendirme.** `kimlik` ve `yonetim` hâlâ SECTIONS'ta (ust=None); `tab_url_getir` önce SECTIONS'a baktığı için ESKI_URL'deki "kimlik"→(ana_kontrol) ve "yonetim"→(musteri_yonetimi) girdileri **hiç çalışmıyor**; eski `?kimlik` URL'i eski login sayfasını açıyor. Plan v4 "kimlik/yonetim SECTIONS'tan çıkarılır" uygulanmamış. Test de fonksiyonu tek başına test ediyor (maskeleniyor). | **ORTA** | tabs/__init__.py:416-426,462-474,548-561; app.py:757 | İki tanımı SECTIONS'tan çıkar (URL'ler ESKI_URL'e düşer) ya da tab_url_getir'de ESKI_URL önceliği; parametrik testi `tab_url_getir` üzerinden yaz |
| O-2 | **GET /api/admin/login kaldırılmış** (yalnız @app.post 2487). Brief şartı "GET login geriye dönük"; `scripts/admin_login_probe.py:32` (D-24 teşhis aracı) GET kullanıyor → şimdi 405. | **ORTA** | web_app.py:2487; scripts/admin_login_probe.py:32 | GET'i deprecated olarak geri koy ya da probe'u POST'a çevir + rapor/docs notu |
| O-3 | **K-1 "tier JSON konfigürasyon" iddiası gerçek değil.** `TIER_SECIMLERI` sabit liste; repo genelinde *tier*.json yok. Test adı `test_tier_secimler_json_konfigurasyon` ama yalnız sabit listeyi doğruluyor — yanıltıcı. | **ORTA** | admin_extras.py:9-10; tests/test_musteri_yonetimi.py:24-28 | Gerçekten config JSON'a taşı ya da yorum/test adını düzelt ("sabit modül listesi") |
| O-4 | **Auth testleri AST seviyesinde.** test_auth_gate.py 6 testin hepsi "fonksiyon var mı / string geçiyor mu"; 403/401 ayrımı, token süresi, tek kullanım, rate-limit davranışı test edilmiyor. roo'nun "CI'da login/reset testleri düşmüş olabilir" notu doğrulandı (yalnız rota-method sözleşme testi var). | **ORTA** | tests/test_auth_gate.py:24-116; tests/test_api_integration.py:59-63 | TestClient + dev_modu fixture ile uç testleri (mevcut kalıp test_api_companies.py'de var) |
| O-5 | **Plan v4 sidebar temizliği uygulanmamış.** Hierarchik menü (ust_sayfalar+alt_sekmeler) eklenmiş AMA planın "çıkarılacaklar" listesi duruyor: Hızlı geçiş selectbox, Kompakt toggle, Marka Blogu placeholder (çift navigasyon). | **ORTA** | app.py:445-478,490-505 | BATCH-02 kapsamı mı? teyit; çıkarılacaksa plana göre çıkar |
| D-1 | **secrets.toml plaintext fallback.** DB'de admin yoksa `.streamlit/secrets.toml` `admin_password` düz metin `==` ile karşılaştırılıyor; DB satırı VARSA fallback hiç ulaşılmıyor (D-24 senaryosunda tekrar kilitlenme). `.gitignore`'da `.streamlit/secrets.toml` girdisi yok (dosya şu an yok, risk potansiyel). | **DÜŞÜK** | web_app.py:2506-2515; .gitignore | Hash tabanlı fallback ya da kaldır; `.gitignore`'a ekle |
| D-2 | **Kompakt mod sütun hatası.** Her üst/alt buton için `st.columns(KOMPAKT_SUTUN)[0]` açılıyor → her buton kendi 4 sütunlu satırında (U-04/U-05 eleştirisi sürüyor). | **DÜŞÜK** | app.py:492-560 | Grid döngüsü dışında tek columns; ya da kompakt modu st.navigation'a bırak |
| D-3 | **bekleyen_gorev etiketi tutarsız.** `musteri_yonetimi` üst sayfası `hazir=False, bekleyen_gorev="NAV-IA-01"`; ama kompozit sayfa içeriği NAV-IA-02/BATCH-02 kapsamında. | **DÜŞÜK** | tabs/__init__.py:529-531 | Etiketi NAV-IA-02 (veya BATCH-02) yap |
| D-4 | `change-password` yeni şifreyi `.strip()` ediyor → baş/son boşluklu şifreler sessizce bozulur (login ise strip etmiyor → tutarsızlık). | **DÜŞÜK** | web_app.py:2578-2579 | Strip kaldır veya login'de de uygula; dokümante et |

## Şart–Karşılaştırma (brief kontrol listesi)

| Kontrol | Sonuç |
|---|---|
| Modal `dismissible=False` (kapatilabilir=False) | ✅ modal.py:171 `dismissible=not self.kapatilabilir` |
| Misafir akışı | ⚠️ var ama rol sızıntısı — Y-4 |
| Reset token süresi / tek kullanım | ✅ TTL 3600 sn (web_app.py:2117); confirm'te reset_token=NULL (2556) |
| Şifre loglanmıyor | ✅ (web_app + UI'da print/log yok; probe yalnız "var/YOK") |
| `_env_kimlik` yalnız DEBUG=1 | ❌ Y-3 |
| GET login geriye dönük | ❌ O-2 |
| 6 üst sayfa | ✅ ana_kontrol, musteri_yonetimi, proje_yonetimi, veri_kalite, sistem, musteri_onizleme (571-573) |
| kimlik/yonetim/sistem menüde yok | ✅ sidebar (UST_SAYFA_ANAHTARLARI filtresi) · ❌ SECTIONS'tan çıkarılmamış (O-1) |
| Eski URL yönlendirme | ⚠️ yalnız "kullanicilar" çalışıyor — O-1 |
| ROL_SEVIYE alt sekmelerde | ✅ alt_sekmeler/ust_sayfalar `erisebilir` filtresi (594, 580) |
| 6 alt sekme | ✅ musteri_yonetimi.py:22-29 (2 tanesi DATA-LOG-01 "yakında") |
| Tier JSON'a doğru gidiyor | ⚠️ tier gövdede gidiyor ✓ ama konfig sabit — O-3 |
| Section deseni | ✅ BOLUMLER + PageHeader |
| Grafik yalnız charts.py | ✅ (plotly/px./go. geçmiyor) |
| Rate-limit yeni uçlarda | ❌ Y-1 |
| Hata mesajı sızıntısı | ❌ Y-2 |
| CI davranışsal kapsam | ❌ O-4 (rota sözleşme testi ✓) |
| Mojibake/BOM | ✅ temiz |

## Pozitifler
- SSOT menü ağacı temiz: UST_SAYFA_ANAHTARLARI + ust/sira alanlarıyla sidebar hiyerarşisi test edilebilir saf veri.
- Rol filtresi hem üst hem alt sekmelerde tutarlı (erisebilir + rol_normalize, bilinmeyen rol anon'a düşer).
- Reset token: UUID4 + TTL + tek kullanım + hash güncelleme doğru.
- `test_admin_auth_login.py` UI'nin POST+JSON kullanmasını zorluyor (get_api yasak) — yönlendirme iyi.

## Dikkat (eleştirel notlar) — defter önerileri (işleme: kilo/roo toplu değerlendirme)
- **M-07 önerisi:** auth uçlarına ortak rate-limit dependency (rate_limiter.py yeniden kullan).
- **M-08 önerisi:** kimlik/yonetim SECTIONS'tan çıkarılsın; ESKI_URL testleri tab_url_getir entegrasyonuyla yazılsın.
- **S-11 önerisi:** misafir akışı ROL_KEY üzerinden; `admin_token="guest"` hack'i kaldırılsın.
- **S-12 önerisi:** auth uçlarına davranışsal TestClient testleri (403/401, TTL, tek kullanım, 429).
- **D-31 önerisi:** "JSON konfigürasyon" iddiası ya gerçek dosyaya bağlansın ya adlandırma (yorum+test adı) düzeltilsin.

## Eksik / Erteleme
- Düzeltme YAPILMADI (brief: yalnız oku; kilo BATCH-02 aynı dosyalarda). Y-1..Y-4 için BATCH-02 sonrası ayrı görev önerilir.
- O-2 (GET login): kilo BATCH-02'de probe'u düzeltecek mi — teyit edilmeli.
- O-5: sidebar temizliğinin BATCH-02 kapsamında olup olmadığı teyit edilmeli.