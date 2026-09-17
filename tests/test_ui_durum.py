# -*- coding: utf-8 -*-
"""ADMIN-ROO-01 Aşama A: durum bileşenleri (hata_kutusu / bos_durum / yukleniyor / api_cagir)."""
from __future__ import annotations

import sys
import types

import pytest

from company_master.ui.components import durum as d


# ---------------------------------------------------------------------------
# Sahte Streamlit
# ---------------------------------------------------------------------------
class _SahteSt:
    def __init__(self) -> None:
        self.session_state: dict = {}
        self.yazilan: list[str] = []

    def markdown(self, html: str, unsafe_allow_html: bool = False) -> None:
        assert unsafe_allow_html is True
        self.yazilan.append(html)


@pytest.fixture()
def sahte_st(monkeypatch):
    st = _SahteSt()
    modul = types.ModuleType("streamlit")
    modul.session_state = st.session_state  # type: ignore[attr-defined]
    modul.markdown = st.markdown  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "streamlit", modul)
    return st


# ---------------------------------------------------------------------------
# hata_metni_kisalt
# ---------------------------------------------------------------------------
def test_hata_metni_istisna_tur_ve_mesaj():
    assert d.hata_metni_kisalt(ValueError("kötü değer")) == "ValueError: kötü değer"


def test_hata_metni_istisna_mesajsiz_yalniz_tur():
    assert d.hata_metni_kisalt(RuntimeError()) == "RuntimeError"


def test_hata_metni_bos_none():
    assert d.hata_metni_kisalt(None) == "Bilinmeyen hata"
    assert d.hata_metni_kisalt("   ") == "Bilinmeyen hata"


def test_hata_metni_satir_sonu_ve_kirpma():
    uzun = "satır1\nsatır2\t" + "x" * 500
    sonuc = d.hata_metni_kisalt(uzun)
    assert "\n" not in sonuc and "\t" not in sonuc
    assert len(sonuc) <= d.HATA_METIN_LIMIT
    assert sonuc.endswith("…")


# ---------------------------------------------------------------------------
# HTML üretimi (Streamlit gerektirmez)
# ---------------------------------------------------------------------------
def test_hata_kutusu_html_yapi_ve_kacis():
    html = d.hata_kutusu_html("KPI alınamadı", "<script>x</script>", ipucu="API <b>8000</b>")
    assert 'class="hg-durum hg-durum-hata"' in html
    assert 'role="alert"' in html
    assert "KPI alınamadı" in html
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "<b>" not in html and "&lt;b&gt;8000" in html
    assert "hg-durum-ipucu" in html


def test_hata_kutusu_html_ipucu_yoksa_satir_yok():
    html = d.hata_kutusu_html("Başlık", "hata")
    assert "hg-durum-ipucu" not in html


def test_bos_durum_html():
    html = d.bos_durum_html("Kayıt yok", ikon="🗂️", aksiyon="Filtreyi temizle")
    assert 'class="hg-durum hg-durum-bos"' in html
    assert 'role="status"' in html
    assert "🗂️" in html and "Kayıt yok" in html
    assert "hg-durum-aksiyon" in html and "Filtreyi temizle" in html


def test_bos_durum_html_aksiyonsuz():
    html = d.bos_durum_html("Boş")
    assert "hg-durum-aksiyon" not in html
    assert "📭" in html


def test_yukleniyor_html():
    html = d.yukleniyor_html("Veri çekiliyor")
    assert "hg-durum-yukleniyor" in html
    assert 'aria-live="polite"' in html
    assert "Veri çekiliyor" in html


def test_css_sabit_renk_icermez():
    # tokens.py SSOT: ham hex/rgba yok, yalnız var(--hg-*) referansları
    assert "#" not in d.DURUM_CSS
    assert "rgba(" not in d.DURUM_CSS
    assert "var(--hg-color-danger)" in d.DURUM_CSS
    assert "var(--hg-radius-card)" in d.DURUM_CSS


# ---------------------------------------------------------------------------
# render (sahte streamlit)
# ---------------------------------------------------------------------------
def test_hata_kutusu_render_css_bir_kez(sahte_st):
    d.hata_kutusu("A", "x")
    d.hata_kutusu("B", "y")
    css_sayisi = sum(1 for h in sahte_st.yazilan if "<style>" in h)
    assert css_sayisi == 1
    assert sahte_st.session_state[d._CSS_SESSION_ANAHTARI] is True
    assert sum(1 for h in sahte_st.yazilan if "hg-durum-hata" in h and "<style>" not in h) == 2


def test_bos_durum_ve_yukleniyor_render(sahte_st):
    cikti1 = d.bos_durum("Yok")
    cikti2 = d.yukleniyor()
    assert cikti1 in sahte_st.yazilan and cikti2 in sahte_st.yazilan
    assert "Yükleniyor…" in cikti2


def test_render_container_hedefi(sahte_st):
    class Kap:
        def __init__(self) -> None:
            self.yazilan: list[str] = []

        def markdown(self, html: str, unsafe_allow_html: bool = False) -> None:
            self.yazilan.append(html)

    kap = Kap()
    d.hata_kutusu("A", "x", container=kap)
    assert len(kap.yazilan) == 1 and "hg-durum-hata" in kap.yazilan[0]
    # CSS yine st'ye (global) yazılır
    assert any("<style>" in h for h in sahte_st.yazilan)


# ---------------------------------------------------------------------------
# api_cagir
# ---------------------------------------------------------------------------
def test_api_cagir_basarili_deger_doner(sahte_st):
    assert d.api_cagir(lambda a, b=0: a + b, 2, b=3, baslik="Topla") == 5
    assert sahte_st.yazilan == []


def test_api_cagir_hata_none_ve_kutu(sahte_st, caplog):
    def patlat():
        raise ConnectionError("8000 kapalı")

    with caplog.at_level("WARNING"):
        sonuc = d.api_cagir(patlat, baslik="API erişilemedi")
    assert sonuc is None
    govde = [h for h in sahte_st.yazilan if "<style>" not in h]
    assert len(govde) == 1
    assert "API erişilemedi" in govde[0]
    assert "ConnectionError: 8000 kapalı" in govde[0]
    assert "docker compose ps api" in govde[0]  # varsayılan ipucu
    assert "api_cagir" in caplog.text


def test_api_cagir_ipucu_kapatilabilir(sahte_st):
    d.api_cagir(lambda: 1 / 0, baslik="Böl", ipucu=None)
    govde = [h for h in sahte_st.yazilan if "<style>" not in h][0]
    assert "hg-durum-ipucu" not in govde
    assert "ZeroDivisionError" in govde


def test_paket_disa_aktarim():
    from company_master import ui
    from company_master.ui import components

    for ad in ("api_cagir", "bos_durum", "hata_kutusu", "yukleniyor"):
        assert ad in ui.__all__ and ad in components.__all__
        assert getattr(ui, ad) is getattr(d, ad)
