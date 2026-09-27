# Brief: ALTYAPI-BENCHMARK-02 — Performans Ölçümü (API + Streamlit)

**Görev ID:** ALTYAPI-BENCHMARK-02
**Sahip:** SALİH (Test Danışman)
**Öncelik:** P2
**Tahmini Süre:** 2s
**Dosyalar:** `docs/raporlar/benchmark_2026-09-20.md`

---

## DURUM
Zincir adımı 2. Önceki: **TEST-KAPSAM-OLCUM-01** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Huginn (API, 8000) ve Muninn (Streamlit, 8501) için **mevcut** yanıt sürelerini ölç. Kod yazımı YOK — yalnız ölçüm + rapor.

---

## İŞ MADDELERİ

### 1. API endpoint yanıt süresi (var olan endpoint'ler)
```
curl -w "@-" -o /dev/null -s http://localhost:8000/health <<< "time_total: %{time_total}s\n"
```
(Windows'ta `curl.exe` veya `Measure-Command { curl http://localhost:8000/health }`)
- Her endpoint için 10 istek ortalaması al
- En az 5 farklı endpoint ölç (mevcut route listesinden seç)

### 2. Streamlit sayfa yükleme süresi
- Manuel: tarayıcıda `time` ölçümü veya `requests.get` ile ilk byte süresi
- 3 farklı sayfa ölç (admin_kpi, admin_errors, admin_kullanici_ayarlari)

### 3. DB sorgu süresi (mevcut sorgular)
- `src/company_master/db/` altındaki 3 sık kullanılan sorguyu bul
- `time.perf_counter()` ile mikro-benchmark (yeni kod DEĞİL, mevcut fonksiyonu çağırıp ölç)
- Not: Bu adım sadece **çalıştırma + ölçüm**; hiçbir dosya değişmez

### 4. Yük altında davranış (basit)
- `ab` (Apache Bench) veya `locust` varsa: 50 concurrent request, 5 saniye
- Yoksa: sıralı 20 istek ile ortalama + p95 hesapla (Python script'siz, elle hesap)

### 5. Raporu yaz
Dosya: `docs/raporlar/benchmark_2026-09-20.md`

Zorunlu tablolar:

**Tablo 1 — API Endpoint Süreleri**
| Endpoint | Ortalama (ms) | p95 (ms) | Durum |
|---|---|---|---|

**Tablo 2 — Streamlit Sayfa Yükleme**
| Sayfa | Süre (ms) | Durum |
|---|---|---|

**Tablo 3 — DB Sorgu Süreleri**
| Sorgu | Süre (ms) | Durum |
|---|---|---|

**Tablo 4 — Yük Testi Özeti**
| Metrik | Değer |
|---|---|
| Concurrent | ... |
| Ortalama yanıt | ... |
| p95 | ... |
| Hata oranı | ... |

---

## KISITLAR
- **Kod yazma YASAK.** Ölçüm için mevcut kod/komutları kullan, yeni dosya yazma.
- Rapor dosyası dışında hiçbir dosyaya dokunma.

---

## TESLİM
- Rapor yazımı ve teslim komutları **YASU üzerinden** yürür (D-59).
- SALİH raporu yazar, YASU teslim eder.
- D-67 rapor formatı ve D-55 renk sınıfı geçerli.

---

## DEĞERLENDİRME KRİTERLERİ
1. ✓ 4 tablo dolu, gerçek ölçüm verisi
2. ✓ En az 5 API endpoint, 3 Streamlit sayfa, 3 DB sorgu ölçülmüş
3. ✓ Yük testi sonucu var (basit veya ab/locust)
4. ✓ Hiçbir kod dosyası değişmemiş
5. ✓ Rapor UTF-8, BOM yok

---

## SONRAKI GÖREV
ALTYAPI-BILGI-TABANI-03 (Bilgi tabanı/runbook güncelleme)
Otomatik tetiklenir: bu görev teslim edilince.
