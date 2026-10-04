# -*- coding: utf-8
"""F3 Kredi cuzdani - bakiye hesabi ve yazma kapisi.

Tablolar (0051_kredi_cuzdani.sql):
  - kullanim_log: her tuketim bir satir (maliyet_kredi dusurur)
  - kredi_hareket: alim/satim (negatif = harcam)

Kapsam (YAGNI): yalniz hesap + kapisi. Odeme saglayici/webhook YOK.

Kullanim:
    from src.company_master.kredi import kullanim_yaz, bakiye, dusebilir_mi
"""
from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from company_master.db.connection import get_engine


class KrediYetersiz(Exception):
    """Bakiye maliyeti karsilamiyor. """


def bakiye(company_id) -> int:
    '''Kalan kredi: SUM(kredi_hareket) - SUM(kullanim_log). Kayit yoksa 0.'''
    sql = 'SELECT COALESCE((SELECT SUM(miktar) FROM kredi_hareket WHERE company_id = :c), 0)'
    sql += ' - COALESCE((SELECT SUM(maliyet_kredi) FROM kullanim_log WHERE company_id = :c), 0)'
    with get_engine().connect() as conn:
        return int(conn.execute(text(sql), {'c': str(company_id)}).scalar() or 0)


def dusebilir_mi(company_id, maliyet: int) -> bool:
    '''Bakiye maliyeti karsiliyor mu? Yazma kapisi bunu cagirir.'''
    return bakiye(company_id) >= int(maliyet)


def kullanim_yaz(company_id, tur: str, source_name: str, maliyet_kredi: int) -> int:
    '''Tuketimi yazar. Bakiye yetmezse KrediYetersiz firlatir (yazma kapisi).'''
    maliyet = int(maliyet_kredi)
    if not dusebilir_mi(company_id, maliyet):
        raise KrediYetersiz(
            f'bakiye yetersiz: {bakiye(company_id)} < {maliyet}'
        )
    sql = 'INSERT INTO kullanim_log (company_id, tur, source_name, maliyet_kredi)'
    sql += ' VALUES (:c, :t, :k, :m) RETURNING id'
    with get_engine().begin() as conn:
        return int(conn.execute(text(sql), {'c': str(company_id), 't': tur,
                                             'k': source_name, 'm': maliyet}).scalar())
