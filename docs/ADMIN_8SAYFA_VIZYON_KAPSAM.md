# Admin Panel — 8 Sayfalık Vizyon Mockup'ı Kapsam Araştırması

**Görev:** tooltip/bilgi-ikonu planı hazırlığı (ihsan) · **Tarih:** 2026-10-03 · **Revize:** 2026-10-03 (K1-K6 kararları işlendi, SSOT v2.8 ile hizalı)
**Kaynak:** `yedekler/Huginn Data Insights (HUGIns).txt` satır 2440-2987
**Kit:** ADMIN-KİT (D-196) — SSOT: [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] (§0.1 bu belgeyi "Vizyon boşluğu" satırıyla gösterir; §11 KK-12, §12 G8, §8.3 C9 buradan beslenir)
**Hub:** [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] §UX/Tasarim

> **Bu bir KOD görevi değildir.** Çıktı tek markdown belgesidir. Hiçbir sayfa inşa edilmedi; kod işleri aşağıdaki "ayrı görevler" tablosuyla panoya açılır (D-77).

---

## Neden bu belge var

SSOT'un §0'ı "Kaynak PRD = HUGIns.txt §889-1687" diyor. HUGIns.txt'nin
2440-2987 satırları (8 ayrıntılı admin sayfa mockup'ı) bu aralığın **dışında**
kalıyor. SSOT içinde bu 8 sayfanın adları (`OSINT Kontrol Merkezi`,
`Prompt Sandbox`, `Skorlama ve Kalibrasyon`, `Global Kara Liste`,
`İlişki Grafiği Görselleştirici`) için arama yapıldı — **0 sonuç**. Yani bu
vizyon hiçbir yerde takip edilmiyor.

## 8 sayfa — vizyon vs gerçek kod (ölçüldü)

| # | Vizyon sayfası (HUGIns.txt) | Durum | Kanıt (kod) |
|---|---|---|---|
| 1 | CRM / Müşteri Yönetimi | 🟡 Kısmi | `musteri_yonetimi`, `musteriler`, `kullanicilar` sekmeleri var, SSOT §7'de de Kısmi işaretli |
| 2 | OSINT Kontrol Merkezi | 🔴 Yok | En yakını `admin_kpi.py:188 load_source_health()` — scraper/proxy/captcha paneli değil, tek sağlık metriği |
| 3 | AI / Prompt Sandbox | 🔴 Yok | `abrakadabra` sekmesi var ama 9Router AI **sohbet** asistanı; prompt versiyonlama/sandbox yok |
| 4 | Skorlama & Kalibrasyon (ağırlık kaydırıcıları) | 🔴 Yok | Güven Skoru ağırlıkları `src/company_master/sunum.py` içinde kod-sabiti; admin UI'dan değiştirilemiyor |
| 5 | Rapor Arşivi & Analist Onayı | 🟡 Kısmi/yanlış kapsam | `rapor_listesi` var ama MIMIR mimari raporları (iç ajan), müşteri şirket raporu arşivi değil |
| 6 | İlişki Grafiği Görselleştirici (Neo4j/Vis.js) | 🔴 Yok | Bağımsız grafik sayfası hiç yok |
| 7 | Global Kara Liste | 🔴 Yok | Dolandırıcılık/blacklist admin sayfası hiç yok |
| 8 | API Gateway & Audit Log (DevPortal) | 🟡 Kısmi/yanlış kapsam | `api`+`denetim` var ama iç analitik/iç denetim; müşteri API-key/webhook self-servis portalı değil |

**Sayım:** 5 tam yok (2,3,4,6,7) · 3 kısmi/yanlış kapsam (1,5,8) · 0 tam var.

## Karar — KK-12 = A′ (SSOT §11'e işlendi, v2.8 · 2026-10-03)

| Kod | Karar | Tek satır gerekçe |
|---|---|---|
| **K1** | Sayfa 2 (OSINT) → **yeni alt sekme `Metrikler › Veri Kaynakları`** (`anahtar="kaynaklar"`, `ust="veri_kalite"`, `sira=5`, `modul="web_dashboard.tabs.admin_kaynaklar"`) | Kaynak işlemleri tek yerde; 0050 tabloları (`scrape_audit_log`/`scrape_errors`/`scrape_pages`) zaten var, UI yok |
| K1b | `webhook_monitor.py:236-302` crawl bloğu oraya taşınır; Webhook'ta caption + link kalır | Webhook = ingest izleme, crawl = kaynak işi; iki iş bir sayfada karışıyordu |
| K1c | Ana Kontrol "Son kazıma" kartı → `bolum_sec("kaynaklar")` | Admin 1 tıkla kaynağa iner |
| **K2** | Sayfa 3/4/6/7 (Prompt Sandbox, Skorlama, Grafik, Kara Liste) → **bilinçli kapsam dışı (backlog)**, §7'ye satır eklenmez | 4'ü için ne veri ne tüketici var (D-236); K2 ağırlıkları için `Skorlama` kısmen `admin_quality` ile örtüşür, not §9'a düştü |
| K3 | Tooltip = yalnız `TabTanimi.aciklama` metinleri (A1) | Yeni alan yok; gerçek tüketici `app.py:render_topbar` (:616-618, `IPUCU_KEY`) — `_nav_ipucu` None döner, tüketici değil |
| K4 | Rehber = `TabTanimi.rehber: str = ""` + `render_icerik` sonunda tek `st.info` kancası (B2); 6 dosya göç | Tek noktadan açılır/kapanır, sayfa kodu değişmez |
| K5 | Bu belge SSOT §0.1'e bağlandı; FAZ6 belgesinin 3 bölümü (ayrı görevler / ölçüm / nodlar) buraya alındı | D-186 yeni belge = yeni bağlantı |
| K6 | §9 K4 "Kaynak Sağlık Skoru" rozeti yeni sayfanın "Durum Özeti" bölümüne | K4 formülü `kaynak_guvenilirlik.py:161`'de hazır, gösteren yer yoktu |

**Reddedilen alternatif (A):** 5 sayfayı §5'e ekleyip §7'ye 5 "Yok" satırı yazmak — matrisi şişirir, hiçbirinin tüketicisi yok (D-236).

## Bu belgeden çıkan ayrı görevler (hiçbiri bu belgede yapılmadı)

> Panoya `scripts/gorev_at.py` ile açılır (D-77 · D-66 brief zorunlu). `UI-ADMIN-CRAWL-KONTROL-19` ve `API-ADMIN-KAYNAK-SAGLIK-18` **kapalı (done, 2026-09-24)**; yeni işler onları öncül sayar, yeniden açmaz (D-222).

| Görev | Ne yapar | Öncül | Öncelik |
|---|---|---|---|
| `UI-ADMIN-KAYNAKLAR-SAYFA-34` | `admin_kaynaklar.py` sayfası + `SECTIONS` kaydı + K4 rozeti ("Durum Özeti", "Son Çalışmalar", "Hatalar", "Toplanan Sayfalar") | -18 (`kaynak_guvenilirlik.py:161`) | P1 |
| `UI-ADMIN-CRAWL-TASI-35` | `webhook_monitor.py:236-302` tetikle/durdur bloğunu `admin_kaynaklar.py`'ye taşı; Webhook'ta caption+link | -19, -34 | P1 |
| `UI-ADMIN-SON-KAZIMA-KART-36` | Ana Kontrol `GIRIS_KARTLARI` (:78-84) 5. kart `("🕷️","Veri Kaynakları","kaynaklar")` → `/kaynaklar` | -34 | P2 |
| `UI-ADMIN-ACIKLAMA-METIN-37` | `SECTIONS` içindeki `aciklama` metinlerini admin diliyle yeniden yaz (K3) | — | P2 |
| `UI-ADMIN-REHBER-ALAN-38` | `TabTanimi.rehber` alanı + `app.py:693 render_icerik` kancası + 6 dosya göçü (K4) | — | P2 |

Brief'ler: `plans/brief_utku_<TASK-ID>.md` · hub tablosu: [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] "Tur 2026-10-03".

## Ölçüm kaynakları

| Ne | Nereden | Sonuç |
|---|---|---|
| 8 sayfa adı SSOT'ta geçiyor mu | `search_files` SSOT, 5 sayfa adı | 0 sonuç |
| Mevcut sekmeler | `web_dashboard/tabs/__init__.py` `SECTIONS` | `kaynaklar` anahtarı yok; `veri_kalite` altında sira 1-4 dolu |
| Crawl bloğu | `web_dashboard/tabs/webhook_monitor.py:236-302` | tetikle/durdur UI var, Webhook sayfasında |
| 0050 tabloları canlı sayım (D-238) | hub "Kapanan isler" SCRAPE-002 satırı, 2026-10-02 | `scrape_pages=2`, `scrape_audit_log=5`, `scrape_errors=1` |
| -18/-19 durumu | `data/orchestrator/task_board.json:131-170` | ikisi de `done`, sahip yasu |
| K4 formülü | `src/company_master/kaynak_guvenilirlik.py:161` | var, UI'da gösterilmiyor |

## Öz-eleştiri

- İlk raporda -18/-19'u "yeniden kapsamla" dedim; panoyu okumadan karar verdim. Ölçünce ikisi de kapalıydı — D-224 deseni, 7. kez.
- SSOT §0 v2.6 / §14 v2.7 çelişkisini ilk okumada atladım; iki satır üstte duruyordu.
- Daha hızlı yol: bu 8 sayfayı hiç karşılaştırmadan tooltip planına geçmek — ama tooltip metinleri var olmayan sayfaları anlatırdı. Ölçüm 30 dk, yanlış plan riskini sıfırladı.

## İlgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]] — SSOT (ADMIN-KİT); §0.1 geri link, §11 KK-12, §12 G8, §8.3 C9
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — hub; §UX/Tasarim geri link, "Tur 2026-10-03" brief tablosu
- [[Huginn Data Insights/docs/FAZ6_GLOBAL_INTEL_KAPSAM]] — aynı belge kalıbı (ayrı görevler / ölçüm / nodlar)
- [[Huginn Data Insights/AGENTS]] — D-196 kit tablosu (v2.8), D-77, D-222, D-236
- [[src/company_master/etl/scrape_kayit]] — 0050 tek yazıcısı; yeni sayfanın veri kaynağı
