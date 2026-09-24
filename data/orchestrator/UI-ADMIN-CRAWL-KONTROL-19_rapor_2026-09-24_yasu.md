# UI-ADMIN-CRAWL-KONTROL-19 — Crawl Tetikle/Durdur UI Raporu

**Görev ID:** UI-ADMIN-CRAWL-KONTROL-19  
**Sahip:** yasu  
**Tarih Tamamlandı:** 2026-09-24  
**Durum:** ✅ DONE  

---

## 📋 Özetim

Crawl işlemlerini tetikle/durdur UI'ı operatör kontrol paneline eklendi. Iki adımlı onay + audit log.

### Yapılan İşler

1. **UI Sekmesi:** `web_dashboard/tabs/webhook_monitor.py`
   - `render_crawl_control_tab()` — Yeni sekme: "🕷️ Crawl Kontrol"
   - ENV durumu (salt okunur checkbox: CRAWL_ENABLED)
   - **Tetikle butonu** (durumu: beklemede/başarısız/durduruldu)
   - **Durdur butonu** (2 adımlı onay — yıkıcı işlem)
   - Durum göstergesi (ikon + metin): çalışıyor/beklemede/hata/durduruldu
   - Admin rol kontrolü (session_state.admin_email)

2. **Sabitler:** `webhook_monitor.py`
   ```python
   CRAWL_STATUS_WAITING = "beklemede"
   CRAWL_STATUS_RUNNING = "çalışıyor"
   CRAWL_STATUS_FAILED = "başarısız"
   CRAWL_STATUS_STOPPED = "durduruldu"
   ```

3. **Yardımcı Fonksiyonlar:**
   - `_crawl_is_enabled()` — ENV kontrol
   - `_log_crawl_action(user_id, action, status)` — Audit log (placeholder)

4. **Testler Geçti:** 5/5 ✅
   ```
   test_crawl_control_ui_render ........ PASS
   test_crawl_start_button_enabled .... PASS
   test_crawl_stop_button_two_step .... PASS
   test_crawl_status_indicator ........ PASS
   test_admin_role_check .............. PASS
   ```

5. **Notlar:**
   - Audit log placeholder: TODO yorumuyla `API-ADMIN-SUPHELI-AKTIVITE-21` referansı
   - AgGrid kullanılmadı (SSOT C6:309 yasak) ✅
   - .env.example'a `CRAWL_ENABLED` eklendi

---

## ✅ Kabul Kriteri

- [x] `render_crawl_control_tab()` yazıldı
- [x] ENV durumu gösteriyor
- [x] Tetikle butonu duruma göre aktif/pasif
- [x] Durdur butonu 2 adımlı onay
- [x] Status göstergesi (4 durum)
- [x] Admin kontrolü
- [x] Audit log placeholder (TODO)
- [x] AgGrid yasak uygulanmış
- [x] Testler geçti (5/5)
- [x] Brief uyumlu

---

## 📊 Matris İlerleme

| Kriter | Durum | Kanıt |
|--------|-------|-------|
| UI Render | ✅ OK | `webhook_monitor.py:render_crawl_control_tab()` |
| Status Icons | ✅ 4 type | waiting/running/failed/stopped |
| Two-Step Confirm | ✅ Yes | Durdur butonu confirmation dialog |
| Admin Check | ✅ Yes | `session_state.admin_email` kontrol |
| Audit Log | ⏳ TODO | Placeholder; API-21 bağımlılığı |
| AgGrid | ✅ None | SSOT C6 uyumlu |
| Test Coverage | ✅ 5/5 | `test_web_dashboard_tabs.py:45-89` |
| SSOT Referans | ✅ Yes | `gorev_taslagi.md:272,373,421` |
| Brief Uyum | ✅ Yes | `brief_utku_UI-ADMIN-CRAWL-KONTROL-19.md` |

---

## 🔗 İlgili Nodlar

- [[Huginn Data Insights/web_dashboard/tabs/webhook_monitor.py]] — Uygulama
- [[Huginn Data Insights/tests/test_web_dashboard_tabs.py#45-89]] — Test suite
- [[Huginn Data Insights/data/orchestrator/gorev_taslagi.md#272]] — SSOT A8 ref
- [[Huginn Data Insights/data/orchestrator/gorev_taslagi.md#373]] — SSOT G8 ref
- [[Huginn Data Insights/AGENTS.md#D-196]] — Task board tracking
- [[Huginn Data Insights/plans/brief_utku_API-ADMIN-SUPHELI-AKTIVITE-21.md]] — Audit log bağımlılığı

---

**Durumu:** Task board'da `aktif` → `done` geçilecek.

**Not:** Audit log gerçek implementasyonu `API-ADMIN-SUPHELI-AKTIVITE-21` tamamlandıktan sonra `_log_crawl_action()` güncellenecek.
