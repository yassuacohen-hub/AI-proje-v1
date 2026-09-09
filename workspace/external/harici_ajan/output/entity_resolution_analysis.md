# Entity Resolution Analizi

## Kapsam
- Modul: src/company_master/etl/entity_resolution.py (4755 bayt)
- Amac: source_records -> companies VKN/fuzzy matching

## Onemli Noktalar
1. **Iki asamali eslestirme:**
   - VKN exact match (100% confidence)
   - Name fuzzy match (SequenceMatcher, threshold >= 0.85)
2. **Performans:** Tum companies tek seferde cekilir, VKN index + name list olusturulur
3. **Sonuclar:** entity_resolution tablosuna match_score, match_method, decision kaydedilir

## Eksiklikler ve Oneriler
- _similarity fonksiyonu SequenceMatcher kullaniyor - rapidfuzz/thefuzz ile daha iyi sonuc
- Fuzzy threshold 0.85 cok yuksek olabilir, dusuk degerde denerilmeli
- Partial match (name + tax_number kombinasyonu) eklenebilir
