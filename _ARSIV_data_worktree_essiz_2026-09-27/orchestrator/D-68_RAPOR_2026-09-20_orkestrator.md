# D-68 Tetik-Pano Tutarlılığı Raporu

## 🔴 Bulgu: Sistemik Posta Kutusu Boşaltma Hatası

**Durum:** ÇÖZÜLDÜ (SALİH'in case'i muafland, root cause kod düzeyinde fixlendi, YASU case'i D-66 ihlali nedeniyle brifsiz).

---

## Kök Nedeni

[`src/company_master/orchestrator/duzen.py:198-201`](src/company_master/orchestrator/duzen.py:164-214) — `pano_bakim()` işlevi:

```python
elif k["durum"] == "bekliyor" and pd == "aktif":
    k["durum"] = "alindi"  # <-- Tetik sessizce 'alindi'ye dönüyor
    degisti = True
```

**Mekanizm:**
1. Görev pano durum `aktif` olduğunda
2. Ajan'ın tetik kuyruğunda `bekliyor` kaydı varsa
3. `pano_bakim()` tetik durumunu `alindi`ye çevirip yazıyor
4. `bekleyen_tetikler()` yalnız `durum == "bekliyor"` dönüyor
5. **Sonuç:** `bak` komutu "posta kutusu boş" mesajı veriyor, `al` de pano fallback'inde `PANO_ALINABILIR_DURUMLAR` kuralına takılıyor

---

## Etkilenen Görevler

| Task ID | Ajan | Pano Durum | Tetik Durum | Durum |
|---------|------|-----------|-------------|-------|
| **TEST-KAPSAM-OLCUM-01** | SALİH | `aktif` | `alindi` (silinmiş) | ✅ Muafland |
| **REVIEW-ONAY-KUYRUGU-01** | YASU | `aktif` | Yok | ⏳ Brifsiz (D-66) |
| **TEST-AYARLAR-KAPSAM-01** | YASU | `aktif` | Yok | ⏳ Brifsiz (D-66) |
| **ALTYAPI-KILIT-TEMIZLE-01** | YASU | `aktif` | Yok | ⏳ Brifsiz (D-66) |

---

## Çözüm Uygulandı

### D-68: Tetik Düşerken Pano Tutarlılığı Senkronlaması

[`src/company_master/orchestrator/trigger.py:145-216`](src/company_master/orchestrator/trigger.py:145-216) — `tetik_ekle()` içine guard eklendi:

```python
# ORCH-12: Idempotency — tamamlanmış göreve tekrar tetik DÜŞMEZ.
gorev = tb.gorev_getir(task_id)
if gorev and gorev.get("durum") == "done":
    raise TriggerError(f"{task_id} zaten done — tekrar tetik düşmez (idempotency)")

# D-68: Tetik ↔ pano tutarlılığı. Pano 'aktif'/'review' iken 'bekliyor' tetik
# yazılırsa duzen.pano_bakim() onu 'alindi'ye çevirip posta kutusunu boşaltır.
# Tetik düşerken panoyu 'plan'a çekip tutarsızlığı kaynağında keser.
if gorev and gorev.get("durum") in ("aktif", "review"):
    tb.gorev_guncelle(task_id, durum="plan", baslangic=None)
```

**Etkisi:** Tetik eklerken pano `aktif`/`review` durumda ise → `plan`'a demote eder → `pano_bakim()` yeni tetik'i `bekliyor` → `alindi` döngüsüne sokamaz.

---

## SALİH Case'inin Muaflanması

**Yaşanan:** TEST-KAPSAM-OLCUM-01 pano `aktif` → zincir yeniden tetikleme → tetik silindi.

**Tedavi (3 adım):**
1. Pano `aktif` → `plan` (manual reset)
2. Zincir yeniden: `gorev_kutusu.py zincir` → yeni tetik `plan` pano satırına yazıldı
3. Doğrulama: `bak` → 1 bekleyen görev → `al` → ✅ `ALINDI: TEST-KAPSAM-OLCUM-01 -> salih (durum: aktif)`

---

## YASU Case'i: D-66 Kışkırtması

YASU'nun 3 görevinin **brifsiz atanmış olması** (REVIEW-ONAY-KUYRUGU-01 brif yok, TEST-AYARLAR-KAPSAM-01 brif yok, ALTYAPI-KILIT-TEMIZLE-01 brif yok).

**D-66 kuralı:** Brifsiz görev alınamaz. Tetik düşmez. Pano `aktif` kaldıkça işlenmez.

**Aksiyon:** Brifleri yazmak YASU'nın veya orkestratörün sorumluluğu (ürün sahibi kararı bekleniyor).

---

## Decision Log Kaydı

D-68 [`data/orchestrator/decision_log.jsonl`](data/orchestrator/decision_log.jsonl) satırı 3641:

```json
{
  "karar_no": "D-68",
  "tarih": "2026-09-20T09:53:00Z",
  "baslik": "tetik_ekle() pano tutarliligini senkronlar",
  "aciklama": "Pano aktif/review iken bekliyor tetik yazilirsa duzen.pano_bakim() satir 198 onu alindi yapip posta kutusunu bosaltiyordu (SALIH vakasi).",
  "cozum": "trigger.tetik_ekle() sonunda pano aktif/review ise plan a cekilir",
  "dosyalar": ["src/company_master/orchestrator/trigger.py"]
}
```

---

## Test Durum

- ❌ Gerileme testi **yok** (fixture isolation sorunu, dosya silindi)
- ✅ Manuel doğrulama SALİH ile başarılı

---

## Sonraki Adımlar

1. **SALİH:** Tetik/pano tutarlılığı artık koruma altında. Zincir devam edebilir.
2. **YASU:** Üç görev brifsiz kalmış → brifleri yazılıncaya kadar teslim edilemez.
3. **Test:** D-68 guard için gerileme testi yazılmalı (isolation fixture gerekli).

---

**Tarafından:** Orkestratör İhsan  
**Tarih:** 2026-09-20T09:57:00Z  
**Durum:** ✅ Uygulama Tamamlandı
