# Muninn Super Admin Panel — PRD + Yol Haritası (v1.0)

---

## 0. Ozet ve Pozisyonlama

Bu belge **Muninn SUPER ADMIN PANEL PRD v1.0** ile **Huginn Data Insights** projesinin mevcut durumunu tek master referans halinde birlesiktir.

**Hedef:** SaaS isletmesinin operasyon merkezi olacak Streamlik tabanli admin panelin mevcut altyapi uzerine kademeli inmasidir.

**Mevcut mimari baglam:** Admin=Streamlit 8501, Musteri=FastAPI 8000; Docker + PostgreSQL; ORCH-08/09 pano ajan sistemi; 14.000 firma; 9Router optimizer; wiki vault (V10).

## 1. Amaç ve Kapsam (PRD §1 + Mevcut Bağlam)

| PRD Amaç | Mevcut Durum | Kapanacak Boşluk |
|---|---|---|
| Müşteri operasyonlarını yönetmek | Kullanıcı onayı (P7-20), API kullanım | Tenant/Abone kavramı, plan/fatura/kredi modülleri YOK |
| Platform sağlığını izlemek | `/api/health`, `/api/performance` | CPU/RAM/Disk, kopma takibi |
| Geliri takip etmek | API usage var | MRR/ARR, fatura, kredi sistemi |
| Veri kalitesini yönetmek | Kalite skorları (0-100) | Eksik alan dashboard, veri güncelliği |
| AI maliyetlerini izlemek | 9Router optimizer | Token/maliyet paneli |
| Veri toplama süreçlerini yönetmek | Scraper'lar, Crawl yönetimi | Crawl yönetim paneli |
| Güvenlik olaylarını takip etmek | Audit logs eksik | Güvenlik dashboardu, MFA, RBAC |
| Churn risklerini tespit etmek | YOK | Churn skoru, tahmine dayalı |
| Ürün kullanımını analiz etmek | API usage | Kullanım trendleri, tenant sağlığı |

---

## 2. Teknoloji Standartları — Gerçeklik ve Adaptasyon (PRD §2)

PRD orijinal şu stack'i önerir; repo'daki mevcut duruma göre **kaide-i kadem** plan:

| Katman | PRD | Repo'da Var? | Adapter / Karar |
|---|---|---|---|
| Frontend | Streamlit Multipage + Plotly + AgGrid | Streamlit (single app.py) | Multipage -> `st.tabs`; AgGrid opsiyonel |
| Backend | FastAPI + PostgreSQL | FastAP (`web_app.py`) + PostgreSQL (Docker) | `/api/admin/*` genişlet |
| Arka plan işleri | Celery + Redis Queue | YOK (Görev Zamanlayıcı) | MVP: zamanlayıcı + subprocess; Celery Faz 3+ |
| Monitoring | Prometheus + Grafana | Kısmi (`/api/performance`) | Prometheus Faz 2; `/api/performance` SSOT |
| Loglama | Loguru + Audit Logs | print/logging | Audit log migration; loguru isteğe bağl. |

**Karar:** PRD stack'ini anında kurmak yerine, mevcut Windows + Docker altyapıyla uyumlu **kademeli katman** kuralım.

---

## 3. Panel Mimarisi ve Sekmeler (PRD §3 adaptasyonu)

Mevcut Streamlit `app.py` (440 satır) tek panel; `st.tabs` ile modülerleştirilecek. Mevcut modüller `web_dashboard/tabs/` klasöründe.

| Sekme | PRD Bölümü | Durum | Sahip |
|---|---|---|---|
| Genel Bakış | §4 Dashboard | Gelistiriliyor | cline |
| Tenant Yönetimi | §5 | yeni | Faz 3 |
| Kullanıcı Yönetimi | §6 | Kısmi (P7-20) | Faz 2 |
| Abonelik Yönetimi | §7 | yeni | Faz 3 |
| Faturalama / Finans | §8 | yeni | Faz 3 |
| Kredi Yönetimi | §9 | yeni | Faz 3 |
| Kullanım Analitiği | §10 | Kısmi (api-usage) | Faz 2 |
| AI Operasyonları | §11 | Kısmi (9router) | Admin-02 |
| Veri Operasyonları | §12 | Kısmi (scraper) | Admin-02 |
| Veri Kalitesi | §13 | Kısmi (quality score) | Faz 2 |
| API Yönetimi | §14 | Kısmi (P7-20) | cline |
| Destek Merkezi | §15 | yeni | Faz 3 |
| Güvenlik | §16-17 | Kısmi | Faz 2 |
| Sistem İzleme | §18 | yeni | Admin-01 |
| Feature Flags | §19 | yeni | Faz 3 |
| Ayarlar | §20 | Kısmi (.env) | Faz 2 |

**Çarpışma kuralı:** Müşteri paneli (FastAPI 8000) — admin-only endpointler Streamlit tüketir.

---

## 4. Veri Modeli ve Schema Planı

### 4.1 Şu anda var — dokunma
- `companies`, `company_signals`, `sources`, `entity_resolution`, `users`, `api_keys`, `api_usage`

### 4.2 Faz 3 ekleri
| Migration | Tablo | Açıklama |
|---|---|---|
| 0012_tenants.sql | tenants | tenant_id, firma_id, plan_id, durum, created_at |
| 0013_plans.sql | plans | name, limit_kullanici, limit_search, limit_ai, limit_export |
| 0014_invoices.sql | invoices | tenant_id, tutar, durum, period |
| 0015_credits.sql | credits | tenant_id, tur, miktar |
| 0016_tickets.sql | tickets | konu, durum, oncelik, tenant_id |
| 0017_feature_flags.sql | feature_flags | tenant_id, ozellik, aktif |
| 0018_audit_logs.sql | audit_logs | kullanici, tenant, islem, eski, yeni, ip, ts |

Migration'lar `src/company_master/schema/migrations/` altında versiyonlanır.

---

## 5. Yol Haritası / Roadmap

### Faz 0 — Temel (şu an / 2 saat)  MUNINN-0x  (ADMIN sistem)
- ADMIN-01: Watchdog çift port (8000+8501) + Telegram alert + otomatik başlatma
- ADMIN-02: Kazıma + 9Router sekmeleri (kilo)
- ADMIN-03: Wiki + UI kit (roo)
- Bu master PRD belgesi + 00-Home.md güncelle

### Faz 1 — PRD P0 (Dashboard, Tenant/Kullanıcı, Kullanım)  MUNINN-1x
- Dashboard KPI genişlet: MRR/ARR, churn trend, DAU/MAU, AI maliyeti
- Kullanıcı yönetimi: filtre eklenir
- API usage → Kullanım analitiği

### Faz 2 — PRD P1 (AI/Veri/Güvenlik)  MUNINN-2x
- AI Operasyonları: 9router token/maliyet panel
- Veri Operasyonları: crawl durumu, veri güncelliği
- Güvenlik: giriş logları + audit log migration
- Audit Log: 0018 migration

### Faz 3 — PRD P2 (Faturalama, API, Destek, Flags)  MUNINN-3x
- Tenant/abone/fatura/kredi migration 0012-0015
- API anahtar yönetimi (P7-20 üzerine)
- Feature Flags migration 0017
- Ticket sistemi migration 0016

### Faz 4 — PRD P3 (Tahminleme)  MUNINN-4x
- Churn prediction, Executive Dashboard, cohort analizi
- Celery worker + Prometheus + Grafana

Her fazdan önce **onay ve test** (pytest + CI). MUNINN-XX görev ID'leri task_board.json kaydolur.

---

## 6. PRD Streamlin İzleme Kuralları (zorunlu)

| PRD Kural | Uygulama |
|---|---|
| AgGrid tablo | `st.dataframe` filtre |
| Plotly grafik | varsa Plotly; yoksa `st.bar_chart` fallback |
| `st.metric()` / `st.status()` | Durum |
| `st.toast()` | Geri bildirim |
| `st.cache_data` | TTL 30/60 s |
| Büyük dataframe | paginate + filtre sorgu |
| Senkron crawl | subprocess async + log |
| Uzun AI işleri | geçici subprocess worker |

---

*Bu belge `Muninn SUPER ADMIN PANEL PRD V1.txt` (792 satır) ve `docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md` esli yola dayanir. Her faz için ilgili PRD numaralari bu belgenin altinda MUNINN-XX ID ile isaretlenir.*

---

## 7. İlgili Analizler ve Karşılaştırmalar

| Belge | Yazar | İçerik | Konum |
|---|---|---|---|
| [[06_muninn_prd_vs_huginn_analiz]] | Roo (Architect) | PRD vs mevcut panel karşılaştırması, modül-hazırlık matrisi, faz roadmap doğrulaması, risk matrisi | `V10/03_mimari/` |

### Roo Analizi ↔ Bu Belge Faz Eşlemesi

| Roo Analizi | Bu Belge (Master PRD) | Not |
|---|---|---|
| Faz 1 (MVP): KPI, Webhook Monitor, AI Cost, Veri Kalitesi, API Analytics, Performans | Faz 1 (MUNINN-1x) + Faz 2 (MUNINN-2x) | İçerik birebir; Roo bunları "P1" tek fazda topluyor |
| Faz 2: Multi-tenant, plan, kredi | Faz 3 (MUNINN-3x, migration 0012-0015) | Aynı öncelik, faz numarası farklı |
| Faz 3: Stripe, fatura, churn | Faz 3-4 (MUNINN-3x/4x) | churn Faz 4'te |
| Faz 4: Ticket, self-service | Faz 3 (MUNINN-3x) | |

**Pano ID gerçeği (2026-09-13):** P7-22/23/24 panoda başka görevlere atanmış (Apify DLQ, Vektör Katmanı, ASO/OSTİM). Yeni admin panel görevleri **P7-25+** ID'leriyle açılmalı. Detay: [[TODO]] ⚠️ notu.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
