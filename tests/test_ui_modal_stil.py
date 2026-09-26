# -*- coding: utf-8 -*-
"""ADMIN-MODAL-STIL-01: modal CSS'inde blur + marka kimliği garantisi.

KAHİN bulgusu: "arka plan blur efekti yok", "modal marka kimliğini yansıtmıyor".
Bu test o iki düzeltmenin geri gitmesini engeller.
"""
from __future__ import annotations

from company_master.ui.styles import _CONTAINER_CSS, _MODAL_CSS, tum_css


def test_backdrop_blur_var() -> None:
    """Arka plan bulanıklığı ve Safari öneki birlikte bulunmalı."""
    assert "backdrop-filter:blur(10px)" in _MODAL_CSS
    assert "-webkit-backdrop-filter:blur(10px)" in _MODAL_CSS


def test_marka_kimligi_var() -> None:
    """Modal üst şeridi marka rengini, başlık okunabilir marka tonunu kullanmalı."""
    assert "border-top:3px solid var(--hg-color-primary)" in _MODAL_CSS
    assert "color:var(--hg-color-primary-text)" in _MODAL_CSS


def test_css_suslu_parantez_dengeli() -> None:
    assert _MODAL_CSS.count("{") == _MODAL_CSS.count("}")


def test_modal_css_uretilen_temada_yer_alir() -> None:
    """_MODAL_CSS bloğu tum_css() çıktısına gerçekten giriyor."""
    for tema in ("karanlik", "aydinlik"):
        css = tum_css(tema=tema)
        assert ".hg-modal-backdrop" in css
        assert "backdrop-filter:blur(10px)" in css


def test_container_cerceve_kategori_rengi_yok() -> None:
    """K3-10h madde 4: tüm bordered container'lar tek global kuralla kalınlaşır;
    kategori rengi (KATEGORI_RENK) YOK, yalnız border-strong token'ı kullanılır."""
    assert 'div[data-testid="stVerticalBlockBorderWrapper"]' in _CONTAINER_CSS
    assert "border:2px solid var(--hg-color-border-strong)" in _CONTAINER_CSS
    for tema in ("karanlik", "aydinlik"):
        assert _CONTAINER_CSS.strip() in tum_css(tema=tema)


if __name__ == "__main__":  # tek çalıştırılabilir kontrol
    test_backdrop_blur_var()
    test_marka_kimligi_var()
    test_css_suslu_parantez_dengeli()
    test_modal_css_uretilen_temada_yer_alir()
    test_container_cerceve_kategori_rengi_yok()
    print("OK: modal stil kontrolleri gecti")
