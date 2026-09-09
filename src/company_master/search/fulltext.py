"""PostgreSQL Full Text Search sarmalayıcısı."""

from typing import Any, Dict, List


def search_companies(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Unvan/adres üzerinde full text search yapar (iskelet)."""
    raise NotImplementedError(
        "search_companies henüz implemente edilmedi. "
        "PostgreSQL bağlantısı ve tsvector index'i TODO P0'da tanımlı."
    )
