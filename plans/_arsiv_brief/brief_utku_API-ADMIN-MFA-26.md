# API-ADMIN-MFA-26 — Multi-Factor Authentication (MFA) Sistem

**Sahip:** utku (ihsan)  
**Öncelik:** P2  
**Durum:** 🟡 Başlama Öncesi  
**Tarih Oluşturuldu:** 2026-09-24  

---

## 🎯 Amaç

Admin giriş sistemine MFA desteği ekle (TOTP tabanlı):
1. Admin profil sekmesinde MFA setup sayfası
2. QR kod göster (secret key için)
3. Doğrulama kodu ile aktifleştir
4. Login sayfasında MFA kodu isteme adımı
5. Backup codes üretimi

---

## 📋 Adımlar

1. Veritabanı tablosu ekle: `admin_mfa`
   ```
   admin_id | secret_key | enabled | backup_codes | created_at | last_used_at
   ```

2. `web_app.py`'ye endpoint yaz:
   - `POST /api/admin/mfa/setup` — secret key üret, QR kod oluştur
   - `POST /api/admin/mfa/verify` — TOTP kodu doğrula, aktifleştir
   - `POST /api/admin/mfa/disable` — MFA kapat (existing password gerekli)
   - `GET /api/admin/mfa/backup-codes` — backup codes regenerate

3. Login flow güncelle (`api_admin_login_post`):
   - MFA enabled ise; `mfa_token` döndür (1 dakika geçerli)
   - 2. adım: `POST /api/admin/login-mfa` {mfa_token, code} → auth token

4. UI ekle (`web_dashboard/tabs/admin_panel.py`):
   - "🔐 MFA Ayarları" sekmesi
   - Setup wizard (QR + backup codes)
   - Status göstergesi (enabled/disabled)

5. Test: `tests/test_admin_mfa.py`
   - Setup & verify flow
   - Backup code kullanımı
   - Invalid code reject
   - Session timeout (1 dakika)

---

## ✅ Kabul Kriteri

- [ ] `admin_mfa` tablosu oluşturuldu ve migration'ı yok
- [ ] `/api/admin/mfa/setup` QR kod döndürüyor
- [ ] `/api/admin/mfa/verify` TOTP kodunu doğruluyor
- [ ] Login flow MFA step ekledi
- [ ] Backup codes üretiliyor (8 kod, 4 karakter)
- [ ] UI sekmesi setup wizard gösteriyor
- [ ] Testler geçiyor: 7/7 test passed
- [ ] TOTP library (pyotp) requirements.txt'e eklendi

---

## 📌 İlgili Nodlar

- [[Huginn Data Insights/AGENTS.md#D-205]] — Admin authentication pattern
- [[Huginn Data Insights/web_app.py#2294-2348]] — Admin login endpoint
- [[Huginn Data Insights/web_dashboard/tabs/admin_panel.py]] — Admin profil sekmesi
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]] — Admin güvenlik

---

**Ponytail:** MFA enforcement (tüm admins zorunlu) değil; opsiyonel per-user. Prod'da global policy eklenebilir (admin_policies tablo).

**Uyarı:** Secret key şifreleme gerekli (env: MFA_SECRET_CIPHER_KEY). Production'da Vault entegrasyonu.

**Karar Referansı:** [[Huginn Data Insights/AGENTS.md#D-205]] — Admin auth hardening D-205 kapsamında.
