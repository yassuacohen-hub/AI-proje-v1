"""Migration çalıştırıcı (PostgreSQL).

`schema/migrations/` altındaki numaralı SQL dosyalarını sırayla uygular.
Uygulanan migration'lar `schema_migrations` tablosunda takip edilir.

Kullanım:
    python -m company_master.db.migrate            # bekleyen migration'ları uygula
    python -m company_master.db.migrate --status   # durum raporu
"""

from __future__ import annotations
import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List
from sqlalchemy import create_engine, text
from .connection import get_database_url

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "schema" / "migrations"

_TRACKING_DDL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename   TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
"""

@dataclass
class MigrationResult:
    filename: str
    applied: bool
    error: str | None = None

def _pending_files(applied: set[str]) -> List[Path]:
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    return [f for f in files if f.name not in applied]

def _split_statements(sql: str) -> List[str]:
    """Basit noktalı virgül ayırıcı; yorum satırlarını atar."""
    statements: List[str] = []
    for chunk in sql.split(";"):
        lines = [
            line for line in chunk.splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        stmt = "\n".join(lines).strip()
        if stmt:
            statements.append(stmt)
    return statements

def _engine_url(database_url: str | None = None) -> str:
    url = database_url or get_database_url()
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

def apply_migrations(database_url: str | None = None) -> List[MigrationResult]:
    engine = create_engine(_engine_url(database_url), future=True)
    with engine.begin() as conn:
        conn.execute(text(_TRACKING_DDL))
        applied = {
            row[0] for row in conn.execute(text("SELECT filename FROM schema_migrations"))
        }

    results: List[MigrationResult] = []
    for path in _pending_files(applied):
        sql = path.read_text(encoding="utf-8")
        try:
            with engine.begin() as conn:
                for stmt in _split_statements(sql):
                    conn.execute(text(stmt))
                conn.execute(
                    text("INSERT INTO schema_migrations (filename) VALUES (:f)"),
                    {"f": path.name},
                )
            results.append(MigrationResult(filename=path.name, applied=True))
        except Exception as exc:
            results.append(MigrationResult(filename=path.name, applied=False, error=str(exc)))
            break
    return results

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    engine = create_engine(_engine_url(), future=True)
    with engine.begin() as conn:
        conn.execute(text(_TRACKING_DDL))
        applied = {
            row[0] for row in conn.execute(text("SELECT filename FROM schema_migrations"))
        }

    all_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if args.status:
        for f in all_files:
            mark = "[uygulandı]" if f.name in applied else "[bekliyor]"
            print(f"{mark} {f.name}")
        return 0

    results = apply_migrations()
    for r in results:
        print(f"{'OK' if r.applied else 'HATA'} {r.filename} {r.error or ''}")
    return 0 if not results or all(r.applied for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
