# Sprint Planı: Ajan Chat Sistemi + Görev Atama

**Tarih:** 2026-09-24 19:30  
**Yazan:** Orchestrator (Analiz + Plan)  
**Durum:** Hazır

---

## 1. Teslim Alınan Görevler

### ✅ Yasu Teslim (TEST-BLOKE-FAKTOR-ARASTIRMA-01)

**Özet:** İlk 5 test görevinin (API-14, API-16, UI-20, API-21, UI-22) hazırlığı ve engel analizi.

| Görev | Durum | Blokaj | Risk | Not |
|-------|-------|--------|------|-----|
| API-14 | ✅ Başlayabilir | VERI-13 (✅ done) | Düşük | Test dosyası yok - oluşturmak gerek |
| API-16 | ⏳ Sonra | API-14 | Düşük | Churn sinyalleri basit |
| UI-20 | ⏳ Sonra | API-14 | Düşük | Search gap normalizasyonu net |
| API-21 | ⏳ Sonra | API-14 | **Orta** | `admin_audit.py` eksik - riskli |
| UI-22 | ⏳ Sonra | API-16 | Düşük | Upsell kuralı basit |

**Teslim Seviyeleri:**
- NINEROUTER-IMAGE-GEN-01: ✅ tamamlandı (skill kayıtlı)
- ALTYAPI-GROQ-KEY-DOGRULA-01: ❌ API key eksik (dış bağımlılık)

---

### ✅ Utku Teslim (DASH-UX-02a-SECTIONS + Review)

**DASH-UX-02a-SECTIONS (P1):** Navigation tesseleri 96/96 ✅ geçti, fonksiyon adı düzeltildi.

**Active Task Board Durum:**
- ✅ VERI-ADMIN-AKTIVITE-LOG-13 (done)
- ✅ UI-ADMIN-DAU-17 (done)
- ⏳ API-ADMIN-AKTIVITE-YAZ-14 (bekliyor)
- ⏳ API-ADMIN-CHURN-3SINYAL-16 (bekliyor)
- ⏳ DOC-ADMIN-DURUM-SENKRON-15 (bekliyor)
- ⏳ API-ADMIN-KAYNAK-SAGLIK-18 (bekliyor)

---

## 2. Chat Sistemi Kullana Alınması Planı

**Hedef:** Tüm ajanlar (UTKU, YASU, İHSAN, ORKESTRATOR) chat'e görev sorunlarını yazabilsin.

### 2.1 Aktif Kullanım Stratejisi

**Kimler yazacak:**
- 🟦 **UTKU** → API/UI/VERİ görevlerindeki blokajlar, test durumu
- 🟨 **YASU** → Araştırma bulgularındaki risk + test hazırlığı
- 🟧 **İHSAN** → Altyapı sorunları (migration, key, lock)
- 🟪 **ORKESTRATOR** → Görev koordinasyon, bağımlılık çözmesi

**Kural (Chat Gönderen → Alıcı):**
- Gönderen sorunun bulunduğu ajan (api yazıyorsa UTKU, altyapı yazıyorsa İHSAN)
- Alıcı sorunun çözülebileceği ajan (ödev başında bildirilir)
- Örnek: "UTKU → ORKESTRATOR" = UTKU API yazarken sorun, ORKESTRATOR çöz

### 2.2 Zorunlu Alan: Önem Derecesi

Tüm mesajda **Önem Derecesi** (renkli ikon gösterilir):
- 🔴 **Kritik** → Blokaj 24h+ (sprint sona kalmadı)
- 🟠 **Yüksek** → Blokaj 6-24h (yarın teslim)
- 🟡 **Orta** → Blokaj <6h ama çözmesi net (test tanımında)
- 🟢 **Düşük** → Info, bilgi paylaşımı

### 2.3 Görev Sorusu Yazım Formatı (Opsiyonel Şablon)

```
**Görev:** [GÖREV-ID]
**Gönderen → Alıcı:** [AJAN] → [AJAN]
**Sorun:** [1-2 cümle, teknik]
**Etkisi:** [Hangi görevler bloklanmış?]
**Öner:** [Hızlı çözüm varsa]
```

Örnek:
```
**Görev:** API-14
**Gönderen → Alıcı:** UTKU → İHSAN
**Sorun:** 0017_user_activity_log migration test'te NULL kontrol hatasında.
**Etkisi:** API-14, API-16, UI-20, API-21, UI-22 (5 görev bloklanmış)
**Öner:** Migration CHECK clause'u sadece client-side validate, DB trigger ekle.
```

---

## 3. Acil Pano Görevleri (Bağımlılığa Göre Atama)

**Öncelik:** Bağımlı olan görevleri **önce** serbest bırakacak görevleri tamamla.

### Faz 1: Utku (Blokajı Aç)

**P0 — Zorunlu (hemen başlasın):**
1. ✅ **VERI-ADMIN-AKTIVITE-LOG-13** (done) ← Başta tamamlandı
2. **API-ADMIN-AKTIVITE-YAZ-14** (2s) ← **Şu an başlasın**
   - web_app.py: giriş/arama/AI olaylarını log'a yaz
   - Brief: plans/brief_utku_API-ADMIN-AKTIVITE-YAZ-14.md
   - Blokaj açacağı görevler: API-16, UI-20, API-21 (3 görev)

**P1 — Başla ama seri olmamalı:**
3. **API-ADMIN-CHURN-3SINYAL-16** (2s, sonra) ← API-14 bitsin
4. **UI-ADMIN-DAU-17** (done)
5. **DOC-ADMIN-DURUM-SENKRON-15** (1s) ← Paralel olabilir
6. **API-ADMIN-KAYNAK-SAGLIK-18** (2s) ← Paralel olabilir (bağımlılık yok)

---

### Faz 2: Yasu (Test + Hazırlık)

**Şu an paralel yapabilir (API-14 bitişini beklemiyor):**
- Test dosyaları oluştur (test_api_aktivite.py, test_churn.py, etc.)
- Mock data hazırlığı
- API-21 riskinde `admin_audit.py` prototipi (İHSAN'a bildir)

**Blokajı Çözmek İçin İHSAN'a Yazacağı Sorun:**
- API-21 (admin_audit.py): 3 sinyal fonksiyonunun tanımı (Orta risk)

---

### Faz 3: İHSAN (Altyapı)

**Blokajlar:**
- 🔴 **GROQ_API_KEY eksik** (Yasu raporu) — Console.groq.com'dan key al
- 🟡 **admin_audit.py prototipi** (API-21 için) — 3 sinyal fonksiyonu

---

## 4. Bağımlılık Haritası

```
VERI-13 ✅
  ↓
API-14 (✅ BAŞLA ŞIMDI)
  ├─→ API-16 (sonra)
  ├─→ UI-20 (sonra)
  ├─→ API-21 (sonra, admin_audit.py bekleniyor)
  └─→ UI-22
       ↓ (UI-22 API-16'ya bağlı)
       API-16 ✅

Paralel (bağımlılığı yok):
  - DOC-15
  - API-18
  - İHSAN altyapı görevleri
```

---

## 5. Iş Bölüşümü: UTKU + YASU

### Utku (API/UI Yazma)

| Görev | Durum | Başla | Teslim |
|-------|-------|-------|--------|
| API-14 | ⏳ Şu an | Hemen | 1 saat |
| API-16 | ⏳ Sonra | API-14 +0.5h | 1 saat |
| API-18 | ⏳ Paralel | Hemen | 1 saat |
| DOC-15 | ⏳ Paralel | Hemen | 0.5 saat |
| **TOTAL** | | | **3.5 saat** |

### Yasu (Test + Araştırma)

| Görev | Durum | Başla | Bitir |
|-------|-------|-------|-------|
| Test dosya prep | ⏳ Şu an | Hemen | 1 saat |
| Mock data (API-14) | ⏳ Paralel | Hemen | 0.5 saat |
| Mock data (API-16) | ⏳ Sonra | API-14 +0.5h | 0.5 saat |
| Mock data (API-21) | ⏳ Bekleniyor | admin_audit.py | 0.5 saat |
| **TOTAL** | | | **2.5 saat** |

**Toplam:** 6 saatte blokajı açabilir (paralel çalışırsa)

---

## 6. Chat Sistemi Etkinleştirme Tarihi

**Canlı Kullanım Başlangıcı:** 2026-09-24 19:45 (15 dakika sonra)

**Ajanlar tarafından yazılacak ilk mesajlar:**
1. **UTKU → ORKESTRATOR:** API-14 başladım, saat 20:45'e teslim
2. **YASU → ORKESTRATOR:** Test prep başladı, 20:30 mock data ready
3. **İHSAN → ORKESTRATOR:** GROQ key problemi + admin_audit.py istendi

---

## 7. Özet: Ne Yapılacak

### Şu An (19:30-20:00)

| Ajan | Yapması Gereken | Durum |
|------|-----------------|-------|
| **UTKU** | API-14 yazma başlasın | 🔴 Acil |
| **YASU** | Test dosya + mock prep | 🟡 Şu an |
| **İHSAN** | GROQ key problemi çöz | 🟠 Blokaj |
| **ORKESTRATOR** | Chat'i monitor, koordine | 🟡 Sürekli |

### Sonraki 6 Saat (20:00-02:00)

- ✅ API-14 tamamla → 3 görev açılacak
- ✅ Test dosya tamamla
- ✅ API-16 başla (API-14'ten sonra)
- ✅ Paralel: DOC-15, API-18
- 🔴 İHSAN: admin_audit.py prototip
- 📢 Chat'te blokaj/çözüm yazılacak

---

## 8. Chat Entegrasyonu: Aktif Kullanım

**UI Yapıldı (bugün):**
- ✅ Gönderen/Alıcı ajan renklendirilmiş (6 renk, tema-uyumlu)
- ✅ Önem Derecesi renkli ikon + arka plan (4 seviye)
- ✅ Tarih sona alındı
- ✅ Tablo + Son 3 Mesaj görünümü iyileştirildi

**Kullanıma Açıldı:**
- URL: http://localhost:8501 → "Ajan Chat Sistemi" sekmesi
- Erişim: Admin token gerekli (MIMIR sekmesi gibi)

---

## 9. Karar Günlüğü

| Tarih | Karar | Gerekçe |
|-------|-------|---------|
| 2026-09-24 | API-14 → Utku'ya atanması | VERI-13 done, 3 görev blokajını açacak (P0) |
| 2026-09-24 | Yasu test prep paralel | Tüm mock data şablon hazırda |
| 2026-09-24 | Chat sistemini aktif aç | UI iyileştirildi, ajanlar kullanmaya hazır |
| 2026-09-24 | İHSAN → GROQ + admin_audit | 2 blokaj, 1 Kritik + 1 Orta |

---

**Sonraki Toplantı:** 2026-09-24 20:45 (Utku teslim, sırada ne var?)
