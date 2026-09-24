# 📋 GÖREV ATAMA BİLDİRİMİ — 2026-09-24

**Tarih:** 2026-09-24T23:21:51Z  
**Orkestrator:** ihsan (D-196)  
**Tema:** ALTYAPI-VERI-GORUNURLUK-01 Gap Kapatma + 2-Katman KVKK Maskeleme  

---

## 📌 İstatistik

| Atanan | Görev Sayısı | Öncelik | Durum |
|--------|-------------|--------|-------|
| **Yasu** | 4 | P1 | 🟡 Beklenmede — Brief oku |
| **Utku** | 5 | 1×P1, 4×P2 | 🟡 Beklenmede — Brief oku |
| **TOPLAM** | 9 | Karma | 🟡 0/9 başlandı |

---

## 🟢 YASU'YA ATANAN GÖREVLER (4 P1 API/Test)

### Görev 1: API-KVKK-KONTROL-25
**Başlık:** Kontör Endpoint Entegrasyonu  
**Öncelik:** P1 (yüksek)  
**Brief Dosyası:** `plans/brief_yasu_API-KVKK-KONTROL-25.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_yasu_API-KVKK-KONTROL-25.md
```

**Özet:** `/api/match` ve `/api/ilan` endpoint'lerine `_charge_module_credit()` entegrasyonu. module_cost tablosundan dinamik olarak kontör düşülecek.

---

### Görev 2: TEST-VISIBILITY-ENTEGRASYON-27
**Başlık:** E2E Senaryosu & Çelişki Test Paketi  
**Öncelik:** P1 (yüksek)  
**Brief Dosyası:** `plans/brief_yasu_TEST-VISIBILITY-ENTEGRASYON-27.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_yasu_TEST-VISIBILITY-ENTEGRASYON-27.md
```

**Özet:** `tests/test_visibility_layer.py` tamamını çalıştırma ve validate etme. 5 senaryo + 4 çelişki (Ç1-Ç4) test kapsamı.

---

### Görev 3: API-LAYER2-DINAMIK-YÜKLEME-30
**Başlık:** plan_field_group Tablosu Yükleme  
**Öncelik:** P1 (yüksek)  
**Brief Dosyası:** `plans/brief_yasu_API-LAYER2-DINAMIK-YÜKLEME-30.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_yasu_API-LAYER2-DINAMIK-YÜKLEME-30.md
```

**Özet:** Layer 2 tablosundan görünürlük matrisi sorgu ediyor, `apply_kvkk_mask()` çağrısında `plan_field_visibility` param geçiliyor.

---

### Görev 4: KONTROL-KVKK-MASKELEME-31
**Başlık:** Admin Mode E2E Test (Strict ↔ Lenient)  
**Öncelik:** P1 (yüksek)  
**Brief Dosyası:** `plans/brief_yasu_KONTROL-KVKK-MASKELEME-31.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_yasu_KONTROL-KVKK-MASKELEME-31.md
```

**Özet:** `/api/admin/kvkk-mode` üzerinden strict → lenient → strict geçişleri test, `/api/company/{id}` response maskeleme farkını doğrula.

---

## 🔵 UTKU'YA ATANAN GÖREVLER (1 P1 + 4 P2 UI/Doc)

### Görev 1: UI-ADMIN-KVKK-MODU-26
**Başlık:** Admin Panel KVKK Mode Toggle  
**Öncelik:** P1 (yüksek)  
**Brief Dosyası:** `plans/brief_utku_UI-ADMIN-KVKK-MODU-26.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_utku_UI-ADMIN-KVKK-MODU-26.md
```

**Özet:** `web_dashboard/tabs/admin_panel.py`'de yeni sekme: strict/lenient radio toggle + reason textarea + `/api/admin/kvkk-mode` POST.

---

### Görev 2: UI-ADMIN-KVKK-RAPOR-28
**Başlık:** KVKK Maskeleme Rapor Sekmesi  
**Öncelik:** P2 (orta)  
**Brief Dosyası:** `plans/brief_utku_UI-ADMIN-KVKK-RAPOR-28.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_utku_UI-ADMIN-KVKK-RAPOR-28.md
```

**Özet:** Admin panelinde `admin_kvkk_mode` audit trail görünümü. Strict/lenient count + 7 gün trend grafik.

---

### Görev 3: DOC-VISIBILITY-KATMANI-29
**Başlık:** Kullanıcı Dokümanı: Visibility Layer Rehberi  
**Öncelik:** P2 (orta)  
**Brief Dosyası:** `plans/brief_utku_DOC-VISIBILITY-KATMANI-29.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_utku_DOC-VISIBILITY-KATMANI-29.md
```

**Özet:** `docs/VISIBILITY_LAYER_GUIDE.md` — Layer 1 (kod dict) + Layer 2 (tablo matrisi), admin mode, kontör, Ç1-Ç4 çözümü detaylı.

---

### Görev 4: UI-KONTROL-PANOSU-32
**Başlık:** Admin Kontrol Panosu  
**Öncelik:** P2 (orta)  
**Brief Dosyası:** `plans/brief_utku_UI-KONTROL-PANOSU-32.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_utku_UI-KONTROL-PANOSU-32.md
```

**Özet:** Dashboard sekmesi: maskeli/açık alan metrikleri + tier bar chart + 7 gün trend line chart.

---

### Görev 5: DOKÜMAN-KVKK-FAQ-33
**Başlık:** KVKK FAQ & Troubleshooting  
**Öncelik:** P2 (orta)  
**Brief Dosyası:** `plans/brief_utku_DOKÜMAN-KVKK-FAQ-33.md`

**Startup Komutu:**
```bash
cd "Huginn Data Insights" && cat plans/brief_utku_DOKÜMAN-KVKK-FAQ-33.md
```

**Özet:** `docs/KVKK_FAQ.md` — 7 SSS + 3 troubleshooting + 3 kod örneği (curl, Python, SQL).

---

## 📊 Bağımlılık Akışı

```
[A1-A4 TAMAMLANDI]
    ↓
[Yasu-25: /api/match, /api/ilan kontör]  ← Yasu-27, Yasu-30 ile paralel
    ↓
[Yasu-27: test_visibility_layer.py]      ← Yasu-30, Yasu-31 ile paralel
    ↓
[Yasu-30: Layer 2 tablo yükleme]         ← Yasu-31 başlayabilir
    ↓
[Yasu-31: Admin mode e2e test]           ← Utku-26, Utku-28 ile paralel
    ↓
[Utku-26: Admin panel UI]                ← Utku-28 başlayabilir
    ↓
[Utku-28: Rapor sekmesi]                 ← Utku-29, Utku-32, Utku-33 paralel
    ↓
[Utku-29, Utku-32, Utku-33: Doküman & Dashboard]
```

**Kısaca:**
- **Yasu görevleri:** Paralel yapılabilir (25 ↔ 27 ↔ 30), 31 son adım
- **Utku görevleri:** P1 (26) → P2 (28, 29, 32, 33) paralel
- **Çapraz:** Yasu-31 tamamlanınca Utku-26 start edilebilir

---

## 🚀 Uyarı & Başlatma Prosedürü

**Adım 1:** Yasu & Utku'na bildirimi gönder:
```
"ALTYAPI-VERI-GORUNURLUK-01 Gap kapatma tamamlandı. 9 görev atandı.
Yasu: 4 P1 API/test görev (25, 27, 30, 31)
Utku: 1 P1 UI + 4 P2 Doc/Dashboard görev (26, 28, 29, 32, 33)

Başlama: plans/brief_<sahip>_<görev_id>.md dosyalarını oku."
```

**Adım 2:** Her görev için startup komutu verilen komutları çalıştırmasını iste.

**Adım 3:** Başlayan görevlerin durum güncellemesini task_board.json'da takip et (D-196 rule).

---

## 📝 Notlar

- **Brief Stratejisi:** P1 görevler detaylı (kod örnekleri + adımlar), P2 görevler hafif (key sections)
- **SSOT Bağlantılar:** Her brief → ilgili nodlar → implementation files (ponytail'ler kaydedildi)
- **Test Coverage:** 5 scenario (terminal, strategic, admin strict, admin lenient, OSINT) + 4 çelişki test (Ç1-Ç4)
- **Module Cost:** Dinamik kontör (module_cost tablosu), hardcoded _TIER_CREDITS'den kurtulundu
- **Layer 2 Fallback:** plan_field_visibility parametresi opsiyonel; missing ise Layer 1'e fallback

---

## ✅ Kabul Kriterleri (Tümü tamamlanmalı)

- [ ] Yasu: 4 görev başlandı + brief okundu
- [ ] Utku: 5 görev başlandı + brief okundu
- [ ] task_board.json: Tüm görevler 🟡 "Başlangıç Öncesi" → "Başlandı" geçişi
- [ ] Yasu rapor: API-25, TEST-27, API-30, KONTROL-31 tamamlandı
- [ ] Utku rapor: UI-26, UI-28, DOC-29, UI-32, FAQ-33 tamamlandı
- [ ] Merges: `chore/visibility-layer-p1-and-p2-tasks` PR ile push

---

**Oluşturulan:** 2026-09-24T23:21:51Z (1 dakika sonra başlatılacak)
