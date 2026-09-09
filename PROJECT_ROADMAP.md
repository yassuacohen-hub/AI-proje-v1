# 🚀 Huginn Data Insights - Web Dashboard Roadmap

> **Hedef**: Local Streamlit dashboard'u production-ready web app'e taşıma

---

## 📋 Mevcut Durum

| Dashboard | Konum | Özellikler | Durum |
|-----------|-------|------------|-------|
| **app.py** | Root | KPI + Task Board + Handoffs | ✅ Çalışıyor |
| **scripts/dashboard.py** | scripts/ | Quality KPI + Coverage + Heatmap + CSV Export | ✅ Çalışıyor |

**Problem**: İki ayrı dashboard; birleştirilip modern tasarımla web'e taşınmalı.

---

## 🎯 FAZ 1: Dashboard Birleştirme & UI/UX (1-2 Hafta)

### 1.1 Tek Dashboard Oluşturma
- [ ] `app.py` + `scripts/dashboard.py` → `app/web_dashboard.py`
- [ ] Sayfa yapısı: Genel Bakış / Veri Kalitesi / Görevler / Explorer / Ayarlar

### 1.2 Modern UI/UX
- [ ] Light/Dark theme toggle
- [ ] Professional renk paleti (Indigo/Slate + Accent)
- [ ] Interactive charts (Plotly) + Progress bars
- [ ] Responsive tasarım, sidebar collapsible

### 1.3 Gelişmiş Görselleştirme
- [ ] Quality score dağılımı (Histogram + KDE)
- [ ] Coverage: radial gauge charts
- [ ] Heatmap: hover details
- [ ] Sankey: Data flow (raw → cleaned → scored)

---

## 🐳 FAZ 2: Docker & Production (1 Hafta)

### 2.1 Docker Optimizasyonu
- [ ] Multi-stage build, non-root user
- [ ] Healthcheck endpoint
- [ ] Production `docker-compose.prod.yml`

### 2.2 Servis Yapısı
- [ ] Web (Streamlit/Gunicorn)
- [ ] PostgreSQL (production config)
- [ ] Redis (caching)
- [ ] Nginx (reverse proxy + SSL)