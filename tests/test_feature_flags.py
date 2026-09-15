# -*- coding: utf-8 -*-
"""PO-BACK-07: Feature Flags MVP testleri.

Kapsam:
  - flag_acik: env > tenant > global priority
  - flag_ayarla: deger ayarlama
  - flaglar_listele: tum flaglar
  - flag_gerekli decorator: flag kapali -> None
  - bilinmeyen flag -> False
  - HUGINN_FLAG_<AD> env kontrolu
"""

from __future__ import annotations

import os
from unittest import mock

import pytest

from company_master.feature_flags import (
    FLAGS_PATH,
    _DEFAULT_FLAGS,
    _kaydet,
    _yukle,
    flag_acik,
    flag_gerekli,
    flag_ayarla,
    flaglar_listele,
)


@pytest.fixture(autouse=True)
def _reset_flags():
    """Her test sonrasi flaglari varsayilana geri yukle."""
    _kaydet(dict(_DEFAULT_FLAGS))
    yield
    _kaydet(dict(_DEFAULT_FLAGS))
    for key in list(os.environ.keys()):
        if key.startswith("HUGINN_FLAG_"):
            del os.environ[key]


def test_flag_acik_global_true():
    """Global flag True -> True."""
    assert flag_acik('data_quality_score') is True

def test_flag_acik_global_false():
    """Global flag False -> False."""
    flag_ayarla('source_reliability', False)
    assert flag_acik('source_reliability') is False

def test_flag_acik_bilinmeyen_false():
    """Bilinmeyen flag -> False."""
    assert flag_acik('yok_boyle_bir_flag') is False

def test_flag_acik_env_overrides_global():
    """Env HUGINN_FLAG_<AD> global i override eder."""
    with mock.patch.dict(os.environ, {'HUGINN_FLAG_DATA_QUALITY_SCORE': 'false'}):
        assert flag_acik('data_quality_score') is False

def test_flag_acik_env_true_when_global_false():
    """Env True, global False -> True."""
    flag_ayarla('source_reliability', False)
    with mock.patch.dict(os.environ, {'HUGINN_FLAG_SOURCE_RELIABILITY': 'true'}):
        assert flag_acik('source_reliability') is True

def test_flag_ayarla_kaydet():
    """flag_ayarla kaydeder."""
    flag_ayarla('test_flag', True)
    assert flag_acik('test_flag') is True

def test_flag_ayarla_false():
    """False de de kaydedilir."""
    flag_ayarla('test_flag_2', False)
    assert flag_acik('test_flag_2') is False

def test_flaglar_listele_icerik():
    """flaglar_listele dict dondurur."""
    result = flaglar_listele()
    assert isinstance(result, dict)
    assert 'data_quality_score' in result
    assert 'source_reliability' in result

def test_flag_gerekli_acik_calisir():
    """Flag aciksa decorator fonksiyon calisir."""
    @flag_gerekli('data_quality_score')
    def sonuc():
        return 'calisti'
    assert sonuc() == 'calisti'

def test_flag_gerekli_kapali_none():
    """Flag kapaliysa decorator None dondurur."""
    @flag_gerekli('yok_flag')
    def sonuc():
        return 'calisti'
    assert sonuc() is None

def test_flag_gerekli_degistir_true():
    """Flag True yapilabilir."""
    @flag_gerekli('toggle_flag')
    def sonuc():
        return 'calisti'
    flag_ayarla('toggle_flag', True)
    assert sonuc() == 'calisti'
    flag_ayarla('toggle_flag', False)
    assert sonuc() is None
