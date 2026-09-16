# NAV-PLAN-01 v4 — Muninn Paneli Navigasyon ve Giriş Kapısı Sentezi

- **Görev:** SENTEZ-01 (orkestratör: roo)
- **Tarih:** 2026-09-16
- **Durum:** Sahip onaylı tasarım (v4) + kod öncesi revize listesi. Kod yazılmadı.
- **Kaynaklar:** NAV-PLAN-01 v4 sahip onayı (D-25…D-29), sahibin panel kontrol turu (4 bulgu), `web_dashboard/tabs/__init__.py` mevcut 28 bölüm envanteri, cline bulguları (`REV-MVP-ADMIN-01`, `UI-MODAL-01`), `docs/plans/UI-CHART-01_arastirma.md`, D-30 (iletişim protokolü düzeltmesi).
- **Kapsam dışı:** Huginn müşteri yüzeyi (8000) ve web_app API'nin genel yapısı. Yalnız AUTH-GATE-01 için 2 yeni admin endpoint eklenir.

---

## 0. Sözlük (kod adı → ne demek)

| Kod | İki kelime | Ne ile ilgili |
|---|---|---|
| NAV-PLAN-01 v4 | Menü tasarımı | Muninn panelinin sol menüsünün 28 dağınık sayfadan 6 üst sayfaya indirilmesi. Sahip onayladı; bu belge onun yazılı hali. |
| SENTEZ-01 | Bu belge | Onaylı tasarım + kod envanteri + cline bulgularını tek dosyada birleştirme. Kod işine girmeden önce "neyi, hangi sırayla" listesi çıkarır. |
| NAV-FIX-01 | Çift tık düzeltme | Menüde bir sayfaya iki kez tıklamak gerekiyor; kök nedeni "Hızlı geçiş" kutusunun eski değeri. Tek tıkta geçiş sağlanır. |
| NAV-FIX-02 | Tooltip kaldırma | Menü düğmelerinin üzerine gelince çıkan açıklama balonları rahatsız ediyor. Kaldırılır, bilgi sayfa içine taşınır. |
| AUTH-GATE-01 | Giriş kapısı | Panel açılınca kapatılamayan giriş penceresi (modal): giriş yap / misafir devam et / şifremi unuttum. Şifre sıfırlama API'si de burada. |
| NAV-IA-01 | Menü ağacı | `TabTanimi`'ne "üst sayfa" alanı eklenir; 6 üst sayfa + alt sekmeler kodlanır. Eski adresler yeni yere yönlendirilir. |
| NAV-IA-02 | Müşteri Yönetimi | Kullanıcılar, paket/kredi, giriş etkinliği, aramalar, destek ve dışa aktarma tek sayfada alt sekme olur. |
| NAV-IA-03 | Proje Yönetimi | Karar Defteri üstte; Açık İşler, Denetim İzi, Hatalar, DLQ alt sekme olur. |
| NAV-IA-04 | Hesap kartı | Sol-alt köşede oturum kartı (şifre değiştir / çıkış / giriş yap). "Kimlik" ve "Yönetim" adlı mükerrer giriş sayfaları kalkar. |
| DATA-LOG-01 | Giriş/arama kaydı | Kim ne zaman giriş yaptı, ne aradı — iki yeni tablo. Müşteri Yönetimi'ndeki "Giriş Etkinliği" ve "Aramalar" sekmelerinin verisi. |
| UI-CHART-01 | Grafik kütüphanesi | Panel grafikleri için Plotly onaylı, ECharts onaysız. Kilo'nun DOC-HIBRIT-01 belgesi ek olarak buraya eklenecek. |
| DOC-HIBRIT-01 | Kilo belgesi | Kilo'nun hazırladığı hibrit grafik geçiş belgesi. Onay bekliyor; bu belgeye "Ek A" olarak girecek. |

---

## 1. Sahibin 4 bulgusu → çözüm eşlemesi

| # | Sahip bulgusu | Kök neden (kod) | Çözen görev |
|---|---|---|---|
| 1 | Sayfaya geçmek için iki kez tıklamak gerekiyor | `app.py` L451-462 "Hızlı geçiş" selectbox rerun'da eski değeri geri yazıyor; topbar arama sorgusu sıfırlanmıyor | **NAV-FIX-01 (P0)** |
| 2 | Menüde tooltip balonları rahatsız ediyor | `_nav_grubu_ciz` → `st.button(help=...)` | **NAV-FIX-02 (P1)** |
| 3 | Aynı işi yapan mükerrer sayfalar var | `kimlik` (admin_auth) + `yonetim` (admin_yonetim, bileşik) ikisi de giriş formu; `sistem` bileşik sayfa alt bölümleri ayrıca menüde | **NAV-IA-01 + NAV-IA-04** |
| 4 | Giriş ve şifre değiştirme ayrı yerlerde | Giriş `kimlik`/`yonetim`; şifre değiştir `render_sifre_degistir` ayrı | **AUTH-GATE-01 + NAV-IA-04** (hesap kartı) |

---

## 2. Hedef bilgi mimarisi (IA) — 6 üst sayfa

Rol kısaltmaları: `anon` misafir, `analyst`, `admin`. Yüzey: 🦅 Huginn önizleme, 🛡️ Muninn.

| Üst sayfa | url_path | min_rol | Alt sekmeler (soldan sağa) |
|---|---|---|---|
| 1. Ana Kontrol | `/ana-kontrol` | anon | — (tek sayfa, KPI kartları) |
| 2. Müşteri Yönetimi | `/musteri-yonetimi` | admin | Özet kartlar (üst) · Kullanıcılar & Onay · Paket & Kredi · Giriş Etkinliği · Aramalar · Destek · Dışa Aktar |
| 3. Proje Yönetimi | `/proje-yonetimi` | admin | Karar Defteri (üst) · Açık İşler · Denetim İzi · Hatalar · DLQ |
| 4. Veri & Kalite | `/veri-kalite` | analyst | KPI · Kalite · Arama · Executive |
| 5. Sistem | `/sistem` | analyst | Teknik Altyapı · Performans · API · Webhook · Maliyet · Canlı Veri · Yenileme · Ayarlar (admin) · Yükleme (admin) |
| 6. Müşteri Önizleme 🦅 | `/musteri-onizleme` | anon | Paketler · Pazarlama |

Not: "Veri & Kalite" sahip onayında açıkça adlandırılmadı; mevcut `kpi/kalite/arama/executive` bölümlerini Müşteri Yönetimi'ne sıkıştırmamak için roo kararıdır. Sahip isterse bu dört sekme Sistem altına da alınabilir (tek satırlık değişiklik: `ust` alanı).

### 2.1 Mevcut 28 bölüm → hedef eşleme

| Mevcut anahtar | Mevcut grup | Hedef üst sayfa | Hedef alt sekme | Karar |
|---|---|---|---|---|
| ana_kontrol | İş | Ana Kontrol | — | Kalır |
| musteriler | İş | Müşteri Yönetimi | Kullanıcılar & Onay | Taşınır; `min_rol` anon→admin |
| kullanicilar | İş | Müşteri Yönetimi | Kullanıcılar & Onay | `musteriler` ile **birleşir** (admin_extras.render_user_management) |
| — (yeni) | — | Müşteri Yönetimi | Paket & Kredi | admin_extras kredi formu + tier seçimi (cline K-1 düzeltmesi burada) |
| — (yeni) | — | Müşteri Yönetimi | Giriş Etkinliği | DATA-LOG-01 `login_events` — tablo gelene dek "yakında" |
| — (yeni) | — | Müşteri Yönetimi | Aramalar | DATA-LOG-01 `search_log` — "yakında" |
| destek | İş | Müşteri Yönetimi | Destek | Taşınır |
| export | İş | Müşteri Yönetimi | Dışa Aktar | Taşınır |
| karar_defteri | İş | Proje Yönetimi | Karar Defteri (üst) | Taşınır |
| abrakadabra | İş | Proje Yönetimi | Açık İşler | Taşınır (görev panosu görünümü) |
| denetim | Sistem | Proje Yönetimi | Denetim İzi | Taşınır |
| hatalar | İş | Proje Yönetimi | Hatalar | Taşınır |
| dlq | Sistem | Proje Yönetimi | DLQ | Taşınır |
| kpi | İş | Veri & Kalite | KPI | Taşınır |
| kalite | İş | Veri & Kalite | Kalite | Taşınır |
| arama | İş | Veri & Kalite | Arama | Taşınır |
| executive | İş | Veri & Kalite | Executive | Taşınır |
| teknik_altyapi | Sistem | Sistem | Teknik Altyapı | Kalır |
| performans | Sistem | Sistem | Performans | Kalır |
| api | Sistem | Sistem | API | Kalır |
| webhook | Sistem | Sistem | Webhook | Kalır |
| maliyet | Sistem | Sistem | Maliyet | Kalır |
| canli_veri | Sistem | Sistem | Canlı Veri | Kalır |
| yenileme | Sistem | Sistem | Yenileme | Kalır |
| ayarlar | Sistem | Sistem | Ayarlar | Kalır (admin) |
| yukleme | Sistem | Sistem | Yükleme | Kalır (admin); placeholder ise sidebar'dan gizlenir |
| sistem | Sistem | — | — | **Kalkar** (bileşik sayfa; alt bölümleri zaten ayrı sekme) |
| paketler | İş 🦅 | Müşteri Önizleme | Paketler | Taşınır |
| pazarlama | İş 🦅 | Müşteri Önizleme | Pazarlama | Taşınır |
| kimlik | Sistem | — | — | **Kalkar** → AUTH-GATE-01 modal + hesap kartı |
| yonetim | Sistem | — | — | **Kalkar** → giriş modal'a, alt panelleri ilgili üst sayfalara |

Sayım: 28 mevcut → 3 kalkar (`sistem`, `kimlik`, `yonetim`), 2 birleşir (`musteriler`+`kullanicilar`), 3 yeni alt sekme (Paket & Kredi, Giriş Etkinliği, Aramalar). Sidebar'da görünen üst öğe: **6**.

### 2.2 Eski adres yönlendirme

- `app.py` `_eski_adresi_cevir()` zaten `?bolum=` → `/{url_path}` çeviriyor. NAV-IA-01'de ikinci katman: `ESKI_URL: dict[str, tuple[str, str]]` = eski url_path → (üst sayfa anahtarı, alt sekme anahtarı). Örn. `/kullanicilar` → (`musteri_yonetimi`, `kullanicilar_onay`), `/kimlik` → (`ana_kontrol`, giriş modalı aç).
- `tab_url_getir` eski yolu bulamazsa `ESKI_URL`'ye bakar; bulursa `st.query_params` günceller ve alt sekmeyi `session_state["alt_sekme"]`'ye yazar.
- Test: `tests/test_dashboard_nav.py`'ye her eski url_path için parametrik yönlendirme testi.

### 2.3 `TabTanimi` değişikliği (NAV-IA-01)

```python
ust: str | None = None        # None → üst sayfa; dolu → o üst sayfanın alt sekmesi
sira: int = 0                 # alt sekme sırası
```

- `gruplar(rol)` yerine `ust_sayfalar(rol)` ve `alt_sekmeler(ust, rol)` yardımcıları; `GRUP_IS/GRUP_SISTEM` geriye dönük korunur (testler kırılmasın), sidebar artık grup değil üst sayfa listeler.
- `test_bk5_zorunlu_bolumler_mevcut` ve `test_u10_*` testleri: kalkan `kimlik/yonetim/sistem` için beklentiler güncellenir; `test_u10_anon_kritik_bolumleri_gormez_yonetimi_gorur` → "anon giriş modalını görür" olarak yeniden yazılır.
- Sidebar'dan çıkarılanlar: "Hızlı geçiş" selectbox, kompakt mod anahtarı, Marka Blogu placeholder.

---

## 3. AUTH-GATE-01 — Giriş kapısı modalı ve hesap kartı

### 3.1 Davranış

- Panel açılışında `admin_token` yoksa `st.dialog` ile **kapatılamaz** modal (`dismissible=False`; Streamlit sürümü desteklemiyorsa CSS ile kapat düğmesi gizlenir + backdrop blur). Modal dışına tıklama sayfayı kapatmaz.
- Misafir modu = `anon` rolü; modalda "Misafir olarak devam et" düğmesi `session_state["misafir"]=True` yazar ve bir daha o oturumda modal açılmaz.
- Giriş başarılı → `admin_token` + `rol`; modal kapanır, `st.rerun()`.

### 3.2 Modal görünümleri (S1–S8)

| Görünüm | Adım | İçerik |
|---|---|---|
| G1 Giriş | S1 | e-posta + şifre + "Giriş yap" · "Misafir olarak devam et" · "Şifremi unuttum" bağlantısı |
| G1 Giriş | S2 | Hata: 401 → "E-posta veya şifre hatalı"; bağlantı hatası → "API (8000) kapalı olabilir" (LOGIN-FIX-02 ile birleşir) |
| G2 Şifremi unuttum | S3 | e-posta al → `POST /api/admin/reset-request` |
| G2 Şifremi unuttum | S4 | "Kod gönderildi" (e-posta/Telegram; ikisi de yoksa terminal scripti ipucu: `scripts/admin_sifre_sifirla.py`) |
| G3 Kod + yeni şifre | S5 | kod + yeni şifre ×2 → `POST /api/admin/reset-confirm` |
| G3 Kod + yeni şifre | S6 | Başarılı → G1'e dön, e-posta ön-dolu |
| G4 Misafir | S7 | Bilgi: "Misafir görünümündesiniz; yalnız Ana Kontrol ve Müşteri Önizleme açık" |
| G4 Misafir | S8 | Hesap kartından "Giriş yap" → G1 yeniden açılır |

### 3.3 API (web_app.py — Docker rebuild gerekir)

- `POST /api/admin/reset-request {email}` → `users` tablosunda admin ise `_store_reset_token` (mevcut buyer akışıyla aynı yardımcı), `_send_email`/`_send_telegram`; yanıt her durumda 200 (kullanıcı sayımı sızmasın).
- `POST /api/admin/reset-confirm {email, token, new_password}` → token+süre doğrula, `_hash_password`, `reset_token=NULL`.
- Mevcut `POST /api/admin/change-password` (ADMIN-RESET-01) korunur; hesap kartı "Şifre değiştir" bunu kullanır.
- Test: `tests/test_web_app_admin_reset.py` (token süre dolumu, yanlış token, başarı).

### 3.4 Sol-alt hesap kartı (NAV-IA-04)

- `st.sidebar` altında `st.popover(f"👤 {email or 'Misafir'}")`: oturum bilgisi (rol, süre), "Şifre değiştir" (modal G5: eski/yeni şifre → change-password), "Çıkış" (`admin_cikis`), misafirse "Giriş yap".
- `render_admin_login`, `render_admin_cikis`, `render_sifre_degistir` (admin_auth.py) fonksiyonları modal/kart içine taşınır; `kimlik` ve `yonetim` sayfaları `SECTIONS`'tan çıkarılır. `render_yonetim_bilesik` (app.py L253-308) silinir; alt panelleri ilgili üst sayfalarda çağrılır.
- `.env` ön-dolum (`_env_kimlik`) yalnız `DEBUG=1`'de çalışır (cline D-2 notu: şifre GET+query bilinçli MVP kararı; AUTH-GATE-01'de `POST /api/admin/login` eklenir, GET geriye dönük kalır).

---

## 4. Grafik geçişi — UI-CHART-01 özeti ve Ek A yer tutucu

- **Onaylı:** Plotly (`web_dashboard/charts.py`: `sparkline_fig`, `donut_fig`, `alan_grafigi_fig`; Plotly yoksa `st.*_chart` fallback). Tema paleti `tema_paleti()` ile tokenlardan gelir.
- **Onaysız:** ECharts (`streamlit-echarts`). D-30: kilo'nun "24 saat sessizlik = otomatik başla" cümlesi geçersiz; ECharts için sahip onayı olmadan kod yazılmaz.
- Yeni alt sekmelerde (Giriş Etkinliği, Aramalar, Paket & Kredi) grafikler yalnız `charts.py` yardımcılarıyla çizilir.

### Ek A — DOC-HIBRIT-01 (kilo) — ONAY BEKLİYOR

> Yer tutucu. Kilo teslimi `review`'a düşünce roo teslim özetinde "BÖLÜM 4 okundu; otomatik başlama yok, ECharts onay bekliyor." teyidini kontrol eder; teyit yoksa reddedilir. Onaylanan belge özeti buraya eklenir; belge onaylansa bile ECharts kodu ayrı sahip kararı ister.

---

## 5. Cline bulguları — bu plana etkisi

| Kaynak | Bulgu | Seviye | Nerede çözülür |
|---|---|---|---|
| REV-MVP-ADMIN-01 K-1 | `admin_extras.py:57` Onayla düğmesi tier'ı sabit `terminal` gönderiyor | YÜKSEK | **NAV-IA-02** Paket & Kredi sekmesi: tier selectbox değeri JSON'a bağlanır + test |
| REV-MVP-ADMIN-01 O-1 | `admin_panel.py:250-256` Ayarlar sekmesi mojibake (çift kodlama) | ORTA | **NAV-FIX-01** ile birlikte (`scripts/mojibake_onar.py`; `page_icon` L68 aynı turda) |
| REV-MVP-ADMIN-01 D-1 | `admin_kpi.py:366-369` Yenile clear+rerun deseni ana_kontrol ile tutarsız | DÜŞÜK | **NAV-IA-01** (tek ortak `yenile()` yardımcısı) |
| REV-MVP-ADMIN-01 D-2 | `admin_auth.py:22` login GET+query ile şifre | DÜŞÜK (bilinçli) | **AUTH-GATE-01** POST login eklenir |
| UI-MODAL-01 B-1 | `X` sonekli Python dosyası kalıntısı | DÜŞÜK | **ORCH-TEMIZLIK-02** |
| UI-MODAL-01 B-2 | `__pycache__` varyantları | BİLGİ | İşlem yok (`.gitignore` kapsar) |

`src/company_master/ui/components/modal.py` `Modal` sınıfı (UI-MODAL-01) mevcut: `html()` + `streamlit(govde_fn)`. AUTH-GATE-01 bunu genişletir (`kapatilabilir: bool = True` parametresi), yeni sınıf yazmaz.

---

## 6. Kod öncesi revize listesi ve görev sırası

| Sıra | Görev | Öncelik | Dokunulan dosyalar | Bitti sayılma ölçütü |
|---|---|---|---|---|
| 1 | NAV-FIX-01 | P0 | `app.py` (L68, L451-462, topbar arama), `admin_panel.py` (O-1) | agent-browser ile 3 sayfa tek tıkta geçiş; mojibake 0; `test_dashboard_nav` yeşil |
| 2 | NAV-FIX-02 | P1 | `app.py` `_nav_grubu_ciz` | `help=` yok; bilgi kartı sayfa içinde |
| 3 | AUTH-GATE-01 | P1 | `modal.py`, `admin_auth.py`, `app.py main()`, `web_app.py` (+2 endpoint), yeni testler | Modal kapatılamıyor; misafir akışı; reset akışı test edildi; Docker rebuild + curl 404 dışı |
| 4 | NAV-IA-01 | P1 | `tabs/__init__.py`, `app.py` sidebar, `test_dashboard_nav.py`, `test_app_menu_rol.py` | 6 üst öğe; eski url yönlendirme testleri; `kimlik/yonetim/sistem` kalktı |
| 5 | NAV-IA-04 | P1 | `app.py` sidebar alt, `admin_auth.py` | Hesap kartı popover; çıkış/şifre değiştir çalışır |
| 6 | NAV-IA-02 | P1 | yeni `tabs/musteri_yonetimi.py`, `admin_extras.py` (K-1) | 6 alt sekme; tier seçimi doğru gidiyor (test) |
| 7 | NAV-IA-03 | P1 | yeni `tabs/proje_yonetimi.py` | 5 alt sekme; Karar Defteri üstte |
| 8 | DATA-LOG-01 | P2 | `web_app.py` (login/search kayıt), migration, `musteri_yonetimi.py` | İki tablo; Giriş Etkinliği/Aramalar gerçek veri |
| — | LOGIN-FIX-02 | P2 | AUTH-GATE-01 S2 içinde | API kapalı ipucu |

Her görevde: `python scripts/streamlit_restart.py` (UI) · `docker compose up -d --build api` (API) · `python -m pytest tests/ -q --continue-on-collection-errors` (koleksiyon hatası 0) · `python scripts/kodlama_denetim.py`.

Atama: 1-2 roo (küçük, P0); 3-7 kilo üretim → cline review → roo onay; 8 kilo.

---

## 7. Kararlar ve riskler

| Karar | Gerekçe |
|---|---|
| Sentez kilo'nun DOC-HIBRIT-01 teslimini beklemedi | Kilo belgesi yalnız onaysız ECharts'ı kapsar; navigasyon işi ondan bağımsız (sahip "tamam", 2026-09-16) |
| "Veri & Kalite" 4. üst sayfa olarak eklendi | KPI/Kalite/Arama/Executive müşteri değil veri odaklı; Müşteri Yönetimi 10 sekmeye şişmesin. Sahip reddederse `ust` alanı değişir |
| `kimlik` + `yonetim` kalkar | Sahip bulgusu #3/#4; giriş tek yerden (modal + hesap kartı) |
| ECharts kodu yok | D-30; sessizlik onay değildir |
| Risk: `st.dialog(dismissible=False)` sürüm desteği | Streamlit sürümü kontrol edilir (`pip show streamlit`); yoksa CSS gizleme + ESC engeli, testte belgelenir |
| Risk: NAV-IA-01 test kırılması | `GRUP_IS/GRUP_SISTEM` geriye dönük korunur; yalnız beklenti güncellenen testler listelenir |
| Risk: Docker imajı eski `web_app.py` | AUTH-GATE-01 teslim ölçütüne `curl` doğrulaması eklendi |
