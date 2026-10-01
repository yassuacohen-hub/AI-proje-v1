# Posta — Utku'ya Görev Bildirimi
**Tarih:** 2026-10-01 | **Gönderen:** Orkestrator (İhsan) | **Alıcı:** Utku

---

## 📋 KONU — Eksiklikler, Bulgu, Yeni Görevler

### 1. **Kapsam Düzeltmesi: "306 Başlıca Sebep" Hatası Tashihi**

**Durum:** Pano kontrolü sırasında (2026-10-01) bulundu.

**Sorun:** Eski beyan — "306/326 unknown'ın başlıca sebebi [hata]" — **YANLIŞ**.

**Gerçek (ölçümle doğrulanan):**
- 326 ilandan 306'sı `ilan_turu` alanı **BOŞ** (empty).
- Boş etiket = veri eksikliği, kod hatası **DEĞİL**.
- Hata yalnız **dolu 20 etiketi** vurur (case-sensitivity bug, `ticaret_sicili_kanit.py:183-192`).

**Özeleştiri:** Beyan ≠ kanıt (D-288 kuralı). Ben ölçmeden yazmışım; senin notunda "20/326 dolu, 306 boş" yazmış ama ben yanış okudum.

**Denetim Kaydı:** 
- ✅ `plans/bulut_tasinma_rehberi.md` satır 406–410 düzeltildi
- ✅ SSOT `admin_panel_hedef_dokumani.md` §502 v2.8 güncellendi
- ✅ `BORC_DEFTERI.md` satır 32 + sayım 35→36 güncellendi

**Sonraki Ölçüm (D-238):**
```sql
SELECT ilan_turu, COUNT(*) FROM ticaret_sicili GROUP BY ilan_turu ORDER BY COUNT(*) DESC;
-- "unknown" sayısı yeniden hesaplanacak, live DB'de.
```

---

### 2. **Pano Üzerinde Denetim Notları (3 Açık Review Görev)**

Senin 3 review görevinde durum **"review" kalıyor** (iade yok). Ama not alanına **DENETİM bulgusu** eklendi:

#### 🔴 **VERI-TSG-04-YAZICI-01** (review)
- **Bulgu:** `oday_esle` case-sensitivity (büyük/küçük harf).
- **Sebep:** `ILAN_TURU_ESLEME` anahtarları karışık harf ("Değişiklik", "Nevi Değişikliği", ...). `ilan_turu_normalize_et().upper()` ile geliren tüm argümanlar büyük harfle, hiçbir anahtarla eşleşmez.
- **Yapılması Gerekenler:**
  1. ILAN_TURU_ESLEME anahtarlarını normalize et **YA DA**
  2. `olay_esle()` giriş normalizasyonu standartlaştır
  3. Sonra canlı DB ölçümü: `SELECT event_type, COUNT(*) WHERE ... GROUP BY event_type`

#### 🟡 **VERI-NACE-ACILIM-01** (review)
- **Bulgu:** Exception handling eksik, doctest çakışması.
- **Not:** Ölçümler **sıralı çalışır** (çelişki yok). Canlı testi yapman gerekiyor.

#### 🟡 **VERI-NACE-SOZLUK-DIL-01** (review)
- **Bulgu:** Gerçek kullanıcı testi eksik.
- **Not:** Veri tanı değil; canlı validation gerekiyor.

---

### 3. **Yeni Görev 1: VERI-TSG-ESLEME-CASE-01** ← **PLANNED**

**Başlık:** `[VERI] TSG ilan türü eşlemesini düzelt → olay_esle normalize + canlı unknown ölçümü (1s)`

**Sahip:** Utku  
**Oncelik:** P1 (Yüksek)  
**Brief:** [`BORC-TSG-ESLEME-CASE-01`](../docs/BORC_DEFTERI.md#borc-tsg-esleme-case-01) — Açık borç, D-260'dan devralındı.

**Dosyalar (İlgili Kodlar):**
- `src/company_master/etl/tsg_yazici.py:88-92` — `ilan_turu_normalize_et()`
- `src/company_master/etl/tsg_yazici.py:188-189` — normalize() çıktısı `olay_esle`'ye geçiliyor
- `skills/services/ticaret_sicili_kanit.py:114-180` — ILAN_TURU_ESLEME dict (65 anahtar)
- `skills/services/ticaret_sicili_kanit.py:183-192` — `olay_esle()` fonksiyonu
- `tests/test_ticaret_sicili_kanit.py:131-139` — Mevcut test (kapsamı dar)

**Adımlar:**
1. **ILAN_TURU_ESLEME normalize et:** Anahtarları "Değişiklik" → "DEGISIKLIK" ya da `olay_esle()` argümanını `.lower()` geçir.
2. **Diğer hatalar:** `_veritabani_baglantisi()` (get_engine bypass), `_kisi_ve_rol_cikar()` (stub), `event_type=None` (INSERT).
3. **Test:** normalize→esle zinciri için yeni test yaz (D-288: yeşil test beyan değil).
4. **Canlı Ölçüm:** SQL sorgusu ile "unknown" yeniden sayılır.

**UYARI:** Ölçüm yapılmadan başlama (D-224).

---

### 4. **Yeni Görev 2: VERI-TENDER-KOLON-01** ← **PLANNED** (VERI-02 Sonrası)

**Başlık:** `[VERI] D-308 tender şema kolon çevirisi → osb_tender_monitor.py uyumlu hale getir (1s)`

**Sahip:** Utku  
**Oncelik:** P1 (Yüksek)  
**Brief:** [`BORC-TENDER-KOD-01`](../docs/BORC_DEFTERI.md#borc-tender-kod-01) — D-308 göçü eksikliği, açık borç.

**Problem:**
- D-308'de `ihale_ilanlari` tablo şeması İngilizceye çevrildi (göç 0043).
- Kolon adları: `ilan_basligi` → `tender_title`, `ilan_turu` → `tender_type`, vb.
- **Ama:** `osb_tender_monitor.py` hâlâ **Türkçe kolon adları** kullanıyor:
  ```python
  row["ilan_basligi"]   # ← YANLIŞ, şimdi tender_title
  row["ilan_turu"]      # ← YANLIŞ, şimdi tender_type
  row["osb_adi"]        # ← YANLIŞ, şimdi osb_name
  row["tahmini_maliyet"] # ← YANLIŞ, şimdi estimated_cost
  ```
- Bu kod **asla çalıştırılmadı** (D-309, benim hatam — bildirilmedi).

**Kanıt:**
- Göç 0043: `information_schema` sorgusuyla 8/8 kolon canli DB'de çevrildi (ölçümü: ✅).
- Kod tarihçesi: `osb_tender_monitor.py` son değişiklik 2026-09-28, göçten sonra.

**Yapılması Gerekenler:**
1. **8 Kolon Adını Güncelle:**
   - `ilan_basligi` → `tender_title`
   - `ilan_turu` → `tender_type`
   - `osb_adi` → `osb_name`
   - `tahmini_maliyet` → `estimated_cost`
   - `birim` → `unit`
   - `aciklama` → `description`
   - `belge_url` → `document_url`
   - `il` → `province`

2. **Test Yaz:** Öncesinde test yok (0), kodun logic'i BORC-TENDER-KOD-01'de listelenen 13 uyumsuzluğu kapsaması gerek.

3. **Prova:** `--dry-run` ile kuru çalışma, sonra gerçek veri.

**UYARI:** `osb_tender_monitor.py` D-308 kilit altında. DAG-bağımlılık kontrol et (başka kod da tender tablosundan okuyabilir).

---

## 📊 Özet Tablo

| Görev | Durum | Oncelik | Brief | Adım Sayısı | Kısıtlama |
|-------|-------|---------|-------|------------|-----------|
| VERI-TSG-04-YAZICI-01 (mevcut) | review → ✅ denetim notu eklendi | P0 | — | Canlı ölçüm | D-238 |
| VERI-NACE-ACILIM-01 (mevcut) | review → ✅ denetim notu eklendi | P1 | — | Sıralı test | D-288 |
| VERI-NACE-SOZLUK-DIL-01 (mevcut) | review → ✅ denetim notu eklendi | P1 | — | Kullanıcı test | — |
| **VERI-TSG-ESLEME-CASE-01** | **planned** ← NEW | **P1** | BORC-TSG-ESLEME-CASE-01 | 4 | D-224, D-288 |
| **VERI-TENDER-KOLON-01** | **planned** ← NEW | **P1** | BORC-TENDER-KOD-01 | 3 + test | D-308 kilit |

---

## 🔗 Bağlantılar (Referans)

- **Chat:** `Huginn Data Insights/data/orchestrator/ajan-chat.jsonl` satır 99–101 (3 mesaj)
- **Pano:** `task_board.json` — 3 review notunda DENETIM + 2 planned görev (eklenmesi bekleniyor)
- **Borç Defteri:** [`BORC_DEFTERI.md`](../docs/BORC_DEFTERI.md) — satır 32, 81 (güncellenmiş sayım 36=12/20/4)
- **Rehber:** [`plans/bulut_tasinma_rehberi.md`](bulut_tasinma_rehberi.md) — satır 406–410 (kapsam düzeltmesi)
- **SSOT:** [`admin_panel_hedef_dokumani.md`](../AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md) — §502 v2.8

---

## ✅ Teslim Listesi

- [ ] **VERI-TSG-ESLEME-CASE-01** — Rapor + Git commit
- [ ] **VERI-TENDER-KOLON-01** — Rapor + Git commit

---

**Soru/Engel varsa:** ajan-chat.jsonl'de yaz (D-210).  
**Başlamadan Önce:** Ölçüm görevlerinde D-224 (kırmızı test) + D-288 (beyan ≠ kanıt) kurallarını hatırla.

---

**Imza:** Orkestrator (İhsan)  
**Pano Kontrolü:** 2026-10-01 14:31 UTC+3
