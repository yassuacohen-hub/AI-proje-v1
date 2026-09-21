# ALTYAPI-KILIT-TEMIZLIK-V10-01 Brifingi

## Görev Tanımı
Tamamlanmış görevler (V10-HIJYEN-01, V10-HIJYEN-02) üzerinde hâlâ kilitli olan dosyaları serbest bırakmak. ORKESTRA-STALE-TEMIZLIK-01 raporunda 2+ gün eski kilitlerin temizlenmesi önerildi.

## Kilitli Dosyalar (Rapordan)

| Dosya | Görev | Durum | Kilit Sahibi | Süre |
|-------|-------|-------|--------------|------|
| src/company_master/search/engine.py | V10-HIJYEN-01 | done | roo | >2 gün |
| tests/test_search_engine_where.py | V10-HIJYEN-01 | done | roo | >2 gün |
| src/company_master/search/fulltext.py | V10-HIJYEN-02 | done | roo | >2 gün |

## İş Maddeleri

1. **Kilitlü dosyaları kontrol et:**
   ```bash
   python -X utf8 -c "
   import json
   from pathlib import Path
   locks = json.loads(Path('data/orchestrator/file_locks.json').read_text())
   v10_files = {
       'src/company_master/search/engine.py': 'V10-HIJYEN-01',
       'tests/test_search_engine_where.py': 'V10-HIJYEN-01',
       'src/company_master/search/fulltext.py': 'V10-HIJYEN-02',
   }
   for f, task_id in v10_files.items():
       if f in locks:
           lock = locks[f]
           print(f'{f}:')
           print(f'  Task: {lock.get(\"task_id\")}')
           print(f'  Sahip: {lock.get(\"sahip\")}')
           print(f'  Zaman: {lock.get(\"zaman\")}')
   "
   ```

2. **Kilidi bırak (3 dosya):**
   ```bash
   python scripts/task_board.py lock_birak --dosya "src/company_master/search/engine.py" --sahip "roo"
   python scripts/task_board.py lock_birak --dosya "tests/test_search_engine_where.py" --sahip "roo"
   python scripts/task_board.py lock_birak --dosya "src/company_master/search/fulltext.py" --sahip "roo"
   ```
   Veya doğrudan Python:
   ```bash
   python -X utf8 -c "
   from pathlib import Path
   from src.company_master.orchestrator.task_board import lock_birak
   lock_birak('src/company_master/search/engine.py', 'roo')
   lock_birak('tests/test_search_engine_where.py', 'roo')
   lock_birak('src/company_master/search/fulltext.py', 'roo')
   print('✓ 3 kilit bırakıldı')
   "
   ```

3. **Doğrula:**
   ```bash
   python -X utf8 -c "
   import json
   from pathlib import Path
   locks = json.loads(Path('data/orchestrator/file_locks.json').read_text())
   v10_files = [
       'src/company_master/search/engine.py',
       'tests/test_search_engine_where.py',
       'src/company_master/search/fulltext.py',
   ]
   for f in v10_files:
       if f in locks:
           print(f'✗ {f}: hâlâ kilitli')
       else:
           print(f'✓ {f}: serbest')
   "
   ```

## Self-Check

- [ ] 3 dosyanın kilidi kontrol edildi
- [ ] 3 dosya serbest bırakıldı (lock_birak çalıştırıldı)
- [ ] file_locks.json 3 satır eksik (verify)
- [ ] V10-HIJYEN-01, V10-HIJYEN-02 görevleri done ve dosyaları serbest

## Rapor

Başarıyla tamamlanırsa:
- Değişen dosyalar: `data/orchestrator/file_locks.json` (3 satır silindi)
- Test: 3 dosya file_locks.json'dan silinmişse ✓
- Rapor: `data/orchestrator/ALTYAPI-KILIT-TEMIZLIK-V10-01_rapor_2026-09-20_orkestrator.md`

Rapor dosyası 5 başlık içermelidir.
