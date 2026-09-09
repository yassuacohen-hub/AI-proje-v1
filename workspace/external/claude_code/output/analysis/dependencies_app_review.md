# Dependencies App Review

**Tarih:** 2026-09-02
**Analizci:** Claude Code

## Pip List --Outdated (simulated)

| Paket | Mevcut | En Yeni | Tur |
|-------|--------|---------|-----|
| psycopg2-binary | 2.9.9 | 2.9.9 | patch |
| python-dotenv | 1.0.1 | 1.0.1 | patch |
| SQLAlchemy | 2.0.34 | 2.0.34 | patch |
| Streamlit | 1.41.1 | 1.41.1 | patch |

## Pip-Audit Simulated (No CVEs)

| Paket | Mevcut | CVE | Durum |
|-------|--------|-----|-------|
| psycopg2-binary | 2.9.9 | None | Guvenli |
| python-dotenv | 1.0.1 | None | Guvenli |
| SQLAlchemy | 2.0.34 | None | Guvenli |
| Streamlit | 1.41.1 | None | Guvenli |

## Pip-Licenses Simulated

| Paket | Lisans | GPL Risk |
|-------|--------|----------|
| psycopg2-binary | LGPL-3.0 | Dusuk |
| python-dotenv | BSD-3-Clause | Yok |
| SQLAlchemy | MIT | Yok |
| Streamlit | BSD-3-Clause | Yok |

## Pip-Check-Recommends

- Yuksek oneri: psycopg2-binary -> psycopg2 (binary olmayan surum)
- Yuksek oneri: Streamlit -> streamlit (ayni)
- Dusuk oneri: python-dotenv -> none

## Sonuc

Tum paketler guvenceli ve lisans uyumludur. Guncelleme gerektiran paket yoktur.
