# UI-ADMIN-FEATURE-FLAG-25 — Feature Flag Yönetim Paneli

**Sahip:** orkestrator (ihsan)  
**Öncelik:** P2  
**Durum:** 🟡 Başlama Öncesi  
**Tarih Oluşturuldu:** 2026-09-24  

---

## 🎯 Amaç

Admin paneline feature flag yönetim sekmesi ekle. Özellikler:
- Flag listesi (aktif/pasif + açıklama)
- Toggle UI (switch componentli)
- Geçmiş kayıtları görüntüle (kim, ne zaman, eski→yeni değer)
- Rol kontrolü (sadece admin)

---

## 📋 Adımlar

1. `web_dashboard/tabs/admin_panel.py` açarak `render_feature_flags_tab()` fonksiyonu yaz
   - Streamlit tabı: "🚩 Feature Flags"
   - Session state'ten aktif flags yükle (dict: `{"flag_name": bool, ...}`)

2. `web_app.py`'ye endpoint yaz: `POST /api/admin/feature-flags`
   - Request: `{flag_name: str, new_value: bool}`
   - Response: `{ok: bool, previous: bool, new: bool, changed_at: str}`
   - Audit log yaz (admin_id, flag_name, eski→yeni, timestamp)

3. Tablo göster: flag_name | status (✅/❌) | açıklama | son değişiklik (kimin, ne zaman)

4. Test yaz: `tests/test_feature_flags.py`
   - Toggle on/off test
   - Audit trail test
   - Permission test (non-admin reject)

---

## ✅ Kabul Kriteri

- [ ] `render_feature_flags_tab()` çalışıyor ve flag listesi gösteriyor
- [ ] Toggle butonu `/api/admin/feature-flags` POST yapıyor
- [ ] Audit trail tablo görünüyor (admin_id, flag_name, changed_at, old→new)
- [ ] Non-admin erişim reddediliyor (403)
- [ ] Testler geçiyor: 3/3 test passed
- [ ] Brief belirtilen nodlara link yapıyor

---

## 📌 İlgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — Admin pano merkezi
- [[Huginn Data Insights/AGENTS.md]] — D-196 (task board), D-200+ (karar defteri)
- [[Huginn Data Insights/web_dashboard/tabs/admin_panel.py]] — Sekme işlemeciliği
- [[Huginn Data Insights/web_app.py]] — API endpoint framework

---

**Ponytail:** Feature flag persistence varsayılan memory-based session state'tir. Prod'da Redis/DB backing eklenebilir (persistence.py/redis_cache).

**Karar Referansı:** [[Huginn Data Insights/AGENTS.md#D-207]] — Admin mode toggle pattern; aynı audit pattern uygulanacak.
