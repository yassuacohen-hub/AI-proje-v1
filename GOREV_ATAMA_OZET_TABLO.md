# TEST-BLOKE-FAKTOR-ARASTIRMA-01 ÖZET TABLOSU

## Görev: API-ADMIN-AKTIVITE-LOG-13 (TEST-BLOKE-FAKTOR-ARASTIRMA-01)

### Amaç
API-ADMIN-AKTIVITE-LOG-13 tablosu (veri verisi yazma) için 3 sinyal tanımlama ve test hazırlığı.

### 3 Sinyal Tanımları

#### 1. Churn Risk Skoru (SSOT §9 K1)
- **Formül:** `sinyal = Σ(1 for g in (g_giris, g_arama, g_ai) if g >= 14)`
- **Çıktı:** `{0: "Yok", 1: "Düşük", 2: "Orta", 3: "Yüksek"}`
- **Veri Kaynağı:** `user_activity_log` tablosu (giris, arama, AI olayları)
- **Eşik:** 3 sinyal = "Yüksek" (kriz durumu)

#### 2. Müşteri Kalitesi Skoru (SSOT §9 K1)
- **Formül:** `puan = min(max(firma_ara_score, 0), 100)`
- **Veri Kaynağı:** `company_master` tablosu (firma adı, kalite skoru)
- **Eşik:** 0-100 arası puan, 0 = düşük kalite

#### 3. Kullanım Veri Analizi (SSOT §9 K1)
- **Formül:** `doğrulanmış kullanım % = (aktif kullanıcılar / toplam kullanıcılar) * 100`
- **Veri Kaynağı:** `user_activity_log` (kullanım zamanı, frekans)
- **Eşik:** 30+ % aktif kullanım = "Yüksek" (gelir potansiyeli)

### Bağımlılıklar
- `user_activity_log` tablosu (migration 0017 ile ilgili)
- `company_master` tablosu (firma verileri)
- `admin_audit` tablosu (report verileri)
- `src/company_master/schema/migrations/0017_user_activity_log.sql` (tablo yapısı)

### Test Plan
1. **Churn Risk Skoru Testi**
   - Doğru sinyal hesaplaması (≥3 sinyal → "Yüksek")
   - Doğru eşik kuralı (3 sinyal = kriz)
   - Doğru formül uygulaması

2. **Müşteri Kalitesi Testi**
   - Puan hesaplaması (0-100 arası)
   - Alt sınıf ayrımı (Düşük/Orta/Yüksek)

3. **Kullanım Analizi Testi**
   - Aktif kullanım oranı hesaplaması
   - Gelir potansiyeli değerlendirme

### Riskler
- **Bağımlılık:** `user_activity_log` tablosu migration 0017 ile ilişkili. Tablo yoksa test yapamaz.
- **Veri Kalitesi:** `company_master` tablosundaki `data_quality_score` verisi güvenilirliği sorunsuz olmalı.
- **Migration Durumu:** Migration 0017 (user_activity_log) başarıyla yapıldı (test_migration_0017.py).

### Gerekli Dokümanlar
- `Huginn Data Insights/AGENTS.md` (SSOT §9 K1, K2, K3)
- `Huginn Data Insights/plans/brief_utku_API-ADMIN-AKTIVITE-LOG-13.md` (eğer var olsaydı)
- `src/company_master/schema/migrations/0017_user_activity_log.sql`

### Kontrol Noktaları
- [ ] Churn risk skorunun doğru hesaplanması
- [ ] Müşteri kalite puanının doğru hesaplanması
- [ ] Kullanım verilerinin doğru analiz edilmesi
- [ ] Test raporunun oluşturulması
- [ ] Bulgular tablosunun oluşturulması
- [ ] Teslim (teslim) işlemi

### Değişiklikler
- `GOREV_ATAMA_OZET_TABLO.md` – bu metodu güncelleyildi.
- Test skeletileri ve raporlar oluşturulacak.
- API-ADMIN-AKTIVITE-LOG-13 için test kodu yazılacak.
