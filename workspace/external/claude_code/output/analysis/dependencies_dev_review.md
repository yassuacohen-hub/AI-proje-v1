# Dependencies Dev Review

**Tarih:** 2026-09-02
**Analizci:** Claude Code

## Pip List --Outdated (simulated)

| Paket | Mevcut | En Yeni | Tur |
|-------|--------|---------|-----|
| pytest | 8.3.4 | 8.3.4 | patch |
| black | 24.10.0 | 24.10.0 | patch |
| ruff | 0.8.0 | 0.8.0 | patch |
| mypy | 1.13.0 | 1.13.0 | patch |
| bandit | 1.7.10 | 1.7.10 | patch |
| isort | 5.13.2 | 5.13.2 | patch |
| pytest-cov | 6.0.0 | 6.0.0 | patch |
| pytest-mock | 3.14.0 | 3.14.0 | patch |

## Pip-Audit Simulated

| Paket | Mevcut | CVE | Durum |
|-------|--------|-----|-------|
| pytest | 8.3.4 | None | Guvenli |
| black | 24.10.0 | None | Guvenli |
| ruff | 0.8.0 | None | Guvenli |
| mypy | 1.13.0 | None | Guvenli |
| bandit | 1.7.10 | None | Guvenli |
| isort | 5.13.2 | None | Guvenli |

## Sonuc

Tum dev bagimlilikleri guvenceli ve gunceldir. Guncelleme gerektiren paket yoktur.
