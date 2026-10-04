# -*- coding: utf-8 -*-
"""§8.4: Overview aksiyon şeridi ve giriş kartları için asgari koşum.

Streamlit çalışma zamanı olmadan test edilebilen saf parçalar: sonuç saklama,
buton renk token'ları, giriş kartlarının gerçek sekmelere işaret etmesi.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from company_master.ui.tokens import RENKLER
from web_dashboard.tabs import tab_getir


@pytest.fixture(autouse=True)
def _oturum(monkeypatch):
    """`st.session_state` yerine düz sözlük koyar (runtime gerekmez)."""
    import web_dashboard.tabs.ana_kontrol as ak

    monkeypatch.setattr(ak.st, "session_state", {}, raising=False)
    return ak


def test_giris_karti_dead_code_kaldirildi(_oturum) -> None:
    """D-266/KART-36: cizilmeyen GIRIS_KARTLARI tuple'i kaldirildi."""
    assert not hasattr(_oturum, "GIRIS_KARTLARI")


def test_kaynaklar_sekmesi_tab_getirden_cozulur(_oturum) -> None:
    """KK-12 K1c: Ana Kontrol'den /kaynaklar tek tıkla erişilebilir olmalı."""
    assert tab_getir("kaynaklar").url_path == "kaynaklar"


def test_buton_renkleri_token_disina_cikmaz(_oturum) -> None:
    izinli = set(RENKLER.values())
    assert set(_oturum._AKSIYON_RENK.values()) <= izinli
    assert len(_oturum._AKSIYON_RENK) == 4  # link_button'lar bu sozlukte degil


def test_sonuc_yaz_oturuma_yazar(_oturum) -> None:
    _oturum._sonuc_yaz("success", "tamam")
    tip, mesaj, saat = _oturum.st.session_state["ovw_sonuc"]
    assert (tip, mesaj) == ("success", "tamam")
    assert len(saat) == 8  # HH:MM:SS


def test_saglik_kontrolu_api_yoksa_hata_verir(_oturum) -> None:
    with patch.object(_oturum, "get_api", side_effect=RuntimeError("baglanti yok")):
        _oturum._saglik_kontrolu()
    tip, mesaj, _ = _oturum.st.session_state["ovw_sonuc"]
    assert tip == "error"
    assert "🔴" in mesaj


def test_saglik_kontrolu_api_varsa_yesil(_oturum) -> None:
    with patch.object(_oturum, "get_api", return_value={}):
        _oturum._saglik_kontrolu()
    tip, mesaj, _ = _oturum.st.session_state["ovw_sonuc"]
    assert tip == "success"
    assert "🔴" not in mesaj


def test_csv_hazirla_bos_veride_kayit_yazmaz(_oturum) -> None:
    with patch.object(_oturum, "get_api", return_value=[]):
        _oturum._csv_hazirla()
    assert "ovw_csv" not in _oturum.st.session_state
    assert _oturum.st.session_state["ovw_sonuc"][0] == "info"


def test_csv_hazirla_veriyle_csv_uretir(_oturum) -> None:
    with patch.object(_oturum, "get_api", return_value=[{"ad": "A"}, {"ad": "B"}]):
        _oturum._csv_hazirla()
    assert "ad" in _oturum.st.session_state["ovw_csv"]
    assert _oturum.st.session_state["ovw_sonuc"][0] == "success"


def test_veri_guncelle_hata_kodunda_hata_yazar(_oturum) -> None:
    class _Proc:
        returncode = 1
        stdout = ""
        stderr = "hat calismadi"

    with patch.object(_oturum.subprocess, "run", return_value=_Proc()):
        _oturum._veri_guncelle()
    assert _oturum.st.session_state["ovw_sonuc"][0] == "error"
