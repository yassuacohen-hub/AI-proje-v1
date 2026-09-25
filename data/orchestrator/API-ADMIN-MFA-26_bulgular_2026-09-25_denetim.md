# API-ADMIN-MFA-26 — Denetim Bulguları

**Görev:** API-ADMIN-MFA-26 — [API] MFA + hesap kilidi akışını yaz
**Tarih:** 2026-09-25
**Rol:** denetim
**Durum:** Görev `review` — teslim kabul kriterlerini karşılamıyor.

---

## Özet

Backend endpoint iskeleti ve `0019_admin_mfa.sql` migration'ı mevcut. Ancak
**login akışı MFA adımını içermiyor**, UI sekmesi yok, test dosyası yoktu ve
hesap kilidi (lockout) hiç uygulanmamış. Bu nedenle teslim "tamam" sayılamaz.

---

## Bulgular

### B-01 (Kritik) — Login akışı MFA adımı içermiyor

**Kanıt:** `web_app.py:2413-2467` (`api_admin_login_post`)
Şifre doğrulandıktan sonra doğrudan `{"token": _user_token(...)}` dönüyor;
`admin_mfa` tablosu okunmuyor, `mfa_token` üretilmiyor.

- Brief adım 3: "MFA enabled ise; `mfa_token` döndür (1 dakika geçerli)"
- Brief kabul: "- [ ] Login flow MFA step ekledi"

`/api/admin/login-mfa` (web_app.py:3610) tanımlı ama login akışı bu uca
yönlendirmediği için **hiçbir kullanıcı MFA ikinci adımına geçemez** — endpoint
ölü kod durumunda.

### B-02 (Yüksek) — MFA token'ı login token'ı yerine kullanılıyor

**Kanıt:** `web_app.py:3622-3634`
`login-mfa`, `admin_mfa_setup_tokens` tablosundan token okuyor. Bu tablo
`login-mfa` için değil **setup** akışı için tasarlanmış. Login adımı için ayrı
kısa ömürlü token/pending-login kaydı yok.

### B-03 (Yüksek) — `status` ve `disable` uçları oturum yerine istek gövdesi kullanıyor

**Kanıt:** `web_app.py:3692` → `email = "admin@huginn.local"  # placeholder`
**Kanıt:** `web_app.py:3530-3537` → `disable` e-postayı `req` gövdesinden alıyor.

İki sonuç: (a) `status` her zaman aynı (yanlış) admin'i raporlar, (b) `disable`
çağıran, gövdede başka bir adminin e-postasını verip şifresini bilirse
**başka hesabın MFA'sını kapatabilir**. Session (`_get_session`) kullanılmalı.

### B-04 (Yüksek) — Hesap kilidi (lockout) uygulanmamış

**Kanıt:** kod tabanında `lockout`, `failed_attempts` için eşleşme yok.
Görev başlığı "MFA + hesap kilidi akışını yaz" olmasına rağmen ardışık hatalı
MFA/şifre denemesinde hesap kilitleme yok; yalnızca `_auth_rate_guard` IP
limiti var.

### B-05 (Orta) — UI sekmesi yok

**Kanıt:** `web_dashboard/tabs/admin_panel.py` içinde `render_mfa*` yok;
`web_dashboard/tabs/admin_auth.py` içinde MFA setup wizard yok.
Brief adım 4 ve "- [ ] UI sekmesi setup wizard gösteriyor" karşılanmıyor.

### B-06 (Düşük) — Bağımlılıklar requirements'ta yoktu (bu denetimde eklendi)

`pyotp` ve `qrcode` `requirements-app.txt` içinde tanımlı değildi; `web_app.py:28-29`
bunları zorunlu import ediyor. **Bu denetimde eklendi** (`pyotp>=2.9.0`,
`qrcode[pil]>=7.4.2`).

### B-07 (Düşük) — Test dosyası yoktu (bu denetimde eklendi)

Brief "Test: `tests/test_mfa.py` (3 test)" diyordu; dosya diskte yoktu.
**Bu denetimde eklendi:** `tests/test_mfa.py` (3 test, 3/3 yeşil) — backup kod
biçimi, hash/doğrulama round-trip, bozuk JSON dayanıklılığı.

---

## Sonuç

| Kriter | Durum |
|--------|-------|
| `admin_mfa` migration | ✅ var (`0019_admin_mfa.sql` + down) |
| MFA setup/verify/backup endpoint'leri | ✅ var |
| Login akışı MFA adımı | ❌ yok (B-01/B-02) |
| Session bazlı status/disable | ❌ istek gövdesi/placeholder (B-03) |
| Hesap kilidi (lockout) | ❌ yok (B-04) |
| UI sekmesi | ❌ yok (B-05) |
| Testler | ✅ 3/3 eklendi (B-07) |
| Requirements | ✅ eklendi (B-06) |

**Karar:** Görev `review` durumunda kalmalı; B-01…B-05 kapatılmadan `done`
verilemez. Bu bulgular ilgili görev sahibine (üretim rolü) ve orkestratöre
bildirilmelidir.
