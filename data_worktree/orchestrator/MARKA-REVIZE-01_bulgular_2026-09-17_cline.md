# MARKA-REVIZE-01 — Kapsam Dışı Bulgular (cline, 2026-09-17)

**Görev:** MARKA-REVIZE-01 (doküman katmanı) · **Brif:** `docs/plans/MARKA-REVIZE-01_brief.md`
**Kural:** Kapsam dışı bulgu DÜZELTİLMEZ; rapor + roo tetiği (AGENTS.md "BULGU NOTU").
**Kilit:** `scripts/marka_denetim.py`, `tests/test_i18n.py`, `tests/test_marka_denetim.py`, `.streamlit/config.toml` → **MARKA-REVIZE-01B (kilo)**; cline dokunmadı.

---

## B-1 (YÜKSEK) — `marka_denetim.py` gerçek repoda her zaman kırmızı; muafiyet mekanizması yok

**Belirti:** `python scripts/marka_denetim.py` → **exit 1, "Toplam ihlal: 140"**. Bu satırların **tamamı yanlış pozitif**; brif kabul kriteri "`python scripts/marka_denetim.py` → temiz" bu haliyle **karşılanamaz**.

**Kök neden:** Araç iki kategoriyi (`yasal_yazim`, `kok_dizin`) satır/dosya muafiyeti olmadan tüm repoda tarıyor. Oysa yasak yazımların **tanımlandığı** satırların kendisi zorunlu olarak bu kelimeleri içerir (D-44 §1 → liste görünür olmalı).

**İhlal dağılımı (ölçüldü, 2026-09-17):**

| Adet | Kategori | Değerlendirme |
|---|---|---|
| 41 | Yasak liste satırları (`AGENTS.md:49,120`, `ANA_KURALLAR.md:81`, `docs/AJAN_DETAY.md:107`, `docs/brand/**`, MRK planı S10) | **Muaf olmalı** — brif açıkça "yalnız yasak listesi satırları muaf" diyor |
| 31 | `scripts/marka_denetim.py` kendi docstring/print satırları (`YASAL_YAZIM` tanımı, `kok_dizin` docstring/başlık) | **Kendi kendini ihlal sayıyor** (öz-referans) |
| 17 | `docs/plans/MARKA-REVIZE-01_brief.md` (D-44 karar tablosu, envanter, kabul kriteri) | **Muaf olmalı** — brif metni listeyi tarif eder |
| 16 | `plans/MRK_marka_ve_dil_paketi_plani.md` (satır 147 regex bekçisi, 241 S10) | **Muaf olmalı** — kural/regex tanımı |
| 11 | `plans/brief_cline_MRK02fg.md:278`, `plans/brief_kilo_MRK03_MRK04.md:117` (arşiv brif) | **Muaf olmalı** — arşiv kayıt |
| 10 | `docs/ROO_ELESTIRI_NOTLARI.md:69,320` (S-09 çözümü, D-33 bulgusu) | **Muaf olmalı** — bulgu kaydı |
| 7 | `tests/test_i18n.py:29-30` (`HATALI_YAZIM`, `ODIN_MISSPELLING` regex tanımı) | **Muaf olmalı** — bekçi regex'i tanım gereği kelimeleri içerir |
| 6 | `_trash/kok_2026-09-16/write_test.py:29` | **Taranmamalı** — çöp kutusu (`ATLANAN_DIZINLER`'de yok) |

**Kanıt (kategori sayımı, tekrarlanabilir):** `runpy` ile `scripts/marka_denetim.py` çalıştırılıp satırlar kategori başlığına göre sayıldı → yukarıdaki tablo. Toplam 140 = 41+31+17+16+11+10+7+6+1(özet satırı).

## B-2 (ORTA) — `ATLANAN_DIZINLER` eksik: çöp/submodule dizinleri taranıyor

`ATLANAN_DIZINLER = {.git, __pycache__, .pytest_cache, .ruff_cache, .mypy_cache, node_modules, .streamlit, data, venv, .venv, env}` — şunlar **yok**:
`_trash`, `.kilo`, `.agents`, `workspace`, `AI proje v1`, `test_reports`, `backups`.
Sonuç: çöp kutusu ve harici skill alt modülü taranıp ihlal listesine giriyor (`.agents/marketplace/**` "Hugging Face" eşleşmeleri).

## B-3 (ORTA) — `kok_dizin` kategorisi kendi belgesini ihlal sayıyor

`KOK_DIZIN = kok\s+dizindeki` deseni: (a) `marka_denetim.py`'nin kendi docstring/print metni, (b) `docs/plans/MARKA-REVIZE-01_brief.md` kabul kriteri, (c) `tests/test_marka_denetim.py` muafiyet testi — hepsi eşleşiyor. Test tarafında muafiyet tanımlı (`ref_sonuc` filtresi), ancak **script exit kodu** bundan etkileniyor → tam tarama asla temiz çıkmıyor.
## B-4 (DÜŞÜK) — `marka_denetim.py` docstring'i yasak listesini hatalı yazıyor

`scripts/marka_denetim.py:6-7`:
```
yasal_yazim: Huginn/Muninn/Odin yasak yazimlari (Huggin, Hugginn, Hugin,
             Munin, Muginn, Odin, Odinn, Muginn, Munnin)
```
- **`Odin` doğru yazımdır**, yasak listesinde olamaz → docstring yanlış.
- **`Muginn` iki kez** yazılmış.
- `Odın` (noktasız ı) docstring'de yok, ayrı regex'te (`ODIN_MISSPELLING`).
- `Huggin` docstring'de var; regex'te de var (`Huggin\b`) — tutarlı, ancak liste kopyası D-44 §1 ile birebir hizalanmalı.

## B-5 (DÜŞÜK) — `test_tarama_clean` muafiyeti metin eşleşmesine bağlı

`tests/test_marka_denetim.py:65` → `if "design-tokens" not in s`. Dosya-bazlı/satır-bazlı muafiyet yerine metin araması kullanılıyor; `docs/brand/` içine meşru bir yasak-liste satırı eklendiği anda test kırılıyor (bu turda **fiilen yaşandı**: 16 bulgu → test failed).

## B-6 (DÜŞÜK) — `docs/ROO_ELESTIRI_NOTLARI.md` D-33 durumu bayat

Satır 320: `AÇIK — görevde` yazıyor; MARKA-REVIZE-01 (doküman) + MARKA-REVIZE-01B (kod, done) tamamlandığına göre bu satır **ÇÖZÜLDÜ** olarak kapatılmalı (doküman katmanı roo'nun onay turunda).

---

## Öneri (kilo / ayrı tetik)

1. **Muafiyet sözleşmesi** — satır içi: `Yasak yazımlar` / `Yasak:` / `HATALI_YAZIM` / `YASAL_YAZIM` / `ODIN_MISSPELLING` / `KOK_DIZIN` içeren satırlar muaf; dosya-bazlı: `tests/**`, `scripts/marka_denetim.py`, `docs/plans/*_brief.md`, `docs/ROO_ELESTIRI_NOTLARI.md`, `_trash/**`, `.agents/**`, `AI proje v1/**`.
2. **`ATLANAN_DIZINLER` genişletmesi:** `_trash`, `.kilo`, `.agents`, `workspace`, `AI proje v1`, `test_reports`.
3. **Beyaz liste yaklaşımı (alternatif):** repo kökünde `data/marka_allowlist.json` (kalıp: `scripts/kodlama_denetim.py` allowlist) → `{dosya, satır, gerekçe}`; böylece meşru liste satırları gerekçeli muaf olur.
4. **Bekçi test:** muafiyet sözleşmesi için `tests/test_marka_denetim.py`'ye "yasak liste satırı muaf" + "çöp kutusu taranmaz" testleri.
5. **Brif kabul kriteri düzeltmesi:** "`python scripts/marka_denetim.py` → temiz" ifadesi, muafiyet sözleşmesi uygulandıktan sonra anlamlıdır; aksi halde her zaman exit 1 verir.

## Ortak Eleştiri (zincir özeti)

- **Zincir sırası doğru işledi** (cline → kilo → roo) ancak **kod katmanı, doküman katmanından önce** bitti (MARKA-REVIZE-01B 2026-09-17T03:07 done; MARKA-REVIZE-01 doküman 2026-09-17). Sonuç: kilo, cline'ın ekleyeceği yasak liste satırlarını **öngöremedi** → araç muafiyetsiz kaldı.
- **Öneri:** MARKA-REVIZE-01 gibi çift katmanlı zincirlerde kod katmanı, doküman katmanının **arbitraj kurallarını** (muafiyet sözleşmesi) brifte sabitlemeli; aksi halde katmanlar birbirini kırar.
- Bu bulgu **bu turda blokaj değildir**: hedef testler yeşil (1419 passed), `docs/brand/` temiz; yalnız denetim aracının tam tarama raporu yanlış pozitif üretiyor.