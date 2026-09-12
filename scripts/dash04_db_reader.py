from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sqlalchemy import text

from company_master.db.connection import get_engine


class DBQueryError(RuntimeError):
    pass


def read_only_query(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if not isinstance(query, str):
        raise ValueError("Sorgu metni string olmalıdır.")

    normalized_query = query.strip().upper()
    if not re.match(r"^SELECT(?:\s|$)", normalized_query):
        raise ValueError("Yalnızca SELECT ile başlayan okuma sorguları çalıştırılabilir.")

    statement = query.strip()
    if ";" in statement.rstrip(";").strip():
        raise ValueError("Tek bir SELECT sorgusu giriniz.")

    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            return [dict(row) for row in result.mappings().all()]
    except Exception as exc:
        raise DBQueryError("Veritabanı bağlantısı veya okuma sorgusu başarısız.") from exc