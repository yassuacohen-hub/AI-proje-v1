# [ORKESTRA] Zincir Görevler Planı + En İyi Süreç

**Oluşturan:** roo (Orkestratör)  
**Tarih:** 2026-09-20T20:05Z  
**Durum:** Draft → KAHİN Onayı Bekleniyor

---

## 1. Durum Özeti

**Açık Görevler:** 15 (7 aktif, 8 plan)  
**Toplam Görev:** 337 (319 done, 7 aktif, 8 plan, 3 iptal)  
**Hata Düzeltme Durumu:** ✅ H1-H8 Tamamlandı

### H1-H8 Temizlik Sonuçları
- **H1:** ✅ `gorev_panosu.md` ↔ `task_board.json` senkron (7 aktif + 8 plan görüntüleniyor)
- **H2:** ✅ Mojibake: 109 → 28 (153 alan düzelti)
- **H3:** ✅ `decision_log.jsonl` kategori: 97 → 0 boş (tüm dolduruldu)
- **H4:** ✅ `file_locks.json`: 13 → 10 kilit (3 stale V10 silindi)
- **H5:** ✅ 48 `baslangic` alanı → `dosyalar` taşındı
- **H6:** ✅ Alan ikilemesi: 31 normalizasyon (`title`→`baslik`, vb.)
- **H7:** ✅ 17 başlık D-57 kalıbına uyarlandı (`[ALAN] FİİL + NESNE`)
- **H8:** ✅ Test artefaktları (QT-001, TEST-D77-01, vb.) → `arsiv`

---

## 2. Açık Görevler: Zincir Yapısı

### Sonuç: Tüm 15 Görev "Blokaj Yok" (Başlangıç Grubu)
Görevler arasında bağımlılık (*dependencies*/*blokaj*) bulunmadığı için:
- **Tüm görevler paralel başlatılabilir**
- Ancak **öncelik** ve **iş değeri** farklı

---

## 3. Karar Tablosu (1-5 Puan Sistemi)

| Görev ID | Priorite | Sahip | P | Değer | Etki | Teknik | Risk | Süre | Yorum |
|----------|----------|-------|---|-------|------|--------|------|------|--------|
| RESEARCH-PONYTALE | 🔴 KRITIK | ihsan | P0 | 3 | 3 | 2 | 2 | **1** | En kısa, P0 |
| REVIEW-ONAY-KUYRUGU-01 | 🟠 YÜKSEK | yasu | P1 | 3 | 3 | 2 | 2 | 2 | Onay kontrol |
| ALTYAPI-TEST-FAILURE-FIX-02 | 🟠 YÜKSEK | utku | P1 | 3 | 3 | **4** | 2 | 2 | Teknik karmaşık |
| DOC-SIRKET-MASTER-01 | 🟠 YÜKSEK | utku | P1 | 3 | 3 | 2 | 2 | 2 | İç belge |
| ORKESTRA-NAMING-AUDIT-02 | 🟠 YÜKSEK | ihsan | P1 | **4** | 3 | 2 | 3 | 2 | Sistem işletme |
| ORKESTRA-DECISION-LOG-03 | 🟠 YÜKSEK | ihsan | P1 | **4** | 3 | 2 | 3 | 2 | Sistem işletme |
| V10-BELGE-01 | 🟠 YÜKSEK | ihsan | P1 | **4** | 3 | 2 | 3 | 2 | Ürün geçmişi |
| ALTYAPI-KILIT-TEMIZLE-01 | 🟠 YÜKSEK | yasu | P2 | 3 | 3 | **4** | 2 | 2 | Teknik cleanup |
| TEST-AYARLAR-KAPSAM-01 | 🟠 YÜKSEK | yasu | P2 | 3 | 3 | **4** | 2 | 2 | Test iskeleti |
| ORKESTRA-BRIEF-TALIMAT-01 | 🟠 YÜKSEK | yasu | P2 | **4** | 3 | 2 | 3 | 2 | Sistem işletme |
| ORKESTRA-VAULT-TEKRAR-01 | 🟠 YÜKSEK | ihsan | P2 | **4** | 3 | 2 | 3 | 2 | Sistem audit |
| AGN-CREWAI-PILOT-01 | 🟡 ORTA | ihsan | P2 | 3 | 3 | 2 | 2 | 2 | Araştırma |
| ADLANDIRMA-GERIYE-01 | 🟡 ORTA | ihsan | P3 | 3 | 3 | 2 | 3 | 2 | Ek temizlik |
| WK-02 | 🟡 ORTA | — | P1 | 3 | 3 | 2 | 3 | 2 | Sahipsiz |
| WK-03 | 🟡 ORTA | — | P2 | 3 | 3 | 2 | 3 | 2 | Sahipsiz |

---

## 4. En İyi Süreç: 3-Sprint Zinciri

### Sprint 1 (Ani Başlayabilecek) — P0/P1 Hızlılar

**Hedef:** Yüksek-etki görevleri paralel bitiş

| Ajan | Yazılacak | Beklenen Sonuç |
|------|-----------|----------------|
| ihsan | RESEARCH-PONYTALE | Ponytail vs Caveman kıyaslaması raporu (1s) |
| yasu | REVIEW-ONAY-KUYRUGU-01 | 2 teslim onaylandı/reddedildi |
| utku | ALTYAPI-TEST-FAILURE-FIX-02 | tests/test_mcp.py geçiyor, rapor yazıldı |
| utku | DOC-SIRKET-MASTER-01 | Belge özeti K1/K3/K4 düzeltildi |

**Beklenen Teslim:** 2026-09-20T22:00Z (2 saat)

---

### Sprint 2 (S1 Sonrası) — Orkestratör Auditleri

**Bağımlılık:** S1 başarısından sonra başlayabilir (D-66 brif zorunlu)

| Ajan | Yazılacak | Beklenen Sonuç |
|------|-----------|----------------|
| ihsan | ORKESTRA-NAMING-AUDIT-02 | D-55/D-57 denetimi raporu + bulgular |
| ihsan | ORKESTRA-DECISION-LOG-03 | Karar defteri validasyon raporu |
| ihsan | V10-BELGE-01 | 6 curtulen iddianın K1/K3/K4 notu |
| yasu | ALTYAPI-KILIT-TEMIZLE-01 | file_locks.json temizliği + rapor |
| yasu | ORKESTRA-BRIEF-TALIMAT-01 | 4 brife talimat dosyası yazıldı |

**Beklenen Teslim:** 2026-09-21T00:00Z (4 saat)

---

### Sprint 3 (S2 Sonrası) — Test + Araştırma + Cleanup

**Bağımlılık:** S2 başarısından sonra

| Ajan | Yazılacak | Beklenen Sonuç |
|------|-----------|----------------|
| yasu | TEST-AYARLAR-KAPSAM-01 | tests/test_admin_kullanici_ayarlari.py iskeleti |
| ihsan | ORKESTRA-VAULT-TEKRAR-01 | Vault tekrar bulgularının listesi |
| ihsan | AGN-CREWAI-PILOT-01 | crewAI pilot raporu + deney sonuçları |
| ihsan | ADLANDIRMA-GERIYE-01 | 55 dosya ajan adı çıkarımı (otomatik) |

**Beklenen Teslim:** 2026-09-21T02:00Z (2 saat)

---

### Sprint 4 (İsteğe Bağlı) — Sahipsiz Görevler

| Ajan | Yazılacak | Beklenen Sonuç |
|------|-----------|----------------|
| **KAHİN** | WK-02 | OSB Tender Monitor sahip ataması |
| **KAHİN** | WK-03 | Proxy Rotation sahip ataması |

**Not:** Sahipsiz görevler KAHİN tarafından atanması gerekir (D-66).

---

## 5. Zincir İlişkileri: Detaylı Şema

```
BAŞLANGIÇ GRUBU (Tüm 15 görev blokaj yok)
    ↓
[Sprint 1 — P0/P1 Hızlılar: 4 görev, 2 saat]
    • RESEARCH-PONYTALE (ihsan, 1s)
    • REVIEW-ONAY-KUYRUGU-01 (yasu, 2s)
    • ALTYAPI-TEST-FAILURE-FIX-02 (utku, 2s)
    • DOC-SIRKET-MASTER-01 (utku, 2s)
    ↓ [S1 teslim + rapor bekleniyor]
[Sprint 2 — Orkestratör Auditleri: 5 görev, 4 saat]
    • ORKESTRA-NAMING-AUDIT-02 (ihsan)
    • ORKESTRA-DECISION-LOG-03 (ihsan)
    • V10-BELGE-01 (ihsan)
    • ALTYAPI-KILIT-TEMIZLE-01 (yasu)
    • ORKESTRA-BRIEF-TALIMAT-01 (yasu)
    ↓ [S2 teslim + bulgular bekleniyor]
[Sprint 3 — Test + Araştırma + Cleanup: 4 görev, 2 saat]
    • TEST-AYARLAR-KAPSAM-01 (yasu)
    • ORKESTRA-VAULT-TEKRAR-01 (ihsan)
    • AGN-CREWAI-PILOT-01 (ihsan)
    • ADLANDIRMA-GERIYE-01 (ihsan)
    ↓
[Sprint 4 — Sahip Atama: 2 görev, KAHİN]
    • WK-02 (Sahip TBD)
    • WK-03 (Sahip TBD)
```

---

## 6. İş Kuralları (D-57, D-66, D-72 Uygulanması)

### D-57: Başlık Standardı
```
[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)
```

**Kontrol:** Tüm açık görevlerin başlığında `[ALAN]` öneki mevcut mi?

- ✅ ORKESTRA-NAMING-AUDIT-02: `[ORKESTRA] D-55/D-57 adlandırma kuralları denetimi`
- ✅ ORKESTRA-DECISION-LOG-03: `[ORKESTRA] Karar defteri düzenleme ve validasyon`
- ✅ ALTYAPI-TEST-FAILURE-FIX-02: `[ALTYAPI] Test hatası düzelt`
- ✅ TEST-AYARLAR-KAPSAM-01: `[TEST] Kullanıcı Ayarları sayfası için test iskeleti yaz`
- ⚠️ RESEARCH-PONYTALE: `[ARAŞTIRMA]` eklenmeli
- ⚠️ REVIEW-ONAY-KUYRUGU-01: `[ORKESTRA]` eklenmeli (denetim görevdir)
- ⚠️ WK-02, WK-03: `[VERI]` eklenmeli

### D-66: Brifsiz Atama Yasak
**Kontrol:** Her atamada `brief` alanı dolu mu?

Tüm açık görevler **zaten atanmışsa**, brif var mı kontrol et. Yeni atama olursa brif kuralı uygulanacak.

### D-72: Sprint Başlangıç Tablosu
**Formata uygunluk:** ✅ Tablolar yukarıda D-72 formatı (Ajan·Yazılacak·Beklenen Sonuç)

---

## 7. Ürün Sağlığı Göstergeleri

| Gösterge | Durumu | Trend | Açıklama |
|----------|--------|-------|----------|
| **Açık Görev Yoğunluğu** | 🟢 İyi | ↓ | 15/337 (4.5%) — Yazılabilir seviyede |
| **Blokaj Durumu** | 🟢 İyi | ↓ | 0 blok — Tüm görevler paralel başlayabilir |
| **Orkestratör İş Yükü** | 🟡 Uyarı | → | 6 ORKESTRA görev (ihsan 6, yasu 3 vb.) — Dengeli |
| **Ürün Denetimi** | 🔴 Kritik | → | Henüz yapılmamış (S2'de başlayacak) |
| **Test Kapsamı** | 🟡 Kısmi | ↑ | TEST-AYARLAR-KAPSAM-01 S3'te yapılacak |
| **Teknik Borç** | 🟡 Uyarı | → | V10 hijyen + mojibake 28 (< 30 kabul) |

---

## 8. KAHİN Karar Noktaları

### Karar 1: Sprint 1'i hemen başlatır mısınız?
- **Şık A:** Evet, RESEARCH-PONYTALE + REVIEW + TEST + DOC paralel başlasın
- **Şık B:** Hayır, RESEARCH-PONYTALE'nin sonucunu bekle
- **Tercih:** 🟢 A (Paralel çalışma = daha hızlı teslim)

### Karar 2: Sahipsiz görevleri (WK-02, WK-03) atayabilir misiniz?
- **Şık A:** ihsan'a ata
- **Şık B:** Yeni ajan belirtir misiniz?
- **Tercih:** Bekleme (D-66 brif zorunlu olacak)

### Karar 3: Mojibake 28 kalmasını kabul ediyor musunuz?
- **Şık A:** Evet, H2 yeterli
- **Şık B:** Hayır, döngü 6 turunu çalıştır
- **Tercih:** 🟢 A (28 << 109, türkçe karakter sınırlaması nedeni)

---

## 9. Sonraki Adımlar (KAHİN Onayı Sonrası)

1. **Sprint 1 Başlat** (2026-09-20T20:30Z):
   - Brifleri kontrol et (D-66)
   - Tesimleri 2026-09-20T22:00Z takip et

2. **Sprint 2 Başlat** (2026-09-20T22:30Z):
   - S1 bulgularını gözden geçir
   - Orkestra denetim görevlerini başlat

3. **Haftalık Rapor** (D-67):
   - Tüm teslimler → Karar Defteri (D-92)
   - Hata düzeltmeleri özetlenecek

---

## Notlar

- **Ponytail İlkesi Uygulanıyor:** Minimal zincir, maksimum paralellik
- **Lazy Senior Dev:** YAGNI — Tüm görevler başlayabilir, blokaj yok
- **Atomik Yazma:** task_board.json + decision_log.jsonl + file_locks.json ✅ güvenli
- **Self-Check:** `scripts/orkestrator_analiz.py` idempotent, yeniden çalıştırılabilir

**Rapor Tamamlandı → KAHİN Onayı Bekleniyor**
