# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import pytest
KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / 'src'))
from company_master.odin_ai import mimir_servis as ms


def test_tanimsiz_rol_valueerror():
    with pytest.raises(ValueError):
        ms.prompt_yukle('admin')


def test_varsayilan_rol_dis():
    assert len(ms.prompt_yukle('ic')) > len(ms.prompt_yukle())


class SahteHit:
    def __init__(self, id, metin):
        self.id = id
        self.metadata = {'text': metin, 'nace_code': '24.51',
                         'last_updated': '2026-09-28'}


class SahteServis:
    def __init__(self, i):
        self._i = i

    def find_similar(self, text, top_k=5, where=None):
        return self._i[:top_k]


def test_bos_baglam_model_cagrilmaz():
    sayac = {'n': 0}

    def cevapla(p):
        sayac['n'] += 1
        return 'x'

    out = ms.mimir_sohbet('bilinmeyen', cevapla, servis=SahteServis([]))
    assert sayac['n'] == 0
    assert out == ms.BOS_BAGLAM_YANITI


def test_dolu_baglam_cagrilir():
    gorunen = {'p': ''}

    def cevapla(p):
        gorunen['p'] = p
        return 'OSTIM'

    ms.mimir_sohbet('dokumcu', cevapla,
                    servis=SahteServis([SahteHit('f1', 'OSTIM')]))
    assert '<BAGLAM>' in gorunen['p']


def test_prompt_kodda_yok():
    src = (KOK / 'src/company_master/odin_ai/mimir_servis.py').read_text(
        encoding='utf-8')
    assert "Sen Mimir'sin" not in src


def test_katalog_kaynak_yoksa_bos(monkeypatch):
    monkeypatch.setenv('MIMIR_KATALOG_DOSYASI', '')
    assert ms.katalog_uret() == ''
