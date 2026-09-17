# FMT-01 — ruff format/lint standardizasyonu (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-01_ortak_kurallar.md`. Zincir halkası 5/6.

## Kapsam
- `src/company_master/**`, `scripts/**`, `tests/**`, `wiki_automation/**`.
- **HARİÇ:** `web_app.py`, `app.py`, `web_dashboard/**` (cline / API-SPLIT-01), `tests/test_auth_gate.py`, `scripts/admin_login_probe.py`, `AI proje v1/`, `data/`, `workspace/`.
- Config: mevcut `pyproject.toml`/`ruff.toml` varsa kullan; yoksa `ruff.toml` oluştur (`line-length = 120`, `target-version = "py311"`, `select = ["E","F","W","I","UP"]`, `ignore = ["E501"]` yalnız gerekçeyle).

## İş
1. `pip install ruff` (requirements-dev.txt'e `ruff>=0.6` ekle).
2. Önce **lint sayımı**: `ruff check <kapsam> --statistics` → rapora.
3. `ruff check --fix` (yalnız güvenli fix'ler; `--unsafe-fixes` YASAK).
4. `ruff format <kapsam>`.
5. Her adımdan sonra tam süit; kırılan test varsa format değil kod hatası → geri al, rapora yaz.
6. `.pre-commit-config.yaml`'a `ruff` + `ruff-format` hook (kapsam exclude ile aynı).
7. Kalan ihlaller (fix edilemeyen) → rapora kod bazlı tablo; elle düzeltme YALNIZ `F` (pyflakes) ailesi.

## Teslim kriteri
- `ruff check <kapsam>` → yalnız gerekçeli kalanlar; `ruff format --check <kapsam>` temiz.
- Tam süit yeşil (test sayısı değişmez); kodlama_denetim temiz.
- Rapor: `data/orchestrator/FMT-01_rapor_<tarih>_kilo.md` (önce/sonra ihlal sayısı, değişen dosya sayısı).
