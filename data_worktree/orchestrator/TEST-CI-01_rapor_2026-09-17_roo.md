[[Huginn Data Insights/data/orchestrator/TEST-CI-01_rapor_2026-09-17_roo.md]]

# TEST-CI-01 Raporu (roo — 2026-09-17, D-49 backlog)

## Yapılanlar
- `scripts/pano_guard.py` (YENİ): `data/orchestrator/*.json` md5 anlık görüntü (`snapshot --out`) ve karşılaştırma (`check --in`); fark varsa GitHub `::error::` annotasyonu + çıkış kodu 1.
- `.github/workflows/ci.yml`: `COVERAGE_THRESHOLD` 80 → 85 (ölçülen ~%88); `PYTEST_TIMEOUT_SN=300`; `pytest-timeout` kurulumu; pytest `-p no:cacheprovider --timeout=...`; test öncesi snapshot, test sonrası `if: always()` izolasyon kontrolü (TEST-ISO-02 guard).
- `requirements-dev.txt`: `pytest-timeout>=2.3.0`.
- `tests/test_ci_workflow.py` (YENİ, 11 test): pano_guard davranışı + ci.yml sözleşmesi (adım sırası, eşik, timeout, cacheprovider).

## Doğrulama
- `pytest tests/test_ci_workflow.py` → 11 passed.
- `pano_guard snapshot` (53 dosya) → `check` → OK.
- Anthropic/OIDC workflow'ları, Codecov ve secrets değişmedi. `-x` eklenmedi (matris raporu tam kalsın).

## Kapsam dışı bulgular (düzeltilmedi)
- `kodlama_denetim.py`: `scripts/apify_webhook_receiver.py` CRLF karışık + sondaki boşluk (L130/135/138/142/263/283/514/614); `_arsiv/9r05/*`, `benchmark_webhook_load.py`, `dash04_smoke_test.py` dosya_sonu → GUARD-ENC-02 backlog.
- Yerelde `pytest-timeout` kurulu değil → `pip install pytest-timeout` (isteğe bağlı).

## Durum
- Commit YOK (sabah roo). Pano: done (roo kendi işi, roo onayı).
