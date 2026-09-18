# MARKA-REVIZE-01 Raporu — Doküman Katmanı

**Tarih:** 2026-09-17
**Ajan:** cline (doküman katmanı)
**Brif:** `docs/plans/MARKA-REVIZE-01_brief.md` (D-44/D-45)
**Zincir konumu:** 1/3 — cline (doküman) → kilo (kod, MARKA-REVIZE-01B done) → roo (onay/commit)

---

## 1. Yapılan Değişiklikler (dosya:satır → iş)

| # | Dosya | Değişiklik |
|---|---|---|
| 1 | `AGENTS.md:49` | Yasak yazım listesi tam hale getirildi: `Huggin, Hugginn, Hugin, Munin, Muginn, Munnin, Odinn, Odın` |
| 2 | `AGENTS.md:50` | Marka kiti köprü satırı eklendi: üretim kaynağı `docs/brand/`, kapsam ayrımı için AJAN_DETAY §11 |
| 3 | `ANA_KURALLAR.md:81` | Yasak yazım listesi tam hale getirildi (Huggin/Hugginn/Odinn eklendi) |
| 4 | `ANA_KURALLAR.md:86-87` | Marka kiti köprü satırı (`docs/brand/` + §11 kapsam ayrımı) |
| 5 | `docs/AJAN_DETAY.md:107` | Yasak yazım listesi tam hale getirildi |
| 6 | `docs/AJAN_DETAY.md:111-118` | **YENİ alt bölüm:** "Marka kiti: `docs/brand/` (D-44/D-45 kapsam ayrımı)" — okuma sırası, iki palet/iki kapsam (birleştirme yok), §11 üstünlüğü |
| 7 | `docs/brand/README.md:5-6` | Bayat "kok dizindeki ai-rules.md ifadeleri" cümlesi → "Tüm marka üretimi bu klasördeki ai-rules.md ile başlar" |
| 8 | `docs/brand/README.md:33` | Durum bölümüne MARKA-REVIZE-01 doküman katmanı kaydı |
| 9 | `docs/brand/ai-rules.md:3-6` | D-45 kapsam notu (pazarlama vs ürün UI, iki palet birleşmez) + izinli yazım listesi + §11 atfı |
| 10 | `docs/brand/company.md:3-7` | D-45 kapsam notu + izinli yazım listesi + §11 atfı |
| 11 | `docs/brand/assets/LOGO.md:3` | `kok dizinindeki ai-rules.md` → `docs/brand/ai-rules.md` |
| 12 | `docs/brand/assets/LOGO.md:6` | `kok dizindeki brand.md` → `docs/brand/brand.md`; `design-tokens.json` → `docs/brand/design-tokens.json` |
| 13 | `docs/brand/prompts/system.md:3` | `kok dizindeki ai-rules.md` → `docs/brand/ai-rules.md` |
| 14 | `docs/brand/prompts/website.md:3,5` | `kok dizinindeki ai-rules.md` → `docs/brand/ai-rules.md`; `kok brand.md` → `docs/brand/brand.md` |
| 15 | `docs/brand/prompts/dashboard.md:3,5` | Aynı düzeltme + `brand.md` → `docs/brand/brand.md` |
| 16 | `docs/brand/prompts/marketing.md:3,5` | Aynı düzeltme + `brand.md` → `docs/brand/brand.md` |
| 17 | `docs/brand/personas/*.md` (5 dosya):3 | `kok dizindeki ai-rules.md ve company.md` → `docs/brand/ai-rules.md ve docs/brand/company.md` (founder, investor, analyst, accelerator, consultant) |
| 18 | `plans/MRK_marka_ve_dil_paketi_plani.md:5-7` | Marka kiti konumu bloğu eklendi (eski "kök dizin" atıfları `docs/brand/`) |
| 19 | `plans/MRK_marka_ve_dil_paketi_plani.md:147` | Marka yazımı bekçisi 13: regex tam listeye çıkarıldı + tarama kapsamı `docs/brand/**/*.md` |
| 20 | `plans/MRK_marka_ve_dil_paketi_plani.md:241` | S10 karar satırı: yasak yazım listesi tam hale getirildi |
| 21 | `plans/brief_cline_MRK02fg.md:3-5` | Başa "ARŞİV — tamamlandı, güncel: `docs/brand/`" notu (içerik silinmedi) |
| 22 | `plans/brief_kilo_MRK03_MRK04.md:3-5` | Başa "ARŞİV — tamamlandı, güncel: `docs/brand/`" notu (içerik silinmedi) |
| 23 | `plans/muninn_prn_vs_huginn_analiz.md:3-5` | Marka kiti köprüsü eklendi (yazım denetimi: içerikte hatalı yazım yok) |

**Toplam:** 23 düzenleme / 18 dosya. `docs/brand/` içinde 13 bayat "kok dizin" atfı düzeltildi.
## 2. Doğrulama Kanıtları

| Kriter | Komut | Sonuç |
|---|---|---|
| Bayat kök dizin atfı yok | `findstr /s /i "kok dizin" docs\brand\*.md docs\brand\*\*.md` | **0 satır** (exit 1) ✓ |
| Yasak yazım (hedef dosyalar) | `findstr /s /i /n "Huggin" AGENTS.md ANA_KURALLAR.md docs\*.md docs\brand\*.md plans\*.md` | Kalan satırların tamamı **yasak listesi / regex bekçisi / brif referansı** → brif'e göre muaf ✓ |
| `docs/brand/` temizlik | `tarama(docs/brand)` (test üzerinden) | `docs/brand/` içinde yasak yazım **0** ✓ |
| Birim testler | `python -m pytest tests/test_i18n.py tests/test_marka_denetim.py -q` | **1419 passed**, 0 failed ✓ |
| Kodlama denetimi (dokunulan dosyalar) | `python scripts/kodlama_denetim.py` | Düzenlenen 18 dosya için **0 bulgu**; repodaki mevcut CRLF/tab bulguları (60 dosya) GUARD-ENC-02 kapsamında, bu görevle ilgisiz ✓ |
## 3. Karar Notu (neden yasak listesi `docs/brand/` içinde yazılmadı)

Brif iki kabul kriteri arasında gerilim vardı:
- `findstr "Huggin"` → "yalnız **yasak listesi satırları muaf**" (yani liste görünebilir)
- `pytest tests/test_marka_denetim.py -q` **yeşil** olmalı; `test_tarama_clean` ise `docs/brand/` taramasında yasak yazım **0** bekliyor (istisna yalnız `design-tokens.json`).

Kilo'nun `scripts/marka_denetim.py` aracı yasak liste satırları için muafiyet uygulamadığından, `docs/brand/company.md` ve `ai-rules.md` içine yasak kelime listesi yazmak testi **kırıyordu** (16 bulgu). Çözüm:
- `docs/brand/` içinde yalnız **izinli yazım listesi** (`Huginn / Muninn / Odin`) tutuldu,
- yasak yazımların tam listesi **teknik SSOT** `docs/AJAN_DETAY.md` §11'e atıfla bırakıldı.

Bu, D-44 §1'i zayıflatmaz: yasak liste AGENTS.md, ANA_KURALLAR.md, §11 ve MRK planında eksiksizdir; kit yalnız atıf yapar. Sonuç: hem test yeşil hem kural görünür.

## 4. Dikkat (Eleştirel Notlar)

1. **`scripts/marka_denetim.py` yanlış pozitif üretiyor** — yasak liste satırları muaf tutulmuyor; tam tarama `Toplam ihlal: 140` veriyor ve büyük çoğunluğu meşru liste/brief/regex satırları. Ayrıntı: `data/orchestrator/MARKA-REVIZE-01_bulgular_2026-09-17_cline.md`.
2. **Zincir kabul kriteri `python scripts/marka_denetim.py` → temiz** bu haliyle **karşılanamıyor**; kilo'nun muafiyet/kapsam düzeltmesi gerekiyor (MARKA-REVIZE-01B done olmasına rağmen).
3. **`test_tarama_clean` istisnası kırılgan** — `"design-tokens" not in s` gibi metin eşleşmesi yerine dosya-bazlı muafiyet (yasak liste satırı muafiyeti) tercih edilmeli.
4. `docs/ROO_ELESTIRI_NOTLARI.md` D-33 satırı hâlâ "AÇIK — görevde" diyor; bu tur sonrası roo kapatmalı.
5. Kapsam dışı olduğu için `tests/test_i18n.py`, `.streamlit/config.toml`, `scripts/marka_denetim.py` **değiştirilmedi** (kilit disiplini).

## 5. Öneri

`marka_denetim.py` için muafiyet sözleşmesi (kilo, ayrı tetik):
- Satır içi muafiyet: `Yasak yazımlar` / `Yasak:` / `HATALI_YAZIM` / regex bekçisi içeren satırlar,
- Dosya-bazlı muafiyet: `docs/plans/*_brief.md`, `docs/ROO_ELESTIRI_NOTLARI.md`, `tests/**`, `scripts/marka_denetim.py`, `_trash/**`, `.agents/**`, `AI proje v1/**`,
- `ATLANAN_DIZINLER` genişletmesi: `_trash`, `.kilo`, `.agents`, `workspace`, `AI proje v1`.