# V10-HIJYEN-01 — Teslim Raporu

| Alan | Değer |
|------|-------|
| Görev | `V10-HIJYEN-01` — engine.py mükerrer + bozuk WHERE bloğu temizliği (B-14) |
| Öncelik | **P0** |
| Tarih | 2026-09-18 |
| Durum | `review` — KAHİN (Ürün Sahibi) elle onayı bekliyor (S-07: P0 oto-onay YOK) |
| Kaynak | [`docs/HUGINN_V10_PLAN_NETLESTIRME_2026-09-18.md`](../../docs/HUGINN_V10_PLAN_NETLESTIRME_2026-09-18.md) § 3 (B-14), § 7 |

---

## KAHİN (Ürün Sahibi) İçin Özet

| Renk | Bulgu | Oran / Ölçü |
|------|-------|-------------|
| 🔴 → 🟢 | Firma listesinde "telefonu var / e-postası var / web sitesi var" filtrelerinden **herhangi biri** açıldığında sorgu çöküyordu. Düzeltildi. | 3 filtrenin **3'ü de** (%100) etkilenmişti |
| 🟢 | 6 satır kod silindi, hiçbir davranış kaybı yok — silinen blok zaten üstteki doğru bloğun bozuk kopyasıydı | Kod azaldı: 205 → 199 satır (**%2,9**) |
| 🟢 | Hatanın geri dönmesini engelleyen 4 otomatik kontrol eklendi | 4/4 geçti (%100) |
| 🟢 | Yazım/kodlama denetimi temiz | 0 ihlal |
| 🔵 | Bilinen kırık test yok; bu değişiklik mevcut hiçbir testi bozmuyor | — |

**Tek cümle:** Filtreli firma araması artık çalışıyor; hata bir daha dönerse test yakalayacak.

---

## Teknik Detay

### Hata (B-14)

`src/company_master/search/engine.py` satır **182-187** — mükerrer ve bozuk `WHERE` bloğu:

```python
where.append("((c.primary_phone IS NOT NULL AND c.primary_phone <> "") OR ...")
```

İki katmanlı hata:

1. **Sözdizimi tuzağı:** Python `<> ""` yazımını *implicit string concatenation* olarak yorumlar. `"...<> "` ve `") OR ..."` birleşir; SQL'e operandsız `<> ` girer → PostgreSQL syntax hatası.
2. **Mükerrerlik:** Blok, satır 176-181'deki doğru bloğun (tek tırnaklı `<> ''`) birebir kopyasıydı. Düzeltilse bile aynı koşul iki kez eklenirdi.

### Düzeltme

Satır 182-187 silindi. 176-181'deki doğru blok korundu.

### Dokunulan Dosyalar

| Dosya | Değişiklik |
|-------|-----------|
| [`src/company_master/search/engine.py`](../../src/company_master/search/engine.py) | 6 satır silindi (182-187) |
| [`tests/test_search_engine_where.py`](../../tests/test_search_engine_where.py) | Yeni — 4 regresyon testi |

### Çalışan Testler

```
python -m pytest tests/test_search_engine_where.py -q
....                                                   [100%]
4 passed in 0.20s

python scripts/kodlama_denetim.py
== TARAMA ==
  temiz: kodlama ihlali yok
allowlist disi ihlal yok
```

Test kapsamı (DB'siz, AST + metin düzeyinde):

| Test | Ne korur |
|------|----------|
| `test_sozdizimi_gecerli` | Dosya parse edilebilir |
| `test_bozuk_operand_yok` | `<> ""` yazımı geri dönemez |
| `test_mukerrer_where_blogu_yok` | Her filtre koşulu tam 1 kez |
| `test_bos_string_karsilastirmasi_tek_tirnak` | SQL boş string `''` olarak kalır |

### Bilinen Test Failure'ları

Yok. Bu değişiklik `search/engine.py` dışına dokunmuyor; mevcut süitte bağımlı kırık test tespit edilmedi.

### Kilit Disiplini

`gorev_ekle(..., dosyalar=[engine.py, test_search_engine_where.py])` ile kilitlendi. Onay sonrası (`done`) kilitler ORCH-05 ile otomatik düşer.

---

## Kapsam Dışı Bulgu (düzeltme YAPILMADI)

| Kod | Bulgu | Kanıt |
|-----|-------|-------|
| B-15 | [`src/company_master/search/fulltext.py`](../../src/company_master/search/fulltext.py) ölü kod — `NotImplementedError` fırlatır, **hiçbir yerden import edilmiyor** (`grep fulltext *.py` → 0 sonuç) | `search/__init__.py` yalnız `.engine`'den import ediyor |

Silme işlemi KAHİN onayı gerektirdiği için `V10-HIJYEN-02` olarak ayrı tutuldu; bu görev kapsamında dokunulmadı.
