# Brif: Roo — 2026-09-13

## 1. Okuduğum Kararlar

- **02_muninn_super_admin_panel_prd_ve_yol_haritasi.md**: Faz 0-4 roadmap, 20 sekme hedefi, teknoloji stack adaptasyonu (Streamlit tabs + FastAPI /api/admin/* endpoints)
- **06_muninn_prd_vs_huginn_analiz.md**: Huginn MVP durumu (12 modülden 7 kısmi/yok), P7-25+ görev ID ayrılışı, Faz 1-4 teknik borçlar (audit trail, monitoring, cost visibility)
- **ADMIN-01-02-03_TASK_BRIEF.md**: ADMIN-03 Wiki + UI Kit sekmesinin tasarım/spesifikasyonu (V10 vault render, bileşen galerisi, .streamlit/config.toml)
- **app.py + web_dashboard/tabs/ mevcut moduller**: 17 sekme (P7-32 ile API Analytics eklendi), st.cache_data(ttl=30/60), st.metric/st.dataframe/st.bar_chart pattern'i
- **V9 bağlam dokümani §1-3**: Platform identity (B2B Intelligence), 6+1 katman mimarisi, V6 prensibi "do not make customer dependent on private CRM", SSOT = PostgreSQL

## 2. Öneriler

### 2.1 Admin Panel Tasarım İlkesi: "Operasyon Merkezi Yaklaşımı"
Muninn'den alınacak en kritik ilke: Admin panel sadece **CRUD + monitoring** değil; **operasyon kararlarını (churn risk, anormal maliyet, data health alert) support etmesi** gerekiyor. Huginn'de bu eksik.

**Uygulama:**
- Her sekme bir "operasyonel signal" sunsun, not sadece metrik sayı.
  - Örn. "API Analytics" (P7-32): çağrı sayısı değil → "enterprise tier'da son 24h'de %15 spike, kontrol etmeye değer mi?"
  - Örn. "Kalite Özeti" (P7-31): kalite skoru değil → "QS < 30 firma sayısı ↑ (3→7), veri güncelleme sürecinde catch edildi mi?"
- Her sekme bir **context button** ("why?" notu, teknik borç, bağlam).

### 2.2 Sekme Tasarım Hiyerarşisi: Prioritize Observable > Actionable > Informational

Mevcut 17 sekme + roadmap 20 sekmeye doğru gidiyor. Navigasyon karmaşıklığı artacak.

**Önerilen Tab Organization (opsiyonel multipage refactor Faz 2):**

**Tier 1 (Günlük Operasyon — Home ekranı gibi ilk açılış):**
- 🏠 Genel Bakış (KPI: API çağrı, firma sayısı, aktif sinyal, sistem sağlığı)
- 🔔 Uyarılar & Anomaliler (9router maliyeti spike, data freshness warning, rate-limit triggered)

**Tier 2 (Müşteri & Kullanım):**
- 👥 Kullanıcı Yönetimi (P7-20)
- 📊 Kullanım Analitiği (API Analytics — P7-32)
- 🔌 API Yönetimi (key rotate, rate-limit config — opsiyonel Faz 2 ek sekme)

**Tier 3 (Platform Sağlığı & Teknik):**
- 🩺 Sistem Performansı (query latency, cache hit, slow queries)
- 🚀 Veri Operasyonları (crawl status, source health — ADMIN-02 kazima.py)
- 💰 AI Maliyetleri (9router provider breakdown — ADMIN-02 router9.py)
- 📈 Veri Kalitesi (QS dağılımı, eksik alanlar — P7-31)

**Tier 4 (Konfigürasyon & Karar Yönetimi):**
- ⚙️ Ayarlar & Feature Flags (Faz 3)
- 📋 Karar Defteri / Audit Log (zaten var)
- 📚 Wiki & Dokümantasyon (ADMIN-03 wiki.py — kurum belgeleri)
- 🧪 UI Kit & Bileşen Galeri (ADMIN-03 ui_kit.py — komponent örnekleri, developer reference)

### 2.3 UX Iyileştirme Önerileri (P7-32 API Analytics uygulama deneyiminden)

**Issue #1: "Bekleyen veri" UX problemi**
- P7-32'de `st.spinner("API kullanım verisi yükleniyor...")` sonra sayfanın üst kısmında info kutusu.
- **Sorun:** Kullanıcı spinner'ı kapatınca info'yu göremeyebilir → "neden veri yok?" mutsuzluğu.
- **Çözüm:**
  1. Kısıtları **sabit sidebar** veya **collapsible header** olarak sayfanın **en üstüne (before spinner)** koy.
  2. Veya sekme açılırken info kutusu "Always On" state'ine koy (session cache).

**Issue #2: "Boş veri" graceful handling**
- P7-32 + P7-31 her ikisi de "henüz kaydedilmiş veri yok" → `st.info("...")` fallback döner.
- **Sorun:** Ekran boş görünüyor; kullanıcı "sistem çalışıyor mu?" şüphe ediyor.
- **Çözüm:**
  1. Empty state icons + helpful text → "⏳ Veri henüz toplanmadı" + "İlk veriler 24 saat içinde görünecek"
  2. Sahte example data (sample mode) `--demo` flag ile → developer/demo environment'de testlenebilir.

**Issue #3: Metrik card layout scalability**
- P7-32'de `st.columns(4)` → 4 metric card. Faz 2-3'te 6-8 metric card olacak.
- **Sorun:** 4K monitörde hava/oran; mobile'da eskilmek.
- **Çözüm:** Responsive column count — `responsive_grid(n_cards=8, max_cols=4)` helper function.

### 2.4 Alternatif Sekme Önerileri (Muninn PRD'den uyarlama)

**ADMIN-04: Churn Risk Dashboard** (Faz 2, optional)
- **Hedef:** Müşteri kaybı riskini operasyonel olarak detect etmek.
- **Sinyaller:**
  - API usage ↓ last 7 days (dönem ortalamasına vs)
  - Query count per user ↓
  - Support ticket ↑ (Faz 3)
- **Output:** "High Risk" kullanıcılar + reactivation recommendation
- **Niçin:** Huginn'de churn modeli yok ama V9 "commercial intent prediction" prensibine uygun inverse signal.

**ADMIN-05: Data Lineage & Source Health** (Faz 2, replaces/extends Veri Operasyonları)
- **Hedef:** "Bu firma verisi hangi kaynaktan geldi? Güncel mi? Trusted mi?"
- **Sinyaller:**
  - Source freshness (last update timestamp per company per source)
  - Entity resolution confidence (multiple VKN same company?)
  - Data completeness %
- **Output:** Quality score breakdown by source; audit trail
- **Niçin:** V9 "do not pretend to know what data cannot prove" → transparency critical.

**ADMIN-06: Tenant Health (Faz 3, multi-tenant ready)**
- **Hedef:** Müşteri tenant'ının "operasyonel wellness" scoresi.
- **Sinyaller:**
  - API quota usage %
  - Search credit usage %
  - Query latency (their perspective)
  - Support backlog
- **Output:** Per-tenant SLA dashboard; churn risk flag
- **Niçin:** Faz 3 multi-tenant + Muninn PRD §5 tenant yönetimi.

## 3. Kritikler

### 3.1 17 Sekme → Navigasyon Bloat Riski

**Durum:** mevcut app.py `st.tabs([..., 17 sekme])` — single row. Faz 3'te 20+ sekme → scroll → UX degradation.

**Uyarı:** Multipage refactor (Streamlit Pages) ertelendi ama "point of no return" yaklaşıyor (Faz 2 sonu).

**Karar:**
- [ ] Faz 2'nin başında tasarım review: st.tabs multirow vb. veya Streamlit Pages + nested navigation.
- [ ] Alternatif: Sidebar categorized menu + st.selectbox (admin_audit.py benzeri pattern).

### 3.2 Admin API Response Consistency

**Durum:** P7-32 `/api/admin/api-usage` → `{"items": dict, "rate_limits": dict}`, ama başka admin endpoint'ler (kpi, quality) farklı schema.

**Uyarı:** Frontend'de `data.get("items")` vs `data.get("quality_overview")` spaghetti kodu artacak.

**Karar:** Faz 2'de admin API response standardı tanımla:
```json
{
  "status": "ok" | "loading" | "error",
  "data": { ... },
  "meta": {
    "ttl_seconds": 30,
    "cached": true,
    "last_updated": "2026-09-13T18:00:00Z"
  },
  "limitations": ["only enterprise tier", "in-memory resets on restart"]
}
```

### 3.3 Audit Trail Incompleteness (V9 Prensibi Riski)

**Durum:** "do not pretend to know" prensibi requires full auditability. Ama admin panel'de yapılan işlemler (kredi yükleme, API key rotate, user approve) **karar defteri'ne düşmüyor** — sadece web_app.py logs.

**Uyarı:** Üretimdeyken "kimin ne ne zaman yaptığı?" sorusu cevaplanamaz.

**Karar:**
- [ ] Admin sekmelerde yapılan her işlem → `decision_log.jsonl` kaydedilsin.
- [ ] Örn. "P7-20 Kullanıcı Yönetimi" → "approve" butonu basılınca → `{"op": "user_approve", "user_id": "X", "agent": "roo", "ts": "...", "decision_url": "/audit"}` yazılsın.
- [ ] Faz 2 görev: decision_log integration layer.

## 4. Eklemeler

### 4.1 Admin Panel Başlık Standarti (Branding/Clarity)

Her sekme başında **Huginn logosu + sekme açıklaması + last-updated badge**.

**Şablon:**
```python
st.subheader("🔌 [İkon] [Sekme Adı]")
st.caption(f"Son güncelleme: {datetime.now().strftime('%H:%M')} · Yenile butonunu klik et")
col_refresh, col_help = st.columns([1, 10])
with col_refresh:
    if st.button("🔄"):
        st.cache_data.clear()  # Force reload
with col_help:
    with st.expander("ℹ️ Bu sekme hakkında"):
        st.markdown("**Amaç:** ...\n**Veri Kaynağı:** `/api/admin/...`\n**Kısıtlar:** ...")
```

### 4.2 Admin "Playground Mode" (Developer Friendly)

Faz 2'de admin panel `?mode=playground` parametresi ile **demo veri + test alanı** sunsin.

**Niçin:**
- Yeni sekme geliştirirken production'a bakmadan test edebilsin.
- Müşteri sunumlarında "örnek" gösterebilsin (fake data, no PII).
- Onboarding dokümanı olsun.

## 5. Riskler + Kota Notu

### Riskler

**Risk #1: P7-32 API Analytics veri kaynağı kırılgan**
- `/api/admin/api-usage` in-memory dict → sunucu restart'ta sıfırlanır.
- **Çözüm:** Kalıcı veri için `api_usage_daily` tablosu oluşturulmalı (separate scope, Faz 2).

**Risk #2: Muninn PRD 20 sekme → Huginn MVP 17 sekme hızlı kapasiteyi aşabilir**
- Faz 1 sonu itibaren "navigation overload" gözlenecek.
- **Çözüm:** Multipage refactor Faz 2 başında; veya sidebar menu + drill-down.

**Risk #3: Admin panel test coverage düşük**
- `test_admin_*.py` testleri var ama integrasyon testi yok (Streamlit component mocking zor).
- **Çözüm:** Playwright/Selenium e2e test suite Faz 2 (ADMIN-07 kandidat).

### Kota Durumu

Roo (tasarım/mimarı) rolü şu anda:
- P7-32 (API Analytics) smoke test ve review ✅
- BRIF-01 (bu brif) 🔄 Tamamlanıyor
- ADMIN-03 (Wiki + UI Kit sekmesi) → Klilo devam etmesi öneriliyor (roo tasarım kısıtlandı, kod density yüksek)
- Tasarım görevleri (Muninn → Huginn adaptation, sekme hiyerarşi, UX standardları) → **Gelecek sprint için hazır**.

### Devretme Önerisi

- **ADMIN-03 (wiki.py + ui_kit.py) → Kilo'ya devret** — kilo Python okuyup hızlı implementer; roo token'ı şu an tasarım review için kullanılmış durumda.
- **Sekme hiyerarşi refactor (Faz 2) → Roo tasarım lead** — multipage strategy + UX standardları belirleme.

## 6. Yol Haritası Katkısı

### 6.1 Admin Panel Tasarım Döngüsü (Faz 1-4)

Bu brif ile tanımlanan "Operasyon Merkezi yaklaşımı" + "3-Tier Navigation" + "Consistent Response Schema" **V10/03_mimari/ referans dokümanı** haline gelsin.

**Döngü:**
1. **Her yeni sekme öncesi:** "Bu sekme ne operasyonel signal'i sunar?" sorgusu.
2. **Sekme tamamlama sonrası:** UX audit (empty states, spinners, error handling).
3. **Faz sonu:** Navigation + API response schema refactor.

### 6.2 Design Debt Tracking

Muninn PRD'den Huginn'e uyarlama sırasında ortaya çıkan kararlar (örn. "AgGrid yerine st.dataframe", "Prometheus yerine `/api/performance`") **ARCHITECTURE_DECISION_HYBRID_ADMIN.md** güncelle.

Bu brif ile yeni kararlar:
- **DECISION-A7:** Admin response schema standardı (Faz 2)
- **DECISION-A8:** Navigation refactor trigger (17 → 20 sekme geçişi)
- **DECISION-A9:** Audit trail integration layer (decision_log.jsonl ↔ web_app.py logs)

### 6.3 Gelecek Briflere Neler Sorulacak

Kilo (ADMIN-02 kazima.py + router9.py) ve sonraki tasarımcılar bu brifte tanımlanan **3-Tier hierarchy** + **empty state UX** + **"why?" context buttons** uygulanıyor mu diye kontrol etsinler.

---

**Brif Hazırlayan:** Roo (Architect — Design & UX critique)
**Tarih:** 2026-09-13
**Kodu:** BRIF-01
**Durum:** Tamamlandı — teslim hazır
