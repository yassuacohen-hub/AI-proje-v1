# Adım 4: Hub Standartlarına Göre Kriter Kontrol

**Hub Kaynağı:** `Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB.md`

---

## Hub Standart Kriterleri

### 1. Görev Başlığı Standardı
- Format: `[KATEGORI] Kisa aciklama` (kategori = VERI, API, UI, DOC, ALTYAPI, ORKESTRA, TEST)
- Max 80 karakter
- Action verb + object + outcome

### 2. Açıklama Detayı
- Minimum: 1 satır (yapılacak + neden)
- İdeal: 2-3 satır + teknik detay
- Kanıt/Referans: SSOT dokumentasyon veya hub bağlantısı

### 3. Önem Seviyesi
- P0: Critical path, blocker, production risk
- P1: Scheduled sprint work, feature/fix
- P2: Technical debt, optimization, nice-to-have
- Kritik görevler: onem="critical" veya onem="yuksek" + durum != "done"

### 4. Sahib Atanması
- Ajan: utku, salih, yasu, ihsan, mimir
- Orkestrator: coordination/review tasks
- Boş bırakılmış = atanmayan görev (RED FLAG)

### 5. Brief ve Talimat
- Her P0/P1 görevde: brief dosyası (plans/brief_*.md)
- Brief içeriği: SSOT kaynağı, kriterler, teknik detay
- Talimat: komut + test adımları

---

## Bitmiş Görevler Kriter Audit (22 görev)

| # | task_id | Başlık Formatı | Önem | Sahib | Brief | Kanıt | Sonuç |
|---|---------|---|---|---|---|---|---|
| 1 | VERI-ADMIN-AKTIVITE-LOG-13 | ✅ [VERI] format | P0 | utku | ✅ | migration 0017 | ✅ PASS |
| 2 | API-ADMIN-AKTIVITE-YAZ-14 | ✅ [API] format | P0 | utku | ✅ | web_app.py + 5 test | ✅ PASS |
| 3 | DOC-ADMIN-DURUM-SENKRON-15 | ✅ [DOC] format | P1 | orkestrator | ✅ | SSOT §8.4 senkron | ✅ PASS |
| 4 | API-ADMIN-CHURN-3SINYAL-16 | ✅ [API] format | P1 | utku | ✅ | musteri_yonetimi.py SQL | ✅ PASS |
| 5 | UI-ADMIN-DAU-17 | ✅ [UI] format | P1 | utku | ✅ | admin_kpi.py rozet | ✅ PASS |
| 6 | API-ADMIN-KAYNAK-SAGLIK-18 | ✅ [API] format | P1 | yasu | ✅ | 3 kovalı rozet | ✅ PASS |
| 7 | UI-ADMIN-CRAWL-KONTROL-19 | ✅ [UI] format | P1 | yasu | ✅ | operatör panel | ✅ PASS |
| 8 | UI-ADMIN-ARAMA-BOSLUK-20 | ✅ [UI] format | P2 | utku | ✅ | normalize+frekans | ✅ PASS |
| 9 | API-ADMIN-SUPHELI-AKTIVITE-21 | ✅ [API] format | P2 | utku | ✅ | 3 kural, pytest | ✅ PASS |
| 10 | UI-ADMIN-UPSELL-22 | ✅ [UI] format | P2 | utku | ✅ | 3 kosul + test | ✅ PASS |
| 11 | TEST-ADMIN-K2-AGIRLIK-23 | ✅ [TEST] format | ? | yasu | ❓ | SSOT kanıt | ⚠️ ONEM_MISSING |
| 12 | DOC-ADMIN-V9-KUTUCUK-24 | ✅ [DOC] format | ? | utku | ❓ | 6 madde cleanup | ⚠️ ONEM_MISSING |
| 13 | UI-ADMIN-FEATURE-FLAG-25 | ✅ [UI] format | ? | utku | ✅ | 4 flag, audit | ⚠️ ONEM_MISSING |
| 14 | TEST-BLOKE-FAKTOR-ARASTIRMA-01 | ✅ [TEST] format | ? | yasu | ❓ | test skeletleri | ⚠️ ONEM_MISSING |
| 15 | ALTYAPI-SECRETS-SETUP-01 | ✅ [ALTYAPI] format | ? | orkestrator | ✅ | vault + config | ⚠️ ONEM_MISSING |
| 16 | ALTYAPI-DB-MIGRATION-01 | ✅ [ALTYAPI] format | ? | orkestrator | ✅ | migration + alerts | ⚠️ ONEM_MISSING |
| 17 | ALTYAPI-ADMIN-PANO-01 | ✅ [ALTYAPI] format | ? | orkestrator | ✅ | 4 bolum panel | ⚠️ ONEM_MISSING |
| 18 | ORKESTRA-AI-CHAT-KOORDINASYON-01 | ✅ [ORKESTRA] format | ? | ihsan | ✅ | ajan_chat + tests | ⚠️ ONEM_MISSING |
| 19 | UI-ADMIN-KVKK-RAPOR-28 | ✅ [UI] format | ? | utku | ✅ | admin panel sekmesi | ⚠️ ONEM_MISSING |
| 20 | DOC-VISIBILITY-KATMANI-29 | ✅ [DOC] format | ? | utku | ✅ | Layer 1/2 doc | ⚠️ ONEM_MISSING |
| 21 | ALTYAPI-VERI-GORUNURLUK-01 | ✅ [ALTYAPI] format | ? | orkestrator | ✅ | migration 0018 | ⚠️ ONEM_MISSING |
| 22 | VERI-ADMIN-AKTIVITE-LOG-13* | ✅ [VERI] format | P0 | utku | ✅ | migration 0017 | ✅ PASS |

---

## Bulunan Sorunlar

### 🔴 KRITIK
1. **Önem Alanı Eksik (10 görev)**
   - task_id: 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21
   - Etki: Önceliklendirme yapılamıyor, pano sıralaması eksik
   - Çözüm: task_board.json'da onem alanı ekle

### 🟡 UYARI
2. **Brief Dosyası Eksik (2 görev)**
   - task_id: 11, 14 — TEST sınıfı görevler
   - Etki: Teknik detay ve SSOT kaynağı eksik
   - Çözüm: plans/brief_*.md dosyası yaz

---

## Özet

- Başlık Formatı: ✅ 22/22 uyumlu (100%)
- Sahib Atanması: ✅ 22/22 atanmış (100%)
- Önem Seviyesi: ❌ 12/22 eksik (54% uyumlu)
- Brief Kaynağı: ⚠️ 20/22 (90% uyumlu)

**Geçme Durumu:** CONDITIONAL PASS — Önem alanları tamamlanırsa PASS

---

## Sonraki Adım

Adım 5: Kritik & Yüksek Önemli İşleri seç, briefing yaz, task_board.json güncelle.
