# Brif: kilo — 2026-09-13

## 1. Okuduğum Kararlar
- `01_etl_mimarisi.md` — ETL pipeline (RAW→COMPANY MASTER), UUID PK, PostgreSQL+FullTextSearch MVP
- `02_muninn_super_admin_panel_prd_ve_yol_haritasi.md` — Streamlit/FastAPI/PostgreSQL stack, Faz 0-4 roadmap
- `06_muninn_prd_vs_huginn_analiz.md` — Modül hazırlık matrisi, risk matrisi, MVP sonrası roadmap
- `ADMIN-01-02-03_TASK_BRIEF.md` — Faz 0 admin panel görev dağılımı (kilo: ADMIN-02 kazima+9router)

## 2. Öneriler
- **Backend:** `web_app.py` (FastAPI) + `web_dashboard/tabs/` (Streamlit) ayrımını koru. Yeni sekme eklerken `st.tabs` + `docs/UX_UI_KURALLARI.md` uyumlu yap.
- **Veri modeli:** mevcut `companies`, `company_signals`, `sources`, `entity_resolution`, `users`, `api_keys`, `api_usage` tabloları yeterli MVP için. Faz 3 migration'lar (0012-0018) admin paneli için şart.
- **AI chat motoru:** 9Router (`/v1/chat/completions` OpenAI format) mevcut. Admin UI'da provider bazlı token/kost dashboards needed (ADMIN-02 kapsamında).
- **Kota:** `api_usage` tablo + rate limiting var. Tenant bazlı quota Faz 2 (MUNINN-2x) gerektirir. MVP'de global limit + kullanım izlemesi yeterli.

## 3. Kritikler
- Admin panel (8501) ve müşteri paneli (8000) arkasında aynı PostgreSQL — tablo kilitleme ve long-running sorgular ayrı bağlantı havuzu gerektirir.
- 9Router provider health monitoring eksik: `/api/performance` kısmi, Prometheus+grafana Faz 2.
- Multi-tenant izolasyon (RLS) Faz 3'te gerekli — şema tasarımı P2'de kararlaştırılmalı.
- Chat motoru uptime garantisi yoksa fallback provider strategisi belirtilmeli (Muninn: Celery+Redis Queue, Huginn: subprocess).

## 4. Eklemeler
- `00_sentez.md` — tüm ajan briflerinin sentezi, herkesin okuduğu tek kaynak (SENTEZ-01'de yapılacak).
- ADMIN-02 (kilo): kazima.py + router9.py Streamlit sekme entegrasyonu — mevcut `scripts/9router_optimizer.py` JSON çıktılarını kullan.
- Audit log migration 0007 — PostgreSQL audit tablosu, decision_log.jsonl entegrasyonu.

## 5. Riskler + Kota Notu
- Kota: API kullanım metrikleri mevcut (`api_usage`), user-level breakdown eksik. Faz 1'de genişletilmeli.
- Risk: Celery+Redis Queue yok — arka plan işleri subprocess ile (MVP yeterli, Faz 4'te Celery).
- Risk: Monitoring blind spot — Prometheus+Grafana yok (Faz 2).
- Devretme önerisi: BRIF-02 tamamladıktan sonra ADMIN-02 (kilo) → router9.py token chart + cost breakdown.

## 6. Yol Haritası Katkısı
- Faz 0 (şu an): admin panel tab paketlemesi, kazima + 9router sekme (kilo)
- Faz 1 (P1): Dashboard KPI genişlet, AI Cost Dashboard, API Analytics
- Faz 2 (P1-P2): multi-tenant hazırlık, tenant bazlı kota, audit log migration
- Faz 4: Celery worker + Prometheus + Grafana
