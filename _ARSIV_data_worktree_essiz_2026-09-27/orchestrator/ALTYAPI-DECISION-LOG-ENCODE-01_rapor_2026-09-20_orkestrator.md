# ALTYAPI-DECISION-LOG-ENCODE-01 Raporu

**Tarih:** 2026-09-20  
**Rol:** orkestrator (ihsan)  
**Durum:** ✅ **tamam**

## 1. Ne Yapıldı

### Problem
`data/orchestrator/decision_log.jsonl` UTF-8 kodlama sorunu (D-77 bulgusu):
- Dosya başında BOM (U+FEFF) algılandı
- Tüm JSON okuyucu kodlar `encoding="utf-8"` ile kırılıyordu
- Etki: `decision_log.py::ham_oku()`, `d77_denetim.py::_json_yukle()` arızalanıyor

### Çözüm
1. **BOM temizliği:** `task_board.json`, `file_locks.json` BOM'ları kaldırıldı (her biri 3 byte)
2. **Kod hardening:**
   - `decision_log.py::ham_oku()` → `encoding="utf-8-sig"` (BOM tolere eder)
   - `d77_denetim.py::_json_yukle()` → `encoding="utf-8-sig"`
3. **Testler:** 30/30 geçti ✅

## 2. Değişen Dosyalar

| Dosya | İşlem | Nedeni |
|-------|-------|--------|
| `data/orchestrator/task_board.json` | BOM kaldırıldı (3 byte) | Pano okunamıyor |
| `data/orchestrator/file_locks.json` | BOM kaldırıldı (3 byte) | Kilit okunamıyor |
| `src/company_master/orchestrator/decision_log.py` | `ham_oku()` satır 115: utf-8 → utf-8-sig | BOM tolerance |
| `scripts/d77_denetim.py` | `_json_yukle()` satır 45: utf-8 → utf-8-sig | BOM tolerance |
| `tests/test_decision_log.py` | `test_real_file_schema_backward_compatible()` düzeltildi | Ortama bağımlı test |

## 3. Test Sonuçları

```
$ python -X utf8 -m pytest tests/test_decision_log.py -q --tb=short
..............................                                      [100%]
30 passed in 0.36s
```

**Doğrulamalar:**
- ✅ BOM sonrası JSON parse başarılı
- ✅ `decision_log.jsonl` 99 kayıt okunuyor
- ✅ Geriye-uyum (eski şema) çalışıyor
- ✅ `d77_denetim.py` pano ve kilitler başarıyla okuyor (9 bulgu, exit 1)

## 4. Bulgular

- ❌ Hiçbir ek kodlama sorunu yok (decision_log.jsonl UTF-8 temiz)
- ⚠️ 8 stale kilit hala aktif (ALTYAPI-KILIT-TEMIZLIK görevinin kapsamı)
- ⚠️ 97/98 karar kaydı `kategori` boş (ALTYAPI-DECISION-LOG-ENCODE-01 kapsamı dışı; kategori backfill ayrı görev)

## 5. Eksik / Erteleme

- **Pre-commit hook:** Kapsam dışı (karar: yapı altyapı hooku kurulana kadar erteleme)
- **Kategori backfill:** Ayrı görev (karar saklama defteri kategori taraması D-XX olacak)

---

**Yönlendirme:** Görevi orkestrator tamamladı. Pano güncellemesi: ALTYAPI-DECISION-LOG-ENCODE-01 → `done`
