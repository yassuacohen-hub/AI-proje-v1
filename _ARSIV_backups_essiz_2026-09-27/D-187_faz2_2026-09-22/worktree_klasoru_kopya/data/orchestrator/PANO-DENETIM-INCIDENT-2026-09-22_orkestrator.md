# PANO-DENETIM OLAY RAPORU
**Tarih:** 2026-09-22  
**Olay Türü:** Otomatik yönetim — yetki aşımı ve geri alma  
**Durum:** Kapatıldı / Kilitlendi  

---

## 1. Olay Özeti

Saatlik otomatik audit sistemi (`pano_denetim.py --uygula`) DASH-UX-02b görevini yanlışlıkla `done` olarak kapattı.

**Neden:** Görev hiçbir zaman gerçekten tamamlanmamıştı — sadece blokaj kaldırılmıştı ve İhsan tarafından tetik bekliyor durumundaydı.

**Hukuki İhlal:** D-66 (Kanıt Zorunluluğu) ve D-77 (Orkestratör Pano Disiplini) ihlali.

---

## 2. Timeline

| Zaman | Olay |
|-------|------|
| 2026-09-13T21:02:50 | DASH-UX-02b `baslangic` (plana girmesi) |
| 2026-09-13T21:46:30 | Copilot teslim eder (onay_kuyrugu eklenir) |
| 2026-09-13T21:46:49 | Oto-nobetçi onaylar |
| 2026-09-22T07:29:00 | pano_denetim.py --uygula, DASH-UX-02b'yi done yazıyor |
| 2026-09-22T07:45:00 | Ortaya çıkma algılandı, durum reverted (plan/null) |
| 2026-09-22T06:15:00 | Kod kilitlemesi tamamlandı (allowlist mekanizması) |

---

## 3. Root Cause Analysis

### 3.1 İlk Sebep: Zaman Damgası Buluşmazlığı

Görev kapatılırken, `_son_hareket()` logic şu alanları kontrol eder:
- `bitis` (bitiş tarihi)
- `atandi_tarihi` (atanma tarihi)
- `baslangic` (başlama tarihi)

Eski onay kaydı (`onaylandi` durum, 2026-09-13) ile yeni durum (`plan`) arasında **re-opening sırasında zaman damgası yazılmadığında**, eski approval heuristic çalışmıyor. Sistem "çelişki var" diye sınıflandırıyor.

**Kök Neden**: Blokaj kaldırma sırasında `baslangic`, `atandi_tarihi`, `bitis` alanları hiçbiri güncellenmedi. Task Board API'ye bkz [`task_board.py:303`](worktree klasoru/src/company_master/orchestrator/task_board.py:303).

### 3.2 İkinci Sebep: Otomatın Yetki Sınırlanması Yok

Orijinal `uygula()` fonksiyonu (`pano_denetim.py` L175+) hiçbir sınırlama olmadan `"done_yap"` duzeltme türünü kabul edip yazıyordu:

```python
elif duzeltme == "done_yap":
    tb.gorev_guncelle(tid, durum="done")
```

Bu, kanıt olmadan görevleri kapatmak demek = D-66/D-77 ihlali.

---

## 4. Çözümler

### 4.1 Kodu Kilitleme: IZINLI_DUZELTMELER Allowlist

**Satır 168** [`pano_denetim.py`](worktree klasoru/scripts/pano_denetim.py:168):
```python
IZINLI_DUZELTMELER = ("plana_ac", "bitis_temizle")
```

**Satır 179**:
```python
if duzeltme not in IZINLI_DUZELTMELER:
    continue
```

- ✓ `plana_ac`: Blokaj kaldırıldı, blocker yok → güvenli, geri alınabilir
- ✓ `bitis_temizle`: Stale bitis tarihi → güvenli, kanıt yok
- ✗ `done_yap`: **Kaldırıldı** — kanıt ister (D-66), orkestratöre aittir (D-77)

### 4.2 Bulgu Seviyelendirmesi

**Satır 129** [`pano_denetim.py`](worktree klasoru/scripts/pano_denetim.py:129):  
Kuyruk uyumsuzluğu `hata` → `uyari` (sadece rapor, otomatik düzeltme yok).

**Açıklama**: Kuyruktaki eski onay kaydı + yeniden açılmış görev = tarihsel kayıt mi çelişki mi belirsiz. Kararı orkestratör versin.

### 4.3 Kod Açıklaması

**Satır 116** [`pano_denetim.py`](worktree klasoru/scripts/pano_denetim.py:116):
```python
# Kuyruk ekleme-günlüğü olduğu için eski bir onay kaydı, görev sonradan
# yeniden açıldıysa çelişki değildir. Yeniden açılma her zaman zaman
# damgası bırakmadığından (bkz. DASH-UX-02b) bu bulgu ASLA otomatik
# uygulanmaz: durum=done kararı kanıt ister (D-66) ve orkestratöre aittir (D-77).
```

### 4.4 Test Regresyonu

[`test_pano_denetim.py`](worktree klasoru/tests/test_pano_denetim.py:44):
```python
def test_otomat_gorevi_done_yapamaz():
    """D-66/D-77: kanıt gerektiren 'done' kararı otomatın yetkisinde değil."""
    assert "done_yap" not in IZINLI_DUZELTMELER
    # ...
```

Yeni test, `done_yap` hiçbir zaman allowlist'e giremeyeceğini sağlar.

---

## 5. Ders: Reopening Timestamp Muhasebesi

Gelecek görev başlat sırasında, blokaj kaldırma işlemi aşağıdaki seçeneği düşünmeli:

1. **Opsyon A (seçildi)**: `baslangic` / `atandi_tarihi` güncellenmesin; bunun yerine `_son_hareket()` logic'ini geliştir (reopening zamanını `not` veya yeni `reopened_at` alanından oku).
2. **Opsyon B**: Blokaj kaldırma sırasında `atandi_tarihi` veya `reopened_at` damgası yaz.

Şu an Opsyon A, çünkü görev aslında "yeni atanmadı" — bloker kaldırıldı. Opsiyonlar open.

---

## 6. Hasarın Tersine Çevrilmesi

| İşlem | Nerede | Sonuç |
|-------|--------|--------|
| DASH-UX-02b revert | [`task_board.json`](worktree klasoru/data/orchestrator/task_board.json:2499) L2499–2521 | durum=plan, bitis=null, olay açıklaması `not` field'ine eklendi |
| Kod kilitlemesi | [`pano_denetim.py`](worktree klasoru/scripts/pano_denetim.py:168) L168–180 | IZINLI_DUZELTMELER allowlist, done_yap branch removed |
| Seviye downgrade | [`pano_denetim.py`](worktree klasoru/scripts/pano_denetim.py:129) L129 | kuyruk bulgusu: hata → uyari |
| Test regresyonu | [`test_pano_denetim.py`](worktree klasoru/tests/test_pano_denetim.py:44) | test_otomat_gorevi_done_yapamaz() |

---

## 7. Doğrulama

```bash
cd worktree klasoru

# Testler: 5/5 geçti
$ python -m pytest tests/test_pano_denetim.py -q
.....                                    [100%]
5 passed in 0.15s

# Read-only audit: DASH-UX-02b 'uyari' olarak görünüyor, auto-close yok
$ python scripts/pano_denetim.py
  [uyari/stuck] DASH-UX-02b: plan / son hareket 2026-09-13T21:02
  [uyari/kuyruk] DASH-UX-02b: kuyruk=onaylandi ama pano=plan — orkestratör kanıtla kapatmalı
  ...
[PANO-DENETIM] status=ok hata=0 uyari=6 ...
```

---

## 8. Yol Haritası (Gelecek)

- [ ] Blokaj kaldırma logic'i → `reopened_at` timestamp ekle (opsyon)
- [ ] Task Board API → re-opening sırasında timestamp seçenekli (future refinement)
- [ ] Saatlik CI → cron 0 * * * * devam ediyor; sync_report.json artifact upload

---

**Orkestratör İmzası:**  
Düzeltmeler uygulandı, otomatik yönetim sınırlandırıldı, regresyon testleri geçti. DASH-UX-02b'ye kanıtla kapatma kararı verdiğinde, `pano_denetim.py` report'a yazacak ama harekete geçmeyecek.
