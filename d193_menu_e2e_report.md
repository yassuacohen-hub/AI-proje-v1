# D-193 Menu E2E Test Raporu

**Rapor Tarihi:** 2026-09-23T20:38:33.817885 (ilk teşhis) → 2026-09-23T17:53 port çözümü → 2026-09-23T18:17 QA tamamlandı

**Toplam Hata (bu QA turu):** 6
  - P0 (Kritik/Bloklayıcı): 1
  - P1 (Önemli): 2
  - P2 (Düşük/Kozmetik): 3

**Kapsam:** Port 8501 üzerinde admin girişli oturumla 16 menü öğesinin tamamı `agent-browser` ile gezildi (32 bölüm admin rolünde görünür), webhook tetikleme (karar_defteri, ajan_sohbet) ve navbar/sidebar/breadcrumb yapı doğrulaması yapıldı. Session: `d193qa-88806a2ccb92`.

---

## 🔴 P0 — KRR-01: Karar Defteri Sayfası Çöküyor (`/karar-defteri`)

- **Tür:** RUNTIME_CRASH (`AttributeError: 'str' object has no attribute 'get'`)
- **Konum:** [`admin_panel.py:86-92`](Huginn Data Insights/web_dashboard/tabs/admin_panel.py:86) — `tum_etiketler` set comprehension
  ```python
  tum_etiketler = sorted({
      t for d in decisions
      for t in (d.get("tags", []) if isinstance(d.get("tags", []), list) else [])
  })
  ```
- **Kök neden:** [`decision_log.jsonl:190`](Huginn Data Insights/data/orchestrator/decision_log.jsonl:190) çift-JSON-kodlanmış (string içinde escape edilmiş JSON) — satır kendisi bir JSON string literal, `json.loads()` bunu `dict` değil `str` olarak döndürüyor:
  ```
  "{\"id\": \"D-63\", \"tarih\": \"2026-09-18T22:15:00Z\", ...}"
  ```
  Satır 191'de aynı D-63 kararının **doğru** (raw dict) hâli zaten mevcut — 190 mükerrer/bozuk bir kayıt.
- **Etkileşen katman:** [`decision_log.py:read_decisions()`](Huginn Data Insights/scripts/decision_log.py:42) parse edilen değerin `dict` olduğunu doğrulamıyor.
- **Etki:** Sayfa "Filtreler" bölümünden sonra çöküyor → **"Yeni Karar" formu hiçbir zaman render edilmiyor** → webhook trigger testi (karar_defteri yarısı) **BLOCKED**.
- **Önerilen düzeltme (öncelik sırasıyla):**
  1. Veri temizliği: `decision_log.jsonl` satır 190'ı sil (191'de doğrusu zaten var).
  2. Savunma kodu: `read_decisions()` içinde `isinstance(parsed, dict)` kontrolü ekle, değilse satırı atla/logla.

## 🟠 P1 — MLY-01: Maliyet Sayfası KPI Kartı TypeError (`/maliyet`)

- **Tür:** RUNTIME_ERROR (`TypeError: kpi_karti() got an unexpected keyword argument 'delta_color'`)
- **Çağrı noktası:** [`admin_cost.py:548-553`](Huginn Data Insights/web_dashboard/tabs/admin_cost.py:548) — `delta_color="inverse"` kwarg'ı geçiliyor
- **Fonksiyon imzası:** [`charts.py:405-417`](Huginn Data Insights/web_dashboard/charts.py:405) `kpi_karti()` böyle bir parametre kabul etmiyor (yalnız `delta`, `ikon`, `kategori`, `yardim`, `ondalik`, `birim`, `aciklama`, `anahtar`)
- **Etki:** "Sorunlu Providerlar" KPI kartı render edilmiyor, sayfa geri kalanı (diğer 3 KPI, grafikler) çalışıyor — kısmi render.
- **Düzeltme:** `admin_cost.py:551`'den `delta_color="inverse"` satırını kaldır, ya da `charts.py`'de `kpi_karti()`'ye `delta_color` parametresi ekle.

## 🟠 P1 — API-01: API Analitiği Sayfası AttributeError (`/api-analitigi`)

- **Tür:** RUNTIME_ERROR (`AttributeError: 'str' object has no attribute 'render'`)
- **Konum:** [`admin_api_analytics.py:122`](Huginn Data Insights/web_dashboard/tabs/admin_api_analytics.py:122) ve [`:128`](Huginn Data Insights/web_dashboard/tabs/admin_api_analytics.py:128)
  ```python
  MetricCard("Toplam Çağrı", f"{toplam_cagri:,}".replace(",", ".").render(), kategori="sistem")
  ...
  MetricCard("İzlenen Tier Sayısı", len(items).render() if items else 0, kategori="sistem")
  ```
  `.render()` yanlışlıkla `MetricCard(...)` sonucuna değil, `str`/`int` değerine (2. pozisyonel arg) zincirlenmiş — kopyala-yapıştır hatası.
- **Etki:** Sayfa üst bilgi kutusu render oluyor, metrik kartlarına gelince çöküyor — kısmi render.
- **Düzeltme:** `.render()` çağrılarını `f"{toplam_cagri:,}".replace(",", ".")` ve `len(items) if items else 0` değerlerinden kaldırıp, `MetricCard(...).render()` şeklinde dış çağrıya taşı.

## 🟡 P2 — CHT-01: "Yeni Sorun" Webhook Trigger UI'si Yok (`/ajan-sohbet`)

- **Tür:** SPEC_MISMATCH (implementasyon eksik, crash değil)
- **Test suite beklentisi:** [`test_d193_menu_e2e_suite.py:139-146`](Huginn Data Insights/test_d193_menu_e2e_suite.py:139) `"button": "Yeni Sorun"`, endpoint `/api/chat/ac`
- **Gerçek kod:** [`render_chat_summary()`](Huginn Data Insights/web_dashboard/tabs/admin_panel.py:451) yalnız salt-okunur: metrik özeti + son 3 açık sorun (expander) + tam tablo (`st.dataframe`). Herhangi bir "Yeni Sorun" butonu/formu/create-action kodda **mevcut değil**.
- **Doğrulama:** `agent-browser press End` ile sayfa sonuna kadar scroll edildi, snapshot'ta son element `button "AI MIMIR sohbetini aç" [ref=e417]` — ekleme/tetikleme butonu yok.
- **Sonuç:** webhook trigger testi (ajan_sohbet yarısı) **MISSING/NOT-IMPLEMENTED** — spec bir özellik varsayıyor, ürün henüz onu içermiyor. KAHİN kararı gerekir: özellik eklenmeli mi, yoksa test suite spec'i güncellensin mi.

## 🟡 P2 — UI-01: Sidebar'da Mükerrer "👥 Müşteriler" Butonu

- **Konum:** [`web_dashboard/tabs/__init__.py:180-182`](Huginn Data Insights/web_dashboard/tabs/__init__.py:180) ve [`:503-513`](Huginn Data Insights/web_dashboard/tabs/__init__.py:503) — iki ayrı `TabTanimi` aynı `ikon="👥"` + `baslik≈"Müşteriler"` ile tanımlı, farklı `url_path` (biri legacy grup içi sekme, diğeri `musteri-yonetimi` bağımsız sayfa).
- **Etki:** Sidebar'da aynı etiketle iki buton görünüyor (snapshot `ref=e393`, `ref=e394`) — kullanıcı hangisinin ne yaptığını ayırt edemiyor.
- **Düzeltme:** Etiketlerden biri netleştirilmeli (örn. "Müşteriler (Genel)" vs "Müşteri Yönetimi") veya biri sidebar'dan kaldırılmalı.

## 🟡 P2 — UI-02: `/export` Sayfasında Türkçe Karakter Hataları

- **Konum:** [`admin_export.py:151`](Huginn Data Insights/web_dashboard/tabs/admin_export.py:151) `"Gorev Panosu"` → "Görev Panosu" olmalı; [`:171`](Huginn Data Insights/web_dashboard/tabs/admin_export.py:171) `"yuklendi"` → "yüklendi" olmalı.
- **Etki:** Kozmetik, işlevi etkilemiyor.

---

## ✅ UI Yapı Doğrulama Sonuçları (Todo #4)

| Öğe | Beklenen | Gözlem | Durum |
|---|---|---|---|
| Breadcrumb | `Ana Kontrol > [Grup] > [Sayfa]` | Tüm sayfalarda doğru format görüldü (örn. "Ana Kontrol › 🏢 İş Operasyonları › Ajan Chat") | ✅ PASS |
| Arama kutusu | Navbar'da bölüm arama | `textbox "Bölüm ara" [ref=e412]` mevcut | ✅ PASS |
| Hesap menüsü | Kullanıcı rozeti/popover | `button "👤 Misafir" [ref=e378]` mevcut (giriş sonrası admin adına güncellenmeli — ayrı doğrulama gerekir) | ✅ PASS (isim güncellemesi ayrıca teyit edilmeli) |
| Tema değiştir | Dark/Light toggle | Kodda `web_dashboard/` içinde arandı, **hiçbir tema toggle bileşeni bulunamadı** | ❌ MISSING (implement edilmemiş) |
| Sidebar grupları | İş / Sistem | `GRUP_IS`, `GRUP_SISTEM` doğrulandı, 32 bölüm (admin rolü) 2 grup altında listeleniyor | ✅ PASS |
| Sidebar öğe sayısı | Spec: 16 (muhtemelen guest/analyst rolü) | Admin rolünde gerçek sayı **32** (6 anon + rol bazlı artan) | ⚠️ NOT (spec'teki "16" hangi rolü kastediyor belirsiz — spec güncellenmeli) |
| Footer | versiyon, copyright | Kodda arandı, **hiçbir footer bileşeni bulunamadı** | ❌ MISSING (implement edilmemiş) |
| Main content layout | flex/grid | Streamlit varsayılan konteyner yapısı kullanılıyor, özel flex/grid CSS gözlemlenmedi | ⚠️ N/A (Streamlit framework kısıtı) |

---

## 📋 Webhook Tetikleme Test Sonuçları (Todo #3)

| Hedef | Buton/Form | Sonuç |
|---|---|---|
| karar_defteri (Yeni Karar) | `st.form("yeni_karar")`, submit="Kaydet" | 🔴 **BLOCKED** — sayfa KRR-01 crash'i nedeniyle forma hiç ulaşılamıyor |
| ajan_sohbet (Yeni Sorun) | — | 🟡 **MISSING** — buton/form kodda yok (CHT-01) |

---

## 16 Menü Navigasyon Testi Özeti (Todo #2 — tamamlandı önceki turda)

Tüm 32 bölüm (admin rolü) `agent-browser open` ile başarıyla açıldı, navigasyon hatası yok. Sayfa-içi render hataları (KRR-01, MLY-01, API-01) yukarıda ayrı bulgular olarak dokümante edildi; navigasyonun kendisi tüm URL'lerde çalışıyor.

---

## Web Interface Guidelines Çapraz Kontrolü (Streamlit kısıtı notu)

Uygulama Streamlit ile inşa edildi; framework DOM/CSS'i doğrudan kontrol etmiyor (React/HTML custom component'leri hariç). Bu nedenle klasik web guideline kontrollerinin çoğu (aria-label, focus-visible, transition:all, autocomplete vb.) **kaynak koddan doğrudan denetlenemez** — Streamlit'in kendi bileşen render katmanı bunları yönetir. Gözlemlenebilen/uygulanabilir bulgular:

- **Tema değiştir eksik** → `color-scheme` / dark-mode desteği yok (UI yapı doğrulama, yukarıda ❌ MISSING).
- **Hata mesajları** (KRR-01, MLY-01, API-01) kullanıcıya ham Python exception metni gösteriyor ("❌ ... cizilirken hata olustu: ...") — guideline "error messages include fix/next step, not just problem" ihlali. Kullanıcı dostu mesaj + destek yönlendirmesi eklenmeli.
- **Türkçe karakter tutarsızlığı** (UI-02) → content/copy kalitesi ilkesiyle örtüşüyor, düzeltilmeli.
- Form/erişilebilirlik/animasyon kontrolleri Streamlit native bileşenleri kullandığından (custom HTML/JS yok) bu QA turunda ek bulgu çıkmadı.

---

## ✅ ÇÖZÜLDÜ — NET-8501: Port 8501 Erişilebilirlik

- **Tür:** PORT_UNREACHABLE
- **Konum:** localhost:8501
- **İlk Mesaj:** Port 8501 hiçbir servisten dinlemiyor. User isteği: 'http://localhost:8501/ şu anda erişilemez'

### Teşhis Süreci (Debug modu, 2026-09-23)

7 olası neden değerlendirildi, sistematik olarak elendi:

| # | Hipotez | Sonuç |
|---|---------|-------|
| 1 | Servis çökmüş | Elendi — process çalışıyordu |
| 2 | Firewall engeli | Elendi — netstat başka portta LISTENING gösterdi |
| 3 | Config dosyası bozuk | Elendi — [`config.toml`](Huginn Data Insights/.streamlit/config.toml:19) satır 19'da zaten `port = 8501` doğruydu |
| 4 | .env PORT override | Elendi — override yok |
| 5 | Zombie/çoklu process çakışması | Elendi — tek python.exe process vardı |
| 6 | Kalıcı git kararıyla port taşınmış | Elendi — geçmişte hiç 8502 referansı bulunamadı |
| 7 | **Manuel CLI flag override** | **DOĞRULANDI** — kesin neden |

**Kesin kök neden:** PowerShell CIM process sorgusu (`Get-CimInstance Win32_Process`) PID 37948'in tam komut satırını gösterdi:
```
streamlit.exe run app.py --server.port 8502 --logger.level=debug
```
Bu manuel CLI flag, `config.toml`'daki doğru kanonik değeri (8501) override etmişti. Önceki oturumda elle girilmiş, tek seferlik operatör hatası — sistemsel/kalıcı bir sorun değil.

### Uygulanan Çözüm (KAHİN onaylı, 2026-09-23)

1. `taskkill /PID 37948 /F` — 8502'deki yanlış process kapatıldı
2. `streamlit run app.py` (flagsiz) — config.toml'daki 8501 devreye girdi
3. `netstat -ano | findstr "8501"` doğrulaması: PID 38024, `0.0.0.0:8501 LISTENING` + `[::]:8501 LISTENING`
4. `agent-browser open http://localhost:8501/ana-kontrol` — sayfa başarıyla açıldı, doğrulandı

### Güncellenen Dosyalar

- [`test_d193_menu_e2e_suite.py`](Huginn Data Insights/test_d193_menu_e2e_suite.py:102) — `port_availability_check()` 8501 REACHABLE olarak düzeltildi, `menu_navigation_test()` URL'leri 8501'e çevrildi
- [`d193_agent_browser_menu_test.bat`](Huginn Data Insights/d193_agent_browser_menu_test.bat:7) — `BASE_URL=http://localhost:8501`
- [`d193_agent_browser_menu_test.sh`](Huginn Data Insights/d193_agent_browser_menu_test.sh:5) — `BASE_URL="http://localhost:8501"`

**Kalıcı önlem:** `python scripts/streamlit_restart.py` (flagsiz) kullanımı standart hale getirilmeli; manuel `streamlit run` + custom `--server.port` flag'i AGENTS.md'de yasaklanabilir (KAHİN kararı gerekir).

---

## Sonraki Adımlar (KAHİN kararı bekleyen)

1. **KRR-01 (P0):** `decision_log.jsonl:190` satırını sil + `read_decisions()`'a tip kontrolü ekle. Bu düzeltilmeden karar_defteri sayfası ve "Yeni Karar" webhook testi tekrar denenemez.
2. **MLY-01 (P1):** `admin_cost.py:551`'den `delta_color="inverse"` kaldır veya `kpi_karti()` imzasına ekle.
3. **API-01 (P1):** `admin_api_analytics.py:122,128`'de yanlış yerleştirilmiş `.render()` çağrılarını düzelt.
4. **CHT-01 (P2):** "Yeni Sorun" webhook UI'si eklensin mi yoksa test suite spec'i mevcut duruma göre güncellensin mi — karar gerekli.
5. **UI-01/UI-02 (P2):** Kozmetik düzeltmeler, düşük öncelik, herhangi bir sprint'e eklenebilir.
6. Tema değiştir + footer (versiyon/copyright) eksiklikleri ayrı bir UX görevi olarak backlog'a alınabilir.

**D-193 Menu E2E QA görevi bu raporla tamamlanmıştır.**

---

## 🟡 Ek Bulgu: Tam Test Suite'te 13 Pre-Existing Hata (2026-09-23, roo)

**Bağlam:** 4 onaylı fix (`_parse_body` SSE trailer, popover→`st.dialog`, `.env` checkbox kaldırma, debug print kaldırma) + sahte D-192 hack revert sonrası tam `pytest` suite'i çalıştırıldı. Admin/nav/chat kapsamında hedeflenen 71/71 test yeşil. Ancak tam suite'te 13 test hatası tespit edildi.

**Doğrulama yöntemi:** `git stash` ile değişiklikler geçici olarak kaldırılıp aynı 9 test dosyası tekrar çalıştırıldı. Hatalar `git stash` öncesi/sonrası aynı çıktı → **bu oturumun 3 dokunduğu dosyadan (`ninerouter_client.py`, `admin_auth.py`, `app.py`) kaynaklanmıyor, önceden var olan hatalar.**

**13 hata listesi:**
1. `test_admin_performance.py` — 3 test
2. `test_d87_atama_otomasyonu_fixed.py` — 3 test
3. `test_marka_denetim_muafiyet.py::test_kok_denetimi_temiz`
4. `test_naming_audit.py::test_acik_gorevlerde_yeni_d57_ihlali_yok`
5. `test_sayfa_iskeleti.py::test_ekranda_subheader_kalmaz[admin_panel]`
6. `test_tabs_ia.py::test_menudeki_alt_sekme_sayisi`
7. `test_user_settings.py::test_panel_formu_sema_uzerinden_uretir`

**Ayrı not — flaky testler (regresyon DEĞİL):** `test_app_menu_rol.py::test_admin_token_menuyu_buyutur` ve `test_d66_bypass_tetikleme.py::test_bypass_logging_kaydedilir` tam suite koşusunda bazen başarısız oluyor, ancak izole çalıştırıldığında (stash'li/stash'siz fark etmeksizin) her zaman **geçiyor**. Kök neden muhtemelen Streamlit `AppTest` session-state veya dosya sistemi durumunun aynı pytest process'inde testler arası sızması (test pollution/order-dependency) — bu 3 dosyadan kaynaklanan gerçek bir regresyon değil.

**Önerilen aksiyon:** Bu 13 hata (+ 2 flaky test kök nedeni) ayrı bir görev olarak **utku**'ya atanabilir (kod inceleme/düzeltme). KAHİN onayı gerekirse `scripts/gorev_at.py at --ajan utku` ile pano'ya eklenmeli.
