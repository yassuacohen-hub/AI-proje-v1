# Sprint Başlangıç Tablosu — D-72 (KAHİN kararı 2026-09-20)

**Tarih:** 2026-09-20 16:18 UTC+3  
**Orkestratör:** İhsan  
**Durum:** Tetiklemeye hazır (4/4 ajan, 4/4 görev beklemede)

---

## Tetikleme Tablosu

| Ajan | Yazılacak | Beklenen Sonuç |
|---|---|---|
| **UTKU** | `basla` | `[utku] 1 bekleyen gorev: ALTYAPI-TEST-FAILURE-FIX-01 (P1) tetik: 2026-09-20T15:48:10 [ALTYAPI] düzelt 4 pre-existing test failure → data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_rapor_2026-09-20_uretim.md (2s)` |
| **SALİH** | `basla` | `[salih] 1 bekleyen gorev: TEST-KAPSAM-OLCUM-01 (P2) tetik: 2026-09-20T13:31:08 [TEST] Mevcut test kapsamını ölç ve raporla → docs/raporlar/test_kapsam_olcum_2026-09-20.md (2s)` |
| **YASU** | `basla` | `[yasu] 1 bekleyen gorev: ORKESTRA-STALE-TEMIZLIK-01 (P1) tetik: 2026-09-20T13:37:37 [ORKESTRA] Denetle → YASU stale görevleri (1s)` |
| **İHSAN** | `basla` | `[ihsan] 1 bekleyen gorev: ORKESTRA-VAULT-TEKRAR-01 (P2) tetik: 2026-09-20T16:04:57 [ORKESTRA] denetle vault isim tekrarlari → ORKESTRA-VAULT-TEKRAR-01_rapor.md (2s)` |

---

## KAHİN'e Sunumu — Tetikleme Adımları

### 1. **Üretim Ajanına (UTKU)**
Kopyala ve UTKU sohbetine yapıştır:
```
basla
```

**Beklentisi:**  
UTKU başlangıç brifi okuyacak. 4 ön var test hatası düzeltme (ALTYAPI-TEST-FAILURE-FIX-01, P1, 2s). Rapor dosyası otomatik kilitlenmiş.

---

### 2. **Test Danışmanına (SALİH)**
Kopyala ve SALİH sohbetine yapıştır:
```
basla
```

**Beklentisi:**  
SALİH test kapsam ölçüm görevini alacak (TEST-KAPSAM-OLCUM-01, P2, 2s). Çıkış dosyası `docs/raporlar/test_kapsam_olcum_2026-09-20.md`.

---

### 3. **Denetim Ajanına (YASU)**
Kopyala ve YASU sohbetine yapıştır:
```
basla
```

**Beklentisi:**  
YASU stale görev temizliğini yapacak (ORKESTRA-STALE-TEMIZLIK-01, P1, 1s). Kilitli iki rapor dosyası (review onay + kilit temizme). 

---

### 4. **Orkestratöre (İHSAN — kendi)**
Kopyala ve İhsan sohbetine yapıştır (veya local çalıştır):
```
basla
```

**Beklentisi:**  
İhsan kendi görevini alacak — Vault isim tekrarları denetimi (ORKESTRA-VAULT-TEKRAR-01, P2, 2s).

---

## Doğrulama Notları

✅ **Her ajan tam 1 görev beklemede** — tetik kuyruğu temiz, çakışma yok.  
✅ **Öncelik dağılımı:** 2×P1 (UTKU, YASU) + 2×P2 (SALİH, İHSAN) — dengeli.  
✅ **Süre tahmini:** 4 görev × 1–2s = toplam 7s.  
✅ **Kilitler:** SALİH 1 dosya, YASU 2 dosya — çakışma yok.

---

## Tetikle — Sıra ve Zamanlama

**Paralel çalışma:** İlk 3 ajan (UTKU, SALİH, YASU) aynı anda başlayabilir.  
İHSAN kendi görevini sırasında çalıştırabilir (orkestratör görev alırken başkalar çalışmaya devam eder).

**Beklenen bitişi:** ~16:30 UTC+3 (10 dakika).

---

## Görev Özeti

| Task ID | Ajan | Alan | Üstlük | Şu Durum |
|---------|------|------|--------|----------|
| ALTYAPI-TEST-FAILURE-FIX-01 | UTKU | ALTYAPI | 2s | 📍 Bekliyor |
| TEST-KAPSAM-OLCUM-01 | SALİH | TEST | 2s | 📍 Bekliyor |
| ORKESTRA-STALE-TEMIZLIK-01 | YASU | ORKESTRA | 1s | 📍 Bekliyor |
| ORKESTRA-VAULT-TEKRAR-01 | İHSAN | ORKESTRA | 2s | 📍 Bekliyor |

---

## Not: D-72 Uyumluluğu

✅ Tablo **D-72 şablonuna uyumlu:**
- Sütunlar: `Ajan` · `Yazılacak` · `Beklenen Sonuç`
- `Yazılacak` = KAHİN'in kopyalayacağı tam komut
- `Beklenen Sonuç` = ajan ekranında göreceği tam output snapshot

**Kurala göre:** Beklenen sonuç gerçekleşmezse, ajan iş yapmaz ve orkestratöre bildirir → blokaj raporu açılır.
