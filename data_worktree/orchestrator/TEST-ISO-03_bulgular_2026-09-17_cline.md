[[Huginn Data Insights/data/orchestrator/TEST-ISO-03_bulgular_2026-09-17_cline.md]]

# TEST-ISO-03 — firmalar.jsonl test kalıntısı kök neden + düzeltme (cline, 2026-09-17)

**Görev:** yok (panodan bağımsız kendi bulgumun tespiti; GIT-HIJYEN-01 çapraz inceleme notundaki madde 4'ün çözümü)
**Kapsam:** yalnız test altyapısı — üretim davranışı DEĞİŞMEDİ.

## Kök neden (kanıtlı)
`tests/company_master/test_base_osfb_scraper.py` — eski sürüm:
- `DummyScraper.STATE_DIR = Path("data/dummy")` + `STATE_DIR.mkdir(...)` **sınıf gövdesinde** → test modülü import edilir edilmez gerçek repo dizini oluşturuluyordu.
- `scrape()` çıktısı `OUTPUT_PATH = data/dummy/firmalar.jsonl`'e **append** modunda yazıyordu → her tam süit koşusunda git'te takip edilen dummy veriye 1 "Test Firma" satırı ekleniyordu (bugün +24 satır; dosya 180. satırdan sonra damgalı kayıtlarla dolu).
- `test_state_management` gerçek `.scrape_state.json` okuyup yazıyordu (`.scrape_state.json` LastWriteTime = son süit damgası 20:26:29 ile kanıtlandı).

## Düzeltme (TEST-ISO-03)
`tests/company_master/test_base_osfb_scraper.py`:
- Sınıf gövdesinden `mkdir` ve gerçek yollar kaldırıldı; DummyScraper docstring'ine regresyon notu eklendi.
- Yeni `scraper` fixture'ı: `STATE_DIR` / `STATE_PATH` / `OUTPUT_PATH` → `tmp_path`.
- 4 test fixture'a geçirildi; `test_state_management` ve `test_scrape_yields_firmalar` artık **gerçek dosyanın bytes'ını koşu öncesi/sonrası md5-benzeri kıyaslayarak izolasyonu assert'liyor** (`once == sonra`).

## Doğrulama (komut + ham çıktı)
```
python -m pytest tests/company_master/test_base_osfb_scraper.py -q --tb=short
→ 5 passed in 0.19s
boyut once=63945 sonra=63945   (gerçek firmalar.jsonl DEĞİŞMEDİ — önceki davranışta her koşu +1 satır idi)

python -X utf8 -m pytest -q   (TAM SÜİT)
→ 3843 passed, 5 skipped, 129 warnings in 198.07s   (0 failed)

python -X utf8 scripts/kodlama_denetim.py
→ temiz: kodlama ihlali yok / allowlist dışı ihlal yok
```

## roo kararı bekleyen madde
- `data/dummy/firmalar.jsonl` içindeki **2026-09-17 damgalı ~24 test kalıntısı** ve `.scrape_state.json` — düzeltme sonrası artık büyümeyecek; mevcut kalıntıların git ile geri alınması (checkout) roo'nun sabah commit turunda. Ben dokunmadım (veri dosyası + git checkout kilo kural setinde yasak).
- `tests/test_post_scrape_workflow.py` benzer risk taşımıyor (pano yalıtımı `izole_pano` fixture'ı ile zaten sağlanıyor; `test_main_gercek_panoya_yazmaz` regresyon testi mevcut).

**Test: 3843 passed / 0 failed · Kodlama denetimi: temiz · Üretim dosyası değişikliği: yok (yalnız test dosyası)**
