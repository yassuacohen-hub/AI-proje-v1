# ADMIN-01, 02, 03 — Muninn Super Admin Panel Faz 0 Görev Dağıtımı

**Tarih:** 2026-09-13
**Proje:** Huginn Data Insights — Muninn SUPER ADMIN PANEL PRD v1.0
**Durum:** 🚀 ÖZETLENDİ VE DAĞITILDI

---

## Özet

Mevcut Streamlit (app.py 440 satır) + FastAPI (web_app.py 8000 satır) + Docker + Görev Zamanlayıcı altyapısını:
1. **Kopma koruma** (çift port watchdog + Telegram alert)
2. **Tab/sekme paketlemesi** (kazıma, 9router, wiki, UI kit)
3. **Otomatik başlatma** (Görev Zamanlayıcı kaydı)

...yolla **3 gün içinde** tamamlamak.

---

## Görev Dağıtımı (Faz 0)

### ADMIN-01: Sunucu Kopma Çözümü + Otomatik Başlatma ⭐ **SOLO (ben/cline)**

**Hedef:** FastAPI (8000) ve Streamlit (8501) kopyasına karşı koruma, Telegram anlık bildirim, sistem restarts.

**Dosyalar (tamamlandi):**
- ✅ `scripts/server_watchdog_v2.py` (200 satır) — çift port izleme, Telegram gönderimi
- ✅ `docker-compose.yml` — streamlit healthcheck + profile cleanup
- ✅ `kurulum_otomatik_baslatma.bat` — Windows Görev Zamanlayıcı kaydı

**Kontroller:**
- `python -m py_compile scripts/server_watchdog_v2.py` — syntax ok
- `docker compose config --profile legacy` — validate (legacy kaldirildi)
- `kurulum_otomatik_baslatma.bat` — çalıştır ve kontrol et

**Kabul Kriterleri:**
- [ ] Watchdog 30s aralığında sağlık kontrolü yapıyor
- [ ] 8000 veya 8501 kopsa → log + Telegram bildirimi (emojili)
- [ ] Otomatik restart (proc.poll())
- [ ] docker compose up -d ile başlıyor
- [ ] .env'de TELEGRAM_BOT_TOKEN + CHAT_ID var

**Not:** Kubernetes üretimine kadar Windows Task Scheduler yeterli. VPS geçişi Faz 2'ye.

---

### ADMIN-02: Kazıma + 9Router Sekmeleri ⭐ **kilo (Senior Code)**

**Hedef:** Mevcut `web_dashboard/tabs/kazima.py` + `router9.py` dosyalarını Streamlit sekme olarak app.py'ye entegre etmek.

**Dosyalar:**
- `web_dashboard/tabs/kazima.py` (TBD) — veri crawl yönetimi sekme
- `web_dashboard/tabs/router9.py` (TBD) — 9Router optimizer sonuçları + AI maliyet paneli
- `app.py` — sekme entegrasyonu (st.tabs içinde)

**Mevcut Kontekst:**
- `scripts/9router_optimizer.py` mevcut (sağlık/probe/watch/backup modülleri)
- Sonuçları JSON: `data/9router_health.json`, `data/9router_probes.json`, etc.
- Mevcut tabs `web_dashboard/tabs/`: admin_extras.py (demo), user_management.py (kısmi)

**Görev İçeriği:**
1. **kazima.py:** Crawl görevlerinin durum tablosu + başlat/durdur butonları (async subprocess yok, synchronous log tail)
2. **router9.py:** 9Router health → bar/line chart (Plotly), token kullanımı, cost breakdown ($/bin token)
3. `app.py`'ye st.tabs ekleme (mevcut KPI bloğunun altında)
4. UX kural uyumluluğu (`docs/UX_UI_KURALLARI.md`)

**Kabul Kriterleri:**
- [ ] İki sekme app.py'de yükleniyor
- [ ] kazima: crawl durumu, başlat/durdur, log tail
- [ ] router9: token chart + cost breakdown
- [ ] Plotly fallback (AgGrid opsiyonel)
- [ ] `st.cache_data(ttl=60)` ile veri önbelleği
- [ ] Hata UI (\"Bekleniyor...\") graceful

**Tarih:** 3 gün (pazartesi EOD)

---

### ADMIN-03: Wiki + UI Kit Sekmeleri ⭐ **roo (Senior Design)**

**Hedef:** Obsidian Wiki V10 vault'u panelde görüntüle + UI component showcase.

**Dosyalar:**
- `web_dashboard/tabs/wiki.py` (TBD) — V10 vault indeksi + arama + markdown render
- `web_dashboard/tabs/ui_kit.py` (TBD) — Streamlit bileşen galeri (st.metric, st.status, st.toast, AgGrid demo)
- `.streamlit/config.toml` — tema + font + favicon

**Mevcut Kontekst:**
- `AI proje v1/V10/` — Obsidian vault (belge sistemi)
- `V10/00-Home.md` — ana indeks (yeni güncellenmiş PRD linki ile)
- Tema: "light" → tüm sekmelerde tutarlı

**Görev İçeriği:**
1. **wiki.py:**
   - V10 klasörünü tarama (file_id -> markdown)
   - Arama kutusu (regex)
   - st.markdown + st.columns düzeni
   - TOC (Table of Contents) → st.selectbox
2. **ui_kit.py:**
   - Streamlit best practices galeri
   - st.metric, st.status, st.toast, st.dataframe demo
   - Plotly örneği
   - Şablonlar (buton, form, tablo)
3. `.streamlit/config.toml`
   - Logo/favicon (Huginn logosu yok, boş bırak)
   - Font (monospace: "JetBrains Mono")
   - Tema: light

**Kabul Kriterleri:**
- [ ] wiki.py vault dosyalarını listele ve görüntüle
- [ ] Arama çalışıyor
- [ ] Markdown render düzgün
- [ ] ui_kit.py bileşen örnekleri hata vermemiş
- [ ] .streamlit/config.toml valide

**Tarih:** 3 gün (pazartesi EOD)

---

## Entegrasyon Kontrolleri (Hepsi)

1. **Import test:** `python -c "from app import app; print('OK')"`
2. **Docker test:** `docker compose up -d && curl http://localhost:8501/_stcore/health`
3. **Streamlit test:** `streamlit run app.py --logger.level=info`
4. **Watchdog test:** `python scripts/server_watchdog_v2.py --status`

---

## Telegram Bildirimi

**Bir kez gönderilecek (işlem tamamında):**
```
🚀 ADMIN-01/02/03 başlatıldı (Faz 0)
✅ Watchdog: çift port + Telegram OK
✅ Kazıma + 9Router sekmesi: kilo
✅ Wiki + UI kit sekme: roo
📋 PRD v1.0 master belge kaydedildi
🎯 Hepsi pazartesi EOD'de tamamlanacak
```

---

## Kaynaklar

- **PRD:** `AI proje v1/V10/03_mimari/02_muninn_super_admin_panel_prd_ve_yol_haritasi.md` (105 satır)
- **Mimari:** `docs/ARCHITECTURE_DECISION_HYBRID_ADMIN.md`
- **UX:** `docs/UX_UI_KURALLARI.md`
- **Vault:** `AI proje v1/V10/00-Home.md` (updated)

---

*cline tarafından hazırlandı, ben/kilo/roo üzerinde çalışacak.*

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
