# -*- coding: utf-8
"""F3 Kredi cuzdani — 4 kabul testi (brief adim 4).

Kapsam: bos bakiye 0; alim artirir; tuketim dusurur; yetersizde hata.
Gercek DB kullanilir. SQLAlchemy 2.x: connect() ROLLBACK yapar,
bu yuzden begin() kullanilir (yoksa kayitlar kaybolur).
"""
import sys, pathlib

import pytest
from sqlalchemy import text

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT))

from company_master.db.connection import get_engine
from src.company_master import kredi


@pytest.fixture
def sirket():
    """Gecerli company_id verir; test sonrasi test kayitlarini siler."""
    with get_engine().begin() as conn:
        cid = str(conn.execute(text('SELECT company_id FROM companies LIMIT 1')).scalar())
    yield cid
    with get_engine().begin() as conn:
        conn.execute(text('DELETE FROM kullanim_log WHERE company_id = :c'), {'c': cid})
        conn.execute(text('DELETE FROM kredi_hareket WHERE company_id = :c'), {'c': cid})


def _hareket(cid, miktar: int):
    """kredi_hareket satir ekler (dengede kalir)."""
    sql = 'INSERT INTO kredi_hareket (company_id, miktar, neden) VALUES (:c, :m, :n)'
    with get_engine().begin() as conn:
        conn.execute(text(sql), {'c': cid, 'm': miktar, 'n': 'test'})


def test_bos_bakiye_sifirdir(sirket):
    """Kayit yoksa bakiye 0 (kabul 1)."""
    assert kredi.bakiye(sirket) == 0


def test_kredi_alim_bakiyeyi_artirir(sirket):
    """+100 hareket -> bakiye 100 (kabul 2)."""
    _hareket(sirket, 100)
    assert kredi.bakiye(sirket) == 100


def test_kullanim_bakiyeyi_dusurur(sirket):
    """100 al, 30 harca -> 70 (kabul 3)."""
    _hareket(sirket, 100)
    kredi.kullanim_yaz(sirket, 'arama', 'test', 30)
    assert kredi.bakiye(sirket) == 70


def test_yetersiz_kredide_hata_firlatir(sirket):
    """0 bakiye, 10 maliyet -> KrediYetersiz (kabul 4, yazma kapisi)."""
    with pytest.raises(kredi.KrediYetersiz):
        kredi.kullanim_yaz(sirket, 'arama', 'test', 10)
