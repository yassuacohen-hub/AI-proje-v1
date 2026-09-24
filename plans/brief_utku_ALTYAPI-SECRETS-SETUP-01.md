# ALTYAPI-SECRETS-SETUP-01 — Credential Vault Kurulumu

**Ajan:** Utku  
**Aciliyet:** P0 (Sunucu geçişi hazırlık)  
**Süre:** 2 saat  
**Tür:** Altyapı (Secrets yönetimi)  
**Kilitli dosya:** `.env.example`  
**Bağımlılık:** yok  
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

## Neden
SSOT §8.1 A5 (gizli yönetim) ve D-195 (credential management kararı) gerektirir. Prod sunucusuna geçiş öncesinde güvenli secrets altyapısı şart.

## Doğrulanacak varsayım
- `.env.example` dosyası repoya commit edilecek, asla `.env` commit edilmeyecek
- API anahtarları için dummy değerler: `GROQ_API_KEY=sk-...`, `NINEROUTER_URL=...`
- DB bağlantısı formatı: `DATABASE_URL=postgresql://user:pass@host:port/db`
- Admin şifresi: `ADMIN_PASSWORD=***OKUNMAZ***` (placeholder)
- Oturum gizli: `SESSION_SECRET=...` (rastgele üretilir)
- Debug modu: `DEBUG=false` (prod'da kapalı)
- Vault backend: başlangıçta `.env.vault` (local), prod'da AWS Secrets Manager / HashiCorp Vault

## Adımlar
1. `.env.example` template dosyasını yaz (repo kökünde)
2. `.env.vault` local template yaz (.gitignore içinde)
3. Rotasyon cron job scripti yaz: `scripts/rotate_secrets.py`
4. Test dosyası yaz: `tests/test_secrets_rotation.py`
5. Config test scriptini güncelle: `scripts/config_test.py` (missing/invalid key detection)
6. Fake credentials log'ta `***REDACTED***` görünüyor mu test et

## Kabul kriteri
- [ ] `.env.example` repo kökünde var ve commit edilebilir durumda
- [ ] `.env.vault` local template var ve .gitignore'da
- [ ] `scripts/rotate_secrets.py` çalışıyor (90 gün rotasyon mantığı)
- [ ] `tests/test_secrets_rotation.py` en az 3 test geçiyor
- [ ] `scripts/config_test.py` eksik/hatalı key tespit ediyor
- [ ] Loglarda gerçek credential yerine `***REDACTED***` görünüyor

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne `<TASK_ID>` satırı yaz (B-14 kapısı).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id ALTYAPI-SECRETS-SETUP-01 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
- [[hubs/ADMIN_DASHBOARD_HUB]]