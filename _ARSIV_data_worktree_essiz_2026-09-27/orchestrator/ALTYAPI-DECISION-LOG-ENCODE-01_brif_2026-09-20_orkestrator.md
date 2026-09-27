# ALTYAPI-DECISION-LOG-ENCODE-01 Briefi

## GÖREV TANIMI
`data/orchestrator/decision_log.jsonl` dosyası UTF-8 kodlama sorunu taşıyor (D-77 bulgusu):
- Bulgu: Dosya Terminal.read_text(encoding='utf-8') ile açılırken UnicodeDecodeError (veya sessiz hata).
- Konum: ~46494 pozisyonunda UTF-8 dışı byte tespit edilmiş (earlier in conversation).
- Etki: `test_doc_audit.py::test_decision_log_yapisi_line_86` testi bu yüzden başarısız (`DID NOT RAISE UnicodeDecodeError`).

## İŞ MADDELERİ

1. **decision_log.jsonl dosyasını kurtarıp temizle:**
   - Dosyayı binary modunda aç, UTF-8 dışı byteları tanımla (position ~46494).
   - Mojibake karakterini sil veya düzeltilmiş byte ile yeniden yaz.
   - `python -X utf8 -m pytest tests/test_doc_audit.py::TestDocAudit::test_decision_log_yapisi_line_86 -xvs` sonucunu raporda yazın.

2. **Kodlama denetim komut dosyasına decision_log ekle:**
   - `scripts/kodlama_denetim.py` decision_log.jsonl'u kontrol listesine ekle (BOM, NUL, non-UTF-8 byte taraması).
   - Raporda: `python scripts/kodlama_denetim.py` çıktısı (decision_log clean olmalı).

3. **Pre-commit hook güncelle (varsa):**
   - `.git/hooks/pre-commit` veya `scripts/` pre-commit script'i decision_log.jsonl'u tarama listesine ekle.

## KENDİ-KONTROL

```bash
# 1. Dosya kodlama doğrulaması
python -X utf8 -c "
with open('data/orchestrator/decision_log.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f'Total lines: {len(lines)}')
print('UTF-8 valid: YES')
"
# Başarısız: UnicodeDecodeError veya hata çıkmaması beklenir.
# Başarılı: "Total lines: N" ve "UTF-8 valid: YES"

# 2. Test tekrarı
python -X utf8 -m pytest tests/test_doc_audit.py::TestDocAudit::test_decision_log_yapisi_line_86 -xvs
# Beklenen: PASS (test artık UnicodeDecodeError raise etmesini beklemiyor veya dosya geçerli)

# 3. Kodlama denetimi
python scripts/kodlama_denetim.py
# Çıktı: decision_log.jsonl yoksa veya clean ise tamam
```

## BEKLENEN ÇIKTI
- `data/orchestrator/decision_log.jsonl` UTF-8 temiz.
- `test_doc_audit.py::test_decision_log_yapisi_line_86` testten PASS.
- Full suite test sayısı: 3978 passed (veya green).
- Rapor dosyası: `data/orchestrator/ALTYAPI-DECISION-LOG-ENCODE-01_rapor_<tarih>_orkestrator.md`
  - Bölüm 1: Ne yapıldı (mojibake pozisyonu, düzeltme adımları)
  - Bölüm 2: Değişen dosyalar (decision_log.jsonl, maybe kodlama_denetim.py, pre-commit)
  - Bölüm 3: Test sonuçları (test_doc_audit testi geçti, full suite sayısı)
  - Bölüm 4: Bulgular (varsa ek kodlama sorunu)
  - Bölüm 5: Eksik/Erteleme
