# Brief: TRIGGER-LOGGING-CLEANUP

## Görev
`[ALTYAPI] trigger.py logging cleanup: print→logger, except→logger.exception (2s)`

**Task ID:** TRIGGER-LOGGING-CLEANUP  
**Ajan:** yasu  
**Öncelik:** P1  
**Tarih:** 2026-09-23

---

## İş Maddeleri

1. **trigger.py temizliği:** `Huginn Data Insights/src/company_master/orchestrator/trigger.py`
   - Tüm `print()` çıktılarını `logger.info()` ile değiştir
   - Tüm `except:` bloklarında sessiz exception'ları `logger.exception()` ile değiştir
   - D-190 yorum bloklarını sil (kapsam dışı notlar)

2. **Test kontrolü:**
   - Testler: `tests/test_trigger.py`, `tests/test_tetik_senk.py`, `tests/test_mojibake_dizin.py`, `tests/test_task_board_kilit.py`
   - Hedef: 34 test yeşil (D-190 rapor başvurmuş)

3. **Teslim:**
   - Rapor: `data/orchestrator/TRIGGER-LOGGING-CLEANUP_rapor_2026-09-23_denetim.md`
   - Git staged: `trigger.py` + test dosyaları
   - Commit hazır (strateji: D-77 sonrası push)

---

## Referans

- **YASU-TRIGGER-CLEANUP-STRATEJI:** `data/orchestrator/YASU-TRIGGER-CLEANUP-STRATEJI-2026-09-23.md`
- **D-77:** Pano monopolü (orkestratör antes)
- **D-68:** Tetik-pano sinkronizasyonu (D-190 uygulaması)
- **D-190:** Yorum blokları silinmesi kararı

---

## Sonraki Adım

Bu görev teslim edildikten sonra:
1. Orkestratör (İhsan) TRIGGER-LOGGING-CLEANUP'ı panoya ekle (`gorev-at` komutu)
2. `tetik_senk.py` D-68 kuralıyla otomatik senkronize olur
3. Push yetkisi yasu'ya (D-80 kuralı, kod = altyapı)
