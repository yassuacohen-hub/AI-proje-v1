# TEST-CI-01 — CI test işi sertleştirme (cline, P2)

## Kapsam
- `.github/workflows/` içindeki test işini incele: `pytest -x -q --timeout=300` (pytest-timeout varsa; yoksa `requirements-dev.txt`'e ekle), `-p no:cacheprovider`.
- Pano artefaktı izolasyon guard'ı: test öncesi/sonrası `data/orchestrator/*.json` md5 karşılaştırması; fark varsa iş kırmızı (TEST-ISO-02 sızıntılarının CI'da yakalanması).
- Kapsam eşiği: `--cov-fail-under` mevcut değerin altına düşürülmez (şu an ~%88); yoksa 85 ile başlat.
- `pytest.ini` yalnız gerekiyorsa (timeout varsayılanı) değişir.

## Sınırlar
- Anthropic PR review / OIDC workflow'una dokunma (`docs/ANTHROPIC_OIDC_KURAL.md`).
- Secrets/Codecov token ekleme yok (sahip işi).
- Commit ATMA; workflow yerelde `python -c "import yaml; yaml.safe_load(open(...))"` ile doğrulanır.

## Teslim
- Rapor: `data/orchestrator/TEST-CI-01_rapor_<tarih>_cline.md`
- `python scripts/gorev_kutusu.py teslim --ajan cline --task-id TEST-CI-01`

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]]


- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
