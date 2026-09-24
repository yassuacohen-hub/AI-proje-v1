"""Admin panel sekmeleri için ortak DB yardımcı fonksiyonları.

UI-ADMIN-SAHTE-KPI-01 / UI-ADMIN-SAHTE-EXEC-02: sorgulanan tablo DB'de yoksa
sessizce 0 dönmek yerine önce varlığı kontrol edilir; yoksa çağıran kod
"veri kaynağı yok" rozeti gösterir.
"""
from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.engine import Engine


def tablo_var_mi(ad: str, engine: Engine | None = None) -> bool:
    """Verilen tablo adının aktif veritabanında var olup olmadığını döner."""
    if engine is None:
        from company_master.db.connection import get_engine

        engine = get_engine()
    return inspect(engine).has_table(ad)
