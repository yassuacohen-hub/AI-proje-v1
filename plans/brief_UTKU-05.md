# GÖREV BRIËFI: UTKU-05 — Kullanıcı Kimlik Doğrulama - Token Yenileme

**Atanan:** utku  
**Öncelik:** P0  
**Deadline:** 2026-09-30T23:59:59Z  
**Bağımlılıklar:** yok

## Özet
JWT token yenileme mekanizması uygula. Refresh token ile access token yenile, token expiry kontrol et, blacklist sistemi kur.

## Kabul Kriterleri
1. Token refresh endpoint yazılmalı (src/auth/token_refresh.py)
2. Token blacklist DB tablosu oluşturulmalı
3. Test coverage ≥85%

## Kaynaklar (SSOT)
- src/auth/token_refresh.py
- JWT RFC 7519

## İmplantasyon Notları
- PyJWT kütüphanesi kullan
- Refresh token rotation
- Secure cookie storage

## Proof-of-Work
File/Output: src/auth/token_refresh.py + integration tests + DB migration
