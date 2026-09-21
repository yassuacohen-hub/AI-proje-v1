[[Huginn Data Insights/data/orchestrator/GUARD-ENC-01_teslim_2026-09-16_cline.md]]

# GUARD-ENC-01 Teslim — kodlama guard'i tam devreye alindi (cline, 2026-09-16)

**Kapsam:** `scripts/kodlama_denetim.py` · `tests/test_kodlama_denetim.py` · `.pre-commit-config.yaml` (+ ratchet'i yeşile çekmek için 4 onarım)

## Yapılanlar
1. **Test dosyası adlandırma:** `tests/test_kodlama_guard.py` → `tests/test_kodlama_denetim.py` (`git mv`; görev tanımı ve tek doküman referansı `docs/PERF_TEMIZLIK_NOTLARI_2026-09-15.md` hizalandı). **12 test passed.**
2. **Pre-commit entegrasyonu:** `.pre-commit-config.yaml`'a local hook eklendi: `python -X utf8 scripts/kodlama_denetim.py --kapsam git` (always_run, changed-file modu). YAML PyYAML ile doğrulandı → hook sırası `bandit, safety, kodlama-denetim`. **Not:** `pre-commit` paketi bu ortamda kurulu değil; `pre-commit install` ilk kullananın ortamında bir kez çalıştırılmalı.
3. **`--kapsam git` modu doğrulandı:** çalışma ağacındaki 24 değişen dosyada tarama → "temiz: kodlama ihlali yok", exit 0.
4. **Ratchet'i yeşile çekme (muafiyet YOK — kök neden onarımı):**
   - `tests/test_kariyernet.py`: UTF-8 BOM kaldırıldı (3 byte) → `utf8_bom` ratchet ihlali bitti (P7-6b sonrası sahipsiz kalıntı).
   - `src/.../job_intelligence/sources/company_career.py`: 22 satır çift-kodlama (mojibake) `scripts/mojibake_onar.py` ile onarıldı (duzeltilen=22, kalan=0) — yalnızca docstring/log metni; iş mantığı dokunulmadı (job_intelligence 36 test passed).
   - `src/data_quality_toolkit/classifier/pii_scanner.py` L75: 184-karakterlik regex literali `\uXXXX` kaçış formuna çevrildi; **davranış kanıtı:** eski/yeni derlenmiş desen karakter kümesi birebir eşit + 7 örnek e-postada birebir aynı eşleşme.
   - `tests/test_admin_export_excel.py` L80 + `scripts/mojibake_onar.py` L5/L23: aynı kaçış dönüşümü; `MOJIBAKE_RX` kanıtı: 5 mojibake örneğini yakalar, 4 temiz Türkçe örneğine dokunmaz; docstring içeriği değişmedi.
5. **Kök-cause tarama artık BOM'suz/NUL'suz:** `.pre-commit-config.yaml` UTF-16 LE+BOM'dan UTF-8'e çevrildi.

## Kabul Kanıtları
- Varsayılan kapsam taraması: `temiz: kodlama ihlali yok`, allowlist dışı ihlal yok, **exit 0**
- `--kapsam git`: 24 dosya, temiz, exit 0 (hook'un commit'te yeşil kalacağının kanıtı)
- `tests/test_kodlama_denetim.py` 12 passed · `test_admin_export_excel.py` + `test_kodlama_denetim.py` 21 passed · job_intelligence 36 passed
- Teslim dosyalarının 9/9 byte-düzey denetimi: BOM yok, NUL yok, strict UTF-8 OK, mojibake göstergesi yok, ast.parse OK

## Notlar
- Guard **kapsam dizinleri** (src/tests/web_dashboard/scripts) içinde çalışır; kök dosyalar (app.py, config'ler) yalnız `--kapsam git` modunda değiştiyse taranır.
- Allowlist'te yalnız "AI proje v1" arşiv klasörü kayıtlı; aktif kod tarafında geçici muafiyet kalmadı.
