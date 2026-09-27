# ORKESTRA-DECISION-LOG-FORMAT-01 Bribi

## Görev
Decision log format standardını implement et. Mevcut `data/orchestrator/decision_log.jsonl` her satırı JSON olmakta — schema net değil. D-XX kararlarının şablonu oluştur.

## İş Maddeleri
1. [`src/company_master/orchestrator/decision_log.py`](src/company_master/orchestrator/decision_log.py) — `DecisionRecord` dataclass yaz (D-XX, kategori, başlık, açıklama, tarih, imza)
2. [`data/orchestrator/decision_log.jsonl`](data/orchestrator/decision_log.jsonl) — Mevcut satırları validasyon et, eksik alanları doldur
3. [`scripts/karar_ekle.py`](scripts/karar_ekle.py) — D-XX karar ekleme CLI (argparse, `DecisionRecord` + atomik yazma)
4. [`tests/test_decision_log.py`](tests/test_decision_log.py) — Unit testler (schema doğrulama, CLI testleri)

## Doğrulama
```bash
python -X utf8 -m pytest tests/test_decision_log.py -q
python scripts/karar_ekle.py ekle --d-xx D-80 --kategori ORCH --baslik "Test kararı" --aciklama "Test"
grep '"D-80"' data/orchestrator/decision_log.jsonl
```

## Ek Notlar
- UTF-8 BOM kontrol edilmeli (kodlama_denetim.py)
- Zincir teslimi önce YASU inceleyecek
