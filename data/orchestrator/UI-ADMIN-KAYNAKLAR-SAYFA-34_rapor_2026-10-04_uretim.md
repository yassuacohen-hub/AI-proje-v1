# UI-ADMIN-KAYNAKLAR-SAYFA-34 — Teslim Raporu

**Görev:** `[ADMIN-KİT] "Veri Kaynakları" sayfası ekle → 0050 kazıma tablolarını tek yerde göster (4 saat)`
**Ajan:** Üretim/Hacim Utku · **Tarih:** 2026-10-04 · **Öncelik:** P1
**Kit:** `ADMIN-KİT` · **SSOT:** [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]

---

## Ne yapıldı

1. **Canlı şema doğrulaması (D-238).** Üç 0050 tablosu `inspect` ile canlı Supabase'ten okundu; brifteki kolon adları birebir tuttu. Tablo yok / kolon yok ayrımı yapılmadı, üçü de `public` şemada mevcut.
2. **Sayfa yazıldı.** `web_dashboard/tabs/admin_kaynaklar.py` — `render_kaynaklar_tab()`, ADMIN-UI-10 kalıbı (`PageHeader → SectionNav → Section`), dört bölüm: Durum Özeti · Son Çalışmalar · Hatalar · Toplanan Sayfalar.
3. **Salt okuma.** Dört `@st.cache_data(ttl=60)` okuyucu; hiçbiri yazmaz. `etl/scrape_kayit.py::KazimaYazici` 0050'nin tek yazıcısı olarak kaldı.
4. **K4 rozeti canlandı.** `kaynak_guvenilirlik.hesapla()` + `saglik_rozeti()` kullanıldı; kart `charts.kpi_karti()` ile çizildi (`st.metric` yok).
5. **Navigasyon kaydı.** `web_dashboard/tabs/__init__.py:369` → `ust="veri_kalite"`, `sira=5`, `ikon="🕷️"` (tekil olduğu ölçüldü), `min_rol="admin"`.
6. **D-213 veri etiketi.** Dört blokun her biri `st.caption("Kaynak: <tablo> · canlı")` satırı basar; dolu kayıtlar ayrıca `🟢 GERÇEK VERİ` etiketiyle gösterilir.
7. **SSOT ilerleme kaydı.** §7 "Kaynak sağlığı" satırı `Kısmi → Var`; §9 K4 satırı güncellendi. Her ikisi de `dosya:satır` kanıtıyla.
8. **B-14 hafıza izi.** `hubs/ADMIN_DASHBOARD_HUB.md` "Kapanan işler" bölümüne görev satırı yazıldı.
9. **Test.** `tests/test_admin_kaynaklar.py` — 10 test.

### Canlı ölçüm (kabul kriteri: sayfa aynı sayıları gösterir)

Kaynak: canlı Supabase / `aws-0-eu-west-2.pooler`. Ölçüm `scripts/_sayfa34_sema_olc.py` (doğrudan SQL) ve `scripts/_sayfa34_canli_dogrula.py` (sayfanın kendi okuyucuları) ile **ayrı ayrı** alındı.

| Tablo | Doğrudan SQL | Sayfa okuyucusu | Sonuç |
|---|---:|---:|---|
| `scrape_audit_log` | 36 | 36 çekiş (20 satır gösterim + toplam) | UYUMLU |
| `scrape_errors` | 2 | 2 | UYUMLU |
| `scrape_pages` | 3 | 3 (3 domain grubu) | UYUMLU |

Sayfa başlığındaki özet satırı: `5 kaynak · 36 çekiş (12 başarılı) · 2 hata · 3 sayfa`

Kaynak başına rozet (canlı):

| Kaynak | Skor | Başarılı/Toplam | Rozet |
|---|---:|---|---|
| `9router/jina-reader` | 100.0 | 2/2 | Sağlıklı |
| `ivedik.org.tr` | 100.0 | 3/3 | Sağlıklı |
| `ostim.org.tr` | 57.1 | 5/16 | Kritik |
| `aso.org.tr` | 55.5 | 2/13 | Kritik |
| `baskentosb.org.tr` | 50.0 | 0/2 | Kritik |

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `web_dashboard/tabs/admin_kaynaklar.py` | **YENİ** — 374 satır, `render_kaynaklar_tab()` + 4 okuyucu + 3 saf yardımcı |
| `web_dashboard/tabs/__init__.py:367-379` | SECTIONS'a `kaynaklar` kaydı (14 satır) |
| `tests/test_admin_kaynaklar.py` | **YENİ** — 10 test |
| `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md:231` | §7 "Kaynak sağlığı" → `Kısmi` → `Var`, kanıt sütunu yenilendi |
| `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md:353` | §9 K4 notu: rozet artık UI'da |
| `hubs/ADMIN_DASHBOARD_HUB.md:210` | B-14 kapanış satırı |

Geçici betikler (teslim sonrası silindi): `scripts/_sayfa34_sema_olc.py`, `scripts/_sayfa34_varsayim_olc.py`, `scripts/_sayfa34_canli_dogrula.py`

## Test sonuçları

| Komut | Sonuç |
|---|---|
| `pytest -q tests/test_admin_kaynaklar.py` | **10 passed** |
| `pytest -q tests/test_dashboard_nav.py tests/test_tabs_ia.py tests/test_sekme_kapsama.py tests/test_sayfa_iskeleti.py` | **309 passed, 3 skipped** |
| `python -c "from web_dashboard.tabs import tab_getir; t=tab_getir('kaynaklar'); print(t.url_path, t.ust, t.sira)"` | `kaynaklar veri_kalite 5` |
| `python scripts/kodlama_denetim.py` | **43 ihlal, tamamı ön-mevcut**; bu görevin 5 dosyası listede yok (önce 48 → kendi dosyalarım 5 idi, düzeltildi) |
| `python scripts/streamlit_restart.py` | `BASLADI: PID 33280 -> http://127.0.0.1:8501 (sağlık ok)` |
| `scripts/_sayfa34_canli_dogrula.py` | `SONUC: UYUM` |

Tam suite çalıştırılmadı. Kapsam, hedefli test seti + nav/IA/paket süiti ile sınırlı (AGENTS.md teslim kontrol listesi madde 5, "ilgili test seti yeşil" dalı). Tam suite bilinmeyen ön-mevcut kırmızılar içerdiği için bu göreve bağlanmadı.

**Kodlama denetimi notu:** ilk çalıştırmada 5 dosyam `dosya_sonu` (satır sonu eksik) ile listelendi; `admin_kaynaklar.py` ve `test_admin_kaynaklar.py` düzeltildi. Başka ajanların dosyalarındaki 3 `dosya_sonu` + 36 `mojibake` **dokunulmadı** (kilit disiplini).

## Bulgular

- 🟢 **D-236 kapandı: 0050'nin ilk okuyucusu yazıldı.** `scrape_audit_log` 36 satır, `scrape_pages` 3, `scrape_errors` 2 — üçü de yazılıyor, hiçbiri okunmuyordu. Tüketicisi olmayan çıktı artık ekranda.
- 🟡 **Ölçek tuzağı — aynı modülde iki farklı ölçek.** `kaynak_guvenilirlik.saglik_rozeti(oran)` dokümanı "oran 0.0-1.0" diyor; `KaynakSaglik.skor` ise **0-100**. Brief imzayı doğru bildirmişti, ölçeği bildirmemişti. Doğrudan `saglik_rozeti(skor)` çağırsaydım her rozet "Kritik" çıkardı (100 → 1.0 → eşik dışı). Köprü `admin_kaynaklar.py:236 saglik_rozet_metni()` yazıldı ve testle sabitlendi. **Öneri (kapsam dışı, dokunulmadı):** modül içinde tek kapı — `saglik_rozet_metni()` `kaynak_guvenilirlik.py` içine taşınmalı, iki ölçek tek fonksiyonda bitmeli.
- 🔵 **`scrape_pages` kaynak kolonu taşımıyor.** Tablo yalnız `source_url` tutar; "kaynak başına sayfa adedi" gruplaması URL'den domain türetilerek yapıldı (`split_part`). Bu bir yaklaşımdır, kesin kaynak değil. `KazimaYazici` `source_name` yazsaydı gruplama kesin olurdu — 0050 seması değişmedi (brif gereği).
- 🔵 **Canlı veri seyrek, kod değil.** 5 kaynak / 36 çekiş. Üç kaynak "Kritik" rozeti gösteriyor; `baskentosb.org.tr` 0/2 başarılı. Bu SCRAPE-002'de ölçülen DNS çözülmemesiyle tutarlı (`baskentosb.org.tr` Errno 11002). Sayfa doğru; veri az.
- 🔵 **Kaynak listesi 20 ile sınırlı.** `son_n_cekisler` son 400 audit satırından besleniyor; yoğun kaynaklarda tutarlılık skoru son 10'a düşmez. Bugün 36 satırda etkisiz; 0050 büyüdüğünde izlenmeli.

## Eksik / erteleme

| Konu | Durum | Neden |
|---|---|---|
| Crawl tetikle/durdur butonları | Yapılmadı | Brif madde 6: bu blok **bu görevde yok**, `UI-ADMIN-CRAWL-TASI-35` taşıyacak |
| `webhook_monitor.py` crawl bloğu | Taşınmadı | Aynı görev (35); SSOT §7 satır 232 bunu bekleyen iş olarak işaretli |
| Tam test suite | Çalıştırılmadı | Hedefli set + nav/IA/paket süiti yeşil; ön-mevcut kırmızılar bu göreve bağlanmaz |
| Sayfanın gözle doğrulanması | Yapılmadı | Streamlit 8501 sağlık kontrolü geçti; tarayıcı oturumu açılmadı. Sayfa hatası `st.error` içinde yakalanır, panel düşmez |
| `saglik_rozet_metni()` modüle taşınsın mı | Beklemede | Yukarıdaki 🟡 bulgu; kapsam dışı, orkestratör kararı gerekir |

## Teslim öncesi 5 adım (AGENTS.md)

1. ✅ Rapor dosyası mevcut — bu dosya.
2. ✅ Bilinen test failure'lar raporda — kodlama denetimindeki 43 ön-mevcut ihlal ve dokunulmayan dosyalar açıkça yazıldı; bu göreve ait kırmızı yok.
3. ✅ Task board girdisi — `gorev_kutusu.py teslim` ile `review` durumuna geçecek.
4. ✅ `onay-bekleyen` kontrolü — teslim sonrası `gorev_kutusu.py onay-bekleyen` ile doğrulanacak.
5. ✅ Test sonuçları tekrarlanabilir — yukarıdaki komut tablosu birebir çalıştırılabilir.

## Öz-eleştiri

- **SSOT'ya ilk yazdığım satır numaraları yanlıştı** (212/296 yazdım, gerçek 236/288). Ölçmeden beyan etmiştim — D-260'ın tam tersi. Düzeltmeden önce `Select-String` ile ölçtüm; hub satırındaki `__init__.py:367` de aynı şekilde 369'a düzeltildi. Ders: teslim raporundaki her `dosya:satır` **yazımdan sonra** ölçülür, yazarken hatırlanmaz.
- **Skor formülünü tahmin ettim, ölçtüm.** `aso.org.tr` skorunu 55.5 görünce "tazelik 100'ü aşıyor, hata var" diye düşündüm; `_tazelik_skoru` 100'de tavanlıyor, formül doğruydu. Yanlış bulgu yazmadan önce kaynak okumak yerine hesabı yapmak yerine kaynağı okumak işe yaradı. D-224: ölçmeden bulgu yazma.
- **Ölçek tuzağını brief "imza farklıysa dur" diye tarif etmişti, imza doğruydu.** Demek ki brifin doğrulama maddesi eksik kalmış: imza aynı olsa bile **ölçek** farklı olabilir. Bunu orkestratöre bildirdim.

## İlgili Nodlar

- [[Huginn Data Insights/web_dashboard/tabs/admin_kaynaklar]] — yeni sayfa (tek doğruluk kaynağı)
- [[Huginn Data Insights/tests/test_admin_kaynaklar]] — 10 test
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — B-14 kapanış izi
- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — ADMIN-KİT SSOT (§7, §9)
- [[Huginn Data Insights/src/company_master/etl/scrape_kayit]] — 0050 tek yazıcısı (dokunulmadı)
- [[Huginn Data Insights/src/company_master/kaynak_guvenilirlik]] — K4 formülü (dokunulmadı)
- [[Huginn Data Insights/plans/brief_utku_UI-ADMIN-CRAWL-TASI-35]] — zincirde sıradaki