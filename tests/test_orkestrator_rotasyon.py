# -*- coding: utf-8 -*-
"""Orkestratör rotasyon mekanizmasının testleri."""
from __future__ import annotations

import json

import pytest

from scripts.orkestrator_rotasyon import (
    BASLANGIC_ORKESTRATOR,
    aktif_orkestrator,
    rotasyon_yap,
)

CHANGELOG_ORNEK = (
    "# CHANGELOG\n"
    "\n"
    "Kronolojik değişiklik günlüğü.\n"
    "\n"
    "## [2026-01-01] Eski Kayıt\n"
    "\n"
    "- eski madde\n"
)


@pytest.fixture
def ortam(tmp_path):
    """Geçici JSONL + CHANGELOG çifti (gerçek dosyalara dokunmaz)."""
    log = tmp_path / "decision_log.jsonl"
    log.write_text("", encoding="utf-8")
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(CHANGELOG_ORNEK, encoding="utf-8")
    return log, cl


def _satirlar(log) -> list[dict]:
    return [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_yanlis_kelime_reddedilir(ortam):
    """Yanlış ritüel sözcüğünde kayıt atılmaz, dosya değişmez."""
    log, cl = ortam
    with pytest.raises(PermissionError):
        rotasyon_yap("roo", "yanlis-kelime", log_path=log, changelog_path=cl)
    assert _satirlar(log) == []
    assert "Orkestratör Rotasyonu" not in cl.read_text(encoding="utf-8")


def test_dogru_kelime_kayit_atar(ortam):
    """Doğru ritüelde yapılandırılmış kayıt (kimden/kime/tetikleyici) düşer."""
    log, cl = ortam
    kayit = rotasyon_yap("roo", "abrakadabra", gerekce="test",
                         log_path=log, changelog_path=cl)
    satirlar = _satirlar(log)
    assert len(satirlar) == 1
    assert satirlar[0]["action"] == "orkestrator_rotasyonu"
    assert satirlar[0]["kimden"] == BASLANGIC_ORKESTRATOR
    assert satirlar[0]["kime"] == "roo"
    assert satirlar[0]["tetikleyici"] == "sahip"
    assert satirlar[0]["gerekce"] == "test"
    assert kayit["kime"] == "roo"


def test_aktif_orkestrator_varsayilan(ortam):
    """Hiç rotasyon kaydı yokken varsayılan orkestratör döner."""
    log, _ = ortam
    assert aktif_orkestrator(log) == BASLANGIC_ORKESTRATOR


def test_rotasyon_sonrasi_aktif_gunceller(ortam):
    """Ardışık rotasyonlarda aktif orkestratör hep son 'kime' olur."""
    log, cl = ortam
    rotasyon_yap("roo", "abrakadabra", log_path=log, changelog_path=cl)
    assert aktif_orkestrator(log) == "roo"
    rotasyon_yap("kilo", "abrakadabra", log_path=log, changelog_path=cl)
    assert aktif_orkestrator(log) == "kilo"


def test_karisan_sema_rotasyonu_atlamaz(ortam):
    """Karışık şemalı log'da (title'lı eski kayıtlar) rotasyon kayıtları doğru seçilir."""
    log, cl = ortam
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"title": "Başka karar", "decision": "accepted"}) + "\n")
    rotasyon_yap("roo", "abrakadabra", log_path=log, changelog_path=cl)
    assert aktif_orkestrator(log) == "roo"


def test_changelog_guncellenir(ortam):
    """CHANGELOG'a tarihli rotasyon bölümü ilk tarihli başlıktan önce eklenir."""
    log, cl = ortam
    rotasyon_yap("roo", "abrakadabra", gerekce="devir", log_path=log, changelog_path=cl)
    text = cl.read_text(encoding="utf-8")
    assert "Orkestratör Rotasyonu" in text
    assert "## [2026-01-01] Eski Kayıt" in text
    assert text.index("Orkestratör Rotasyonu") < text.index("## [2026-01-01] Eski Kayıt")


def test_import():
    """Fonksiyonlar import edilebildiğini kontrol eder."""
    assert callable(aktif_orkestrator)
    assert callable(rotasyon_yap)
