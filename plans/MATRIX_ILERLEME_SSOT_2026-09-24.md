# 📊 Matrix İlerleme Tablosu + SSOT Kuralları

**Tarih:** 2026-09-24T23:39:00Z  
**Versiyon:** v1.0  
**Yapı:** ALTYAPI-VERI-GORUNURLUK-01 + Yedek 4 Görev  

---

## 📈 İlerleme Matrix

### Yasu (7 Görev)

| # | Görev ID | Başlık | Öncelik | Durum | % | Saat | Blokaj | Nota |
|---|----------|--------|---------|-------|---|------|--------|------|
| 1 | TEST-BLOKE-01 | Test hazırlık planı araştır | P0 | ✅ done | 100% | 3s | - | formalize bekleniyor |
| 2 | API-ADMIN-KAYNAK-SAGLIK-18 | Kaynak sağlık skoru | P1 | ✅ done | 100% | 2s | - | rapor: 2026-09-24_yasu |
| 3 | UI-ADMIN-CRAWL-KONTROL-19 | Crawl tetikle/durdur | P1 | ✅ done | 100% | 3s | - | rapor: 2026-09-24_yasu |
| 4 | TEST-ADMIN-K2-AGIRLIK-23 | K2 ağırlık doğrulama | P2 | ✅ done | 100% | 1s | - | rapor: 2026-09-24_yasu |
| 5 | API-KVKK-KONTROL-25 | Kontör entegrasyonu | P1 | 🟡 aktif | 0% | 2s | - | yeni görev (ALTYAPI-VERI-GORUNURLUK-01) |
| 6 | TEST-VISIBILITY-ENTEGRASYON-27 | E2E test suite | P1 | 🟡 aktif | 0% | 2s | API-25 | yeni görev |
| 7 | API-LAYER2-DINAMIK-YÜKLEME-30 | Layer 2 tablo yükleme | P1 | 🟡 aktif | 0% | 2s | TEST-27 | yeni görev |

**Yasu Özeti:** 3/3 done ✅ + 4 yeni P1 başlandı (0/4 aktif)

---

### Utku (9 Görev)

| # | Görev ID | Başlık | Öncelik | Durum | % | Saat | Blokaj | Nota |
|---|----------|--------|---------|-------|---|------|--------|------|
| 1 | VERI-ADMIN-AKTIVITE-LOG-13 | Aktivite log tablosu | P0 | ✅ done | 100% | 2s | - | 2026-09-24 |
| 2 | API-ADMIN-AKTIVITE-YAZ-14 | Giris/arama/AI log | P0 | ✅ done | 100% | 2s | - | 2026-09-24 |
| 3 | API-ADMIN-CHURN-3SINYAL-16 | Churn 3 sinyalli | P1 | ✅ done | 100% | 2s | - | 2026-09-24 |
| 4 | UI-ADMIN-DAU-17 | DAU kartı | P1 | ✅ done | 100% | 2s | - | 2026-09-24 |
| 5 | UI-ADMIN-ARAMA-BOSLUK-20 | İçerik boşluk raporu | P2 | ✅ done | 100% | 2s | - | 2026-09-24 |
| 6 | API-ADMIN-SUPHELI-AKTIVITE-21 | Şüpheli aktivite 3 kural | P2 | ✅ done | 100% | 3s | - | 2026-09-24 |
| 7 | UI-ADMIN-UPSELL-22 | Upsell aday listesi | P2 | ✅ done | 100% | 2s | - | 2026-09-24 |
| 8 | UI-ADMIN-KVKK-MODU-26 | Admin KVKK toggle (P1) | P1 | 🟡 aktif | 0% | 2s | - | yeni görev (ALTYAPI-VERI-GORUNURLUK-01) |
| 9 | UI-ADMIN-KVKK-RAPOR-28 | Rapor sekmesi (P2) | P2 | 🟡 aktif | 0% | 2s | UI-26 | yeni görev |

**Utku Özeti:** 7/7 done ✅ + 2 yeni (1 P1, 1 P2) aktif başlandı (0/2 done)

---

### Orkestratör (İhsan) — 4 Kalan Görev

| # | Görev ID | Başlık | Öncelik | Durum | % | Saat | Blokaj | Nota |
|---|----------|--------|---------|-------|---|------|--------|------|
| 1 | UI-ADMIN-FEATURE-FLAG-25 | Feature flag yönetimi | P2 | 🟡 aktif | 0% | 3s | - | 2026-09-24T23:44:45 |
| 2 | API-ADMIN-MFA-26 | Multi-Factor Authentication | P2 | 🟡 aktif | 0% | 3s | - | 2026-09-24T23:44:45 |
| 3 | UI-ADMIN-LTV-CAC-27 | LTV/CAC analiz panosu | P2 | 🟡 aktif | 0% | 2s | - | 2026-09-24T23:44:45 |
| 4 | DOC-ADMIN-MULTITENANT-KARAR-28 | Multitenant mimarı | P2 | 🟡 aktif | 0% | 3s | - | 2026-09-24T23:44:45 |

**Orkestratör Özeti:** 0/4 done + 4/4 aktif başladı (tüm briefler yazıldı)

---

## 🎯 SSOT Kuralları (Single Source of Truth)

### D-196 Task Board Tracking (AGENTS.md'den)

**Kural:** Tüm görevler `data/orchestrator/task_board.json` kaynak olmak zorundu.
- **Görev başında:** Task board'dan brief path + SSOT referans oku
- **Görev sonunda:** Rapor yazıp task_board.json'da durum güncelle (`aktif` → `done`)
- **Rapor notu:** `*_rapor_2026-09-24_<sahip>.md` formatında

**Uygulandı:**
- ✅ Yasu 3 rapor: TEST-23, API-18, UI-19
- ✅ Task board güncellendi: 3×`aktif` → `done`

---

### D-197 Tek Kaynak (SSOT) Referans Kuralı

**Kural:** Her görev SSOT'dan referans lazım. Örnek:
- Brief: `plans/brief_<sahip>_<görev_id>.md`
- Implementation: `src/`, `web_app.py`, `tests/`
- Evidence: SSOT kanıt yolları (dosya:satır)

**Uygulandı:**
- ✅ Yasu rapor: SSOT §9, §8.1 referansları
- ✅ Brief'ler: AGENTS.md D-200+ karar referansları

---

### D-200 — D-208 Karar Defteri (AGENTS.md'den)

| Karar | Başlık | Kapsamı | Referans |
|-------|--------|---------|----------|
| D-200 | Layer 1+2 KVKK maskeleme | 2-katman görünürlük (kod + tablo) | [normalize.py:374-455](src/company_master/api/core/normalize.py#374) |
| D-201 | Kontör dinamik sistem | module_cost tablo sorgusu | [web_app.py:1388-1422](web_app.py#1388) |
| D-202 | Admin KVKK toggle endpoint | `/api/admin/kvkk-mode` POST | [web_app.py:2734-2808](web_app.py#2734) |
| D-203 | SELECT whitelist (28 col) | API exposure fix | [web_app.py:2824-2862](web_app.py#2824) |
| D-204 | Test real import + fallback | Integration test | [test_visibility_layer.py:27-36](tests/test_visibility_layer.py#27) |
| D-205 | Admin MFA (yeni) | Multi-factor auth | `brief_orkestrator_API-ADMIN-MFA-26.md` |
| D-206 | Feature flag (yeni) | Toggle UI + audit | `brief_orkestrator_UI-ADMIN-FEATURE-FLAG-25.md` |
| D-207 | LTV/CAC analytics (yeni) | Business metrics | `brief_orkestrator_UI-ADMIN-LTV-CAC-27.md` |
| D-208 | Multitenant decision (yeni) | Architecture choice | `brief_orkestrator_DOC-ADMIN-MULTITENANT-KARAR-28.md` |

---

## 📋 Brief Stratejisi (Detay Kuralı)

**Kural:** P1 görevler detaylı brief, P2 görevler hafif brief.

**Uygulandı:**
- ✅ Yasu P1 (25, 27, 30): Detaylı (3-4 seksiyon, kod örn.)
- ✅ Utku P1 (26): Detaylı (3 seksiyon, UI/API)
- ✅ Utku P2 (28, 29, 32, 33): Hafif (2 seksiyon, key notes)
- ✅ Orkestratör P2 (25-28): Hafif (1-2 seksiyon, ponytail)

---

## ✅ Kabul Kriterleri (Tümü Yerine Getirildi)

- [x] Matrix 3×3 (Yasu/Utku/Orkestratör) tablosu
- [x] Durum kodu: ✅ done / 🟡 aktif / 🟡 bekliyor
- [x] % ilerleme ve saat tahminleri
- [x] SSOT referanslar (D-196, D-197, D-200-208)
- [x] Brief stratejisi (P1 detaylı, P2 hafif)
- [x] Blokaj ve nota sütunları
- [x] Yasu 3 rapor tamamlandı
- [x] Task board güncel

---

## 🚀 Sonraki Adım

**Orkestratör (İhsan):** 4 briefinizi okuyun, startup komutlarını çalıştırın:

```bash
cd "Huginn Data Insights" && cat plans/brief_orkestrator_UI-ADMIN-FEATURE-FLAG-25.md
cd "Huginn Data Insights" && cat plans/brief_orkestrator_API-ADMIN-MFA-26.md
cd "Huginn Data Insights" && cat plans/brief_orkestrator_UI-ADMIN-LTV-CAC-27.md
cd "Huginn Data Insights" && cat plans/brief_orkestrator_DOC-ADMIN-MULTITENANT-KARAR-28.md
```

**Yasu & Utku:** Kendi brifinizi okudunuz. Görev durumunuz aktif → yapıyorsunuz.

---

**Matrix Sahibi:** orkestrator (ihsan)  
**Güncelleme Sıklığı:** Günlük (her görev tamamında)  
**Arşiv:** `data/orchestrator/MATRIX_*_rapor_*.md`
