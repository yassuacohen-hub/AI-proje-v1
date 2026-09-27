# ALTYAPI-TEST-FAILURE-FIX-02 — Brif (UTKU)

## Görev
`docs/raporlar/test_kapsam_olcum_2026-09-20.md` Tablo 3'te listelenen 4 başarısız testi düzelt (2 kök neden).

## Kök neden 1 — sqlite tablo eksik
- `tests/test_job_intelligence_dikey.py::test_insert_batch_dedup_gercek_db`
- Hata: `sqlite3.OperationalError: no such table: job_postings`
- Zaten hazır brif var, oku ve uygula: `data/orchestrator/ALTYAPI-SQLITE-INIT_brif_2026-09-20_uretim.md`

## Kök neden 2 — PolicyEngine günlük limit
- `tests/test_mcp.py::TestPolicyEngine::test_evaluate_all_pass`
- `tests/test_mcp.py::TestApifyAdapter::test_apify_run_actor_no_client`
- `tests/test_mcp.py::TestApifyAdapter::test_apify_run_actor_with_mock_client`
- Kaynak: [`src/company_master/mcp/policy_engine.py:83`](src/company_master/mcp/policy_engine.py:83) `daily_spend_limit: float = 5.0` (default).
- Rapor diyor testte limit 0 görünüyor — testin `PolicyEngine(...)` çağrısını incele (muhtemelen `daily_spend_limit=0` ile örnekleniyor ama test senaryosu `cost_credits=0.5` geçmeyi bekliyor). Testin niyetini oku, ya testi düzelt ya da `policy_engine.py` mantığını düzelt — hangisi doğruysa. Testi kırma, davranışı netleştir.

## Doğrulama
```
python -X utf8 -m pytest tests/test_job_intelligence_dikey.py::test_insert_batch_dedup_gercek_db tests/test_mcp.py::TestPolicyEngine::test_evaluate_all_pass tests/test_mcp.py::TestApifyAdapter -xvs
python -X utf8 -m pytest tests/ -q
```

## Teslim
Rapor: `data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-02_rapor_2026-09-20_uretim.md` (D-67: 5 başlık, bulgular boş bırakılmaz).
