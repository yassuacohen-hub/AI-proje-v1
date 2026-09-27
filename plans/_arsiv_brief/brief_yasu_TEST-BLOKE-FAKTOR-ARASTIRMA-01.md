# BLOKE-FAKTOR-TEST-ARASTIRMA-01 — İlk 5 Görev Engel Analizi

**Ajan:** Yasu  
**Aciliyet:** P0 (Sprint 2 hızlandırma)  
**Süre:** 3 saat  
**Tür:** Test + Araştırma (bağımlı olmayan paralel)

## Özet

API-ADMIN-AKTIVITE-YAZ-14 başında 5 görev birbirine bağlı (zincir):
- API-14 → (API-16, UI-20, API-21 paralel) → UI-22

Yasu'nun görevi: **Her 5 görevin test hazırlığını, bağımlılık risklerini ve implementasyon blokeyleri araştırması.**

## Görevler (Bağımlılık Sırası)

### 1️⃣ API-ADMIN-AKTIVITE-YAZ-14 (P0, 2s)
- Brief: [`plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14.md`](../plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14.md)
- **Blokaj:** VERI-ADMIN-AKTIVITE-LOG-13 done ✅ → açık
- **Test hazırlığı:** 
  - Şu test dosyaları var mı? `tests/test_api_aktivite.py`
  - User, search, AI event log fonksiyonları mock'lanabiliyor mu?
  - Bağımlılık: `src/company_master/schema/migrations/0017_user_activity_log.sql` mevcut mi? ✅

### 2️⃣ API-ADMIN-CHURN-3SINYAL-16 (P1, 2s)
- Brief: [`plans/brief_utku_API-ADMIN-CHURN-3SINYAL-16.md`](../plans/brief_utku_API-ADMIN-CHURN-3SINYAL-16.md)
- **Blokaj:** API-14 ✅ (activity log yazımı gerekli)
- **Test hazırlığı:**
  - [`src/company_master/churn.py`](../../src/company_master/churn.py):40 `risk_etiketi()` mevcut, bozulmayacak
  - Yeni formül: 3 sinyal nedir? (Retention, DAU trend, feature kullanımı?)
  - Mock data: 50+ user, 1-30 gün veri, pozitif/negatif örnekler

### 3️⃣ UI-ADMIN-ARAMA-BOSLUK-20 (P2, 2s)
- Brief: [`plans/brief_utku_UI-ADMIN-ARAMA-BOSLUK-20.md`](../plans/brief_utku_UI-ADMIN-ARAMA-BOSLUK-20.md)
- **Blokaj:** API-14 ✅ (aktivite log → arama olayları gerekli)
- **Test hazırlığı:**
  - Normalize → frekans → esik>=3 (3+ aynı sorgu)
  - Test: 100+ arama, 20+ boş sonuç, frekans dağılımı
  - Semantik kümeleme bu turda YOK ✅

### 4️⃣ API-ADMIN-SUPHELI-AKTIVITE-21 (P2, 3s)
- Brief: [`plans/brief_utku_API-ADMIN-SUPHELI-AKTIVITE-21.md`](../plans/brief_utku_API-ADMIN-SUPHELI-AKTIVITE-21.md)
- **Blokaj:** API-14 ✅ (aktivite log → sinyal gerekli)
- **Test hazırlığı:**
  - 3 sinyal: nedir? (Failed login × 5, Password change × 2, API key rotation × 1?)
  - KAPSAM: sadece tespit — action (kilit, email) DAHIL DEĞİL ✅
  - Test: false positive rate <10% (normal aktivite × 100, şüpheli × 50)

### 5️⃣ UI-ADMIN-UPSELL-22 (P2, 2s)
- Brief: [`plans/brief_utku_UI-ADMIN-UPSELL-22.md`](../plans/brief_utku_UI-ADMIN-UPSELL-22.md)
- **Blokaj:** API-16 (churn sinyalleri gerekli)
- **Test hazırlığı:**
  - Kural: doygunluk>=0.85 AND churn in {Yok,Düşük} AND büyüme>0
  - Girdi (credit_ledger) DB'de mevcut ✅
  - Mock: 50 müşteri, 10 upsell aday, 15 negatif, 25 boundary

## Yasu'nun Çıktılar

### ✅ Test Hazırlığı (per görev)
- [ ] **API-14:** Mock data, test fonksiyon iskeleti, bağımlılık ok?
- [ ] **API-16:** 3 sinyal formülü araştırma, mock data, test iskeleti
- [ ] **UI-20:** Frekans normalizasyon, test veri setleri
- [ ] **API-21:** Sinyal tanımları, false positive test planı
- [ ] **UI-22:** Upsell kural test planı, sınır değerleri

### 📋 Engel Raporu
```
Görev | Blokaj | Durum | Risk | Not
------|--------|-------|------|-----
API-14| VERI-13| ✅ açık | Düşük | Teslim: migration 0017 done
API-16| API-14 | ⏳ API-14'den sonra | Düşük | Paralel test prep ok
UI-20 | API-14 | ⏳ API-14'den sonra | Düşük | Normalize mantığı net
API-21| API-14 | ⏳ API-14'den sonra | Orta | 3 sinyal tanımı + FP rate kritik
UI-22 | API-16 | ⏳ API-16'den sonra | Düşük | Kural basit, girdi mevcut
```

## Teslim Kriterleri

1. **Test dosyaları:** 5 görevin tümü için `tests/test_*.py` iskeleti + mock data
2. **Engel listesi:** API-14 başlayabilir, paralel görevler prep hazır
3. **Araştırma notu:** 3 sinyal tanımları (churn, şüpheli aktivite, upsell) — Utku'nun kodu için
4. **Risk özeti:** False positive, veri kalitesi, bağımlılık şefafi

## Bağlantılar

- **Sprint 2 planlama:** Beklemede 8 görev, ilk 5'i bu görev açıyor
- **ADMIN-KIT:** SSOT §7 izlenebilirlik (D-196)
- **Simulasyon:** `scripts/gorev_kutusu.py cmd_simulasyon` — test hazırlığı simüle et

## D-57 Adlandırma

✅ Türü (BLOKE-FAKTOR): Blokaj faktörü araştırması  
✅ Alanı (TEST-ARASTIRMA): Test + araştırma  
✅ Sıra (01): İlk batch  

---
**Durum:** Yeni task → ready to assign  
**Sahip:** Yasu  
**Tetik:** Beklemede 8 görev analiziyle başla
