# HANDOFF-TEMIZ-01 — P0-2 handoff/pano tarih damgası temizliği (cline, P2)

Kaynak: `data/orchestrator/TEST-ISO-02_bulgular_2026-09-17_cline.md` bölüm 7-10 (cline önerisi).

## Kapsam
- `data/orchestrator/handoffs.json` ve `task_board.json` içinde **P0-2** kaydının test-zamanı damgalı `bitis`/`tarih` alanlarını git geçmişinden (`git log -p -- data/orchestrator/handoffs.json`) gerçek ilk değere döndür.
- Aynı kalıpta (test kaynaklı yeniden yazılmış) başka kayıt varsa listele, düzeltme yalnız P0-2; diğerleri rapora.
- Regresyon: `tests/test_post_scrape_workflow.py` izole fixture'ının gerçek panoya yazmadığını doğrulayan tek test ekle (md5 öncesi/sonrası).

## Sınırlar
- Kilo canlı görevlerinin (VEC-TEST-01 … API-SPLIT-01) kayıtlarına dokunma; yalnız P0-2 alanları.
- Commit ATMA.

## Teslim
- Rapor: `data/orchestrator/HANDOFF-TEMIZ-01_rapor_<tarih>_cline.md`
- `python scripts/gorev_kutusu.py teslim --ajan cline --task-id HANDOFF-TEMIZ-01`
