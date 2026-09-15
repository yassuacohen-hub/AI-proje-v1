# -*- coding: utf-8 -*-
"""Tests for destek module — Ticket CRUD + durum makinesi."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pytest
from company_master.destek import (
    ticket_olustur,
    ticket_getir,
    ticket_guncelle,
    ticket_sil,
    ticketlar_listele,
    durum_gecis,
    durum_gecis_depo,
    Ticket,
    GEÇERLİ_GEÇİŞLER,
)

TENANT = "test_tenant"


def setup_module():
    """Clean test data before tests."""
    dep = ROOT / "data" / "destek" / "tickets.json"
    if dep.exists():
        dep.write_text("{}", encoding="utf-8")


def teardown_module():
    """Clean test data after tests."""
    dep = ROOT / "data" / "destek" / "tickets.json"
    if dep.exists():
        dep.write_text("{}", encoding="utf-8")


def test_olustur_acik():
    """Ticket oluşturulduğunda varsayılan durum 
acik olmalı."""
    t = ticket_olustur(TENANT, "Test Başlık", "Test Açıklama")
    assert t.id is not None
    assert t.tenant_id == TENANT
    assert t.baslik == "Test Başlık"
    assert t.aciklama == "Test Açıklama"
    assert t.durum == "acik"
    assert t.olusturma != ""
    assert t.guncelleme != ""


def test_getir():
    """Oluşturulan ticket getirilebilmeli."""
    t = ticket_olustur(TENANT, "Getir Test", "Açıklama")
    got = ticket_getir(t.id)
    assert got is not None
    assert got.id == t.id
    assert got.baslik == "Getir Test"
    assert got.durum == "acik"


def test_listele_bos():
    """Boş depo için listeleme boş liste dönmeli."""
    # Clean first
    dep = ROOT / "data" / "destek" / "tickets.json"
    dep.write_text("{}", encoding="utf-8")
    lst = ticketlar_listele()
    assert isinstance(lst, list)
    assert len(lst) == 0


def test_durum_gecis_acik_inceleniyor():
    """acik -> inceleniyor geçişi geçerli olmalı."""
    t = ticket_olustur(TENANT, "Geçiş Test", "Açıklama")
    assert t.durum == "acik"
    updated = durum_gecis(t, "inceleniyor")
    assert updated.durum == "inceleniyor"
    assert updated.guncelleme != t.guncelleme


def test_durum_gecis_inceleniyor_cozuldu():
    """inceleniyor -> cozuldu geçişi geçerli olmalı."""
    t = ticket_olustur(TENANT, "Geçiş Test 2", "Açıklama")
    t = durum_gecis(t, "inceleniyor")
    updated = durum_gecis(t, "cozuldu")
    assert updated.durum == "cozuldu"


def test_durum_gecis_gecersiz_hata():
    """Geçersiz durum geçişi ValueError fırlatmalı."""
    t = ticket_olustur(TENANT, "Geçersiz Geçiş", "Açıklama")
    # acik -> cozuldu doğrudan geçersiz (inceleniyor ara adım gerekir)
    with pytest.raises(ValueError) as exc:
        durum_gecis(t, "cozuldu")
    assert "Geçersiz geçiş" in str(exc.value)


def test_guncelle():
    """Ticket başlık ve açıklama güncellenebilmeli."""
    t = ticket_olustur(TENANT, "Eski Başlık", "Eski Açıklama")
    updated = ticket_guncelle(t.id, baslik="Yeni Başlık", aciklama="Yeni Açıklama")
    assert updated is not None
    assert updated.baslik == "Yeni Başlık"
    assert updated.aciklama == "Yeni Açıklama"
    assert updated.guncelleme != t.guncelleme


def test_sil():
    """Ticket silinebilmeli ve tekrar getirilememeli."""
    t = ticket_olustur(TENANT, "Silinecek", "Açıklama")
    assert ticket_getir(t.id) is not None
    result = ticket_sil(t.id)
    assert result is True
    assert ticket_getir(t.id) is None
    # Tekrar silme False dönmeli
    assert ticket_sil(t.id) is False


def test_durum_gecis_depo():
    """durum_gecis_depo ticket durumunu depoda güncellemeli."""
    t = ticket_olustur(TENANT, "Depo Geçiş", "Açıklama")
    updated = durum_gecis_depo(t.id, "inceleniyor")
    assert updated is not None
    assert updated.durum == "inceleniyor"
    # Depodan tekrar oku
    got = ticket_getir(t.id)
    assert got.durum == "inceleniyor"


def test_listele_tenant_filtre():
    """tenant_id filtresi ile listeleme çalışmalı."""
    ticket_olustur("tenant_a", "A1", "A")
    ticket_olustur("tenant_b", "B1", "B")
    ticket_olustur("tenant_a", "A2", "A")
    lst_a = ticketlar_listele(tenant_id="tenant_a")
    assert len(lst_a) == 2
    assert all(t.tenant_id == "tenant_a" for t in lst_a)
    lst_b = ticketlar_listele(tenant_id="tenant_b")
    assert len(lst_b) == 1
    assert lst_b[0].tenant_id == "tenant_b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
