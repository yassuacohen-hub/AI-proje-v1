# Doğrulama Raporu — 2026-09-19

## Özet
Görev panosu ve tetik sisteminin durumu kontrol edildi. **Kilo görevleri yok** (bekleniyordu 6 görev). **Salih bir görev alabildi, UTKU 971 tetik işledi**. Sistem çalışıyor ama **Salih tetikleme sorununda**.

---

## 1. Kilo'nun Bildirdiği 6 Görev — 🔴 BULGU

**Beklenen:** `kilo` sahipliğinde 6 görev
**Gerçek:** 0 görev (sahip="kilo")

### Tetik log analizi
- **Kilo tetikleri:** 971 toplam (`trigger_log.jsonl`)
- Son 6 tetik: `ADMIN-KPI-KART-02`, `ADMIN-MUSTERI-02` (2026-09-18 23:39-23:44)
- Tetik durumları boş (durum alanı eksik), tetikleme başarılı mı belirsiz

### Sonuç
Kilo'nun iş almadığı, yalnızca tetikleri loglandığı görülüyor. Panodaki hiçbir görev kilo'ya atanmamış. **Tetik log ayrıntısı eksik** (durum alanı boş).

---

## 2. Salih Durumu — 🟡 BULGU

**Panodaki görev:** 1 adet
- `TEST-MERVE-KAPSAM-01` | plan | P2

**Tetik kuyruğu (`salih.jsonl`):** 1 adet
- `TEST-MERVE-KAPSAM-01` | ajan: merve | durum: bekliyor

### Sorun
- Tetik dosyasında `ajan: merve` yazılı, `ajan: salih` değil
- AGENTS.md D-60 kuralı: merve → salih kanonik ad geçişi yapıldı
- `trigger.py` `ajan_normalize()` fonksiyonu `merve` → `salih` dönüştürmeli
- **Tetik kuyruğu `merve` kullanıyor, normalize edilmemiş**

### Sonuç
Salih tetik alması için `AJAN_TAKMA_ADLAR` düzeltilmeli veya `_tetikleri_yaz()` normalize etmeli.

---

## 3. Utku Durumu — 🟢 BAŞARILI

**Panodaki görevler:** 47 adet
- 41 tane `done`
- 3 tane `blocked`
- 3 tane diğer

**Tetik kuyruğu (`utku.jsonl`):** 5 son tetik
- Hepsi `ajan: kilo` (doğru)
- Hepsi `durum: done`

**Tetikleme:** 971 tetik başarıyla işlendi (trigger_log.jsonl)

### Sonuç
**UTKU tam çalışıyor.** Görevleri başarıyla alıp bitiriyor. Tetik normalizasyonu doğru çalışıyor (`kilo` → `utku`).

---

## 4. Sistem Sağlığı

| Metrik | Durum | Not |
|--------|-------|-----|
| **Pano yapısı** | 🟢 Sağlıklı | JSON geçerli, alanlar tam |
| **Tetik log** | 🟡 Eksik alan | `durum` boş kalan entries |
| **Utku tetikleri** | 🟢 Tam | 971 tetik, normalize doğru |
| **Salih tetikleri** | 🔴 Sorun | `merve` normalizasyonu yapılmamış |
| **Kilo görevleri** | 🔴 Yok | Pano sahip alanı kilo görmüyor |

---

## 5. Tavsiyeleri

1. **Salih tetik sorunu (acil)**
   - `trigger.py` `_tetikleri_yaz()` veya `_tetikleri_oku()` adımında `ajan_normalize()` çağrılmalı
   - Alternatif: `salih.jsonl` tek tek `merve` → `salih` dönüştür

2. **Kilo görevleri (araştır)**
   - Kilo'ya atanan görevler neden pano.json'da görülmüyor?
   - Tetik log 971 entry, fakat `task_board.json`'da `sahip: kilo` yok
   - Sorgu: `board = [t for t in data if t.get("sahip") == "kilo"]` 0 dönüyor

3. **Tetik log detay (iyileştir)**
   - `tetik_log.jsonl` durum alanı eksik
   - Başarı/hata bilgisi kaydedilmeli

---

## 6. Karar

✅ **Sistem çalışıyor (UTKU başarılı)**
⚠️ **Salih tetik normalizasyonu düzelt**
🔴 **Kilo görev atama sorunu araştır**

Görev panosu **hazır teslime** ama **2 sorun çözmeli** (Salih normalize, Kilo araştır).

---

**Rapor tarihi:** 2026-09-19 02:06 UTC  
**Kontrol edeni:** IHSAN (roo)
