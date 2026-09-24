# Muninn SUPER ADMIN PANEL PRD V1 vs Huginn Admin Panel Karşılaştırmalı Analizi

**Analiz Tarihi:** 2026-09-13
**Hazırlaması:** Roo (Architect)
**Durum:** ⚠️ ARŞİV — geçersiz (2026-09-22 SUPERSEDED, 2026-09-24 KK-4 ile teyit edildi)

> Bu analiz **arşiv/tarihsel kayıttır**. Güncel ve en yüksek otoriteli admin panel dökümanı:
> [`05_versiyonlar/02_admin_panel_hedef_dokumani.md`](../05_versiyonlar/02_admin_panel_hedef_dokumani.md) (SSOT, `ADMIN-KİT`, v2.0).
> Çelişki halinde SSOT dökümanı geçerlidir. Bu dosyadaki §"V9'a 16.5 ekle" maddesi kapanmıştır
> (V9 §16.5 satır 827'de mevcut — SSOT §8 EK BULGU-4).

---

## ÖZET

Muninn PRD, SaaS yönetim paneli için kapsamlı bir operasyon merkezi tasarımı sunarken, Huginn şu anda **minimal admin panel** (Streamlit tabanlı, karar defteri sekmesi) ile başlamıştır. Muninn'in 9+ modülü (tenant, abonelik, faturalama, AI ops, veri ops, kalite, API, destek, güvenlik) Huginn için MVP sonrası **faz roadmap'i**nde bulunmalıdır.

---

## 1. TEKNOLOJİ YÖNÜ

### Muninn
| Katman | Teknoloji | Açıklama |
|--------|-----------|----------|
| Frontend | Streamlit Multipage | Modüler, hızlı geliştirme |
| | Plotly | Grafikler |
| | AgGrid | Veri tabloları |
| Backend | FastAPI | Yeni API'ler (admin için) |
| Database | PostgreSQL | SSOT veri deposu |
| Cache | Redis | Session, rate limit, cache |
| Background Jobs | Celery + Redis Queue | Async işleri |
| Monitoring | Prometheus + Grafana | Sistem metriği |
| Logging | Loguru + PostgreSQL Audit | Detaylı denetim |

### Huginn (Mevcut)
| Katman | Teknoloji | Durum |
|--------|-----------|--------|
| Customer Panel | FastAPI + statik web_dashboard | ✅ Aktif (8000) |
| Admin Panel | Streamlit | ⚠️ Minimal (8501) |
| Backend | FastAPI (web_app.py) | ✅ Operational |
| Database | PostgreSQL (Supabase) | ✅ Aktif |
| Cache | Redis | ⏳ Kurulmuş, az kullanılmış |
| Background Jobs | Apify Webhook + ingest pipeline | ⚠️ Event-driven |
| Monitoring | Prometheus metrikleri + OpenTelemetry skeleton | ⏳ Eksik |
| Logging | Telegram bot + file logs | ⚠️ Minimal |

**Sonuç:** Huginn'in core stack Muninn'e uyumlu. Admin panel genişletme yapılabilir.

---

## 2. MUNINN MODÜLLERİ vs HUGINN HAZIRLIĞI

| Modül | Muninn Gerekçe | Huginn Durumu | MVP'ye İhtiyaç? | Faz | Açıklama |
|-------|---|---|---|---|---|
| **Dashboard (KPI)** | Platform özeti, MRR/ARR, aktif tenant, DAU | ✅ Kısmi var (`/api/kpi`, web_app.py) | **YET** | P1 | Müninn'in 12 KPI'sının 6'sı (MRR/ARR eksik). |
| **Tenant Yönetimi** | Tenant CRUD, plan atama, kredi | ❌ Yok | ❌ MVP sonrası | P2 | Huginn B2B şu anda single-tenant. Multi-tenant gerekliyse bu modül gerekli. |
| **Abonelik Yönetimi** | Plan CRUD, yükselt/düşür, trial | ❌ Eksik | ❌ MVP sonrası | P2 | `users` tablosu var ama plan versioning yok. |
| **Kullanım Analitiği** | Search, AI, API, export kullanımı | ⚠️ Kısmi (`/api/metrics`, 9router_optimizer) | ✅ YET | P1 | API kullanım metriği var; user-level breakdown eksik. |
| **Veri Operasyonları** | Kaynak sağlığı, crawl yönetimi, güncellik | ✅ Kısmi (`source_registry`, OSINTEngine, APIFY) | ✅ YET | P1 | Apify webhook monitoring eksik; UI gerekli. |
| **AI Operasyonları** | Model kullanımı (GPT/Claude/Gemini), token, maliyet | ⚠️ Başlangıç (`9router_optimizer.py`, scoring) | ✅ YET | P1 | 9router provider health monitored; admin UI eksik. |
| **Sistem İzleme** | Hata, queue, performans metriği | ⚠️ Kısmi (OpenTelemetry skeleton, Prometheus) | ✅ YET | P1 | `/api/performance` endpoint'i var; Streamlit UI eksik. |
| **Güvenlik & Audit** | Login, MFA, audit logs | ✅ Kısmi (Telegram auth, session) | ✅ YET | P1 | Karar defteri sekmesi var; full audit trail eksik. |
| **API Yönetimi** | Key CRUD, limit, analytics | ⚠️ Kısmi (rotate-key, require_api_key) | ⚠️ PARTIAL | P1-P2 | API key rotate var; analytics Dashboard eksik. |
| **Faturalama** | Invoice, payment, refund | ❌ Yok | ❌ MVP sonrası | P3 | Huginn şu anda freemium/manual plan. Stripe entegrasyonu gerekli. |
| **Destek Merkezi** | Ticket CRUD, priority, escalation | ❌ Yok | ❌ MVP sonrası | P3 | Müşteri talebine bağlı. |
| **Veri Kalitesi** | QS 0-100, eksik alan takibi | ✅ Var (`quality_gate.yaml`, kalite_skoru) | ✅ YET | P1 | Kalite metriği backend'de var; admin UI eksik. |

---

## 3. HUGINN MVP SONRASI ROADMAP (Muninn'den Esinlenerek)

### Faz 1: Admin Panel MVP (Tamamlanacak — Temmuz 2026)
**Hedef:** Operasyon ekibinin günlük işlerini çalıştırması.

- [x] **Dashboard KPI** — Müşteri sayısı, API çağrıları, toplam sinyal, sistem sağlığı
- [x] **Karar Defteri** — Archival + Searchable decision log (✅ mevcut)
- [ ] **Webhook Monitörü** — Apify webhook health, DLQ sayısı, rate limit status
- [ ] **AI Cost Dashboard** — Daily/monthly maliyet, provider bazlı break-down
- [ ] **Veri Kalitesi Özeti** — 8313 firma, kalite skoru dağılımı, eksik alanlar
- [ ] **API Analytics** — Endpoint kullanımı, error rate, top users
- [ ] **Sistem Performansı** — Query latency, cache hit ratio, slow queries

### Faz 2: Tenant & Subscription (Eylül 2026)
- [ ] Multi-tenant yapı (şu anda single-tenant)
- [ ] Plan yönetimi (Starter/Growth/Enterprise)
- [ ] Credit system (Search/AI/Export/API)

### Faz 3: Faturalama & Ödeme (Ekim 2026)
- [ ] Stripe entegrasyonu
- [ ] Invoice generation
- [ ] Churn risk detection

### Faz 4: Destek & Ticketing (Kasım 2026)
- [ ] Ticket CRUD
- [ ] User self-service portal

---

## 4. HUGINN'İN MUNINN'DEN ALMASI GEREKEN TASARIM İLKELERİ

1. **Operasyon Merkezi Yaklaşımı:** Admin panel sadece CRUD değil; operasyon kararları (churn risk, anormal maliyet, veri sağlığı uyarısı) desteklemeli.

2. **Real-time Monitoring:** SSE (Huginn'de zaten P7-19b) ile canlı metrikler.

3. **Audit Confidence:** Her işlem — tenant oluşturma, kredi atama, API key rotate — audit log'a düşmeli. Huginn'de decision_log.jsonl var; bunu PostgreSQL audit tablosuna entegre et.

4. **Multi-Provider Cost Visibility:** 9router kullanan her request maliyeti izlenmeli (Muninn: model bazlı, Huginn: provider bazlı).

5. **Kalite Skoru Operasyon:** Kalite metriği (QS < 30) siparişi riskli işaretleme, otomatik düzeltme görevleri tetikleme.

---

## 5. TEKNIK BORÇ & RISKLER

| Risk | Muninn Çözümü | Huginn Durum |
|------|---|---|
| Audit trail incompleteness | PostgreSQL audit logs + Loguru | decision_log.jsonl + file logs (eksik) |
| Monitoring blind spots | Prometheus + Grafana | OpenTelemetry skeleton (eksik) |
| Cost visibility | Model-based token tracking | Provider-based routing (doğru ama incomplete UI) |
| Multi-tenant isolation | Tenant-scoped RLS (PostgreSQL) | Single-tenant (MVP sonrası gerekli) |

---

## 6. SONRAKI ADIMLAR

### İmmediately (Bu Sprint)
1. Muninn PRD'den **Faz 1 görevlerini** Huginn TODO'ya ekle (P7-22 → P7-27)
2. Admin Panel roadmap'ini V9 bağlam dokümana ekle (§16.5)
3. PostgreSQL audit table schema tasarımı (migration 0007)

### Next Sprint
1. Webhook Monitor UI (Streamlit) — Apify DLQ, rate limit
2. AI Cost Dashboard — 9router provider breakdown
3. Veri Kalitesi Özeti — company_quality_scores aggregation

### Later
1. Multi-tenant preparation (şema tasarım)
2. Plan versioning + credit system
3. Stripe integration

---

## 7. İLGİLİ DOSYALAR

- **Muninn PRD:** `../Muninn SUPER ADMIN PANEL PRD V1.txt`
- **Huginn V9 Bağlam:** `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` (§16.4)
- **Huginn Admin Panel:** `web_dashboard/tabs/admin_panel.py` (karar defteri sekmesi)
- **Mevcut Admin API'ler:** `web_app.py` → `/api/admin/*`, `/api/performance`, `/api/metrics`
- **9Router Optimizer:** `scripts/9router_optimizer.py` (provider health, anomali tespiti)
- **Decision Log:** `scripts/decision_log.py` + `data/orchestrator/decision_log.jsonl`

---

## 8. RISK MATRISI

| Risk | Olasılık | Etki | Mitigation |
|------|---|---|---|
| Multi-tenant migration karmaşıklığı | MEDIUM | HIGH | Şema tasarımı P2 içinde kararlaştır |
| PostgreSQL audit table oluşturma overhead | LOW | MEDIUM | Migration 0007 ile yapı, populate lazy |
| Muninn PRD'nin Huginn context'ine uyumsuzluğu | MEDIUM | LOW | Yalnızca uygulanabilir kısımları al (faturalama MVP sonrası) |

---

**Son Güncelleme:** 2026-09-13 03:29 UTC+3

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
