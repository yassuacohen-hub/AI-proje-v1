# Admin Panel (Muninn) — SSOT Hedef Dökümanı

> **AJAN KURALI (zorunlu).** Admin panelle ilgili **her görevin başında** bu dosya okunur; **her görevin sonunda** ilerleme §7 Gereksinim İzlenebilirlik Matrisi ve §14 Revizyon Tablosu'na işlenir. Bu dosya ile başka bir döküman çelişirse **bu dosya geçerlidir** (teknik altyapı çelişkilerinde V9 §16.4 üstündür).

## 0. Statü Bloğu


| Alan        | Değer                                                                      |
| ----------- | -------------------------------------------------------------------------- |
| **Kit adı** | **`ADMIN-KİT`** (SSOT Kiti — AGENTS.md D-196)                              |
| **Statü**   | **SSOT — En Yüksek Otorite (admin panel kapsamı)**                         |
| Versiyon    | v2.1                                                                       |
| Tarih       | 2026-09-22                                                                 |
| Sahip       | Ürün Sahibi (KAHİN)                                                        |
| Kapsam      | Muninn admin paneli: hedef, gereksinim, boşluk, algoritma, yol haritası    |
| Kapsam dışı | Müşteri paneli (Huginn, port 8000) · çekirdek veri modeli (V9)             |
| Üst otorite | V9 §16.4 (panel konumlandırma teknik kararı)                               |
| Kaynak PRD  | `Huginn Data Insights (HUGIns).txt` §889-1687 — SUPER ADMIN PANEL PRD v1.0 |




### 0.1 Bağlantılı dökümanlar


| Döküman      | Yol                                                                                                                                                            | İlişki                                | Geri link var mı |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ---------------- |
| PRD kaynağı  | `[../../../Huginn Data Insights (HUGIns).txt](../../../Huginn%20Data%20Insights%20(HUGIns)`.txt) §889-1687                                                     | Hedef tanımı (değişmez girdi)         | Yok (ham kaynak) |
| V9 bağlam    | `[01_versiyon_9_baglam_dokumani.md](01_versiyon_9_baglam_dokumani.md)` §16.4, §16.5                                                                            | Teknik SSOT; çelişkide V9 üstün       | ✅ eklendi        |
| Mimari karar | `[../../../docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md](../../../docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md)`                                                   | Hibrit admin mimarisi, 4 kural        | ✅ eklendi        |
| Eski analiz  | `[../03_mimari/06_muninn_prd_vs_huginn_analiz.md](../03_mimari/06_muninn_prd_vs_huginn_analiz.md)`                                                             | 2026-09-13; bu dökümanla değiştirildi | ✅ eklendi        |
| CHANGELOG    | `[../../../CHANGELOG.md](../../../CHANGELOG.md)`                                                                                                               | Uygulama geçmişi                      | ✅ eklendi        |
| Görev panosu | `[../../../data/orchestrator/ADMIN_PANEL_PLAN_VE_GOREV_PAKETLERI_2026-09-22.md](../../../data/orchestrator/ADMIN_PANEL_PLAN_VE_GOREV_PAKETLERI_2026-09-22.md)` | Görev yürütme                         | ✅ eklendi        |




### 0.2 Panoya sabitlenecek tek satır

```
[SSOT] Admin panel referansı: AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md — her admin görevi bu dosyayla başlar, ilerleme §7/§12 tablolarına işlenir.
```

---



## 1. Tanım

Muninn admin paneli **CRUD ekranı değil, SaaS operasyon merkezidir.** Varlık sebebi: adminin bir soruyu 3 tıkta cevaplayıp aksiyon alabilmesi.


| #   | Panelin yaptığı iş             |
| --- | ------------------------------ |
| 1   | Müşteri operasyonlarını yönet  |
| 2   | Platform sağlığını izle        |
| 3   | Geliri takip et                |
| 4   | Veri kalitesini yönet          |
| 5   | AI maliyetini izle             |
| 6   | Veri toplama süreçlerini yönet |
| 7   | Güvenlik olaylarını takip et   |
| 8   | Churn riskini tespit et        |
| 9   | Ürün kullanımını analiz et     |


**Marka ayrımı:** Huginn = müşteri yüzü (8000) · **Muninn = admin paneli (8501)** · Odin = çekirdek.

---



## 2. Soru Envanteri (panelin var oluş sebebi)

Panel tasarımı modülden değil **sorudan** başlar. Durumlar §7 matrisindeki kanıtla doğrulanmıştır.


| Kod | Şapka    | Soru                                                 | Cevaplanıyor mu | Sorumlu modül                                       |
| --- | -------- | ---------------------------------------------------- | --------------- | --------------------------------------------------- |
| S1  | CS       | Hangi müşteri churn riski taşıyor (kullanıcı bazlı)? | ❌ Yok           | (yeni) `admin_churn`                                |
| S2  | CFO      | MRR / ARR / ARPA ne?                                 | ✅ Var           | `admin_executive.py:253`                            |
| S3  | CFO      | Abonelik churn oranı (%) ne?                         | ✅ Var           | `admin_executive.py:269`                            |
| S4  | CFO      | Kim ödemedi, hangi ödeme başarısız?                  | ❌ Yok           | (yok — faturalama yok)                              |
| S5  | COO      | AI bugün/bu ay ne yaktı, model kırılımı?             | ✅ Var           | `admin_cost.py:507`                                 |
| S6  | COO      | Token başına maliyet anomalisi var mı?               | 🟡 Kısmi        | `admin_kpi.py:236` (sayaç var, hesap 9router'da)    |
| S7  | Data Ops | Hangi kaynak bozuk/eski?                             | 🟡 Kısmi        | `admin_kpi.py:188` + `kaynak_guvenilirlik.py:161`   |
| S8  | Data Ops | Dün kaç crawl patladı, DLQ'da ne var?                | ✅ Var           | `webhook_monitor.py:135`, `admin_dlq.py:87`         |
| S9  | Data Ops | Veri kaç gün eski (güncellik kovaları)?              | ❌ Yok           | (yeni) K3                                           |
| S10 | Data Ops | Kalite skoru dağılımı, eksik alanlar?                | ✅ Var           | `admin_quality.py:387`                              |
| S11 | SRE      | Sistem ayakta mı, latency/queue?                     | ✅ Var           | `admin_performance.py:107`                          |
| S12 | Security | Kim neyi ne zaman değiştirdi (audit)?                | ✅ Var           | `admin_audit.py:85`                                 |
| S13 | Security | Şüpheli aktivite / MFA / kilitli hesap?              | ❌ Yok           | (yeni) K10                                          |
| S14 | PM       | DAU / MAU / oturum süresi?                           | 🟡 Kısmi        | `admin_kpi.py:70` (yalnız "aktif kullanıcı" sayımı) |
| S15 | PM       | Başarısız aramalar = veri boşluğu?                   | ❌ Yok           | (yeni) K9                                           |
| S16 | PM       | Feature flag kimde açık?                             | ❌ Yok           | (yok)                                               |
| S17 | CS       | Hangi tenant limitini doldurdu (upsell)?             | ❌ Yok           | (yeni) K7                                           |
| S18 | CS       | Onay bekleyen kullanıcı, kim onayladı?               | ✅ Var           | `musteri_yonetimi.py:66`                            |


**Skor:** 8 Var · 4 Kısmi · 6 Yok → soru kapsama ≈ **%56** (önceki tur %30 demişti; hatalıydı, bkz. EK BULGU-2).

| Kapsama ölçütü                                      | Oran      | Ne demek                                                              |
| --------------------------------------------------- | --------- | --------------------------------------------------------------------- |
| **Modül varlığı** — ekran/fonksiyon kodda var mı     | **%56**   | 8 Var · 4 Kısmi · 6 Yok                                               |
| **Veri gerçekliği** — ekran gerçek veri gösteriyor mu | **≈%30** | "Var" sayılanların bir kısmı olmayan tabloya sorgu atıyor, 0/— basıyor |

> ⚠️ **Uyarı:** %56 bir **modül sayımıdır**, yetenek sayımı değildir. Canlı DB doğrulaması (§8.4 · EK BULGU-8/9/10) `api_usage_daily`, `packages`, `company_packages` tablolarının **olmadığını** ve `users` tablosunda `last_login` **bulunmadığını** gösterdi. Gerçekten çalışan kapsama ≈ **%30**.

---



## 3. Yönetim Araçları (soruya cevap yetmez, aksiyon şart)


| Alan       | Araç                                                                             | Durum                                      |
| ---------- | -------------------------------------------------------------------------------- | ------------------------------------------ |
| Tenant     | Aktifleştir / Pasifleştir / Askıya Al / Plan Yükselt-Düşür / Kredi Tanımla / Sil | ❌ (single-tenant)                          |
| Kullanıcı  | Pasifleştir / Şifre Sıfırla / Force Logout / Rol Değiştir / Onayla               | 🟡 Onayla ✅, gerisi ❌                      |
| Abonelik   | Plan Oluştur / Güncelle / Kopyala / Kapat                                        | 🟡 `paketler.py:443` okuma var, CRUD kısmi |
| Faturalama | Fatura Görüntüle / İade / Ödemeyi Yeniden Dene                                   | ❌                                          |
| Kredi      | Ekle / Düş / Sıfırla / Aylık Yenile                                              | ✅ `musteri_yonetimi.py:145`                |
| Veri Ops   | Crawl Tetikle / Durdur / DLQ Yeniden Dene / Kaynak Devre Dışı                    | 🟡 DLQ ✅, crawl kontrolü ❌                 |
| AI Ops     | Model Değiştir / Token Limiti / Rate Limit                                       | ❌                                          |
| Güvenlik   | MFA Zorunlu / Hesap Kilidi Aç / Rol Ata                                          | ❌                                          |
| Destek     | Ticket Ata / Kapat / Eskale                                                      | 🟡 `admin_destek.py:50`                    |
| Feature    | Tenant bazlı flag aç/kapa                                                        | ❌                                          |


**Demir kural:** Her aksiyon audit log'a düşer (Kullanıcı, Tenant, İşlem, Eski Veri, Yeni Veri, Tarih, IP).

---



## 4. Teknoloji Standardı


| Katman   | Zorunlu                             | Huginn durumu                                                                |
| -------- | ----------------------------------- | ---------------------------------------------------------------------------- |
| Frontend | Streamlit Multipage                 | ✅                                                                            |
| Grafik   | **Plotly** (UI-CHART-01 tek onaylı) | ✅                                                                            |
| Tablo    | AgGrid (PRD)                        | ⛔ **Reddedildi** — yeni bağımlılık, `st.dataframe` yeterli (bkz. EK BULGU-5) |
| Backend  | FastAPI + PostgreSQL + Redis        | ✅ / ✅ / 🟡                                                                   |
| Arkaplan | Celery + Redis Queue                | ❌ (Apify webhook event-driven)                                               |
| İzleme   | Prometheus + Grafana                | 🟡 Prometheus ✅, Grafana ❌                                                   |
| Log      | Loguru + PG Audit                   | 🟡 dosya log + Telegram                                                      |


**Streamlit kuralları:** `st.cache_data`, `st.cache_resource`, lazy loading, server-side pagination.
**Yasak:** büyük dataframe direkt yükleme · senkron crawl · uzun AI işi Streamlit içinde.
**Navigasyon:** en fazla 3 seviye, 6 üst sayfa.

### 4.1 Mimari demir kurallar (V9 §16.4 + ADR)


| #   | Kural                                                          | Uyum                                               |
| --- | -------------------------------------------------------------- | -------------------------------------------------- |
| 1   | `/api/admin/*` yalnız `require_admin`; müşteri paneli çağırmaz | ✅                                                  |
| 2   | Müşteri panelinde admin UI render edilmez                      | ✅                                                  |
| 3   | Performans metriği tek kaynak `/api/performance`               | ✅ `admin_performance.py:38`                        |
| 4   | SSE yalnız müşteri panelinde; admin polling                    | ✅ **UYUMLU** — `admin_realtime.py:239` `render_auto_refresh()` (UI-ADMIN-SSE-IHLAL-03) |


---



## 5. Hedef Modül Mimarisi (PRD §3)

```text
📊 Dashboard
🏢 Müşteri Yönetimi   — Tenantlar / Kullanıcılar / Roller
💳 Abonelik Yönetimi  — Paketler / Faturalar / Ödemeler
📈 Kullanım Analitiği — Aramalar / AI / API / Exportlar
🔍 Veri Operasyonları — Kaynaklar / Kalite / Crawl / Güncellik
🤖 AI Operasyonları   — Prompt / Token / Maliyet / Model
🚨 Sistem İzleme      — Hata / Queue / Performans
🛡 Güvenlik           — Audit / Yetki / MFA
⚙ Ayarlar
```

---



## 6. Öncelik Merdiveni (PRD)


| Seviye | Modüller                                             |
| ------ | ---------------------------------------------------- |
| **P0** | Dashboard · Tenant · Kullanıcı · Kullanım Analitiği  |
| **P1** | AI Ops · Veri Ops · Güvenlik · Audit Log             |
| **P2** | Faturalama · API Yönetimi · Destek · Feature Flags   |
| **P3** | Tahminleme · Gelişmiş Analitik · Executive Dashboard |


> ⚠️ Huginn'de P3 (Executive) zaten yapılmış, P0 (churn) yapılmamış. Merdiven **tersine uygulanmış** (EK BULGU-2).

---



## 7. Gereksinim İzlenebilirlik Matrisi

> Her görev sonunda bu tablo güncellenir. Durum: Var / Kısmi / Yok / Çelişkili.


| PRD § | Gereksinim                                                            | Modül                                    | Durum         | Kanıt (dosya:satır)                                                   |
| ----- | --------------------------------------------------------------------- | ---------------------------------------- | ------------- | --------------------------------------------------------------------- |
| §4    | Dashboard KPI (tenant, kullanıcı, DAU, MAU, arama, AI, API, MRR, ARR) | `admin_kpi.py`                           | Kısmi         | `admin_kpi.py:41` — firma/MAU/API/sinyal var; DAU yok, MAU `last_login` üzerinden `:65` |
| §4    | Canlı veri akışı (KPI + 24s trend)                                    | `admin_realtime.py`                      | **Var**       | `admin_realtime.py:118` `_db_kpi_oku()` · `:239` `render_auto_refresh()` — polling |
| §4    | Ana kontrol / genel bakış                                             | `ana_kontrol.py`                         | Var           | `ana_kontrol.py:209`                                                  |
| §5    | Tenant listesi + filtre + detay                                       | `tenant_health_dashboard.py`             | Kısmi         | `tenant/model.py:22` `VARSAYILAN_TENANT` — tek tenant sabit           |
| §6    | Kullanıcı listesi + detay + oturum geçmişi                            | `musteri_yonetimi.py`                    | Kısmi         | `musteri_yonetimi.py:216` `_giris_aktinligi()` + `:272` churn risk kolonu |
| §6    | Kullanıcı onay akışı                                                  | `musteri_yonetimi.py`                    | Var           | `musteri_yonetimi.py:66`                                              |
| §6    | Kullanıcı yönetimi (2. kopya)                                         | `admin_extras.py`                        | **Çelişkili** | `admin_extras.py:43` + `admin_musteriler.py:85` → 3 paralel uygulama  |
| §7    | Paket / plan tanımı                                                   | `paketler.py`                            | Kısmi         | `paketler.py:443`; fiyat SSOT `company_master.paketler`               |
| §8    | MRR / ARR / ARPA                                                      | `admin_executive.py`                     | **Var**       | `executive_ozet.py:246` `mrr_arr()`                                   |
| §8    | Churn oranı (%)                                                       | `admin_executive.py`                     | **Var**       | `executive_ozet.py:306` `churn_orani()`; UI `admin_executive.py:302`  |
| §8    | MRR trend (6 ay)                                                      | `admin_executive.py`                     | Var           | `executive_ozet.py:423` `mrr_trend()`                                 |
| §8    | LTV / CAC                                                             | —                                        | Yok           | —                                                                     |
| §8    | Fatura / ödeme listesi                                                | —                                        | Yok           | —                                                                     |
| §9    | Kredi (Search/AI/Export/API)                                          | `musteri_yonetimi.py`                    | Kısmi         | `musteri_yonetimi.py:145` `_paket_kredi()` — tek kredi türü           |
| §10   | Arama analitiği                                                       | `musteri_yonetimi.py`, `admin_search.py` | Kısmi         | `musteri_yonetimi.py:252` `_aramalar()`, `admin_search.py:236`        |
| §10   | **Churn kuralı (14 gün × 3 sinyal)**                                  | —                                        | **Yok**       | Kullanıcı bazlı risk etiketi hiçbir yerde yok                         |
| §10   | DAU / MAU / oturum süresi                                             | `admin_kpi.py`                           | Kısmi         | `admin_kpi.py:65` yalnız `status IN ('onayli','aktif')` sayımı        |
| §11   | AI model/maliyet/token                                                | `admin_cost.py`                          | Var           | `admin_cost.py:507`                                                   |
| §11   | AI maliyet anomali                                                    | `admin_kpi.py`                           | Kısmi         | `admin_kpi.py:236` `anomaliler` sayacı okunur, hesap dışarıda         |
| §12   | Kaynak sağlığı                                                        | `admin_kpi.py`                           | Kısmi         | `admin_kpi.py:188` `load_source_health()`                             |
| §12   | Crawl yönetimi (tetikle/durdur)                                       | —                                        | Yok           | —                                                                     |
| §12   | Webhook / ingest izleme                                               | `webhook_monitor.py`                     | Var           | `webhook_monitor.py:135`                                              |
| §12   | DLQ                                                                   | `admin_dlq.py`                           | Var           | `admin_dlq.py:87`                                                     |
| §12   | Veri güncelliği (1/7/30/90g kova)                                     | —                                        | Yok           | —                                                                     |
| §13   | Kalite skoru 0-100 + dağılım                                          | `admin_quality.py`                       | **Var**       | `admin_quality.py:74` `load_quality_overview()`                       |
| §13   | Eksik alan kırılımı                                                   | `admin_kpi.py`, `admin_quality.py`       | Var           | `admin_kpi.py:140` `load_field_quality_breakdown()`                   |
| §13   | Kalite riski listesi (QS<30)                                          | `admin_quality.py`                       | Var           | `admin_quality.py:184` `load_risky_companies()`                       |
| §14   | API key yönetimi                                                      | `admin_extras.py`                        | Kısmi         | `admin_extras.py:17`                                                  |
| §14   | API analitiği (istek/hata/latency)                                    | `admin_api_analytics.py`                 | Var           | `admin_api_analytics.py:91`                                           |
| §15   | Destek ticket                                                         | `admin_destek.py`                        | Kısmi         | `admin_destek.py:50`                                                  |
| §16   | Giriş / kimlik                                                        | `admin_auth.py`                          | Var           | `admin_auth.py:65`                                                    |
| §16   | **Giriş anında `users.last_login` yaz** (API-ADMIN-LASTLOGIN-YAZ-05)    | `web_app.py:2232` + fallback `:2246`     | **Var**       | `web_app.py:2232` `UPDATE users SET last_login=NOW()` + `:2246` fallback |
| §16   | Şüpheli aktivite / kilitli hesap / MFA                                | —                                        | Yok           | —                                                                     |
| §16   | 6 rol (Super/Ops/Billing/Security/Support/Readonly)                   | `tabs/__init__.py`                       | **Çelişkili** | `tabs/__init__.py:86` `ROL_SEVIYE` — 4 seviye (admin/analyst/anon/…)  |
| §17   | Audit log                                                             | `admin_audit.py`                         | Var           | `admin_audit.py:85` (DASH-08)                                         |
| §17   | Karar defteri (Huginn'e özel)                                         | `admin_panel.py`                         | Var           | `admin_panel.py:66`                                                   |
| §18   | Sistem performansı (CPU/RAM/latency/queue)                            | `admin_performance.py`                   | Var           | `admin_performance.py:107`                                            |
| §18   | Hata izleme                                                           | `admin_errors.py`                        | Var           | `admin_errors.py:60`                                                  |
| §19   | Feature flags                                                         | —                                        | Yok           | —                                                                     |
| §20   | Ayarlar                                                               | `admin_panel.py`                         | Var           | `admin_panel.py:246` (P7-46)                                          |


---



## 8. Fark Listeleri



### 8.1 PRD'de var, kodda yok


| #   | Gereksinim                                          | PRD §  | Not                      |
| --- | --------------------------------------------------- | ------ | ------------------------ |
| A1  | Churn risk kuralı (14g × 3 sinyal, kullanıcı bazlı) | §10    | P0 · en yüksek etki/efor |
| A2  | Veri güncellik kovaları (1/7/30/90g)                | §12    | P1                       |
| A3  | Multi-tenant yapı                                   | §5     | Yapısal delta            |
| A4  | Faturalama / ödeme / LTV / CAC                      | §8     | Stripe gerekir           |
| A5  | Feature flags                                       | §19    | P2                       |
| A6  | MFA / hesap kilidi / şüpheli aktivite               | §16    | P2                       |
| A7  | 6 rol modeli                                        | §16    | Kod 4 seviye             |
| A8  | Crawl tetikle/durdur kontrolü                       | §12    | P1                       |
| A9  | DAU/MAU + oturum süresi                             | §4/§10 | P1                       |
| A10 | Başarısız arama analizi                             | §10    | P2                       |




### 8.2 Kodda var, PRD'de yok — **EK BULGU-1**


| #   | Modül                                                                      | Kanıt  | Değerlendirme                                                                                    |
| --- | -------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------ |
| B1  | `admin_loading.py`                                                         | `:23`  | UI yardımcısı — PRD kapsamı dışı, zararsız                                                       |
| B2  | `admin_export.py`                                                          | `:145` | Dışa aktarma — PRD'de kredi türü olarak geçer, ekran olarak yok                                  |
| B3  | `admin_errors.py`                                                          | `:60`  | §18'e mantıken ait, PRD ayrı modül saymamış                                                      |
| B4  | `admin_auto_refresh.py`                                                    | `:76`  | Polling yardımcısı — kural 4'ün doğru uygulaması                                                 |
| B5  | `abrakadabra.py` (MIMIR sohbet)                                            | `:222` | Huginn'e özel, PRD dışı                                                                          |
| B6  | `pazarlama.py`                                                             | `:613` | PRD dışı                                                                                         |
| B7  | `proje_yonetimi.py`                                                        | `:35`  | PRD dışı (iç görev yönetimi)                                                                     |
| B8  | `teknik_altyapi.py`                                                        | `:48`  | PRD dışı                                                                                         |
| B9  | `admin_panel.py` Karar Defteri                                             | `:66`  | Huginn'e özel, **korunmalı**                                                                     |
| B10 | Toplayıcı sarmalayıcı deseni (`admin_sistem.py:66`, `admin_yonetim.py:61`) | —      | PRD düz modül mimarisi tanımlar; 3 seviye kısıtı yüzünden doğmuş — meşru sapma, dökümante edildi |




### 8.3 Çelişkiler


| #   | Çelişki                                                             | A tarafı                                                                                                          | B tarafı                                                                                                                                            | Karar                                                                       |
| --- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| C1  | **SSE kullanımı** — **EK BULGU-3**                                  | ADR + V9 §16.4 kural 4: "SSE yalnız müşteri panelinde, admin polling"                                             | `admin_realtime.py:143` `_sse_oku(SSE_URL)` admin panelde SSE okur                                                                                  | ✅ **Kapandı** — polling (KK-1, 2026-09-24) → UI-ADMIN-SSE-IHLAL-03          |
| C2  | Kullanıcı yönetimi 3 kopya                                          | `musteri_yonetimi.py:66`                                                                                          | `admin_extras.py:43` + `admin_musteriler.py:85`                                                                                                     | NAV-PLAN-01 §2.1 birleştirme kararı uygulanmamış                            |
| C3  | Rol modeli                                                          | PRD §16: 6 rol                                                                                                    | `tabs/__init__.py:86`: 4 seviye                                                                                                                     | PRD tenant-SaaS varsayar; Huginn 4 seviye yeterli → **PRD'den sapma kabul** |
| C4  | **V9 §16.5 durumu** — **EK BULGU-4**                                | `06_muninn_prd_vs_huginn_analiz.md:123` "§16.5'i V9'a ekle" (açık görev)                                          | V9 `:827`'de §16.5 **zaten var**                                                                                                                    | Eski analiz **bayat** → §11 KK-4                                            |
| C5  | Executive Dashboard önceliği — **EK BULGU-2**                       | PRD: Executive = P3                                                                                               | Kodda yapılmış (`admin_executive.py`), P0 churn yapılmamış                                                                                          | Merdiven tersine işlemiş; düzeltme §10                                      |
| C6  | AgGrid — **EK BULGU-5**                                             | PRD §2: AgGrid zorunlu                                                                                            | UI-CHART-01: tek onaylı kütüphane Plotly; AgGrid onaysız                                                                                            | **AgGrid reddedildi**, `st.dataframe` kullanılır                            |
| C7  | V9 §16.5 MVP listesi bayat — **EK BULGU-6**                         | V9 `:833-838`: Dashboard KPI, Webhook Monitor, AI Cost, Kalite Özeti, API Analytics, Perf → hepsi `[ ]` işaretsiz | Kodda **6'sı da var** (`admin_kpi.py`, `webhook_monitor.py`, `admin_cost.py`, `admin_quality.py`, `admin_api_analytics.py`, `admin_performance.py`) | V9 §16.5 kutucukları güncellenmeli → §11 KK-5                               |
| C8  | `06_muninn_prd_vs_huginn_analiz.md:854` dosya yolu — **EK BULGU-7** | V9 `:854` "İlgili Dosya: `plans/muninn_prn_vs_huginn_analiz.md`"                                                  | Gerçek yol `AI proje v1/V10/03_mimari/06_muninn_prd_vs_huginn_analiz.md`, ayrıca isim yazım hatası (`prn`)                                          | Kırık link — ✅ 2026-09-22 düzeltildi                                       |

### 8.4 ⛔ Şema doğrulaması — **EK BULGU-8/9/10** (DB'den canlı doğrulandı, 2026-09-22)

> Doğrulama komutu (tekrar üretilebilir, `Huginn Data Insights/` içinden):
> ```
> set PYTHONPATH=src&& python -c "from sqlalchemy import inspect; from company_master.db.connection import get_engine; i=inspect(get_engine()); print(sorted(i.get_table_names())); print([c['name'] for c in i.get_columns('users')])"
> ```
> **Sonuç: 30 tablo.** `commercial_signals, companies, company_aliases, company_capabilities, company_contacts, company_events, company_identifiers, company_industries, company_intelligence_scores, company_locations, company_names, company_products, company_signals, company_state, company_tech_profile, credit_ledger, entity_resolution, evidence, job_postings, kvkk_bireysel_email_yedek, momentum_snapshot, nace_codes, osbs, product_categories, products, quarantine_firms, schema_migrations, source_records, sources, users`

| #                | Bulgu                                                                                    | Kanıt                                                                                    | Sonuç                                                                                                                                              | Öncelik |
| ---------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| **EK BULGU-8**   | **Kullanıcı davranış logu hiç yok.** Giriş/arama/AI kullanım tablosu sıfır; `users` 28 kolonda `last_login` yok (yalnız `created_at`, `updated_at`). | DB inspect çıktısı                                                                        | **K1 Churn girdisi mevcut değil.** G2 "S efor" değil; önce log altyapısı gerekir. Mevcut `musteri_yonetimi.py:216` `_giris_aktinligi()` neyi okuyorsa ya boş ya proxy. | **P0**  |
| **EK BULGU-9**   | **`api_usage_daily` tablosu DB'de yok.**                                                 | `admin_kpi.py:105` `SELECT COALESCE(SUM(request_count),0) FROM api_usage_daily`           | KPI kartı ya `try/except` ile sessizce **0** gösteriyor ya hata yutuyor → **panelde sahte/boş metrik**. API Analytics sekmesi de aynı riskte.        | **P0**  |
| **EK BULGU-10**  | **`packages` ve `company_packages` tabloları DB'de yok.**                                | `admin_executive.py:74` `FROM company_packages cp JOIN packages p …`                      | **MRR/ARR/ARPA/churn/paket dağılımının tamamı veri kaynaksız.** §2'deki "Var" işaretleri *kod var* demek, *veri var* demek değil.                   | **P0**  |

> **Kapsama oranı düzeltmesi:** §2'deki **%56** rakamı *modül varlığına* göredir.
> **Veri kaynağı gerçekliğine göre fiili kapsama ≈ %30'dur** — çünkü MRR/ARR/churn/API KPI'sı
> besleyen tablolar yok. Panelin en büyük riski eksik modül değil, **boş modülün dolu görünmesi**dir.


---



## 9. Algoritma Tablosu


| Kod     | Algoritma                    | Girdi alanları                                           | Formül                                                                                       | Çıktı                         | Veri kaynağı                                   | Hazır mı                                                                 |
| ------- | ---------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------ |
| **K1**  | Churn Risk Skoru (P0)        | `son_giris`, `son_arama`, `son_ai_kullanim`              | `sinyal = Σ(1 for g in (g_giris,g_arama,g_ai) if g>=14)` → `{0:Yok,1:Düşük,2:Orta,3:Yüksek}` | Kullanıcı/tenant risk etiketi | ⛔ 3 girdinin 2'si YOK: `users.last_login` eklendi (v0016), arama logu yok, AI log yok (EK BULGU-8) | 🟡 **kısmi** — tek sinyal (`last_login`) ile `src/company_master/churn.py:27` `risk_etiketi()` mevcut, doctest 7/7 geçti; arama/AI log atlandı (G2) |
| **K2**  | Veri Kalite Skoru (P1)       | vergi_no, website, email, telefon, nace, adres, linkedin | `100*Σ(w_i*dolu_i)/Σw_i`; w: 3,3,2,2,2,1,1; `veri_yasi>90g → -15`                            | 0-100 skor                    | `companies.data_quality_score`                 | ✅ **mevcut** (`admin_quality.py:74`) — ağırlık şeması doğrulanmalı       |
| **K3**  | Veri Güncellik Kovaları (P1) | `son_guncelleme`                                         | `≤1g Taze · ≤7g İyi · ≤30g Kabul · ≤90g Eski · >90g Bayat`                                   | Kaynak × kova dağılımı        | `companies.updated_at`                         | ❌ yok                                                                    |
| **K4**  | Kaynak Sağlık Skoru (P1)     | `basarili_crawl`, `toplam_crawl`, DLQ adedi              | `oran=başarılı/toplam`; 🟢≥0.95 · 🟠≥0.70 · 🔴<0.70; +DLQ birikme hızı                       | Kaynak sağlık rozeti          | `source_records`, `kaynak_guvenilirlik.py:161` | 🟡 kısmi                                                                 |
| **K5**  | AI Maliyet Anomali (P1)      | 30 günlük maliyet serisi                                 | `z=0.6745*(bugün-medyan)/MAD`; alarm `                                                       | z                             | >3.5`                                          | Anomali listesi                                                          |
| **K6**  | Tenant Sağlık Skoru (P2)     | kullanım, churn, ödeme, destek, feature                  | `0.35*kullanım + 0.25*(1-churn) + 0.20*ödeme + 0.10*destek⁻¹ + 0.10*feature`                 | 0-100 + bant                  | `tenant/health.py:157`                         | ✅ **mevcut** (`hesapla()`), tek tenant                                   |
| **K7**  | Upsell Adayı (P2)            | kullanım/limit oranları, churn, 30g büyüme               | `doygunluk=max(...)≥0.85 ∧ churn∈{Yok,Düşük} ∧ büyüme>0`                                     | Aday listesi                  | kredi tabloları                                | ❌ yok                                                                    |
| **K8**  | Gelir Metrikleri (P2)        | abonelik tutar/durum/tarih                               | `MRR=Σaktif`; `ARR=MRR*12`; `ARPA=MRR/adet`; `Churn%=kayıp/dönem_başı`; `LTV=ARPU/Churn%`    | KPI kartları                  | `company_packages ⋈ packages`                  | ✅ **MRR/ARR/ARPA/Churn mevcut** (`executive_ozet.py:246,306`); LTV/CAC ❌ |
| **K9**  | Arama Boşluğu (P2)           | başarısız arama terimleri                                | normalize → frekans → eşik üstü                                                              | Veri toplama görev adayı      | arama logu ❓                                   | ❌ yok                                                                    |
| **K10** | Şüpheli Aktivite (P2)        | giriş logu, IP, export olayı                             | 5dk'da >5 başarısız · >2 ülke IP · gece toplu export                                         | Güvenlik alarmı               | `admin_audit` verisi                           | ❌ yok                                                                    |


**İlke:** Her algoritma önce kural tabanlı çalışır, ölçülür, gerekirse ML'e yükselir. ML ile başlamak = ölçülemeyen kara kutu.
**Faz 2 (ML):** Churn Prediction (gradient boosting) · Revenue Forecasting · Cohort Analysis · Davranış Kümeleme · AI Cost Optimizer.

---



## 10. Boşluk & Risk Tablosu (etki/efor sıralı)


| Sıra | Bulgu                                      | Etki   | Efor | Etki/Efor      | Öncelik |
| ---- | ------------------------------------------ | ------ | ---- | -------------- | ------- |
| 1    | **EK BULGU-9/10** sahte metrik — `api_usage_daily`, `packages`, `company_packages` tabloları YOK | Kritik | S    | **En yüksek**  | P0      |
| 2    | ✅ C1 SSE mimari ihlali — **KAPANDI** (UI-ADMIN-SSE-IHLAL-03)                                                   | Yüksek | S    | **Çok yüksek** | P0      |
| 3    | **EK BULGU-8** sıfır aktivite verisi — giriş/arama/AI log tablosu YOK                            | Yüksek | M    | Yüksek         | P0      |
| 4    | C4/C6/C7 bayat döküman + kırık link — **✅ kapandı (G3)**                                        | Orta   | S    | Yüksek         | ✅ bitti |
| 5    | A1 Churn risk kuralı yok (PRD P0) — **girdisiz**, önce G2(a) migration                           | Yüksek | M    | Orta-Yüksek    | P1      |
| 6    | A9 DAU/MAU yok — **bloklu**, aktivite tablosu şart                                               | Yüksek | L    | Orta           | P1      |
| 7    | C2 kullanıcı yönetimi 3 kopya                                                                    | Orta   | M    | Orta-Yüksek    | P1      |
| 8    | A2 veri güncellik kovaları                                                                       | Orta   | S    | Yüksek         | P1      |
| 9    | K5 AI maliyet anomali panelde yok                                                                | Orta   | M    | Orta           | P1      |
| 10   | A8 crawl tetikle/durdur                                                                          | Orta   | M    | Orta           | P1      |
| 11   | A6 MFA / şüpheli aktivite                                                                        | Orta   | L    | Düşük          | P2      |
| 12   | A10/K9 arama boşluğu                                                                             | Orta   | M    | Orta           | P2      |
| 13   | A5 feature flags                                                                                 | Düşük  | M    | Düşük          | P2      |
| 14   | A3 multi-tenant                                                                                  | Yüksek | L    | Düşük          | P3      |
| 15   | A4 faturalama + LTV/CAC                                                                          | Yüksek | L    | Düşük          | P3      |


---



## 11. Karar Kaydı Tablosu (açık sorular)


| Kod  | Açık soru                                                           | Kime/neye sorulacak               | En hızlı doğrulama yolu                                                                                                                                                                                                        | Bloklanan iş                    | Durum                          |
| ---- | ------------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------- | ------------------------------ |
| KK-1 | `admin_realtime.py` SSE kalacak mı, polling'e mi dönecek?           | Ürün sahibi (mimari kural sahibi) | Kullanıcı onayı — kod zaten okundu, ihlal kesin                                                                                                                                                                                | Kural 4 uyumu, ADR güncellemesi | ✅ **KAPALI — Polling seçildi (KK-1 kararı, 2026-09-24)**    |
| KK-2 | Kullanıcı giriş/arama/AI logları sorgulanabilir tablo mu, JSONL mi? | Kod + DB                          | `set PYTHONPATH=src&& python -c "from sqlalchemy import inspect; from company_master.db.connection import get_engine; print(sorted(inspect(get_engine()).get_table_names()))"` | **K1 Churn**                    | ✅ **DOĞRULANDI 2026-09-22 — CEVAP: HİÇBİRİ YOK.** 30 tabloda `login/search/usage/session/ai_*` log tablosu sıfır. Tek yakın: `company_events` (firma olayı, kullanıcı değil). → EK BULGU-8 |
| KK-3 | `users` tablosunda `last_login` var mı?                             | DB şeması                         | `set PYTHONPATH=src&& python -c "from sqlalchemy import inspect; from company_master.db.connection import get_engine; print([c['name'] for c in inspect(get_engine()).get_columns('users')])"` | **K1 Churn**                    | ✅ **DOĞRULANDI — CEVAP: EKLENDİ (2026-09-24, v0016 migration).** 28 kolon var, `last_login` `TIMESTAMPTZ NULL` eklendi, `idx_users_last_login` indeksi oluştu. → K1 Churn girdisi açıldı. |
| KK-4 | Eski analiz (`06_muninn_prd_vs_huginn_analiz.md`) arşivlensin mi?   | Ürün sahibi                       | Karar — bayatlığı §8.3 C4'te kanıtlandı                                                                                                                                                                                        | Döküman hijyeni                 | 🔴 Onay bekliyor               |
| KK-5 | V9 §16.5 kutucukları güncellensin mi (6 madde tamam)?               | Ürün sahibi                       | Kanıt §8.3 C7'de                                                                                                                                                                                                               | V9 doğruluğu                    | 🔴 Onay bekliyor               |
| KK-6 | AgGrid reddi onaylanıyor mu?                                        | Ürün sahibi                       | UI-CHART-01 zaten Plotly'yi tek onaylı ilan etmiş                                                                                                                                                                              | PRD §2 uyumu                    | 🟡 Varsayılan: reddedildi      |
| KK-7 | Huginn multi-tenant'a geçecek mi, geçecekse ne zaman?               | Ürün sahibi (ürün kararı)         | Karar                                                                                                                                                                                                                          | PRD §5/§7/§8/§9/§19'un tamamı   | 🔴 Açık (P3)                   |
| KK-8 | `api_usage_daily` tablosu dolu mu (API KPI gerçek mi)?              | DB                                | Yukarıdaki tablo listesi komutu                                                                                                                                                                                                 | §14 doğruluğu                   | ✅ **DOĞRULANDI — CEVAP: TABLO HİÇ YOK.** `api_usage_daily` DB'de mevcut değil. → EK BULGU-9 |
| KK-9 | Executive Dashboard'un okuduğu `packages` / `company_packages` tabloları var mı? | DB | Yukarıdaki tablo listesi komutu | MRR/ARR/churn/ARPA'nın tamamı | ✅ **DOĞRULANDI — CEVAP: İKİSİ DE YOK.** Executive sekmesi kalıcı boş/hata. → EK BULGU-10 |


---



## 12. Yol Haritası — "Nereden başlanırsa en büyük etki"


> ⚠️ **2026-09-22 şema doğrulaması sonrası yeniden sıralandı (§8.4).** Eski G1/G2 sırası
> geçersiz: churn'ün girdisi DB'de yok. Yeni 1. iş **G0 — sahte metrik avı**.

| #      | İş                             | Etki   | Efor | Etki/Efor   | İlk somut adım                                                                                                                                                                                                                                                                         |
| ------ | ------------------------------ | ------ | ---- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **G0** | **Sahte/boş metrik avı** — EK BULGU-9/10 | **Kritik** | **S** | **En yüksek** | **Dosya:** `web_dashboard/tabs/admin_kpi.py` · **Fonksiyon:** `load_admin_kpi_summary()` **satır 41**, sorgu **satır 105** (`api_usage_daily`). Ve `web_dashboard/tabs/admin_executive.py` · `load_executive_ozet()` **satır 74** (`company_packages`/`packages`). **Yapılacak:** eksik tabloda `try/except` içinde `0` dönmek yerine kartı `"veri kaynağı yok"` rozetiyle çiz. Sıfır yeni tablo, sıfır yeni bağımlılık. |
| **G1** | SSE ihlalini kapat             | Yüksek | S    | Çok yüksek  | **Dosya:** `web_dashboard/tabs/admin_realtime.py` · **Fonksiyon:** `_sse_oku()` **satır 143** · Ya `_db_kpi_oku()` (`:154`) + `admin_auto_refresh.render_auto_refresh()` (`:76`) ile polling'e çevir, ya ADR kural 4'e istisna maddesi yaz. Karar KK-1.                                |
| **G2** | K1 Churn risk skoru            | Yüksek | ~~S~~ → **M** | Yüksek | ⚠️ **Efor yükseldi (EK BULGU-8).** Girdi yok: log tablosu ve `users.last_login` mevcut değil. **Sıra:** (a) `users` tablosuna `last_login TIMESTAMP` kolonu (tek migration, `schema_migrations` zaten var) → (b) giriş anında `UPDATE users SET last_login=NOW()` → (c) yeni `src/company_master/churn.py` · `risk_etiketi(son_giris, bugun) -> str` saf fonksiyon + doctest → (d) `musteri_yonetimi.py` `_giris_aktinligi()` **satır 216** SQL'ine risk kolonu. Ayrı arama/AI log tablosu **şimdilik atlanır**, tek sinyal (`last_login`) ile başla. |
| **G3** | Döküman hijyeni                | Orta   | S    | Yüksek      | ✅ **2026-09-22 tamamlandı.** `01_versiyon_9_baglam_dokumani.md` §16.5 durum tablosuna çevrildi (kanıtlı), satır 854 kırık yol düzeltildi, geri linkler eklendi. |
| G4     | DAU/MAU                        | Yüksek | L    | Düşük-Orta  | ⚠️ **Bloklu (EK BULGU-8):** oturum/aktivite tablosu yok. `admin_kpi.py:65` yalnız `status IN ('onayli','aktif')` sayar — bu **kayıtlı kullanıcı**, DAU değil. Önce G2(a)(b) tamamlanmalı; sonra `last_login` üzerinden MAU tek sorguyla çıkar, gerçek DAU için ayrı olay tablosu gerekir. |
| G5     | Kullanıcı yönetimi birleştirme | Orta   | M    | Orta-Yüksek | NAV-PLAN-01 §2.1 uyarınca `admin_extras.render_user_management` tek uygulama; `admin_musteriler.py:85` ve `musteri_yonetimi.py:66` yönlendirilir.                                                                                                                                      |
| G6     | K3 veri güncellik              | Orta   | S    | Yüksek      | `admin_quality.py`'ye kova dağılımı sorgusu ekle (`updated_at` yaşı).                                                                                                                                                                                                                  |
| G7     | K5 AI anomali paneli           | Orta   | M    | Orta        | `admin_cost.py:507` içine robust z-skor bloğu.                                                                                                                                                                                                                                         |
| G8     | Crawl kontrolü                 | Orta   | M    | Orta        | `webhook_monitor.py` üzerine tetikle/durdur aksiyonu.                                                                                                                                                                                                                                  |
| G9     | K10 güvenlik kuralları         | Orta   | L    | Düşük       | `admin_audit.py` verisi üzerine eşik kuralları.                                                                                                                                                                                                                                        |


---



## 13. Huginn'e Uyarlama Kaydı


| Konu          | Karar                                                                      |
| ------------- | -------------------------------------------------------------------------- |
| Multi-tenant  | Ertelendi (P3) — `VARSAYILAN_TENANT` (`tenant/model.py:22`) ile tek tenant |
| Faturalama    | Ertelendi (P3) — Stripe yok; MRR/ARR abonelik tablosundan hesaplanıyor     |
| 6 rol         | Sapma kabul — 4 seviyeli `ROL_SEVIYE` yeterli                              |
| AgGrid        | Reddedildi — Plotly + `st.dataframe`                                       |
| SSE           | **Polling seçildi (KK-1, 2026-09-24)**                                                  |
| Karar Defteri | PRD dışı, Huginn'e özel, korunur                                           |
| Desen         | Eksiklerin ortak deseni: **backend veri var, admin UI yok**                |


---



## 14. Revizyon Tablosu


| Ver.     | Tarih          | Değişen / eklenen                                                                  | Gerekçe                                                      |
| -------- | -------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| v1.0     | 2026-09-22     | İlk sürüm: §0 tanım, §1 sorular, §2 araçlar, §3 teknoloji, §4 modüller, §5 öncelik | PRD §889-1687 sentezi                                        |
| v1.1     | 2026-09-22     | §5.5 Algoritmalar K1-K10                                                           | Ürün sahibi talebi                                           |
| **v2.0** | **2026-09-22** | **SSOT statü bloğu + ajan kuralı + §0.1 bağlantı tablosu + §0.2 pano satırı**      | SSOT yükseltmesi                                             |
| v2.0     | 2026-09-22     | §7 Gereksinim İzlenebilirlik Matrisi (38 satır, dosya:satır kanıtlı)               | Kanıtsız durum beyanı yasak                                  |
| v2.0     | 2026-09-22     | §8 Fark listeleri + **EK BULGU-1…7**                                               | Kod-PRD-döküman üçlü karşılaştırma                           |
| v2.0     | 2026-09-22     | §9 Algoritma tablolaştırıldı + "hazır mı" kolonu                                   | K2/K6/K8'in zaten mevcut olduğu keşfedildi                   |
| v2.0     | 2026-09-22     | §10 Boşluk & Risk, §11 Karar Kaydı, §12 Yol haritası, §14 Revizyon                 | Talep edilen 5 tablo                                         |
| v2.0     | 2026-09-22     | Soru kapsama %30 → **%56** düzeltildi                                              | Önceki tur MRR/ARR/churn/kaliteyi "yok" saymıştı — hatalıydı |
| v2.1     | 2026-09-22     | §0.1 geri linkler 5 dosyaya **gerçekten** yazıldı + pano satırı sabitlendi        | Önceki tur yalnızca iddia etmişti                             |
| v2.1     | 2026-09-22     | §8.4 eklendi — canlı DB doğrulaması (30 tablo + tekrarlanabilir komut)            | EK BULGU-8/9/10 buradan çıktı                                 |
| v2.1     | 2026-09-22     | §9 K1 satırı düzeltildi: `users.last_login` **yok** (28 kolon tarandı)           | Girdisiz algoritma yazılamaz                                  |
| v2.1     | 2026-09-22     | §10 yeniden sıralandı; EK BULGU-8/9/10 P0 olarak eklendi                          | Sahte metrik en yüksek etki/efor oranına sahip                |
| v2.1     | 2026-09-22     | §11 KK-2/KK-3/KK-8 ✅ DOĞRULANDI, KK-9 eklendi                                    | SQL ile canlı doğrulandı, soru bekletilmedi                   |
| v2.1     | 2026-09-22     | §12 G0 eklendi ve ilk sıraya alındı; G2 S→M, G3 ✅, G4 bloklu                     | Yol haritası veri gerçekliğine göre yeniden kuruldu           |
| v2.1     | 2026-09-22     | §2 kapsama ayrıştırıldı: **%56 modül** · **≈%30 veri gerçekliği**                 | Tek sayı yanıltıcıydı                                         |
| v2.1     | 2026-09-24     | §4.1 kural 4 ✅, §7'ye canlı veri akışı satırı, §8.3 C1 kapandı, §10 risk 2 kapandı, §11 KK-1 kapatıldı (Polling), §13 SSE satırı; `admin_realtime.py` SSE→polling | UI-ADMIN-SSE-IHLAL-03 tamamlandı (KK-1 kararı)                |
| v2.1     | 2026-09-24     | §11 KK-3 kapatıldı (v0016 migration: users.last_login TIMESTAMPTZ + index), `src/company_master/schema/migrations/0016_users_last_login.sql/.down.sql` eklendi | VERI-ADMIN-LASTLOGIN-MIGRATION-04 tamamlandı                   |
| v2.1     | 2026-09-24     | §16 Giriş anında last_login yaz (API-ADMIN-LASTLOGIN-YAZ-05), `web_app.py:2232` + fallback `:2246` DB UPDATE eklendi, §14 Revizyon Tablosu v2.1 2026-09-24 eklendi | API-ADMIN-LASTLOGIN-YAZ-05 tamamlandı                           |
| v2.1     | 2026-09-24     | §9 K1 kısmi: `src/company_master/churn.py` `risk_etiketi()` eklendi (tek sinyal last_login), doctest 7/7 geçti, §14 Revizyon Tablosu v2.1 2026-09-24 eklendi | API-ADMIN-CHURN-FONKSIYON-06 tamamlandı                         |
| v2.1     | 2026-09-24     | §6 Matris: `_giris_aktinligi()` churn risk kolonu eklendi (UI-ADMIN-CHURN-KOLON-07), `musteri_yonetimi.py:272` `risk_etiketi()` kullanımı, §14 Revizyon Tablosu v2.1 2026-09-24 eklendi | UI-ADMIN-CHURN-KOLON-07 tamamlandı                             |
| v2.1     | 2026-09-24     | §4 Matris: `admin_kpi.py` MAU `last_login` üzerinden hesaplanıyor (UI-ADMIN-MAU-08), "Aktif Kullanıcı" → "MAU (30 Gün)" etiketi düzeltildi, `load_admin_kpi_summary()` `:65` MAU sorgu eklendi, §14 Revizyon Tablosu v2.1 2026-09-24 eklendi | UI-ADMIN-MAU-08 tamamlandı                                     |


---



## 15. Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani]]
- [[Huginn Data Insights/AI proje v1/V10/03_mimari/06_muninn_prd_vs_huginn_analiz]]
- [[Huginn Data Insights/docs/ARCHITECTURE_DECISION_HYBRID_ADMIN]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]

