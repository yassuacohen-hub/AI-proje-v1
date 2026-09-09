# Normalize Analizi

## Kapsam
- Modul: src/company_master/etl/normalize.py (4108 bayt)
- Amac: source_records -> companies (NORMALIZATION)

## Onemli Noktalar
1. **Idempotent:** LEFT JOIN ile company_id IS NULL kontrolu, tekrar calistirma guvenli
2. **NACE Guvenilirlik:** nace_confidence (high/medium/low) -> nace_validity
3. **data_quality_score:** 70 (phone var), 40 (yok) - basit scoring
4. **Batch Insert:** Tek transaction icinde toplu yazma

## Eksiklikler ve Oneriler
- Daha detayli data_quality_score (adres, web, email, telefon agirliklari)
- Trade name / company_type parsing eklenebilir
- Validation hatti eklenebilir (required fields check)
