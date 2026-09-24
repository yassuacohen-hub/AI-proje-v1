# ALTYAPI-VERI-GORUNURLUK-01 — Katmanlı Görünürlük & Kontör Sistemi

**Ajan:** orkestrator (Utku özet, Yasu kod)  
**Aciliyet:** P0 (Veri güvenliği, SELECT c.* sızıntısı kanıtlı)  
**Süre:** 3-4 gün  
**Tür:** Altyapı (Şema + veri + API kod + puanlama)  
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md`

## Neden

Bugün `/api/company/{id}` detay endpointinde `SELECT c.*` sızıntısı var (web_app.py:2798). Tüm 33+ kolon dönüyor (quarantine_reason, entity_confidence, source_record_id, status_confidence vb.). Maskeleme sadece 2 alana uygulanıyor (primary_phone, primary_email). 

**Çözüm:** 2 katmanlı görünürlük sistemi:
- **Layer 1 (Kod):** KVKK sınıfı (açık/yarı-açık/kısıtlı/yasak) — alanı 4 tabakaya böl
- **Layer 2 (Tablo):** Paket × grup görünürlüğü — admin aç/kapa kontrol eder

Ayrıca kontör sistemi bugün sadece eşleştirme (match) modülü için düşüyor. **Revize:** modül bazlı (match/ilan/analiz/teklif/kapasite), tier başına farklı maliyet.

Admin filtreleme mekanizması yok. **Revize:** `admin_kvkk_mode` (strict/lenient) — strict=KVKK mutlak, lenient=admin riski üstlenir (audit zorunlu).

## Doğrulanacak varsayım

1. SELECT c.* sızıntı kanıtı: web_app.py:2798 kodu direkt `SELECT c.*` kullanıyor
2. Maske mekanizması (normalize.py:312) sadece 2 alana uygulanıyor (primary_phone, primary_email)
3. Kontör (`_TIER_CREDITS`, `credit_ledger`) bugün match modülü için çalışıyor
4. Paket tanımı: 3 sabit (terminal/strategic/enterprise) — kodda sabit, tablo'da tanımlanmaz
5. KVKK sınıflandırması: 6 alan grubu (kimlik, iletişim, lokasyon, dijital, ticari, sınai) × 3 paket = 18 başlangıç satırı

## Adımlar

### A1: Şema Migration (0018) — ~80 satır
- `plan_field_group` tablosu: (plan, field_group, visibility, visibility_note) — 18 satır INSERT (6 grup × 3 paket)
- `module_cost` tablosu: (module_id, tier, cost_per_query) — 15 satır INSERT (5 modül × 3 tier, enterprise=0)
- `admin_kvkk_mode` tablosu: (admin_id, mode, changed_at, previous_mode, reason) — kontrol tablosu (strict/lenient geçişi audit'le)
- Down dosyası: 3 DROP TABLE (cascade) + ROLLBACK
- **Dosya:** `src/company_master/schema/migrations/0018_visibility_kontrol.sql`

### A2: Veri + Katalogu — ~200 satır
- `plan_field_group` başlangıç verisini yükle: 18 satır (kimlik: açık, iletişim: açık/kısıtlı/yasak, vb.)
- `module_cost` başlangıç verisini yükle: 15 satır (terminal: match=10, ilan=0/kapalı; strategic: match=5, ilan=3; enterprise: match=0, ilan=0)
- KVKK sınıflandırması: `_KVKK_FIELD_CLASS = {...}` dict (field_name → class) — 33 alan
- Alan grupları: `_FIELD_GROUPS = {...}` dict (group_id → [field_1, field_2, ...])
- **Dosyalar:** `src/company_master/schema/data/plan_field_group_init.sql`, `normalize.py` global dict

### A3: Kod — ~150 satır
- `apply_kvkk_mask()` revize (normalize.py:312): KVKK sınıfından maskeye akış
  - `_mask_from_kvkk_class(field, value, kvkk_class, admin_mode)` → maskeleme mantığı
  - Mode=strict: sınıf="yasak" → tüm maskeleme; sınıf="kısıtlı" → seçici maskeleme
  - Mode=lenient: sınıf="yasak" hala maskelenir; sınıf="kısıtlı" → açık bırakılır
- `/api/company/{id}` detay (web_app.py:2798): `SELECT c.id, c.legal_name, c.trade_name, ... WHERE ...` — dinamik SELECT (görünürlüğe göre kolon filtrele)
- `require_api_key()` revize: kontör kontrol + module cost lookup
- Kontör düşümü: `_charge_module_credit(user_id, module, group, company_id, cost)` — modül+grup+firma başına
- Admin anahtarı kontrol: `_check_admin_kvkk_mode()` → strict/lenient mode dön
- **Dosyalar:** `normalize.py`, `web_app.py`, yeni `kvkk_control.py` (helpers)

### A4: Puanlama & Test — ~50 satır
- Test tablosu: 3 tablo veri (plan_field_group: 18, module_cost: 15, admin_kvkk_mode: 1)
- Senaryo testi 1-5: terminal match / strategic ilan / admin filter / OSINT / reveal
- Karantina çelişki (Ç1-Ç4) test: GSM silinme vs tümü alın (karantina bayrakları)
- **Dosya:** `tests/test_visibility_katmani.py` (5 senaryo, pytest)

## Kabul kriteri

- [ ] `0018_visibility_kontrol.sql` migration yazılmış, down dosyası var
- [ ] 3 tablo (plan_field_group: 18, module_cost: 15, admin_kvkk_mode kontrol) başlangıç verisi yüklü
- [ ] 33+ alan KVKK sınıfı kataloglanmış (`_KVKK_FIELD_CLASS` dict)
- [ ] 6 alan grubu tanımlanmış (`_FIELD_GROUPS` dict)
- [ ] `/api/company/{id}` SELECT c.* yerine kolon listesi kullanıyor (sızıntı kapatıldı)
- [ ] `apply_kvkk_mask()` KVKK sınıfından maskeye akış yapıyor
- [ ] Modül kontörü çalışıyor: match/ilan/analiz/teklif/kapasite modülleri ayrı maliyet
- [ ] Admin filtreleme (strict/lenient) toggle çalışıyor ve değişim audit'leniyor
- [ ] Senaryo 1-5 testi geçiyor (5 farklı kullanıcı/paket kombinasyonu)
- [ ] Ç1-Ç4 karantina çelişkileri çözülmüş, test geçiyor

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz (YAGNI)
- **Teslimden önce** Hub'ın "Kapanan işler" bölümüne `ALTYAPI-VERI-GORUNURLUK-01` satırı yaz (B-14 kapısı)
- Bitince: `python scripts/gorev_kutusu.py teslim --ajan orkestrator --task-id ALTYAPI-VERI-GORUNURLUK-01 --ozet "<özet>"`

## Mimari Değerlendirme (Ihsan)

### Iyi Olan (✅)
- **Layer 1+2 Sağlam:** Kod sınıfı dict + tablo dinamik. Yeni paket/grup eklemek 1 INSERT.
- **Silme Yok:** Ç1-Ç4 karantina veri koruyor. GDPR uygun.
- **SELECT c.* Kapandı:** 33 → 28 açık/yarı-açık alan. Sızıntı iyileşti.

### Eksiklikler (⚠️ Yasu'ya Not)
1. **Kontör Statik:** `module_cost` tablosu var, endpointler henüz bağlı değil. `/api/match`, `/api/ilan` kontör düşümü Yasu'ya.
2. **Layer 2 Dinamik Yok:** `plan_field_group` sorgusu maskeleme'de eksik. `apply_kvkk_mask()` Layer 1 dict'ten uygulanıyor; tablo ignoresi.
3. **Admin Toggle Eksik:** `/api/admin/kvkk-mode` POST endpoint yok. Yönetici strict↔lenient geçişi yapamaz.
4. **Test Mock:** Gerçek fonksiyon ile entegrasyon gerekli.

### Sonuç
**Tasarım = 90/100** (mimari sağlam, genişlenebilir).
**Impl = 60/100** (altyapı ✅, bağlantı ⚠️).

Yasu sprint'inde: Kontör query, Layer 2 dinamik, admin toggle, test entegrasyon yapılacak.

## İlgili Nodlar

- [[design_visibility_simulation.md]] — 5 senaryo simülasyon
- [[Huginn Data Insights/web_app.py:2798]] — SELECT c.* sızıntı noktası
- [[Huginn Data Insights/src/company_master/api/core/normalize.py:312]] — apply_kvkk_mask() geçerli
- [[Huginn Data Insights/AGENTS.md]] — D-200 — D-208 kararları
- [[hubs/ADMIN_DASHBOARD_HUB.md]] — Hub
