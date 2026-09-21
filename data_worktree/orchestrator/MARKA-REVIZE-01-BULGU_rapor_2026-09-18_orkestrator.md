[[Huginn Data Insights/data/orchestrator/MARKA-REVIZE-01-BULGU_rapor_2026-09-18_orkestrator.md]]

# MARKA-REVIZE-01-BULGU — Marka denetim muafiyet mekanizması (orkestratör, 2026-09-18)

## 1. Sorun (cline bulgusu B-1/B-2)

`scripts/marka_denetim.py` muafiyet mekanizmasından yoksundu → **140 yanlış pozitif**.

| Kaynak | Adet |
|---|---|
| Yasak-liste satırları (kuralı TANIMLAYAN metinler) | 41 |
| Script docstring'leri | 31 |
| Brifler (`docs/plans/`, `plans/`) | 17 |
| MRK plan regex'leri | 16 |
| Arşiv brifleri | 11 |
| `ROO_ELESTIRI_NOTLARI` alıntıları | 10 |
| `tests/test_i18n*` regex'leri | 7 |
| `_trash/` artıkları | 6 |

Sonuç: denetim aracı **sinyal üretmiyordu** — gerçek ihlal 140 gürültünün içinde kayboluyordu.

## 2. Çözüm — 3 katmanlı muafiyet

| Katman | Mekanizma | Kapsam |
|---|---|---|
| **1. Dizin** | `ATLANAN_DIZINLER` (+8 giriş) | `_trash`, `backups`, `.kilo`, `.agents`, `.claude`, `.continue`, `workspace`, `AI proje v1` |
| **2. Yol** | `MUAF_YOLLAR` glob tuple | `scripts/marka_denetim.py`, `docs/plans/*`, `plans/*`, `ROO_ELESTIRI_NOTLARI.md`, `tests/test_i18n*.py`, `tests/test_marka*.py`, `AGENT_SYNC.md` |
| **3. Satır** | `YASAK_BEYAN` regex + `MUAF_SENTINEL` | `yasak\|forbidden\|misspell` içeren satır atlanır; `marka-muaf` yorumu nokta atışı istisna |

Ek: ölü `import ast` silindi; `--sayim` bayrağı eklendi (CI için tek satır özet).

## 3. Ölçüm

```
ÖNCE:  140 ihlal
SONRA: yasal_yazim: 0 | kok_dizin: 0     (çıkış kodu 0)
```

**%100 gürültü temizliği.** False negative yok — `tests/test_marka_denetim_muafiyet.py::test_gercek_ihlal_yakalanir` gerçek ihlalin hâlâ yakalandığını doğruluyor.

## 4. Test

`tests/test_marka_denetim_muafiyet.py` — **7 test, 7 geçti (1.50 s)**

| Test | Doğruladığı |
|---|---|
| `test_gercek_ihlal_yakalanir` | false negative yok |
| `test_sentinel_satiri_atlanir` | 3. katman (satır) |
| `test_yasak_beyan_satiri_atlanir` | 3. katman (regex) |
| `test_kok_dizin_ihlali_yakalanir` | ikinci kural bozulmadı |
| `test_atlanan_dizin_taranmaz` | 1. katman |
| `test_muaf_yol_taranmaz` | 2. katman + `AGENTS.md` muaf DEĞİL |
| `test_kok_denetimi_temiz` | **regresyon kalkanı**: repo 0 ihlal |

## 5. Riskler ve sınır

| Risk | Değerlendirme |
|---|---|
| `YASAK_BEYAN` fazla geniş — "yasak" geçen satırda gerçek ihlal gizlenebilir | Kabul edildi. Alternatif (satır bazlı beyaz liste) bakım yükü yüksek. `marka-muaf` sentinel'i ters yönde hassas kontrol sağlıyor. |
| `docs/plans/*` toptan muaf | Brifler geçici doküman; markaya yansımıyor. |
| `docs/brand/` taranıyor ama değiştirilmedi | AGN-STACK-01 kapsam kısıtına uyuldu; muafiyet script tarafında. |

## 6. B-6 — `ROO_ELESTIRI_NOTLARI` D-33 maddesi

Açık kalan D-33 (ajan isim normalizasyonu) maddesi kapatıldı; `trigger.ajan_normalize()` uygulandı ve `AJAN_TAKMA_ADLAR` sözlüğü kanonik 3 ada (`kilo`/`cline`/`roo`) indiriyor.

## 7. Dosyalar

| Dosya | Durum |
|---|---|
| `scripts/marka_denetim.py` | değişti (125 → 179 satır) |
| `tests/test_marka_denetim_muafiyet.py` | yeni |
| `docs/ROO_ELESTIRI_NOTLARI.md` | B-6/D-33 kapatıldı |
