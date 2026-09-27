# Brief: TEST-KAPSAM-OLCUM-01 — Mevcut Test Kapsamını Ölç ve Raporla

**Görev ID:** TEST-KAPSAM-OLCUM-01
**Sahip:** SALİH (Test Danışman)
**Öncelik:** P2
**Tahmini Süre:** 2s
**Dosyalar:** `docs/raporlar/test_kapsam_olcum_2026-09-20.md`

---

## DURUM
Zincir başlangıcı (SALİH'in 1. görevi). Önceki görev yok; hemen tetiklenir.

---

## AMAÇ
Mevcut test süitinin kapsamını **ölç** ve raporla. Kod yazımı YOK — sadece komut çalıştır, sayıları topla, tabloya dök.

---

## İŞ MADDELERİ

### 1. Tam süit çalıştır ve sayıları kaydet
```
python -X utf8 -m pytest tests/ -q
```
- Kaydet: passed / failed / skipped / süre (saniye)

### 2. Modül bazlı coverage ölç
```
python -X utf8 -m pytest tests/ --cov=src/company_master --cov-report=term-missing -q
```
- Kaydet: her alt paket için coverage yüzdesi

### 3. Kapsamsız modülleri listele
- `src/company_master/` altında **hiç testi olmayan** modülleri bul
- Yöntem: coverage raporunda `0%` veya `missing` satırları

### 4. En yavaş 10 testi ölç
```
python -X utf8 -m pytest tests/ --durations=10 -q
```

### 5. Raporu yaz
Dosya: `docs/raporlar/test_kapsam_olcum_2026-09-20.md`

Zorunlu tablolar:

**Tablo 1 — Süit Özeti**
| Metrik | Değer |
|---|---|
| Toplam test | ... |
| Passed | ... |
| Failed | ... |
| Skipped | ... |
| Süre (sn) | ... |

**Tablo 2 — Modül Coverage**
| Modül | Coverage % | Hedef % | Durum |
|---|---|---|---|
| `ui/` | ... | 70 | 🔴/🟡/🟢 |
| `orchestrator/` | ... | 75 | ... |
| `auth/` | ... | 80 | ... |
| `db/` | ... | 70 | ... |

**Tablo 3 — Testsiz Modüller**
| Modül yolu | Satır sayısı | Öncelik |
|---|---|---|

**Tablo 4 — En Yavaş 10 Test**
| Test | Süre (sn) |
|---|---|

---

## KISITLAR
- **Kod yazma YASAK.** Tek satır `.py` dosyası oluşturma/düzenleme yok.
- Yalnız komut çalıştır + markdown rapor yaz.
- Dosya kilidi: sadece kendi rapor dosyan.

---

## TESLİM
- Rapor yazımı ve teslim komutları **YASU üzerinden** yürür (D-59).
- SALİH raporu yazar, YASU teslim eder.
- Rapor formatı: D-67 (5 zorunlu başlık: Ne yapıldı / Değişen dosyalar / Test sonuçları / Bulgular / Eksik-erteleme)
- Bulgular D-55 renk sınıfıyla: 🔴 acil · 🟡 dikkat · 🟢 tamam · 🔵 öneri

---

## DEĞERLENDİRME KRİTERLERİ
1. ✓ 4 tablo da dolu, sayılar gerçek komut çıktısından
2. ✓ Testsiz modül listesi eksiksiz
3. ✓ Her coverage satırında renk sınıfı var
4. ✓ Hiçbir `.py` dosyası değişmemiş (git status temiz, sadece rapor)
5. ✓ Rapor UTF-8, BOM yok

---

## SONRAKI GÖREV
ALTYAPI-BENCHMARK-02 (Performans ölçümü)
Otomatik tetiklenir: bu görev teslim edilince.
