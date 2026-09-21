# ALTYAPI-SQLITE-INIT Briefi

## GÖREV TANIMI
UTKU, test suite'de `test_insert_batch_dedup_gercek_db` testi başarısız oluyor: `sqlite3.OperationalError: no such table: job_postings`.

Görev: `job_postings` tablosunu SQLite veritabanında oluştur veya migration'ı çalıştır.

## İŞ MADDELERİ

1. **Test hatasını doğrula:**
   ```bash
   python -X utf8 -m pytest tests/test_job_intelligence_dikey.py::test_insert_batch_dedup_gercek_db -xvs
   ```
   Hata: `sqlite3.OperationalError: no such table: job_postings`

2. **job_postings tablosu olup olmadığını kontrol et:**
   ```bash
   python -c "
   from src.company_master.db.connection import get_engine
   from sqlalchemy import text, inspect
   
   engine = get_engine()
   insp = inspect(engine)
   tables = insp.get_table_names()
   print('job_postings' in tables)  # True/False
   "
   ```

3. **Tablo eksikse migration/schema'yı çalıştır:**
   - `src/company_master/db/migrations/` veya `src/company_master/db/schema.sql` dosyasını bulup kontrol et.
   - Ya tablo tanımını migration'a ekle, ya `schema.sql` yeniden çalıştır.
   - Tablo oluştur:
     ```bash
     python src/company_master/db/init_tables.py  # varsa
     # veya
     python -c "from src.company_master.db.connection import init_db; init_db()"
     ```

4. **Testi tekrarla:**
   ```bash
   python -X utf8 -m pytest tests/test_job_intelligence_dikey.py::test_insert_batch_dedup_gercek_db -xvs
   ```
   **Beklenen:** PASS

5. **Tam test kümesini çalıştır:**
   ```bash
   python -X utf8 -m pytest tests/ -q
   ```
   **Beklenen:** Hata düşmeli (en az 3972 passed).

## KENDİ-KONTROL

```bash
# Tablo kontrol
python -c "
from src.company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM job_postings'))
    count = result.scalar()
print(f'job_postings tablo var, {count} satır')
"

# Test başarı
python -X utf8 -m pytest tests/test_job_intelligence_dikey.py::test_insert_batch_dedup_gercek_db -xvs
# Beklenen: PASSED
```
