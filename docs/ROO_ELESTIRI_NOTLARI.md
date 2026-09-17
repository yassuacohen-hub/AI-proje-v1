# Ortak Eleştiri, Dikkat ve Risk Defteri (Tüm Ajanlar Okusun ve Yazsın)

> Son güncelleme: 2026-09-16 23:15 (S-09/S-10/D-07 ÇÖZÜLDÜ, D-31/D-32, Bölüm 8 görev dönüşüm listesi ekleyen: roo)
> Kapsam: DASH-UX serisi + UX-01/02/03 + P7-46 + dashboard mimarisi + MVP-ADMIN + AI-CI (Anthropic × GitHub)
> Amaç: Teslim edilen işlerde bilerek bırakılan eksikleri, tespit edilen
> tutarsızlıkları ve diğer ajanları etkileyecek riskleri tek yerde toplamak.
>
> **🔎 SORUN ÇIKINCA İLK BURAYA BAK.** Bir hata/beklenmedik davranış görüldüğünde
> önce bu defterde ara (`findstr /i "anahtar" docs\ROO_ELESTIRI_NOTLARI.md`), sonra
> `python scripts/decision_log.py` (`search_decisions`) — çoğu sorun daha önce
> "Dikkat" notu olarak yazılmıştır. Kural: [`AGENTS.md`](../AGENTS.md) → "Dikkat Notları Defteri Kuralı".python, git, pytest, pip.

Bu dosya **kalıcı ve ortak bir uyarı listesidir**. Bir madde çözüldüğünde satırı
silmeyin; `Durum` sütununu `ÇÖZÜLDÜ (görev-id)` olarak güncelleyin — denetim izi kalsın.

### Katkı Kuralı (tüm ajanlar için)

1. Yeni madde eklerken ilgili bölümün **sonuna** satır ekleyin; mevcut satırları yeniden yazmayın.
2. Kod (`K-`), Mimari (`M-`), Veri (`V-`), Süreç (`S-`), Orkestratör (`O-`), Dikkat (`D-`) öneklerini kullanın;
   numarayı o bölümdeki son numaranın bir fazlası yapın.
3. `Etkilenen` sütununa kendi ajan adınızı ve etkilediğiniz ajanları yazın.
4. Maddeyi göreve dönüştürmek **orkestratörün / sahibin** kararıdır; buraya yazmak görev açmak değildir.
5. Sahip talimatı (2026-09-14): maddeler burada biriktirilir, **toplu değerlendirme sonrası** göreve dönüştürülür.
6. Sahip talimatı (2026-09-15): her teslim raporundaki **"Dikkat (eleştirel notlar)"** bölümü aynı turda
   Bölüm 7'ye (`D-` satırı) işlenir; işlenmemiş dikkat notu = eksik teslim.

---

## 1. Kritik / Kullanıcıya Doğrudan Yansıyan

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| K-01 | **Paketler ve Pazarlama sekmeleri ekrana bağlı değil** | DASH-UX-04'te [`web_dashboard/tabs/paketler.py`](../web_dashboard/tabs/paketler.py) ve [`web_dashboard/tabs/pazarlama.py`](../web_dashboard/tabs/pazarlama.py) yazıldı ve teste geçti; ancak görev kilit listesinde [`app.py`](../app.py) olmadığı için sidebar bağlantısı yapılamadı. Kullanıcı hâlâ `⏳ hazırlanıyor` yer tutucusu görüyor. **Yazılmış kod kullanıcıya görünmüyor.** | roo, orkestratör | **ÇÖZÜLDÜ (P7-44)** — Navigasyon tek kaynağa taşındı: [`SECTIONS`](../web_dashboard/tabs/__init__.py:78). Sidebar ve yönlendirme aynı listeden üretiliyor, bu yüzden "kod var ama ekranda yok" durumu yapısal olarak imkânsız. [`tests/test_dashboard_nav.py`](../tests/test_dashboard_nav.py) her hazır bölümün çağrılabilir bir render fonksiyonuna çözümlendiğini doğruluyor (15 test). |
| K-02 | **Müşteri listesi + filtre + bildirim bloğu kayboldu** | DASH-UX-01'de [`app.py`](../app.py) yeniden yazılırken eski firma listesi, filtre paneli ve bildirim bloğu yeni yapıya taşınmadı. Eğer COP-26 ("MÜŞTERİLER ekranı") bunu karşılamıyorsa işlevsel gerileme var. | copilot, roo | AÇIK — COP-26 çıktısıyla karşılaştırılmalı |
| K-03 | **Görev tanımındaki dosya yolu gerçekte yok** | P7-44 `baslangic` alanı `web_dashboard/app.py` diyor; fakat böyle bir dosya yok, Streamlit uygulaması kökteki [`app.py`](../app.py). Panoya yol yazan ajanlar yolu doğrulamadan yazıyor; bu yanlış dosya oluşturulmasına yol açabilir. | tüm ajanlar | **KISMEN** — P7-44'te doğru dosya (kök `app.py`) kilitlendi ve görev notuna yazıldı; panodaki hatalı `baslangic` değeri düzeltilmedi. Kalıcı çözüm önerisi: `gorev_ekle`/`gorev_at` içinde `baslangic` + `dosyalar` yollarının diskte var olup olmadığını kontrol eden bir uyarı. |
| K-04 | **Kullanıcı ayarları kaydediliyor ama hiçbir ekran onları okumuyor** | P7-46 ile [`src/company_master/settings/user_settings.py`](../src/company_master/settings/user_settings.py) ve [`render_ayarlar_tab()`](../web_dashboard/tabs/admin_panel.py:137) yazıldı; 13 ayar kalıcı olarak diske yazılıyor. Ancak tüketen taraf yok: [`admin_auto_refresh.py`](../web_dashboard/tabs/admin_auto_refresh.py) hâlâ kendi `REFRESH_INTERVALS` sabitini ve `st.session_state`'i kullanıyor; KVKK maskeleme, sayfa boyutu, varsayılan bölüm, tema ve dil ayarları hiçbir ekranda okunmuyor. **Kullanıcı ayarı değiştiriyor, ekranda hiçbir şey değişmiyor** — panel şu an kozmetik. Önerilen kapsam: her ayar için tüketici nokta belirlenip `ayarlari_getir()` çağrısıyla bağlanması, en az `otomatik_yenileme`/`yenileme_araligi`/`kvkk_maskeleme`/`sayfa_boyutu`/`varsayilan_bolum` ile başlanması. | roo, kilo, orkestratör | AÇIK — sahip kararıyla göreve dönüştürülecek (şimdilik bekletiliyor) |

## 2. Mimari / Tutarlılık

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| M-01 | **İki ayrı arayüz, tek isim karmaşası** | `web_dashboard/css/style.css` + `index.html` **FastAPI** panelidir ([`web_app.py`](../web_app.py) `/static/css/style.css` ile sunar, `tests/test_web_app.py::test_css_served` korur). Streamlit uygulaması bu CSS'i **okumaz**. "Dashboard CSS'ini düzelt" gibi görevler hangi arayüzü kastettiğini açıkça yazmalı. | tüm ajanlar | AÇIK — görev tanımlarında arayüz adı belirtilmeli |
| M-02 | **Streamlit teması config'te, CSS'te değil** | Koyu tema [`.streamlit/config.toml`](../.streamlit/config.toml) `[theme]` bloğuyla verildi (style.css paletiyle aynı). Streamlit tarafında renk değiştirmek isteyen ajan `style.css`'e dokunmasın — FastAPI panelini bozar. | tüm ajanlar | BİLGİ |
| M-03 | **Tanımsız CSS sınıfları** | [`web_dashboard/tabs/ana_kontrol.py`](../web_dashboard/tabs/ana_kontrol.py) içindeki `_get_metric_color()` `metric-blue` / `metric-orange` döndürüyor; bu sınıflar hiçbir yerde tanımlı değil ve `unsafe_allow_html` da kullanılmıyor. Yani K4 (mavi=müşteri, turuncu=sistem) kuralı **görsel olarak uygulanmıyor** — sadece ölü kod. | roo, copilot | AÇIK |
| M-04 | **`__init__.py` saf veri modülü streamlit import** | `web_dashboard/tabs/__init__.py` tasarım olarak Streamlit runtime'ından bağımsız saf veri taşıyor (`test_dashboard_nav` Streamlit'siz çalışır). Ancak `yenile()` yardımcısı `st.cache_data.clear()` + `st.rerun()` çağırıyor → `import streamlit as st` eklendi. Bu modül **saf veri sözleşmesini bozuyor**. Çözüm: `yenile()` başka bir modüme taşınmalı (örn. `web_dashboard/charts.py`). | kilo | AÇIK |
| M-05 | **`musteri_yonetimi.py` inline import** | `_paket_kredi()` içinde `from web_dashboard.tabs.admin_extras import get_api, post_api` inline import kullanıyor. Modül seviyesine taşınmalı. | kilo | AÇIK |
| M-06 | **`web_app.py` FastAPI monoliti (2835 satır)** | Tüm endpoint'ler tek dosyada; `routers/services/repositories/schemas` katman ayrımı yok — `CLAUDE.md` → `docs/AJAN_DETAY.md` §21 FastAPI kuralıyla çelişiyor. Büyümeyle review/test maliyeti artıyor. (Gezinti bulgusu, cline 2026-09-16.) | cline, kilo, roo | AÇIK — sahib kararıyla katman taşıma görevi |

## 3. Veri / Dayanıklılık

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| V-01 | **Panelin büyük kısmı demo veriyle çalışıyor** | Paketler, Pazarlama ve firma kartı verileri DB bağlantısı olmadığı için `data/demo/*.jsonl`'den geliyor. DEMO rozeti var ama **karar verici gerçek sanabilir**. Gerçek DB bağlanana kadar demo rozetinin her ekranda görünür kalması şart. | tüm ajanlar | AÇIK |
| V-02 | **Geniş `except Exception` kullanımı** | Sekmelerde DB hatası sessizce yutulup demo veriye düşülüyor. Bu MVP için bilinçli bir tercih; ancak gerçek DB devreye girince **hata gizleyecek**. DB bağlandığında bu bloklar daraltılmalı ve hata sebebi kullanıcıya gösterilmeli. | roo, kilo | AÇIK |
| V-03 | **Demo veri şeması ile DB şeması birebir aynı değil** | Örn. kampanya demo verisinde `impressions/clicks/conversions/segment` var, `_kampanya_row` bunları döndürmüyor. DB'ye geçildiğinde CTR/dönüşüm metrikleri boşalacak (K2 yer tutucusu devreye girer, çökmez ama bilgi kaybolur). | kilo, roo | AÇIK |

## 4. Süreç / Koordinasyon

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| S-01 | **Kilit listesi işin kapsamından dar olabiliyor** | DASH-UX-04 iki sekme dosyasını kilitledi ama bu sekmeleri görünür kılacak `app.py`'yi kilitlemedi. Sonuç: iş "bitti" göründü, kullanıcı hiçbir değişiklik görmedi. **Görev açan ajan, çıktının kullanıcıya ulaşması için gereken TÜM dosyaları kilitlemeli.** | orkestratör | AÇIK |
| S-02 | **Teslim özetleri doğrulama kanıtı içermeli** | `py_compile` tek başına yeterli değil. Teslimde en az bir çalıştırma/test kanıtı (`pytest` sonucu veya veri akışı çıktısı) verilmeli; aksi halde onaylayan kontrolör körlemesine onaylıyor. | tüm ajanlar | ÖNERİ |
| S-03 | **Türkçe karakter bozulması riski** | [`ana_kontrol.py`](../web_dashboard/tabs/ana_kontrol.py) içinde Kiril `д` harfiyle yazılmış `Trenд` bulundu ve düzeltildi. Kopyala-yapıştır kaynaklı bu tür bozulmalar gözle fark edilmiyor — dosya kaydetmeden önce UTF-8 ve karakter kontrolü yapın. | tüm ajanlar | ÇÖZÜLDÜ (DASH-UX-01) — kural olarak geçerli |
| S-04 | **Bekleyen kullanıcı sorusu** | `pip install "headroom-ai[proxy]"` talebi hâlâ askıda; bağımlılık eklemek onay gerektirdiği için kurulmadı. | roo | AÇIK — sahibe sorulacak |
| S-05 | **Tek bozuk kayıt tüm panoyu çökertiyordu** | `WIKI-01` görevinde `oncelik` alanı yoktu. [`_md_yaz()`](../src/company_master/orchestrator/task_board.py:511) ve [`agent_sync_olustur()`](../src/company_master/orchestrator/task_board.py:363) alanlara doğrudan `t['oncelik']` ile eriştiği için **her ajanın** her pano yazımı `KeyError: 'oncelik'` ile çöküyordu (P7-44 teslimi sırasında yakalandı). Tüm erişimler `.get(..., '-')` ile sağlamlaştırıldı. **Bu O-06'nın somut sonucudur.** Kalıcı çözüm önerisi: `gorev_ekle` içinde zorunlu alan şeması (task_id/baslik/sahip/oncelik/durum) doğrulaması + eksik alanları varsayılanla dolduran tek bir normalize fonksiyonu. | tüm ajanlar, orkestratör | **ÇÖZÜLDÜ (P7-44)** — savunma amaçlı düzeltme yapıldı; şema doğrulaması hâlâ AÇIK |
| S-06 | **`gorev_kutusu.py al` panodaki göreve çalışmıyor** | Panoya doğrudan eklenmiş (`source: ic`) görevlerde posta kutusunda tetik olmadığı için `al` komutu "bekleyen tetik yok" diyor; ajan görevi ancak `task_board.gorev_guncelle(...)` ile üstüne alabiliyor. İki farklı yol olması ajanı yanıltıyor. Öneri: `al` komutu tetik bulamazsa panoya bakıp görev o ajana atanmışsa doğrudan aktifleştirsin. | tüm ajanlar, orkestratör | AÇIK |
| S-07 | **Otomatik onay, "onaysız done olmaz" kuralını fiilen delebiliyor** | P7-44 teslimi `oto-nobetci` tarafından 29 saniye içinde otomatik onaylandı; insan/kontrolör incelemesi olmadan `done` oldu. Kural metni "onaysız done geçersizdir" derken pratikte otomatik onay devrede. Ya kural metni otomatik onayı açıkça tanımlamalı ya da kritik (P0/P1) görevler otomatik onay dışında tutulmalı. | orkestratör | ÇÖZÜLDÜ (sahip kararı 2026-09-16): P0/P1 elle roo onayı, P2 ve altı otomatik (`trigger.otomatik_onaylanabilir`, `tests/test_oto_onay_oncelik.py`); tekrar ihlalde oto-nobetci kapatılır |
| S-08 | **Kullanıcı kimliği zayıf: herkes aynı `misafir` dosyasını paylaşıyor** | P7-46'daki [`aktif_kullanici()`](../web_dashboard/tabs/admin_panel.py:75) oturumdan sırasıyla `admin_email` → `user_email` → `kullanici_id` arıyor; hiçbiri yoksa sabit `misafir` kimliğine düşüyor. Streamlit oturumunda bu alanlar çoğu akışta dolmadığı için pratikte **tüm kullanıcılar `data/user_settings/misafir.json` dosyasını paylaşır**; biri ayarı değiştirince diğerininki de değişir. Ayrıca ayarlar kullanıcıya değil tarayıcı oturumuna bağlı görünür. Kalıcı çözüm: kimliğin [`company_master.auth.session`](../src/company_master/auth/session.py) üzerinden çözülmesi ve kimlik yoksa panelin salt-okunur/uyarılı çalışması. Geçici azaltma: panelde "misafir modunda ayarlar paylaşılır" uyarısı. | roo, kilo, orkestratör | AÇIK — sahip kararıyla göreve dönüştürülecek (şimdilik bekletiliyor) |
| S-09 | **Marka kimliği seti versiyon kontrolü dışında** | Kök dizindeki `brand.md`, `design-tokens.json`, `ai-rules.md`, `company.md`, `assets/`, `prompts/`, `personas/` git kapsamı DIŞINDA ve tek kopya (kök `C:\Huginn Data Projesi` repo değil). Kayıp/yazım hatasında iz ve geri dönüş yok. (Gezinti bulgusu, cline 2026-09-16.) | cline, roo, sahip | ÇÖZÜLDÜ (BRAND-KIMLIK-01, D-44) — kit `docs/brand/` altına taşındı, üst dizin temizlendi, 14 dosyada Huggin→Huginn |
| S-10 | **Kök dizindeki geçici scriptler birikmiş** | Kökte `fix_*.py` ×7, `update_and_submit*.py` ×4, `modify_topbar*.py` ×2, `replace_app_functions.*`, `temp_script.py`, `dummy` — 18+ dosya; `scripts/` ise 243 dosya. D-25 ad kuralı var, arşiv/temizlik kuralı yok. (Gezinti bulgusu, cline 2026-09-16.) | cline, sahip | ÇÖZÜLDÜ (roo 2026-09-16) — üst dizin çöpleri `_trash/kok_disi_2026-09-16/`, repo kökü çöpleri `_trash/kok_2026-09-16/`, `scripts/_tmp_*` → `_trash/scripts_tmp_2026-09-16/`; kökte 5 .py kaldı |

## 5. Orkestratör Eleştirileri (Kilo)

| # | Konu | Açıklama | Etkilenen | Durum |
|---|------|----------|-----------|-------|
| O-01 | **P7-44 başlangıc alanı yanlış dosya yolu** | P7-44 başlangıc alanı web_dashboard/app.py diyor — böyle bir dosya yok. Kök app.py Streamlit uygulamasıdır. Bu hatalı yol, panoya yazan ajanlarda kök dosya yolu doğrulaması gerektirir. | orkestratör, roo | ÇÖZÜLDÜ (P7-45 tarafından düzeltildi) |
| O-02 | **P7-46 baslangic nonexistent dosyaya işaret ediyor** | P7-46 başlangıc web_dashboard/tabs/admin_settings.py diyor — dosya yok. copilot bu dosyayı yazmamış. Görev açıklamasında hedef dosya yolu doğrulanmalı. | orkestratör, copilot | **KISMEN (P7-46)** — iş, panoda kilitli olan gerçek dosya [`web_dashboard/tabs/admin_panel.py`](../web_dashboard/tabs/admin_panel.py) üzerinde yapıldı; `admin_settings.py` oluşturulmadı. Panodaki hatalı `baslangic` değeri hâlâ düzeltilmedi (K-03 ile aynı kök neden). |
| O-03 | **SSE endpointi testi yok** | /api/intelligence/dashboard/stream (P7-45) için herhangi bir test yok. Endpoint backend'de var ama Streamlit tarafı consume etmiyor. Backend-Frontend entegrasyonu kanıtlanmamış. | kilo | AÇIK |
| O-04 | **Demo rozetli alanlar gerçek veriyi gizliyor** | data/demo/*.jsonl ile çalışan ekranlar (Paketler, Pazarlama, Canli Veri) DEMO rozetini gösterse bile kullanıcı gerçek ile demo arasındaki farkı anlayamayabilir. Demo vs gerçek ayrımı daha belirgin olmalı. | kilo, roo | AÇIK |
| O-05 | **P7-44 kilit dosyası eksik** | DASH-UX-04 dosyalar alanında web_dashboard/tabs/paketler.py ve pazarlama.py var ama bunların backend servisleri (src/company_master/paketler.py, src/company_master/pazarlama.py) kilitlenmedi. UI kilitlendi ama backend kilitlemedi — tam tersi olmalı. | orkestratör, roo | AÇIK |
| O-06 | **Task board format tutarsızlığı** | Bazı görevlerde başlangıc string, bazıda liste. dosyalar bazıda dolu bazıda boş. Tutarlı format zorunlu olmalı. | orkestratör | ÇÖZÜLDÜ (FIX-ID-01) |

---

## Diğer ajanlara kısa özet

1. Streamlit rengi → `.streamlit/config.toml`. FastAPI rengi → `web_dashboard/css/style.css`. **Karıştırmayın.**
2. Bir sekme dosyası yazmak yetmez; `app.py`'de yönlendirmesi yoksa kullanıcı göremez.
3. Görev açarken `dosyalar` alanına yolu yazmadan önce dosyanın **var olduğunu doğrulayın**.
4. Demo veriyle çalışan her ekran DEMO rozetini korumalı.
5. Bir **ayar** yazmak yetmez; onu okuyan bir ekran yoksa kullanıcı için hiçbir şey değişmez (K-04).
6. Kullanıcıya özel veri yazarken kimliğin gerçekten çözüldüğünden emin olun; `misafir` düşüşü veriyi paylaştırır (S-08).

---

## Devredilen / Başka Ajanda Olan Konular

| Konu | Sorumlu | Not |
|------|---------|-----|
| Onay kuyruğunun birikmesi (UX-01, UX-02, UX-03, ROO-UX-ADMIN-01, ORCH-13, P7-46 `review`'da bekliyor) | cline (aktif orkestratör) | roo yalnızca sonucu gözlemler; onay verilmedikçe kilitler düşmez |
| `scripts/gorev_at.py pano` çıktısının okunaksız olması + pano kayıtlarında `id` alanının `None` dönmesi | cline (aktif orkestratör) | Düzeltme sonrası roo tekrar test eder |

---

## 6. UI Revizyon 2. Tur — Menü Ağacı Analizi (2026-09-14, roo)

> **Durum:** Sahip sitemap/menü ağacını hazırlıyor. Bu bölüm **sitemap gelmeden önce yapılan kök-sebep araştırmasıdır**; kod değişikliği yapılmadı. Sitemap gelince buradaki maddeler görev kalemlerine dönüştürülecek.
>
> **Referans:** https://docs.streamlit.io/get-started/installation/streamlit-playground
> **Ortam:** Streamlit **1.62.0** — `st.navigation` ve `st.Page` **mevcut** (doğrulandı).

### 6.1 Sahibin tespit ettiği 7 eksik → kod karşılığı

| # | Sahip şikayeti | Koddaki yeri | Kök sebep |
|---|---|---|---|
| U-01 | "Zaten Streamlit'in gece/gündüz teması var, sen sayfaya ikinci bir tema düğmesi koymuşsun" | [`app.py:403`](../app.py:403) `ThemeToggle(...)` — [`render_topbar()`](../app.py:390) içinde | Yerleşik ⋮ › Settings › Appearance zaten tema değiştiriyor. İkinci düğme **mükerrer** ve iki kaynak (URL `?tema=` vs Streamlit ayarı) birbirini tutmuyor |
| U-02 | "⋮ menüde **Wide mode** ayarı yok, orijinalinde olması gerekiyor" | [`app.py:63`](../app.py:63) `layout="wide"` **+** [`.streamlit/config.toml:29`](../.streamlit/config.toml:29) `toolbarMode = "minimal"` | **İki ayrı sebep birlikte çalışıyor:** (a) `set_page_config(layout="wide")` verildiğinde Streamlit "Wide mode" geçişini menüden kaldırır; (b) `toolbarMode="minimal"` menüyü zaten budar. İkisi de düzeltilmeden ayar geri gelmez |
| U-03 | "Ana menülerin altında **alt menüler** olmalı" | [`web_dashboard/tabs/__init__.py:44-75`](../web_dashboard/tabs/__init__.py:44) `TabTanimi` | Yapı **tek seviyeli (flat)**. Yalnız `grup` alanı var (2 grup), hiyerarşi alanı (`ebeveyn`/`alt_bolumler`) yok. Alt menü veri modeli olmadan çizilemez |
| U-04 | "Kompakt menüde **sadece menü isimleri** yazmalı, sen sadece ikon koymuşsun" | [`app.py:77`](../app.py:77) `KOMPAKT_SUTUN = 4` + [`_nav_grubu_ciz()`](../app.py:296) | Kompakt mod **ters kurgulanmış**: `st.button(tanim.ikon)` ile 4 sütunlu ikon ızgarası çiziliyor. Sahip tam tersini istiyor — **ikon yok, isim var** (ya da tek sütun dar liste) |
| U-05 | "Kompakt menü **responsive değil**" | [`app.py:299`](../app.py:299) `st.columns(KOMPAKT_SUTUN)` | `st.columns(4)` sabit; dar ekranda sütunlar sıkışıyor, Streamlit'in kendi kırılma noktası devreye girmiyor |
| U-06 | "Örnekteki **ikonlar ve ikon renkleri** güzeldi, sen yapmamışsın" | `TabTanimi.ikon` = emoji (🏠 👥 📦 …) | Playground **Material Symbols** kullanıyor (`:material/home:`) ve rengi temadan alıyor. Emoji **renk alamaz**, tema ile uyumlanmaz, platformlar arası farklı görünür |
| U-07 | "Cache temizleme ⋮ menüde zaten var, alta bir daha koymuşsun" | [`app.py:505`](../app.py:505) `render_footer()` → "🔄 Cache Temizle" | Mükerrer. `toolbarMode="minimal"` menüdeki "Clear cache"i gizlediği için footer'a eklenmiş olabilir — U-02 düzeltilince bu düğme gereksizleşir |

### 6.2 Kritik bulgu: mevcut navigasyon Streamlit'in kendi API'sini kullanmıyor

Şu an menü **elle** çiziliyor: `st.sidebar` + `st.button` döngüsü + `?bolum=` URL parametresi ([`app.py:290-382`](../app.py:290)). Streamlit 1.62 ise bunun **resmi karşılığını** sunuyor:

```python
st.navigation({"🏢 İş Operasyonları": [st.Page(...), ...],
               "🔧 Sistem & Yönetim": [st.Page(...), ...]})
```

`st.navigation` hazır olarak veriyor:

| İhtiyaç | Elle çizim (bugün) | `st.navigation` |
|---|---|---|
| Grup başlıkları / alt menü | `st.markdown("#####")` + manuel | Sözlük anahtarı = grup başlığı (**yerleşik**) |
| Aktif öğe vurgusu | `type="primary"` + `disabled=True` hilesi | Yerleşik, tema renginde |
| URL yönlendirme | Elle `?bolum=` + `st.query_params` | `st.Page(url_path=...)` ile **gerçek rota** |
| Responsive daralma | Yok | Yerleşik |
| Material ikon + tema rengi | Emoji (renksiz) | `icon=":material/home:"` |
| Erişilebilirlik (`nav` semantiği) | Buton yığını | Yerleşik |

**Sonuç:** U-03, U-04, U-05, U-06'nın dördü de tek hamlede — `st.navigation`'a geçerek — çözülüyor. Elle çizimi yamamak yerine taşınması önerilir.

> ⚠️ **Maliyet uyarısı (dürüst değerlendirme):** `st.navigation` **çok sayfalı (multipage)** modeli varsayar; her bölüm bir `st.Page` olur. Bugünkü tek-dosya + `render_icerik()` hata sınırı mimarisi buna göre yeniden kurulmalıdır. Bu **küçük bir yama değil**, orta ölçekli bir taşımadır. Sahibin "kısım kısım gidelim" talimatına uygun olarak **sitemap onaylandıktan sonra** ayrı bir görev olarak açılmalıdır.

### 6.3 Menü ağacı önerileri (sitemap ile karşılaştırılacak taslak)

Bugün **11 bölüm, 2 grup, 0 alt menü** var. Sahip alt menü istediğine göre olası kırılım:

| Ana menü | Önerilen alt menüler | Bugünkü karşılığı |
|---|---|---|
| 🏠 Ana Kontrol | — (tek sayfa kalmalı, giriş ekranı) | `ana_kontrol` |
| 👥 Müşteriler | Firma Listesi · Firma Detayı · Segmentler | `musteriler` (tek sayfa, içinde 3 bölüm) |
| 📦 Paketler | Paket Kataloğu · Çapraz Satış | `paketler` (içinde `_render_capraz_satis`) |
| 📢 Pazarlama | Kampanyalar · Segmentler · Performans | `pazarlama` (içinde `BOLUMLER` + `ALT_BOLUMLER` **zaten var**) |
| 🤖 Abrakadabra | — | `abrakadabra` (hazır değil) |
| ⚙️ Sistem | Sağlık · Kuyruk/DLQ · Performans · Dışa Aktarma | `sistem` (içinde 4+ panel) |
| 📡 Canlı Veri | — | `canli_veri` |
| 📋 Denetim | Dosya Kilitleri · Handoff · Tetik Günlüğü | `denetim` (içinde 3 bölüm) |
| 👨‍💼 Yönetim | Karar Defteri · Görev Panosu | `yonetim` (bileşik) |
| 🎛️ Ayarlar | — | `ayarlar` |
| ⏳ Yükleme | — | `yukleme` (demo/geliştirici) |

**Gözlem:** Alt menü adayları **zaten var** — ekranların içinde `Section`/`BOLUMLER` olarak duruyorlar (örn. [`pazarlama.py:41-85`](../web_dashboard/tabs/pazarlama.py:41) `BOLUMLER` + `ALT_BOLUMLER`). Yani alt menü **sıfırdan içerik üretmek değil, var olan bölümleri menüye yükseltmek** demek. Bu işi ucuzlatır.

**Açık sorular (sahibe) ve cevapları:**

| # | Soru | Cevap | Tarih |
|---|---|---|---|
| 1 | Alt menü **ayrı sayfa mı** (URL değişir) yoksa **sayfa içi çapa** mı? | ✅ **Ayrı sayfa** — sahip kararı: *"alt menü ayrı sayfa"* | 2026-09-14 |
| 2 | `⏳ Yükleme` bölümü menüde kalsın mı, Ayarlar altına mı gizlensin? | ⏸ **Sitemap'e göre birlikte karar** | — |
| 3 | `st.navigation` taşıması onaylanıyor mu? | ⏸ **Sitemap'e göre birlikte karar** | — |
| 4 | Genişlik varsayılanı (`layout` verilmesin mi, `config.toml`'a mı yazılsın)? | ⏸ **Sitemap'e göre birlikte karar** — *"menüler otursun sonra bu soruları sor"* | — |

**Soru 1'in teknik sonucu:** Alt menüler ayrı sayfa olacağına göre **`st.navigation` + `st.Page` doğru araç**tır; her alt menü kendi URL'ine sahip bir `st.Page` olur. Sayfa içi çapa (`SectionNav`) alternatifi elendi. Bu, 6.2'deki taşıma önerisini teknik olarak zorunlu kılar — ancak **sitemap onayı hâlâ ön şarttır**.

### 6.4 Önerilen uygulama sırası (kısım kısım)

| Sıra | İş | Risk | Durum | Not |
|---|---|---|---|---|
| 1 | U-01 + U-07: mükerrer tema ve cache düğmelerini kaldır | **Düşük** | ✅ yapıldı (2026-09-14) | Sadece silme; sitemap beklemeden yapıldı |
| 2 | U-02: `toolbarMode` + `layout="wide"` kararını düzelt | **Düşük** | ✅ yapıldı (2026-09-14) | Wide mode geri geldi; genişlik kararı kullanıcıda |
| 3 | U-06: emoji → Material Symbols | Orta | ⏸ sitemap bekliyor | `TabTanimi.ikon` sözleşmesi değişir, testler güncellenir |
| 4 | U-03 + U-04 + U-05 + **U-08**: `st.navigation` taşıması + sidebar arama modalı | **Yüksek** | ⏸ sitemap bekliyor | Sitemap onayı şart; ayrı görev. U-08 aynı bölgeye (sidebar) dokunduğu için bu pakete katıldı — bkz. 6.6 |

**Not (U-01 ile ilgili dikkat):** `ThemeToggle` bileşeni silinmiyor; yalnız `app.py`'deki çağrısı kaldırılıyor. Bileşen [`topbar.py:63`](../src/company_master/ui/components/topbar.py:63) ve testleri yerinde kalır — HTML müşteri paneli (8000) onu kullanmaya devam edebilir.

### 6.5 Uygulanan değişiklikler (2026-09-14, roo)

Sahibin "tamam halledelim" onayıyla 1. ve 2. sıra uygulandı. Dokunulan noktalar:

| Dosya / Konum | Değişiklik | Gerekçe |
|---|---|---|
| [`.streamlit/config.toml:29`](../.streamlit/config.toml:29) | `toolbarMode = "minimal"` → `"auto"` | `"minimal"` sağ üst ⋮ menüsünü buduyor, **Wide mode** ve **Clear cache** seçeneklerini gizliyordu. U-02 + U-07'nin ortak kök sebebi |
| [`app.py`](../app.py) — `set_page_config` | `layout="wide"` kaldırıldı | `layout` açıkça verilince Streamlit ⋮ menüsünden "Wide mode" geçişi kaybolur; genişlik kararı kullanıcıya bırakıldı |
| [`app.py`](../app.py) — import bloğu | `ThemeToggle`, `tema_dogrula`, `tema_karsiti` çıkarıldı | Sayfa içi tema düğmesi kaldırıldı (U-01) |
| [`app.py`](../app.py) — sabitler | `TEMA_PARAM` silindi; `STREAMLIT_TEMA_ESLEME` eklendi; `VARSAYILAN_TEMA` `"karanlik"` → `"aydinlik"` | `config.toml` `base = "light"` ile hizalandı |
| [`app.py:152`](../app.py:152) `aktif_tema()` | URL/oturum yerine `st.context.theme.type` okunuyor; `try/except` ile eski sürümde varsayılana düşüyor | Tema için **tek doğru kaynak** artık ⋮ menüsü › Settings › Appearance |
| [`app.py:390`](../app.py:390) `render_topbar` | İmza `(tanim, tema)` → `(tanim)`; `ThemeToggle` çağrısı ve `sag=[...]` kaldırıldı | U-01 mükerrer tema düğmesi |
| [`app.py:486`](../app.py:486) `render_footer` | `st.columns(4)` → `st.columns(3)`; `footer_cache_temizle` butonu silindi, yerine ⋮ menüsüne yönlendiren caption | U-07 mükerrer cache temizleme |

**Doğrulama:**
- Odak testi (`test_ui_components`, `test_dashboard_nav`, `test_web_dashboard_tabs`, `test_theme_system`): **204 passed / 3.76 sn**
- Tam regresyon (`python -m pytest tests -q`): **1423 passed, 2 skipped, 1 failed / 55.6 sn**. Tek hata `test_api_integration.py::TestVeriUclari::test_companies_liste_sozlesme` (`assert 14000 == 1`) — mock DB devreye girmiyor, gerçek veritabanına düşüyor. **Bilinen ve UI ile ilgisiz** izolasyon sorunu; ayrı görev olarak kayıtlı.

**Ortam notu — ✅ ÇÖZÜLDÜ (2026-09-14):** Kök dizinden `pytest -q` koşulduğunda `AI proje v1/` submodule'ü, `scripts/test_*.py`, `src/company_master/services/test_*.py` ve `workspace/external/...` de toplanıp **77 `import file mismatch`** hatası veriyordu. Sahibin onayıyla ([`pytest.ini`](../pytest.ini)) `testpaths = tests` + `norecursedirs` eklendi.

Doğrulama: `python -m pytest -q --collect-only` → **1426 test toplandı, 0 hata** (önce 77 error). Artık kök dizinden `pytest` koşmak güvenlidir.

---

## 6.6 U-08 — Arama konumu ve arama modalı (yeni istek, 2026-09-14)

**Sahibin isteği:** *"[docs.streamlit.io/develop/concepts](https://docs.streamlit.io/develop/concepts) arama kısmının konumu güzel ve arama yapınca modal açılıyor, bu özellik de hoşuma gitti."*

### Referansın davranışı

| Özellik | Referans (docs.streamlit.io) | Bugünkü Huginn paneli |
|---|---|---|
| **Konum** | Sol üst — sidebar'ın tepesinde, logonun hemen altında; sayfa kaydırılsa da sabit | Sağ üst içerik şeridinde ([`app.py:407`](../app.py:407) `render_topbar`), H1 ile aynı satırı paylaşır |
| **Tetikleme** | Tıklama **veya** `Ctrl/Cmd + K` kısayolu | Yalnız tıklama |
| **Sonuç sunumu** | Sayfanın üstünde açılan **modal (overlay)**; arka plan kararır | Aynı satırın altında **yan yana buton kolonları** (`st.columns`) |
| **Sonuç sayısı** | Kaydırılabilir liste, sınırsız | `ARAMA_MAKS_SONUC = 5` ile kesiliyor |
| **Kapatma** | `Esc`, dışarı tıklama, ✕ | Yok — sonuçlar sayfada asılı kalır |

### Bugünkü kodun sınırları

1. **Arama sonuçları düzeni bozuyor:** [`app.py:422-433`](../app.py:422) çoklu eşleşmede `st.columns` açıp topbar'ın altına buton satırı ekliyor; sayfa içeriği aşağı kayıyor.
2. **Sorgu temizlenemiyor:** [`app.py:414-416`](../app.py:414) yorumunda belirtildiği gibi, widget oluştuktan sonra `st.session_state[ARAMA_KEY]` yazılamaz (`StreamlitAPIException`). Sonuç: seçim yapıldıktan sonra arama kutusu dolu kalır.
3. **Tek eşleşmede sessiz zıplama:** [`app.py:420`](../app.py:420) tek sonuç bulunca kullanıcıya sormadan bölüm değiştiriyor — yazım sırasında istenmeyen sayfa geçişi riski.

### Çözüm önerisi

`st.dialog` mevcut (**Streamlit 1.62.0** ile doğrulandı; `st.dialog`, `st.popover`, `st.navigation` üçü de var).

```python
@st.dialog("Bölüm ara", width="large")
def arama_modali() -> None:
    sorgu = st.text_input("Ara", key="_hg_modal_sorgu", label_visibility="collapsed")
    for aday in bolum_ara(sorgu):
        if st.button(f"{aday.ikon} {aday.baslik}", key=f"m_{aday.anahtar}",
                     use_container_width=True, help=aday.aciklama):
            bolum_sec(aday.anahtar)   # modal kapanır, sayfa değişir
```

Tetikleyici sidebar'ın en üstüne taşınır (referansın konumu):

```python
with st.sidebar:
    if st.button("🔍 Ara…", use_container_width=True):
        arama_modali()
```

**Kazanımlar:** düzen bozulmaz (overlay), sorgu modal kapanınca sıfırlanır (2. sınır çözülür), sessiz zıplama ortadan kalkar (3. sınır çözülür), sonuç listesi sınırsız kaydırılabilir.

**Maliyet ve riskler:**
- `render_topbar` imzası ve testleri değişir (`test_ui_components.py` topbar arama testleri).
- `ARAMA_MAKS_SONUC` sabiti anlamsızlaşır veya kaydırma sınırına dönüşür.
- `Ctrl+K` kısayolu Streamlit'te **yerleşik değildir**; JS enjeksiyonu gerektirir — MVP'de kapsam dışı bırakılması önerilir.
- Arama sidebar'a taşınırsa, `st.navigation` taşıması (U-03/04/05) ile **aynı bölgeye** dokunur → **ikisi tek görevde yapılmalı**, aksi halde sidebar iki kez yeniden yazılır.

**Karar:** U-08, U-03/U-04/U-05 ile **birleştirilip sitemap sonrasına** bırakılır. Tek başına yapılırsa iş iki kez yapılmış olur.

---

## 7. Dikkat Notları Defteri (tur bazlı, 2026-09-15'ten itibaren)

> Her teslim raporunun "Dikkat (eleştirel notlar)" bölümü buraya `D-` satırı olarak işlenir.
> Sütunlar: **Belirti** = sorun ortaya çıkınca ne görürsün (arama için anahtar kelime buraya);
> **Çözüm / Önlem** = ilk yapılacak iş. Çözülünce `Durum` güncellenir, satır silinmez.

### 7.1 Ortam / Altyapı (sık tekrar eden tuzaklar)

| # | Tarih | Görev | Belirti | Kök neden / Risk | Çözüm / Önlem | Etkilenen | Durum |
|---|---|---|---|---|---|---|---|
| D-01 | 2026-09-15 | genel | Streamlit'te kod değişikliği ekrana yansımıyor; F5 işe yaramıyor | [`.streamlit/config.toml`](../.streamlit/config.toml) `fileWatcherType = "none"` — otomatik yükleme kapalı | UI dosyasına dokunan ajan `python scripts/streamlit_restart.py` çalıştırır; sahip yalnız F5 | tüm ajanlar | KURAL (AGENTS.md) |
| D-02 | 2026-09-15 | genel | `/api/health` ok ama yeni endpoint **404** | 8000 portu Docker container'ında; `web_app.py` imaja **kopyalanır**, volume değil → yerel watchdog restart container'ı güncellemez | `docker compose up -d --build api` → `curl` ile yeni yolu doğrula | tüm ajanlar | KURAL (AGENTS.md) |
| D-03 | 2026-09-15 | genel | Test dosyası "BOM" / `test_guard_bom_ratchet` kırmızı; `SyntaxError: invalid non-printable character` | PowerShell `Out-File -Encoding utf8` BOM yazar; kilo teslimlerinde tekrar etti ([`tests/test_kariyernet.py`](../tests/test_kariyernet.py), [`app.py`](../app.py) bozuk kopya) | Python `open(..., encoding="utf-8")` ile yaz; teslim öncesi `python scripts/kodlama_denetim.py` | kilo, tüm ajanlar | AÇIK — P7-6b bekliyor; GUARD-ENC-01 (cline) guard yazıyor |
| D-04 | 2026-09-15 | genel | cmd'de `python -c "...\n..."` → SyntaxError; `findstr /v "^$"` boş çıktıda **exit 1** | Windows cmd çok satır `-c` desteklemez; findstr eşleşme yoksa hata kodu döner | Tek satır list comprehension / geçici script `data/_tmp/`; findstr'ı `|| exit 0` ile sarma ya da sonucu yorumlarken exit 1'i hata sayma | roo, tüm ajanlar | BİLGİ |
| D-05 | 2026-09-15 | genel | `git push` sonrası status "[ahead 1]" kalıyor | Submodule (`AI proje v1`) pin'i / bayat ref; commit aslında origin'de | `git fetch` + `git log origin/<dal> -1` ile doğrula; submodule değişikliği ayrıca commit edilmeli | roo | BİLGİ |
| D-06 | 2026-09-15 | genel | Commit'te bol **CRLF uyarısı** | `.gitattributes` renormalize yapılmadı | Ertelendi: `git add --renormalize .` ayrı bir hijyen görevi | roo | AÇIK — ertelendi |
| D-07 | 2026-09-15 | genel | Kökte `fix_*.py`, `apply_fix*.py`, `original_content.txt`, `fix.ps1` çöpleri | kilo geçici düzeltme scriptlerini repo köküne bıraktı (Proje Sınırı Kuralı md.2 ihlali) | Geçici dosya `data/_tmp/`'ye; kök temizliği hijyen görevi | kilo, roo | ÇÖZÜLDÜ (roo 2026-09-16, bkz. S-10) — `original_content.txt` sahip izniyle `_trash/kok_2026-09-16/`'ya taşındı (içerik: kilo'nun mojibake bozuk `yonetim` sekmesi yedeği; canlı kodda karşılığı yok) |
| D-08 | 2026-09-15 | genel | `tests/test_api_integration.py::test_companies_liste_sozlesme` `assert 14000 == 1` | Mock DB devreye girmiyor, gerçek DB'ye düşüyor (izolasyon) | UI ile ilgisiz; ayrı görev | tüm ajanlar | AÇIK |

### 7.2 MVP-ADMIN serisi (2026-09-15)

| # | Tarih | Görev | Belirti | Kök neden / Risk | Çözüm / Önlem | Etkilenen | Durum |
|---|---|---|---|---|---|---|---|
| D-09 | 2026-09-15 | ADMIN-ENV-01 | Admin giriş formu `.env`'deki e-posta/şifreyle **ön-dolu** geliyor | Kolaylık için `ADMIN_EMAIL/ADMIN_PASSWORD` okunuyor; şifre formda görünür (paylaşımlı ekranda risk) | Yalnız yerel geliştirmede kabul; üretimde ön-dolum kapatılmalı (env bayrağı) | roo, sahip | BİLGİ — üretim öncesi kapat |
| D-10 | 2026-09-15 | MVP-KUL-01 | Sahip bildirimi: giriş/çıkış sonrası **başarı mesajı yok**, **şifre değiştirme yok** | İlk teslim kapsam dışı bırakmış | ADMIN-RESET-01 ile [`render_sifre_degistir()`](../web_dashboard/tabs/admin_auth.py:108) + `flash_goster()` eklendi | kilo, roo | ÇÖZÜLDÜ (ADMIN-RESET-01) — rota envanteri eksik, bkz. D-11 |
| D-11 | 2026-09-15 | ADMIN-RESET-01 | Rota envanteri testi `/api/admin/change-password`'ü tanımıyor | Yeni endpoint eklendi, envanter listesi güncellenmedi | kilo: rota envanterine ekle | kilo | AÇIK |
| D-12 | 2026-09-15 | MVP-KUL-02 | 4 test failed → tek kök neden `admin_extras.py` **SyntaxError** | kilo'nun elle "fix" scriptleri dosyayı bozdu (D-07 ile aynı olay) | kilo düzeltti, onay kuyruğunda; cline review → roo onay | kilo, cline, roo | REVIEW |
| D-13 | 2026-09-15 | UI-SIDEBAR-02/TOPBAR-02 | `app.py` bozuk kopya (encoding), teslim reddedildi | D-03 ile aynı kök neden | `git checkout app.py`; kilo yeniden teslim | kilo | AÇIK — yeniden teslim bekliyor |
| D-14 | 2026-09-15 | UI-CHART-01 | KPI trend grafikleri **tek noktalı** / geçmiş verisi yok | `/api/kpi` yalnız anlık değer döner; `/api/kpi/history` yok | Sparkline şimdilik mevcut trend tablolarından; `/api/kpi/history` ertelendi | roo, kilo | AÇIK — ertelendi |
| D-15 | 2026-09-15 | UI-CHART-01 | plotly yoksa grafik çökmesin | [`web_dashboard/charts.py`](../web_dashboard/charts.py) `try: import plotly` + `st.bar_chart` fallback | Fallback var; plotly `requirements`'ta olmalı | roo | BİLGİ |
| D-16 | 2026-09-15 | orkestrasyon | roo posta kutusunda **bayat ADMIN-RESET-01 tetiği** (görev kilo'ya devredildi ama tetik kaldı) | `devret` tetiği kaynaktan silmiyor | Tetiği elle temizle; `cmd_devret` düzeltmesi önerisi | roo | AÇIK |
| D-17 | 2026-09-15 | orkestrasyon | Streamlit 1.63.0 yükseltmesi | Yeni sürüm `st.navigation` iyileştirmeleri getiriyor; test kırılma riski | Ertelendi; sitemap taşımasıyla birlikte | roo | AÇIK — ertelendi |

### 7.3 AI-CI serisi — Anthropic × GitHub (2026-09-15, commit `caa71c8`)

| # | Tarih | Görev | Belirti | Kök neden / Risk | Çözüm / Önlem | Etkilenen | Durum |
|---|---|---|---|---|---|---|---|
| D-18 | 2026-09-15 | AI-CI-01 | CI kırmızı ama **"CI hata açıklama" yorumu gelmiyor** | `workflow_run` tetikleyicisi yalnız **varsayılan daldaki** workflow dosyasından çalışır; [`anthropic-ci-explain.yml`](../.github/workflows/anthropic-ci-explain.yml) henüz `main`'de değil | `chore/monorepo-merge` → `main` merge edilince aktifleşir; o zamana kadar beklenen davranış, hata değil | roo, sahip | AÇIK — main merge bekliyor |
| D-19 | 2026-09-15 | AI-CI-01 | Yerelde `ModuleNotFoundError: anthropic` | `.venv`'de SDK yok; runner'da composite action kurar | Script geç import (`claude_sor` içinde) — yerel testler SDK'sız çalışır; yerelde kurma **gerekmez** | tüm ajanlar | BİLGİ |
| D-20 | 2026-09-15 | AI-CI-01 | `develop`'a açılan PR'da CI ve review çalışmıyor | [`ci.yml`](../.github/workflows/ci.yml) `pull_request.branches: [main]` | İstenirse `[main, develop]` yapılır (isteğe bağlı) | roo | AÇIK — isteğe bağlı |
| D-21 | 2026-09-15 | AI-CI-01 | Federation/org/workspace ID'leri workflow'da **düz metin** | [`action.yml`](../.github/actions/anthropic-oidc/action.yml) içinde sabit; gizli değil ama repo public olursa görünür | Public'e geçmeden `vars.ANTHROPIC_*` (repo variables) altına taşı | roo | AÇIK — public öncesi |
| D-22 | 2026-09-15 | AI-CI-01 | İlk PR'da `401/403` Anthropic kimlik hatası | Anthropic Console → Workload Identity federation rule `repository` claim'i bu repo ile eşleşmiyor olabilir | İlk PR'da Actions logunu izle; claim'i `owner/repo` olarak doğrula | sahip, roo | AÇIK — ilk PR'da doğrulanacak |
| D-23 | 2026-09-15 | AI-CI-01 | decision_log yazımında exit 1 → çift kayıt olasılığı | D-04 (findstr) | Kayıt zaten yazılmışsa ikinci çağrı yapma; `search_decisions` ile kontrol | roo | BİLGİ |
| D-24 | 2026-09-15 | LOGIN-FIX-01 | `/kimlik` admin girişi "çalışıyor gibi" ama menü büyümüyor (P0) | `.env`'de `ADMIN_EMAIL/ADMIN_PASSWORD` **3x tekrar**; python-dotenv dosya içi tekrarda **son** değeri alır → DB ile uyuşmayan çift ön-dolduruldu → API 401. Ek: sayfa token varken de boş form çiziyor, flash gösterilmiyordu → sahip sonucu göremedi | (1) [`env_upsert`](../scripts/admin_sifre_sifirla.py:48) tekrarları siler; (2) `.env` tekilleştirildi; (3) [`render_admin_login`](../web_dashboard/tabs/admin_auth.py:59) token varken oturum+çıkış+"N bölüm görünür", 401'de ipucu; (4) teşhis araçları [`admin_env_eslesme.py`](../scripts/admin_env_eslesme.py), [`admin_login_probe.py`](../scripts/admin_login_probe.py). **Kural:** `.env` düzenlerken tek anahtar-tek satır; ön-dolum bug'ında önce `admin_env_eslesme` | tüm ajanlar | ÇÖZÜLDÜ |
| D-25 | 2026-09-15 | genel | Dosya adları çok uzun (sahip şikâyeti) | Tarih + görev ID + ajan adı dosya adına yazılıyordu | **Kural:** kısa snake_case; tarih dosya **içinde** (başlıkta), adda değil; görev ID ≤10 kr; doküman adı ≤3 kelime. Örn. `admin_login_probe.py`, `admin_env_eslesme.py` | tüm ajanlar | KURAL |
| D-26 | 2026-09-15 | LOGIN-FIX-01 | cmd'de çok satırlı `python -c "..."` sessizce çıktı vermiyor / etkisiz; `curl -w "%{http_code}"` `%` yorumu | Windows cmd tırnak/satır işleme; `%` cmd değişken önekidir | Tek satır `python -c` ya da `scripts/` altında kısa script; curl'de `%%{http_code}` | tüm ajanlar | KURAL |
| D-27 | 2026-09-15 | KPI-EXA-01 | KPI kartları "iğrenç/rezalet" (sahip): gradient + renkli sol şerit + gölge; "diyagram" isteği renk kodu sanıldı | Sahip referansı (dashboard.exa.ai) okunmadan "süslü" yorumlandı; "diyagram" = **süreç/akış** diyagramıydı | **KPI sade sözleşme:** `surface` zemin + `1px solid border`, radius 10, **gradient/box-shadow/border-left yasak**, hover yalnız çerçeve; kategori = 6px nokta; değer tabular-nums. Akış = Graphviz `veri_akisi()` (LR, dolgusuz kutu). Test: [`test_kpi_karti_html_sabit_genislik_yok`](../tests/test_charts.py:179) `width:` yasaklar | tüm ajanlar (UI) | KURAL |
| D-28 | 2026-09-15 | KPI-EXA-01 | `veri_akisi()` içinde `st` tanımsız — üretimde `NameError` olurdu; test ilk turda yanlış mock (`charts.st`) ile yakalayamadı | `charts.py` `st`'yi modül düzeyinde import etmez; sarmalayıcılar fonksiyon içi `import streamlit as st` kalıbı kullanır | Sarmalayıcı eklerken kalıbı kopyala; testte `sahte_st` fixture (`sys.modules["streamlit"]`) kullan, `monkeypatch.setattr(charts,"st",..)` değil | roo | BİLGİ |
| D-29 | 2026-09-16 | ELESTIRI-01 | Defter başlığındaki "Son güncelleme" tarihi bayat kalıyor | Dosya 2026-09-16 21:23'te güncellendi; başlık 2026-09-15 gösteriyordu — ajanlar bayat/güncel ayrımı yapamıyor | **Kural önerisi:** her katkıda başlık tarihi güncellenir | tüm ajanlar | ÖNERİ |
| D-30 | 2026-09-16 | ELESTIRI-01 | Paylaşımlı defterler görev kilit listesine alınmamalı | ELESTIRI-01 ataması bu dosyayı otomatik kilitledi; defter ortak, katkı kuralı "sona ekle" — kilit diğer ajanların katkısını engeller (sahip düzeltti, kilit bırakıldı) | **Kural önerisi:** `gorev_at --dosya` paylaşımlı defterleri (bu dosya, decision_log) kilit mesafesinde tutmalı; inceleme görevi `--dosya`sız açılır | orkestratör, tüm ajanlar | ÖNERİ |
| D-31 | 2026-09-16 | BRAND-KIMLIK-01 | cmd `for %f in (...) do @cmd1 & cmd2 & cmd3` zinciri **her iterasyonda** cmd2/cmd3'ü tekrar çalıştırdı (5 kez robocopy+dir) | `&` zinciri `for` gövdesine dahil sayılır; parantezsiz gövde sınırı belirsiz | `for` gövdesini `( ... )` ile sınırla veya döngüyü ayrı komut olarak çalıştır; tek satır `python -c "exec(...)"` tercih et (D-04 ile aynı aile) | tüm ajanlar | BİLGİ |
| D-32 | 2026-09-16 | BRAND-KIMLIK-01 | `robocopy /MOV` aynı içerikli hedef varsa kaynağı **silmeden atlar** (üst dizinde orijinaller kaldı) | robocopy "same" dosyaları kopyalamaz → MOV silme adımı da atlanır | Taşıma sonrası `dir` ile kaynağı doğrula; gerekirse `del` + `rd /s /q` ile elle temizle | tüm ajanlar | BİLGİ |
| D-33 | 2026-09-16 | MARKA-REVIZE-01 | `tests/test_i18n.py:29` `HATALI_YAZIM` regex'i `Huggin` (tek n, çift g) yazımını yakalamıyor; kit 14 dosyada bu yazımla gelmişti | Regex yalnız Muginn/Hugin\b/Munin\b/Hugginn/Munnin/Odinn kapsıyor | MARKA-REVIZE-01 kilo adımı: `Huggin\b` + `Odın` ekle, `docs/brand/` taramaya dahil et | kilo, cline | AÇIK — görevde |
| D-34 | 2026-09-16 | BRAND-KIMLIK-01 | Üç farklı primary renk: kit `#2563FF`, dashboard `tokens.py #6366f1`, Streamlit `config.toml #FF4B4B` | Kit pazarlama için üretildi; dashboard Copilot UX sözleşmesi ile Indigo; config.toml Streamlit varsayılanı | **D-45 kararı:** kit = pazarlama/web/logo; tokens.py = ürün UI (değişmez); `config.toml primaryColor` → `#6366f1` hizası MARKA-REVIZE-01 kilo adımı | kilo, roo | AÇIK — görevde |
| D-35 | 2026-09-16 | ROO-REV-01 tetiği | Panoda kaydı olmayan tetik (`ROO-REV-01`, 21× uyarı) `al` ile alınamıyor (`Görev panoda bulunamadı`), `teslim` ile "review"e geçip **hayalet onay** üretiyor: `trigger.onay_bekleyenler()` `tb.gorev_getir()` boş dönünce `durum != done` sayıp tetik `teslim` kaydını kuyruğa ekliyor | `onay_bekleyenler` pano-dışı görev için `g = {}` fallback'i "done değil" olarak yorumluyor; `bakim` de bu kaydı temizlemiyor | ORCH-13 kapsamı: (1) `onay_bekleyenler` panoda olmayan task_id'yi atlasın veya "PANO DIŞI" etiketiyle göstersin; (2) `bakim` panosuz `bekliyor/teslim` tetiklerini `onaylandi`/`iptal`e çeksin; (3) `tetik_ekle` panoda olmayan görev için uyarı versin. Geçici çözüm: roo tetik kaydını elle `onaylandi` yaptı | roo, kilo | AÇIK — ORCH-13'e bağlı |

## 8. Madde → Görev Dönüşüm Listesi (ELESTIRI-01, roo 2026-09-16)

Sahip talimatı (md.5) gereği toplu değerlendirme. Öncelik: A = bu sprint, B = sonraki, C = sahip kararı.

| Madde | Önerilen görev | Ajan | Öncelik | Not |
|---|---|---|---|---|
| S-09, S-10, D-07 | — | — | ✅ | Bu tur çözüldü |
| D-33, D-34 | MARKA-REVIZE-01 (zincir cline→kilo→roo) | cline, kilo | A | Brif: `docs/plans/MARKA-REVIZE-01_brief.md` |
| K-04, S-08 | SEC-AUTH-01 (Aşama A cline'da) | cline | A | Zaten açık; `misafir` paylaşımı Aşama B |
| D-08 | TEST-ISO-01: `test_api_integration` mock DB izolasyonu | kilo | A | 1 test, `conftest` fixture |
| D-06 | GIT-HIJYEN-01: `git add --renormalize .` + `.gitattributes` | roo | B | Tek commit, diğer ajanlar boşken |
| M-06 | API-SPLIT-01: `web_app.py` (3141 satır) → `routers/` | kilo | B | SEC-AUTH-01 Aşama B bitince; 4 parça (buyer/admin/companies/intelligence) |
| M-03, M-04, M-05 | UI-MIMARI-02 | kilo | B | UI-SIDEBAR-02/TOPBAR-02 ile birleştir |
| O-03, S-06 | ORCH-13: kilit/tetik bayatlama otomasyonu | kilo | B | `gorev_kutusu.py bakim` genişletme |
| D-11, D-16 | GUARD-ENC-02 | kilo | B | Backlogda var |
| D-29, D-30 | Kural: `AGENTS.md` sözlük satırı + `gorev_at` paylaşımlı-defter istisnası | roo | A | Bu sprint AGENTS.md sözlük işi ile |
| S-07 | Kod + AGENTS.md kuralı | roo | C | ÇÖZÜLDÜ 2026-09-16 — sahip kararı: P0/P1 elle, P2+ otomatik; oto_nobetci/hepsini-tamamla filtreli; tekrar ihlalde oto-nobetci kapatılır |
| `original_content.txt` (kök) | Silme | roo | C | ÇÖZÜLDÜ 2026-09-16 — `_trash/kok_2026-09-16/`'ya taşındı (git mv) |
| Codecov token | GitHub secret `CODECOV_TOKEN` | sahip | C | Yoksa yalnız kapsam raporu yüklenmez; CI kırılmaz (`fail_ci_if_error: false`) |
| Anthropic OIDC 401 | Anthropic Console federasyon kuralı (`fdrl_01N5WF…`) repo/branch eşleşmesi | sahip | C | Yoksa PR'a otomatik Claude yorumu gelmez; CI kırılmaz |
